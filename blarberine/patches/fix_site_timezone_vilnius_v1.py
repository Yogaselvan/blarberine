import frappe

TZ = "Europe/Vilnius"


def execute():
    """Force the site clock back to Lithuanian time.

    System Settings had drifted to Asia/Kolkata (UTC+5:30) while the shop is in
    Kaunas (UTC+3 in summer), so Frappe believed it was ~2.5 hours later than
    it really was. That is not cosmetic:

      * _lead_cutoff() hid same-day slots that were genuinely still bookable,
        costing real bookings;
      * after ~21:30 local the site rolled over to "tomorrow", so the current
        day could not be booked at all;
      * send_visit_reminders() compared appointment times against a clock
        2.5 hours out, so the 2-hour reminder could never match.

    launch_defaults sets this on a fresh site, but it has already run here, so
    it cannot correct an existing site — hence this patch.
    """
    if frappe.db.get_single_value("System Settings", "time_zone") == TZ:
        return

    frappe.db.set_single_value("System Settings", "time_zone", TZ)
    frappe.clear_cache()
    frappe.logger().info("blarberine: system time zone reset to %s" % TZ)
