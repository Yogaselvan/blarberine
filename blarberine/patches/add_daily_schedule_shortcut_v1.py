"""Task 3 (manager 2026-09): surface the Daily Schedule report on the
Barbershop workspace, so the manager can see which barbers have appointments
today and at what times without knowing a URL. Idempotent, and wrapped so a
workspace problem can never break a migrate."""

import json

import frappe

WORKSPACE = "Barbershop"
REPORT = "Daily Schedule"
LABEL = "Today's schedule"


def execute():
    if not frappe.db.exists("Workspace", WORKSPACE):
        return

    try:
        ws = frappe.get_doc("Workspace", WORKSPACE)
        if any((s.link_to or "") == REPORT for s in ws.shortcuts):
            return

        ws.append(
            "shortcuts",
            {
                "type": "Report",
                "label": LABEL,
                "link_to": REPORT,
                "report_ref_doctype": "Appointment",
                "color": "Cyan",
            },
        )

        # Render it alongside the existing shortcut tiles rather than at the end.
        try:
            blocks = json.loads(ws.content or "[]")
        except Exception:
            blocks = []
        tile = {"id": "bsschd", "type": "shortcut", "data": {"shortcut_name": LABEL, "col": 3}}
        last = max(
            (i for i, b in enumerate(blocks) if b.get("type") == "shortcut"), default=None
        )
        if last is None:
            blocks.append(tile)
        else:
            blocks.insert(last + 1, tile)
        ws.content = json.dumps(blocks)

        ws.flags.ignore_permissions = True
        ws.save(ignore_permissions=True)
    except Exception:
        frappe.log_error(
            frappe.get_traceback(), "Blarberine: could not add Daily Schedule shortcut"
        )
