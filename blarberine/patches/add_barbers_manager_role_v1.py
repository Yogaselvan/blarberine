import frappe

ROLE = "Barbers Manager"


def execute():
    """Task 3 (manager 2026-09): role whose holders are copied on every
    barber's booking SMS.

    Recipients are read from User.mobile_no of everyone holding this role (see
    blarberine.blarberine.api._manager_numbers), so onboarding a manager is:
    assign this role to their User and fill in their mobile number.
    """
    if not frappe.db.exists("Role", ROLE):
        frappe.get_doc(
            {
                "doctype": "Role",
                "role_name": ROLE,
                "desk_access": 1,
            }
        ).insert(ignore_permissions=True)
