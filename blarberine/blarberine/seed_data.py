# Copyright (c) 2026, Blarberine and contributors
# Idempotent sample-data seeder for the Blarberine barbershop (Lithuania market).
#
# Run with:
#   bench --site builder.localhost execute blarberine.blarberine.seed_data.run
#
# Re-running is safe: every record is checked before insert and skipped if
# already present.

import frappe

# ---------------------------------------------------------------------------
# Data definitions
# ---------------------------------------------------------------------------

CATEGORIES = [
    ("Haircuts", "Cuts, fades and styling for all hair types."),
    ("Beard", "Beard trims, shaping and styling."),
    ("Shaves", "Traditional hot-towel and head shaves."),
    ("Add-ons", "Quick extras to finish the look."),
]

# (service_name, category, duration_min, price_eur, description)
SERVICES = [
    ("Classic Haircut", "Haircuts", 45, 25.0, "Scissor and clipper cut, washed and styled."),
    ("Skin Fade", "Haircuts", 45, 28.0, "Clean skin fade with a sharp finish."),
    ("Kids Haircut", "Haircuts", 30, 15.0, "Haircut for children under 12."),
    ("Buzz Cut", "Haircuts", 15, 12.0, "Single-guard all-over clipper cut."),
    ("Beard Trim", "Beard", 20, 12.0, "Tidy-up and line-up of the beard."),
    ("Beard Sculpt & Style", "Beard", 30, 18.0, "Full beard shaping, trim and conditioning."),
    ("Hot Towel Shave", "Shaves", 30, 22.0, "Traditional straight-razor shave with hot towels."),
    ("Head Shave", "Shaves", 30, 20.0, "Smooth razor head shave."),
    ("Hair Wash", "Add-ons", 15, 6.0, "Shampoo, conditioner and blow-dry."),
    ("Eyebrow Trim", "Add-ons", 15, 5.0, "Quick eyebrow tidy-up."),
]

WORKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]  # Sunday off

# (barber_name, bio, phone, email, [service names])
BARBERS = [
    (
        "Mantas Petrauskas",
        "Master barber with 12 years behind the chair. Specialises in fades and classic cuts.",
        "+37061000011", "mantas@blarberine.lt",
        ["Classic Haircut", "Skin Fade", "Kids Haircut", "Buzz Cut", "Hot Towel Shave", "Head Shave"],
    ),
    (
        "Tomas Kazlauskas",
        "Beard specialist who loves a precise line-up and a sharp scissor cut.",
        "+37061000012", "tomas@blarberine.lt",
        ["Beard Trim", "Beard Sculpt & Style", "Classic Haircut", "Hair Wash"],
    ),
    (
        "Lukas Jankauskas",
        "Fast, friendly and great with kids. Your go-to for buzz cuts and quick refreshes.",
        "+37061000013", "lukas@blarberine.lt",
        ["Buzz Cut", "Skin Fade", "Eyebrow Trim", "Hair Wash"],
    ),
]

# (customer_name, phone, email)
CUSTOMERS = [
    ("Jonas Kazlauskas", "+37060000001", "jonas.k@example.lt"),
    ("Ruta Vaitkute", "+37060000002", "ruta.v@example.lt"),
    ("Andrius Petrauskas", "+37060000003", "andrius.p@example.lt"),
    ("Egle Stankeviciute", "+37060000004", "egle.s@example.lt"),
    ("Marius Butkus", "+37060000005", "marius.b@example.lt"),
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _service_duration(service_name):
    return int(frappe.db.get_value("Service", service_name, "duration") or 0)


def _add_minutes(time_str, minutes):
    """'HH:MM' + minutes -> 'HH:MM:SS'."""
    h, m = time_str.split(":")[:2]
    total = int(h) * 60 + int(m) + minutes
    return "%02d:%02d:00" % (total // 60, total % 60)


# ---------------------------------------------------------------------------
# Seeding
# ---------------------------------------------------------------------------

def _seed_categories(log):
    for name, desc in CATEGORIES:
        if frappe.db.exists("Service Category", name):
            log["category_skipped"] += 1
            continue
        frappe.get_doc({
            "doctype": "Service Category",
            "category_name": name,
            "description": desc,
        }).insert(ignore_permissions=True)
        log["category_created"] += 1


def _seed_services(log):
    for name, category, duration, price, desc in SERVICES:
        if frappe.db.exists("Service", name):
            log["service_skipped"] += 1
            continue
        frappe.get_doc({
            "doctype": "Service",
            "service_name": name,
            "service_category": category,
            "duration": duration,
            "price": price,
            "description": desc,
        }).insert(ignore_permissions=True)
        log["service_created"] += 1


def _seed_barbers(log):
    for name, bio, phone, email, services in BARBERS:
        if frappe.db.exists("Barber", name):
            # Backfill phone/email on already-seeded barbers (idempotent).
            existing = frappe.get_doc("Barber", name)
            updated = False
            if not existing.get("phone"):
                existing.phone = phone
                updated = True
            if not existing.get("email"):
                existing.email = email
                updated = True
            if updated:
                existing.save(ignore_permissions=True)
                log["barber_updated"] += 1
            else:
                log["barber_skipped"] += 1
            continue
        doc = frappe.get_doc({
            "doctype": "Barber",
            "barber_name": name,
            "photo": "",
            "bio": bio,
            "phone": phone,
            "email": email,
            "is_active": 1,
        })
        for svc in services:
            doc.append("services", {"service": svc})
        for day in WORKDAYS:
            doc.append("working_hours", {
                "day": day,
                "start_time": "09:00:00",
                "end_time": "18:00:00",
            })
        doc.insert(ignore_permissions=True)
        log["barber_created"] += 1


def _seed_customers(log):
    for name, phone, email in CUSTOMERS:
        if frappe.db.exists("Customer", {"phone": phone}):
            log["customer_skipped"] += 1
            continue
        frappe.get_doc({
            "doctype": "Customer",
            "customer_name": name,
            "phone": phone,
            "email": email,
        }).insert(ignore_permissions=True)
        log["customer_created"] += 1


def _appointments_spec():
    """Build appointment specs relative to today so seeded data always sits in
    the near future for the availability logic to exclude against."""
    today = frappe.utils.nowdate()
    d1 = frappe.utils.add_days(today, 1)
    d2 = frappe.utils.add_days(today, 2)
    d3 = frappe.utils.add_days(today, 3)
    # (barber, customer_phone, service, date, start 'HH:MM', status)
    return [
        ("Mantas Petrauskas", "+37060000001", "Classic Haircut", d1, "09:00", "Confirmed"),
        ("Mantas Petrauskas", "+37060000002", "Skin Fade", d1, "11:00", "Scheduled"),
        ("Mantas Petrauskas", "+37060000003", "Hot Towel Shave", d1, "14:00", "Completed"),
        ("Tomas Kazlauskas", "+37060000004", "Beard Trim", d1, "10:00", "Scheduled"),
        # Cancelled -> should NOT be excluded by availability:
        ("Tomas Kazlauskas", "+37060000005", "Beard Sculpt & Style", d2, "15:00", "Cancelled"),
        ("Lukas Jankauskas", "+37060000001", "Buzz Cut", d3, "09:30", "No Show"),
    ]


def _seed_appointments(log):
    for barber, phone, service, date, start, status in _appointments_spec():
        customer = frappe.db.get_value("Customer", {"phone": phone}, "name")
        if not customer:
            log["appointment_skipped"] += 1
            continue
        # Idempotency key: one appointment per barber+date+start_time.
        existing = frappe.get_all("Appointment", filters={
            "barber": barber,
            "appointment_date": date,
            "start_time": start + ":00",
        }, limit=1)
        if existing:
            log["appointment_skipped"] += 1
            continue
        end = _add_minutes(start, _service_duration(service))
        frappe.get_doc({
            "doctype": "Appointment",
            "customer": customer,
            "barber": barber,
            "service": service,
            "appointment_date": date,
            "start_time": start + ":00",
            "end_time": end,
            "status": status,
        }).insert(ignore_permissions=True)
        log["appointment_created"] += 1


def run():
    """Entry point. Seeds all sample data idempotently and prints a summary."""
    log = {
        "category_created": 0, "category_skipped": 0,
        "service_created": 0, "service_skipped": 0,
        "barber_created": 0, "barber_skipped": 0, "barber_updated": 0,
        "customer_created": 0, "customer_skipped": 0,
        "appointment_created": 0, "appointment_skipped": 0,
    }

    _seed_categories(log)
    _seed_services(log)
    _seed_barbers(log)
    _seed_customers(log)
    _seed_appointments(log)

    frappe.db.commit()

    print("=== Blarberine seed summary ===")
    print("Service Categories : created %d, skipped %d" % (log["category_created"], log["category_skipped"]))
    print("Services           : created %d, skipped %d" % (log["service_created"], log["service_skipped"]))
    print("Barbers            : created %d, updated %d, skipped %d" % (log["barber_created"], log["barber_updated"], log["barber_skipped"]))
    print("Customers          : created %d, skipped %d" % (log["customer_created"], log["customer_skipped"]))
    print("Appointments       : created %d, skipped %d" % (log["appointment_created"], log["appointment_skipped"]))
    return log
