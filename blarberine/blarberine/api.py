# Copyright (c) 2026, Blarberine and contributors
# Public booking API for the Blarberine barbershop site.
#
# Both endpoints are whitelisted with allow_guest=True because the public
# website (anonymous visitors, not logged-in Desk users) calls them during
# the booking flow.

import frappe
from frappe import _

# Monday=0 ... Sunday=6, matching datetime.date.weekday()
WEEKDAYS = [
    "Monday", "Tuesday", "Wednesday",
    "Thursday", "Friday", "Saturday", "Sunday",
]


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

    slots = []
    for row in wh:
        start_min = _to_minutes(row.start_time)
        end_min = _to_minutes(row.end_time)
        if start_min is None or end_min is None:
            continue
        t = start_min
        while t + duration <= end_min:
            overlaps = any(t < b_end and (t + duration) > b_start for (b_start, b_end) in busy)
            if not overlaps:
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

    return {"service_categories": out_cats, "barbers": barbers}


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
    starts = []
    for (ws, we) in windows:
        t = ws
        while t + total <= we:
            if not any(t < b_end and (t + total) > b_start for (b_start, b_end) in busy):
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
def create_basket_booking(customer_name, services, date, start_time, phone=None, email=None, barber=None):
    """Create back-to-back Appointments for a basket of services. Picks a
    qualified barber for `any`. Re-validates availability server-side."""
    services = frappe.parse_json(services) if isinstance(services, str) else services
    if not (customer_name and services and date and start_time):
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
    return {"success": True, "appointments": appts, "barber": barber,
            "start_time": _fmt(start_min), "end_time": _fmt(start_min + total)}
