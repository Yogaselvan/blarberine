# Copyright (c) 2026, Blarberine and contributors
# Manager overview (task 3): which barbers have appointments on a given day,
# and at what times. Defaults to today.

import frappe
from frappe import _

from blarberine.blarberine.api import _fmt, _to_minutes


def execute(filters=None):
    filters = filters or {}
    date = filters.get("date") or frappe.utils.nowdate()

    rows = frappe.get_all(
        "Appointment",
        filters={"appointment_date": date, "status": ["!=", "Cancelled"]},
        fields=["name", "barber", "customer", "service", "start_time", "end_time", "status"],
        order_by="barber asc, start_time asc",
    )

    data = []
    for r in rows:
        start = _to_minutes(r.start_time)
        end = _to_minutes(r.end_time)
        cust = (
            frappe.db.get_value("Customer", r.customer, ["customer_name", "phone"], as_dict=True)
            or frappe._dict()
        )
        data.append(
            {
                "barber": frappe.db.get_value("Barber", r.barber, "barber_name") or r.barber,
                "start_time": _fmt(start) if start is not None else "",
                "end_time": _fmt(end) if end is not None else "",
                "customer_name": cust.get("customer_name") or r.customer,
                "phone": cust.get("phone"),
                "service": r.service,
                "status": r.status,
                "appointment": r.name,
            }
        )

    return get_columns(), data


def get_columns():
    return [
        {"label": _("Barber"), "fieldname": "barber", "fieldtype": "Data", "width": 170},
        {"label": _("From"), "fieldname": "start_time", "fieldtype": "Data", "width": 80},
        {"label": _("To"), "fieldname": "end_time", "fieldtype": "Data", "width": 80},
        {"label": _("Customer"), "fieldname": "customer_name", "fieldtype": "Data", "width": 180},
        {"label": _("Phone"), "fieldname": "phone", "fieldtype": "Data", "width": 140},
        {"label": _("Service"), "fieldname": "service", "fieldtype": "Link",
         "options": "Service", "width": 190},
        {"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 100},
        {"label": _("Appointment"), "fieldname": "appointment", "fieldtype": "Link",
         "options": "Appointment", "width": 130},
    ]
