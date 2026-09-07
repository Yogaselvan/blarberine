import frappe


def execute():
    """Task 2 (manager 2026-09): stop the booking SMS going to every barber.

    The Desk Notification "New appointment SMS" fires on every new Appointment
    and picks its recipients by ROLE. Frappe resolves a role to the mobile_no of
    EVERY user holding it (see Notification.get_receiver_list), which is why all
    barbers and the manager received every booking.

    Booking SMS is now sent from blarberine.blarberine.api._send_barber_sms,
    addressed only to the barber the appointment was assigned to, so this rule
    is disabled — otherwise each booking would send twice. Disabled rather than
    deleted so the original configuration stays visible and reversible.
    """
    for name in frappe.get_all(
        "Notification",
        filters={"document_type": "Appointment", "channel": "SMS", "enabled": 1},
        pluck="name",
    ):
        frappe.db.set_value("Notification", name, "enabled", 0)
        frappe.logger().info("blarberine: disabled broadcast SMS notification %s" % name)
