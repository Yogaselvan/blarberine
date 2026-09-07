# Copyright (c) 2026, Blarberine and contributors
# Public booking API for the Blarberine barbershop site.
#
# Both endpoints are whitelisted with allow_guest=True because the public
# website (anonymous visitors, not logged-in Desk users) calls them during
# the booking flow.

import re

import frappe
from frappe import _

# Monday=0 ... Sunday=6, matching datetime.date.weekday()
WEEKDAYS = [
    "Monday", "Tuesday", "Wednesday",
    "Thursday", "Friday", "Saturday", "Sunday",
]

# A same-day slot must start at least this many minutes from now.
MIN_LEAD_MINUTES = 15

SHOP_NAME = "Blarberinė"
SHOP_ADDRESS = "Utenos g. 16, Kaunas"

# Role copied on every barber's booking (task 3). Created by patch.
MANAGER_ROLE = "Barbers Manager"

# A reminder this many minutes before the visit (task 5). Bookings made inside
# this window get no reminder — the manager asked to skip those.
REMINDER_LEAD_MINUTES = 120
# Width of the slice the reminder job scans; must match the cron interval in
# hooks.py or appointments would be missed (too narrow) or double-sent.
REMINDER_WINDOW_MINUTES = 15


def _to_minutes(value):
    """Normalise a Frappe Time value to minutes-since-midnight.

    Frappe returns Time fields as datetime.timedelta; client/string input
    arrives as "HH:MM" or "HH:MM:SS". Returns None for empty values.
    """
    if value is None or value == "":
        return None
    # datetime.timedelta (how the DB hands back Time fields)
    if hasattr(value, "total_seconds"):
        return int(value.total_seconds() // 60)
    # datetime.time
    if hasattr(value, "hour") and hasattr(value, "minute"):
        return value.hour * 60 + value.minute
    # string "HH:MM" or "HH:MM:SS"
    parts = str(value).split(":")
    return int(parts[0]) * 60 + int(parts[1])


def _fmt(minutes):
    """Minutes-since-midnight -> 'HH:MM'."""
    return "%02d:%02d" % (minutes // 60, minutes % 60)


def _lead_cutoff(date_obj):
    """Earliest bookable start (minutes-since-midnight) for `date_obj`.

    Past dates get an impossible cutoff (whole day unbookable); today gets
    now + MIN_LEAD_MINUTES in the site's timezone; future dates get 0.
    """
    now = frappe.utils.now_datetime()
    today = now.date()
    if date_obj < today:
        return 24 * 60 + 1
    if date_obj == today:
        return now.hour * 60 + now.minute + MIN_LEAD_MINUTES
    return 0


def _time_off_intervals(barber, date_obj):
    """[(start_min, end_min), ...] blocked by Barber Time Off records covering
    `date_obj`. all_day records block the whole day; otherwise the given time
    window. (Never infer full-day from empty times — Frappe fills empty Time
    fields with the current clock time on insert.)"""
    rows = frappe.get_all(
        "Barber Time Off",
        filters={
            "barber": barber,
            "from_date": ["<=", date_obj],
            "to_date": [">=", date_obj],
        },
        fields=["all_day", "start_time", "end_time"],
    )
    out = []
    for r in rows:
        s = _to_minutes(r.start_time)
        e = _to_minutes(r.end_time)
        if r.all_day or s is None or e is None:
            out.append((0, 24 * 60))  # whole day off
        else:
            out.append((s, e))
    return out


def _busy_intervals(barber, date_obj):
    """Return [(start_min, end_min), ...] for non-cancelled appointments
    of `barber` on `date_obj`, plus any Barber Time Off blocks. End is derived
    from the service duration when end_time was not stored."""
    appts = frappe.get_all(
        "Appointment",
        filters={
            "barber": barber,
            "appointment_date": date_obj,
            "status": ["!=", "Cancelled"],
        },
        fields=["start_time", "end_time", "service"],
    )
    busy = []
    for a in appts:
        start = _to_minutes(a.start_time)
        if start is None:
            continue
        end = _to_minutes(a.end_time)
        if end is None:
            dur = frappe.db.get_value("Service", a.service, "duration") or 0
            end = start + int(dur)
        busy.append((start, end))
    busy.extend(_time_off_intervals(barber, date_obj))
    return busy


@frappe.whitelist(allow_guest=True)
def get_available_slots(barber, service, date):
    """Return free start times (list of 'HH:MM') for a barber/service/date.

    - Reads the barber's Barber Working Hours row for that date's weekday.
    - Steps candidate start times by the service's duration.
    - Drops any candidate overlapping a non-cancelled Appointment.
    """
    if not (barber and service and date):
        frappe.throw(_("barber, service and date are all required"))

    date_obj = frappe.utils.getdate(date)
    weekday = WEEKDAYS[date_obj.weekday()]

    duration = frappe.db.get_value("Service", service, "duration")
    if not duration:
        frappe.throw(_("Service {0} not found or has no duration").format(service))
    duration = int(duration)

    # Working hours for that weekday (Sunday/off days simply have no row).
    wh = frappe.get_all(
        "Barber Working Hours",
        filters={"parent": barber, "parenttype": "Barber", "day": weekday},
        fields=["start_time", "end_time"],
        order_by="start_time asc",
    )
    if not wh:
        return []  # barber doesn't work that day

    busy = _busy_intervals(barber, date_obj)
    cutoff = _lead_cutoff(date_obj)

    slots = []
    for row in wh:
        start_min = _to_minutes(row.start_time)
        end_min = _to_minutes(row.end_time)
        if start_min is None or end_min is None:
            continue
        t = start_min
        while t + duration <= end_min:
            overlaps = any(t < b_end and (t + duration) > b_start for (b_start, b_end) in busy)
            if t >= cutoff and not overlaps:
                slots.append(_fmt(t))
            t += duration

    return slots


@frappe.whitelist(allow_guest=True)
def create_booking(customer_name, phone=None, email=None, barber=None,
                   service=None, date=None, start_time=None):
    """Create an Appointment from a public booking request.

    Re-checks slot availability server-side (never trusts the client),
    reuses an existing Customer matched by phone or creates a new one,
    and returns the new Appointment name or a clear error.
    """
    required = {
        "customer_name": customer_name,
        "barber": barber,
        "service": service,
        "date": date,
        "start_time": start_time,
    }
    missing = [k for k, v in required.items() if not v]
    if missing:
        return {"success": False, "error": _("Missing required fields: {0}").format(", ".join(missing))}

    date_obj = frappe.utils.getdate(date)
    start_min = _to_minutes(start_time)
    if start_min is None:
        return {"success": False, "error": _("Invalid start_time")}
    start_label = _fmt(start_min)

    duration = frappe.db.get_value("Service", service, "duration")
    if not duration:
        return {"success": False, "error": _("Service {0} not found").format(service)}
    duration = int(duration)
    end_min = start_min + duration
    end_label = _fmt(end_min)

    # 1) Re-validate against the live availability list (working hours + grid).
    free = get_available_slots(barber, service, date)
    if start_label not in free:
        return {
            "success": False,
            "error": _("Sorry, {0} on {1} is no longer available. Please choose another time.").format(
                start_label, frappe.utils.formatdate(date_obj)
            ),
        }

    # 2) Final overlap guard against the race where a slot was taken in the
    #    meantime by an appointment that doesn't sit on this service's grid.
    for (b_start, b_end) in _busy_intervals(barber, date_obj):
        if start_min < b_end and end_min > b_start:
            return {
                "success": False,
                "error": _("Sorry, {0} was just booked. Please choose another time.").format(start_label),
            }

    # 3) Reuse customer by phone, else create.
    customer = None
    if phone:
        customer = frappe.db.get_value("Customer", {"phone": phone}, "name")
    if not customer:
        cdoc = frappe.get_doc({
            "doctype": "Customer",
            "customer_name": customer_name,
            "phone": phone,
            "email": email,
        })
        cdoc.insert(ignore_permissions=True)
        customer = cdoc.name

    # 4) Create the appointment.
    appt = frappe.get_doc({
        "doctype": "Appointment",
        "customer": customer,
        "barber": barber,
        "service": service,
        "appointment_date": date_obj,
        "start_time": start_label + ":00",
        "end_time": end_label + ":00",
        "status": "Scheduled",
    })
    appt.insert(ignore_permissions=True)
    frappe.db.commit()
    _send_booking_emails([appt.name], customer_name, phone, email, barber,
                         [service], date_obj, start_label, end_label)
    _send_booking_sms(barber, customer_name, phone, [service], date_obj, start_label)

    return {
        "success": True,
        "appointment": appt.name,
        "customer": customer,
        "start_time": start_label,
        "end_time": end_label,
    }


def _eur(p):
    p = p or 0
    return ("€%d" % int(p)) if float(p) == int(p) else ("€%.2f" % p)


BARBER_FALLBACK = "https://images.unsplash.com/photo-1503443207922-dff7d543fd0e?auto=format&fit=crop&w=600&q=80"


def _tr(text, lang):
    """Translate a DB display string via Frappe's built-in translation layer:
    Translation DocType records (editable at /app/translation) merged with app
    CSV files by frappe.translate.get_all_translations (Redis-cached)."""
    if not text:
        return ""
    if lang == "en":
        return text
    from frappe.translate import get_all_translations
    return get_all_translations(lang).get(text, text)


@frappe.whitelist(allow_guest=True)
def get_booking_data(lang="lt"):
    """Public catalogue for the booking wizard: services grouped by category
    plus active barbers. Display strings translated to `lang`; `name` docnames
    stay in English (used as booking keys)."""
    mins = "min" if lang == "lt" else "mins"
    categories = frappe.get_all(
        "Service Category", fields=["name", "category_name"], order_by="category_name asc"
    )
    out_cats = []
    for c in categories:
        svcs = frappe.get_all(
            "Service",
            filters={"service_category": c.name},
            fields=["name", "service_name", "duration", "price", "description"],
            order_by="price asc",
        )
        for s in svcs:
            s["price_display"] = _eur(s.price)
            s["duration_display"] = "%d %s" % (int(s.duration or 0), mins)
            s["description"] = _tr(s.description, lang)
            s["service_name"] = _tr(s.service_name, lang)
        if svcs:
            out_cats.append({"category_name": _tr(c.category_name, lang), "services": svcs})

    barbers = frappe.get_all(
        "Barber",
        filters={"is_active": 1},
        fields=["name", "barber_name", "bio", "photo"],
        order_by="barber_name asc",
    )
    for b in barbers:
        rows = frappe.get_all(
            "Barber Service", filters={"parent": b.name, "parenttype": "Barber"}, fields=["service"]
        )
        b["service_names"] = [r.service for r in rows]
        b["bio"] = _tr(b.bio, lang)
        if not b.photo:
            b["photo"] = BARBER_FALLBACK

    # Manager-uploaded "Our work" photos (Gallery Image DocType). The same set
    # the home page repeater uses, so the team page shows identical photos
    # rather than the stock placeholders it had before (manager 2026-09).
    gallery = frappe.get_all(
        "Gallery Image",
        fields=["image", "caption"],
        order_by="display_order asc, creation asc",
    )
    gallery = [g for g in gallery if g.get("image")]

    return {
        "service_categories": out_cats,
        "barbers": barbers,
        "gallery_images": gallery,
    }


# ---------------------------------------------------------------------------
# Multi-service ("basket") booking with per-professional availability.
# ---------------------------------------------------------------------------

def _service_duration(name):
    return int(frappe.db.get_value("Service", name, "duration") or 0)


def _working_windows(barber, date_obj):
    weekday = WEEKDAYS[date_obj.weekday()]
    wh = frappe.get_all(
        "Barber Working Hours",
        filters={"parent": barber, "parenttype": "Barber", "day": weekday},
        fields=["start_time", "end_time"], order_by="start_time asc",
    )
    out = []
    for row in wh:
        s = _to_minutes(row.start_time); e = _to_minutes(row.end_time)
        if s is not None and e is not None:
            out.append((s, e))
    return out


def _free_block_starts(barber, date_obj, total, step=15):
    """Start minutes where a contiguous [t, t+total] block fits in one working
    window and overlaps no non-cancelled appointment."""
    windows = _working_windows(barber, date_obj)
    if not windows:
        return []
    busy = _busy_intervals(barber, date_obj)
    cutoff = _lead_cutoff(date_obj)
    starts = []
    for (ws, we) in windows:
        t = ws
        while t + total <= we:
            if t >= cutoff and not any(t < b_end and (t + total) > b_start for (b_start, b_end) in busy):
                starts.append(t)
            t += step
    return starts


def _qualified_barbers(service_names):
    """Active barbers who perform ALL requested services; falls back to all
    active barbers if none list every service."""
    active = frappe.get_all("Barber", filters={"is_active": 1}, pluck="name")
    q = []
    for b in active:
        offered = set(frappe.get_all("Barber Service",
            filters={"parent": b, "parenttype": "Barber"}, pluck="service"))
        if offered and all(s in offered for s in service_names):
            q.append(b)
    return q or active


@frappe.whitelist(allow_guest=True)
def get_basket_slots(services, date, barber=None):
    """Free start times for a whole basket of services on a date. If `barber`
    is given, only that barber; otherwise any qualified professional."""
    services = frappe.parse_json(services) if isinstance(services, str) else services
    total = sum(_service_duration(s) for s in services)
    if not total:
        return {"slots": [], "total_minutes": 0}
    date_obj = frappe.utils.getdate(date)
    cands = [barber] if barber else _qualified_barbers(services)
    slot_barber = {}
    for b in cands:
        for t in _free_block_starts(b, date_obj, total):
            if t not in slot_barber:
                slot_barber[t] = b
    slots = [{"time": _fmt(t), "barber": slot_barber[t]} for t in sorted(slot_barber)]
    return {"slots": slots, "total_minutes": total}


@frappe.whitelist(allow_guest=True)
def get_week_availability(services, start_date, barber=None):
    """For 7 days from start_date, the count of free basket slots per day."""
    services = frappe.parse_json(services) if isinstance(services, str) else services
    start = frappe.utils.getdate(start_date)
    out = []
    for i in range(7):
        d = frappe.utils.add_days(start, i)
        res = get_basket_slots(services, d, barber)
        out.append({"date": str(d), "count": len(res["slots"])})
    return out


@frappe.whitelist(allow_guest=True)
def get_month_availability(services, month_start, barber=None):
    """Free-slot count for every day of the month containing `month_start`.

    Powers the calendar grid on the time-selection step: past days and
    fully-booked days come back with count 0 (rendered greyed/unclickable),
    days with capacity come back with their remaining slot count.
    """
    services = frappe.parse_json(services) if isinstance(services, str) else services
    first = frappe.utils.getdate(month_start).replace(day=1)
    if first.month == 12:
        nxt = first.replace(year=first.year + 1, month=1)
    else:
        nxt = first.replace(month=first.month + 1)
    out = []
    d = first
    while d < nxt:
        res = get_basket_slots(services, d, barber)
        out.append({"date": str(d), "count": len(res["slots"])})
        d = frappe.utils.add_days(d, 1)
    return out


@frappe.whitelist(allow_guest=True)
def create_basket_booking(customer_name, services, date, start_time, phone=None, email=None, barber=None):
    """Create back-to-back Appointments for a basket of services. Picks a
    qualified barber for `any`. Re-validates availability server-side."""
    services = frappe.parse_json(services) if isinstance(services, str) else services
    # phone is required too (manager 2026-07-08) — the JS enforces it, this
    # keeps direct API calls honest
    if not (customer_name and phone and services and date and start_time):
        return {"success": False, "error": _("Missing required fields")}
    date_obj = frappe.utils.getdate(date)
    start_min = _to_minutes(start_time)
    if start_min is None:
        return {"success": False, "error": _("Invalid time")}
    total = sum(_service_duration(s) for s in services)

    cands = [barber] if barber else _qualified_barbers(services)
    chosen = None
    for b in cands:
        if start_min in _free_block_starts(b, date_obj, total):
            chosen = b; break
    if not chosen:
        return {"success": False, "error": _("Sorry, that time is no longer available. Please choose another.")}
    barber = chosen

    customer = None
    if phone:
        customer = frappe.db.get_value("Customer", {"phone": phone}, "name")
    if not customer:
        cdoc = frappe.get_doc({"doctype": "Customer", "customer_name": customer_name,
                               "phone": phone, "email": email})
        cdoc.insert(ignore_permissions=True); customer = cdoc.name

    appts = []
    t = start_min
    for s in services:
        dur = _service_duration(s)
        appt = frappe.get_doc({"doctype": "Appointment", "customer": customer, "barber": barber,
            "service": s, "appointment_date": date_obj, "start_time": _fmt(t) + ":00",
            "end_time": _fmt(t + dur) + ":00", "status": "Scheduled"})
        appt.insert(ignore_permissions=True); appts.append(appt.name); t += dur
    frappe.db.commit()
    _send_booking_emails(appts, customer_name, phone, email, barber, services,
                         date_obj, _fmt(start_min), _fmt(start_min + total))
    _send_booking_sms(barber, customer_name, phone, services, date_obj, _fmt(start_min))
    return {"success": True, "appointments": appts, "barber": barber,
            "start_time": _fmt(start_min), "end_time": _fmt(start_min + total)}


# ---------------------------------------------------------------------------
# Booking notification SMS (Twilio, via Frappe's "SMS Settings" single).
#
# Task 2 (manager 2026-09): only the barber the booking was assigned to is
# notified. The Desk Notification rule that did this before ("New appointment
# SMS") picked recipients by ROLE, and Frappe resolves a role to the mobile_no
# of EVERY user holding it — which is why all barbers and the manager received
# every booking. That rule is disabled by patch; recipients are decided here.
# ---------------------------------------------------------------------------


def _sms_safe(receivers, msg):
    """send_sms that can never break the booking flow.

    `success_msg=False` matters: the default pushes a msgprint that would leak
    into the guest booking response's _server_messages (same class of bug the
    email path guards against in _safe_send).
    """
    try:
        nums = [n for n in dict.fromkeys(receivers) if n]
        if not nums:
            return
        from frappe.core.doctype.sms_settings.sms_settings import send_sms

        send_sms(receiver_list=nums, msg=msg, success_msg=False)
    except Exception:
        frappe.clear_last_message()
        frappe.log_error(frappe.get_traceback(), "Blarberine booking SMS failed")


def _service_labels(services):
    """Readable service names for an SMS body."""
    return ", ".join(
        frappe.db.get_value("Service", s, "service_name") or s for s in services
    )


def _send_barber_sms(barber, customer_name, phone, services, date_obj, start_label):
    """Notify ONLY the barber assigned to this booking.

    `barber` is already resolved by both callers, so when the client picks
    "any professional" the auto-assigned barber — the one stored on the
    Appointment — is the one messaged here.
    """
    to = frappe.db.get_value("Barber", barber, "phone")
    if not to:
        return
    _sms_safe(
        [to],
        "Nauja rezervacija: %s %s. Klientas: %s, tel. %s. Paslaugos: %s."
        % (
            frappe.utils.formatdate(date_obj, "dd.MM.yyyy"),
            start_label,
            customer_name,
            phone or "-",
            _service_labels(services),
        ),
    )


def _manager_numbers():
    """Mobile numbers of everyone holding the Barbers Manager role (task 3).

    Read straight off User.mobile_no — the same field Frappe's own role-based
    notification recipients use.
    """
    users = frappe.get_all(
        "Has Role",
        filters={"role": MANAGER_ROLE, "parenttype": "User"},
        pluck="parent",
    )
    nums = []
    for u in users:
        row = frappe.db.get_value("User", u, ["mobile_no", "enabled"], as_dict=True)
        if row and row.enabled and row.mobile_no:
            nums.append(row.mobile_no)
    return nums


def _send_manager_sms(barber, customer_name, phone, services, date_obj, start_label):
    """Task 3: the shop manager is copied on every barber's booking."""
    nums = _manager_numbers()
    if not nums:
        return
    barber_name = frappe.db.get_value("Barber", barber, "barber_name") or barber
    _sms_safe(
        nums,
        "Nauja rezervacija (%s): %s %s. Klientas: %s, tel. %s. Paslaugos: %s."
        % (
            barber_name,
            frappe.utils.formatdate(date_obj, "dd.MM.yyyy"),
            start_label,
            customer_name,
            phone or "-",
            _service_labels(services),
        ),
    )


def _send_client_sms(barber, phone, date_obj, start_label, lang=None):
    """Task 4: confirmation to the client the moment the booking completes.

    Wording is the manager's own, kept verbatim in both languages.
    """
    if not phone:
        return
    lang = lang or _booking_lang()
    barber_name = frappe.db.get_value("Barber", barber, "barber_name") or barber
    when = "%s %s" % (frappe.utils.formatdate(date_obj, "yyyy-MM-dd"), start_label)
    if lang == "en":
        msg = "Your appointment at %s is confirmed for %s. Your barber is %s." % (
            SHOP_NAME, when, barber_name)
    else:
        msg = "Jūsų vizitas %s patvirtintas %s. Jūsų meistras – %s." % (
            "Blarberinėje", when, barber_name)
    _sms_safe([phone], msg)


def _send_booking_sms(barber, customer_name, phone, services, date_obj, start_label):
    """All booking-time SMS in one place: assigned barber, manager, client."""
    _send_barber_sms(barber, customer_name, phone, services, date_obj, start_label)
    _send_manager_sms(barber, customer_name, phone, services, date_obj, start_label)
    _send_client_sms(barber, phone, date_obj, start_label)


def send_visit_reminders():
    """Task 5: remind the client ~2 hours before the visit. Cron, every 15 min.

    Picks appointments starting inside [now+2h, now+2h+15min) that haven't been
    reminded yet, so each booking is caught exactly once. A booking made less
    than two hours ahead never enters that window and therefore gets no
    reminder — the skip the manager asked for, with no extra check needed.

    A basket booking creates one Appointment per service, so reminders are
    grouped per customer: one SMS for the earliest slot, then every row in the
    group is flagged.
    """
    now = frappe.utils.now_datetime()
    win_start = frappe.utils.add_to_date(now, minutes=REMINDER_LEAD_MINUTES)
    win_end = frappe.utils.add_to_date(win_start, minutes=REMINDER_WINDOW_MINUTES)
    rows = frappe.get_all(
        "Appointment",
        filters=[
            ["status", "=", "Scheduled"],
            ["reminder_sent", "=", 0],
            ["start_dt", ">=", win_start],
            ["start_dt", "<", win_end],
        ],
        fields=["name", "customer", "start_dt"],
        order_by="customer asc, start_dt asc",
    )
    if not rows:
        return

    by_cust = {}
    for r in rows:
        by_cust.setdefault(r.customer, []).append(r)

    for cust, group in by_cust.items():
        phone = frappe.db.get_value("Customer", cust, "phone")
        if phone:
            _sms_safe(
                [phone],
                "Po dviejų valandų jūsų laukia vizitas Blarberinėje – iki pasimatymo!",
            )
        # Flag regardless of phone: without a number it can never be sent, and
        # leaving it unflagged would re-query the same rows every 15 minutes.
        for r in group:
            frappe.db.set_value("Appointment", r.name, "reminder_sent", 1)

    frappe.db.commit()


# ---------------------------------------------------------------------------
# Booking notification emails: confirmation to the customer, alert to the shop.
# ---------------------------------------------------------------------------

EMAIL_STRINGS = {
    "lt": {
        "subject": "Rezervacija patvirtinta – {shop}, {date} {time}",
        "heading": "Rezervacija patvirtinta",
        "intro": "Sveiki, {name}! Jūsų vizitas užregistruotas. Lauksime jūsų.",
        "date": "Data", "time": "Laikas", "barber": "Meistras",
        "services": "Paslaugos", "address": "Adresas", "reference": "Užsakymo nr.",
        "pay": "Atsiskaitymas vietoje – grynaisiais arba kortele.",
        "change": "Norite pakeisti ar atšaukti vizitą? Atsakykite į šį laišką.",
    },
    "en": {
        "subject": "Booking confirmed – {shop}, {date} {time}",
        "heading": "Booking confirmed",
        "intro": "Hi {name}! Your appointment is booked. See you soon.",
        "date": "Date", "time": "Time", "barber": "Professional",
        "services": "Services", "address": "Address", "reference": "Reference",
        "pay": "Pay at the venue – cash or card.",
        "change": "Need to change or cancel? Just reply to this email.",
    },
}


def _booking_lang():
    """lt/en inferred from the page the booking was made on (Referer header) —
    the widget itself doesn't send a language."""
    try:
        ref = frappe.request.headers.get("Referer") or ""
    except Exception:
        ref = ""
    return "en" if re.search(r"/en([/?#]|$)", ref) else "lt"


def _email_html(heading, intro, rows, notes):
    body_rows = "".join(
        '<tr><td style="padding:7px 16px 7px 0;color:#948c7a;font-size:13px;'
        'white-space:nowrap;vertical-align:top">%s</td>'
        '<td style="padding:7px 0;color:#1c1a15;font-size:14px;font-weight:600">%s</td></tr>'
        % (label, value)
        for (label, value) in rows if value
    )
    note_html = "".join(
        '<p style="margin:6px 0 0;color:#6b6455;font-size:13px;line-height:1.5">%s</p>' % n
        for n in notes if n
    )
    return (
        '<div style="background:#f6f2ea;padding:28px 16px;font-family:Georgia,serif">'
        '<div style="max-width:520px;margin:0 auto;background:#ffffff;border-radius:12px;'
        'border:1px solid #e6dfd0;overflow:hidden">'
        '<div style="background:#0d0d0d;padding:20px 28px">'
        '<span style="color:#b3873c;font-size:20px;letter-spacing:0.08em">' + SHOP_NAME + "</span></div>"
        '<div style="padding:24px 28px 28px">'
        '<h2 style="margin:0 0 6px;color:#1c1a15;font-size:22px;font-weight:600">' + heading + "</h2>"
        '<p style="margin:0 0 18px;color:#6b6455;font-size:14px;line-height:1.5">' + intro + "</p>"
        '<table style="border-collapse:collapse">' + body_rows + "</table>"
        '<div style="border-top:1px solid #e6dfd0;margin-top:18px;padding-top:14px">'
        + note_html + "</div></div></div></div>"
    )


def _safe_send(**kwargs):
    """frappe.sendmail that can never break the booking flow: failures are
    logged and any msgprint pushed by the mail stack is popped so it doesn't
    leak into the API response's _server_messages."""
    try:
        frappe.sendmail(**kwargs)
    except Exception:
        frappe.clear_last_message()
        frappe.log_error(frappe.get_traceback(), "Blarberine booking email failed")


def _send_booking_emails(appointments, customer_name, phone, email, barber,
                         services, date_obj, start_label, end_label, lang=None):
    """Queue the customer confirmation and the shop notification. A mail
    problem must never kill a valid appointment, so everything is wrapped."""
    try:
        lang = lang or _booking_lang()
        binfo = frappe.db.get_value("Barber", barber, ["barber_name", "email"], as_dict=True) or {}
        svc_bits = []
        for s in services:
            row = frappe.db.get_value("Service", s, ["service_name", "duration", "price"], as_dict=True)
            if row:
                svc_bits.append("%s (%d min) – %s" % (
                    _tr(row.service_name, lang), int(row.duration or 0), _eur(row.price)))
        svc_html = "<br>".join(svc_bits)
        date_label = frappe.utils.formatdate(date_obj, "dd.MM.yyyy")
        time_label = "%s–%s" % (start_label, end_label)
        notify = frappe.conf.get("blarberine_notify_email")

        if email:
            s = EMAIL_STRINGS.get(lang) or EMAIL_STRINGS["lt"]
            rows = [
                (s["date"], date_label), (s["time"], time_label),
                (s["barber"], binfo.get("barber_name") or barber),
                (s["services"], svc_html), (s["address"], SHOP_ADDRESS),
                (s["reference"], ", ".join(appointments)),
            ]
            _safe_send(
                recipients=[email],
                subject=s["subject"].format(shop=SHOP_NAME, date=date_label, time=start_label),
                message=_email_html(s["heading"], s["intro"].format(name=customer_name),
                                    rows, [s["pay"], s["change"]]),
                reply_to=notify or None,
            )

        # Shop copy always in Lithuanian; barbers get their own only if opted in
        # (their @blarberine.lt mailboxes may not exist yet).
        shop_rcpts = [notify] if notify else []
        if frappe.conf.get("blarberine_notify_barbers") and binfo.get("email"):
            shop_rcpts.append(binfo["email"])
        if shop_rcpts:
            rows = [
                ("Klientas", customer_name), ("Telefonas", phone), ("El. paštas", email),
                ("Data", date_label), ("Laikas", time_label),
                ("Meistras", binfo.get("barber_name") or barber),
                ("Paslaugos", svc_html), ("Užsakymo nr.", ", ".join(appointments)),
            ]
            _safe_send(
                recipients=shop_rcpts,
                subject="Nauja rezervacija: %s – %s %s (%s)" % (
                    customer_name, date_label, start_label, binfo.get("barber_name") or barber),
                message=_email_html("Nauja rezervacija",
                                    "Per svetainę gauta nauja rezervacija.", rows, []),
            )
    except Exception:
        frappe.clear_last_message()
        frappe.log_error(frappe.get_traceback(), "Blarberine booking email failed")


def send_reminders():
    """Daily scheduler job: remind tomorrow's customers about their visit.
    Appointments of one customer are grouped into a single email."""
    tomorrow = frappe.utils.add_days(frappe.utils.nowdate(), 1)
    appts = frappe.get_all(
        "Appointment",
        filters={"appointment_date": tomorrow, "status": "Scheduled"},
        fields=["name", "customer", "barber", "service", "start_time"],
        order_by="customer, start_time",
    )
    by_cust = {}
    for a in appts:
        by_cust.setdefault(a.customer, []).append(a)
    date_label = frappe.utils.formatdate(tomorrow, "dd.MM.yyyy")
    for cust, rows in by_cust.items():
        cinfo = frappe.db.get_value("Customer", cust, ["customer_name", "email"], as_dict=True)
        if not (cinfo and cinfo.email):
            continue
        start = _fmt(min(_to_minutes(r.start_time) for r in rows if _to_minutes(r.start_time) is not None))
        barber_name = frappe.db.get_value("Barber", rows[0].barber, "barber_name") or rows[0].barber
        svc_bits = []
        for r in rows:
            srow = frappe.db.get_value("Service", r.service, ["service_name", "duration", "price"], as_dict=True)
            if srow:
                svc_bits.append("%s (%d min) – %s" % (
                    srow.service_name, int(srow.duration or 0), _eur(srow.price)))
        _safe_send(
            recipients=[cinfo.email],
            subject="Priminimas: rytoj %s – %s" % (start, SHOP_NAME),
            message=_email_html(
                "Primename apie jūsų vizitą",
                "Sveiki, %s! Laukiame jūsų rytoj. / A reminder that your visit is tomorrow."
                % cinfo.customer_name,
                [("Data", date_label), ("Laikas", start), ("Meistras", barber_name),
                 ("Paslaugos", "<br>".join(svc_bits)), ("Adresas", SHOP_ADDRESS)],
                ["Atsiskaitymas vietoje – grynaisiais arba kortele.",
                 "Negalite atvykti? Atsakykite į šį laišką. / Can't make it? Just reply to this email."],
            ),
            reply_to=frappe.conf.get("blarberine_notify_email") or None,
        )
