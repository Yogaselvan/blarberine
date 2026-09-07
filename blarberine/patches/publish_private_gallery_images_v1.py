import frappe


def execute():
    """Repair gallery photos whose file was uploaded as private.

    A private file lives under /private/files/ and cannot be fetched by
    anonymous visitors, so the photo renders broken on the website while
    looking correct in the Desk. Re-saving each affected row runs
    GalleryImage.validate(), which flips the File to public and rewrites the
    stored URL.
    """
    names = frappe.get_all(
        "Gallery Image",
        filters={"image": ["like", "/private/files/%"]},
        pluck="name",
    )
    for name in names:
        try:
            frappe.get_doc("Gallery Image", name).save(ignore_permissions=True)
            frappe.logger().info("blarberine: published gallery image %s" % name)
        except Exception:
            frappe.log_error(
                frappe.get_traceback(), "Blarberine: could not publish gallery image %s" % name
            )
