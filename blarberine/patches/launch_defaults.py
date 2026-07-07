import frappe
from frappe.installer import update_site_config


def execute():
    """Launch defaults: the shop lives in Kaunas, so date/time math (slot
    cutoffs, reminder scheduling) must run on Lithuanian time; and booking
    notifications need a shop inbox out of the box. Both are no-ops when
    already configured."""
    frappe.db.set_single_value("System Settings", "time_zone", "Europe/Vilnius")
    if not frappe.conf.get("blarberine_notify_email"):
        update_site_config("blarberine_notify_email", "yogaselvansaravanan557@gmail.com")
