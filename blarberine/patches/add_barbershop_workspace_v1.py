"""Create the "Barbershop" desk Workspace so the manager finds everything in
one place: bookings, services, barbers & schedules, gallery photos, blog,
translations. Idempotent — skipped if the workspace already exists."""

import json

import frappe

SHORTCUTS = [
    ("Appointments", "Appointment", "Orange"),
    ("Barbers", "Barber", "Blue"),
    ("Services", "Service", "Green"),
    ("Gallery photos", "Gallery Image", "Yellow"),
    ("Blog posts", "Blog Post", "Purple"),
    ("Translations (LT)", "Translation", "Grey"),
]

CARDS = [
    ("Bookings", ["Appointment", "Customer"]),
    ("Team & schedule", ["Barber", "Barber Working Hours", "Barber Time Off"]),
    ("Services & prices", ["Service", "Service Category"]),
    ("Website content", ["Gallery Image", "Blog Post", "Testimonial", "Translation", "Builder Page"]),
]


def execute():
    if frappe.db.exists("Workspace", "Barbershop"):
        return

    blocks = [{"id": "bsh0", "type": "header",
               "data": {"text": "<span class=\"h4\"><b>Barbershop</b></span>", "col": 12}}]
    for i, (label, _dt, _color) in enumerate(SHORTCUTS):
        blocks.append({"id": "bss%d" % i, "type": "shortcut",
                       "data": {"shortcut_name": label, "col": 3}})
    blocks.append({"id": "bsp0", "type": "spacer", "data": {"col": 12}})
    blocks.append({"id": "bsh1", "type": "header",
                   "data": {"text": "<span class=\"h4\"><b>Manage</b></span>", "col": 12}})

    ws = frappe.new_doc("Workspace")
    ws.label = "Barbershop"
    ws.title = "Barbershop"
    ws.icon = "tool"
    ws.module = "Blarberine"
    ws.public = 1

    for label, dt, color in SHORTCUTS:
        if not frappe.db.exists("DocType", dt):
            continue
        ws.append("shortcuts", {"type": "DocType", "label": label, "link_to": dt,
                                "doc_view": "List", "color": color})

    for i, (card, doctypes) in enumerate(CARDS):
        real = [dt for dt in doctypes if frappe.db.exists("DocType", dt)]
        if not real:
            continue
        blocks.append({"id": "bsc%d" % i, "type": "card", "data": {"card_name": card, "col": 4}})
        ws.append("links", {"type": "Card Break", "label": card, "link_count": len(real)})
        for dt in real:
            ws.append("links", {"type": "Link", "label": dt, "link_type": "DocType",
                                "link_to": dt, "hidden": 0, "onboard": 0})

    ws.content = json.dumps(blocks)
    ws.flags.ignore_permissions = True
    ws.insert(ignore_permissions=True)
