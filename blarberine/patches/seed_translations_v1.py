import frappe


def execute():
    """One-time seed of the Lithuanian DocType-data translations (service names,
    descriptions, category names, barber bios) onto the site so LT text renders
    on the pages AND the booking widget. Idempotent: only inserts a Translation
    when one doesn't already exist for that source string, so manual edits made
    at /app/translation are never overwritten."""
    from blarberine.website_build.build_page import DATA_TR_LT

    created = 0
    for source, translated in DATA_TR_LT.items():
        if not source or not translated:
            continue
        if frappe.db.exists("Translation", {"language": "lt", "source_text": source}):
            continue
        frappe.get_doc({
            "doctype": "Translation",
            "language": "lt",
            "source_text": source,
            "translated_text": translated,
        }).insert(ignore_permissions=True)
        created += 1

    if created:
        frappe.db.commit()
    frappe.clear_cache()
    print("seed_translations_v1: created %d LT translations" % created)
