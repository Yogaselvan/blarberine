from frappe.installer import update_site_config


def execute():
    """Route shop booking notifications to the owner's inbox (launch testing).
    Supersedes the earlier default set by launch_defaults."""
    update_site_config("blarberine_notify_email", "yogaselvansaravanan557@gmail.com")
