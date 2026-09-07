import frappe
from frappe.model.document import Document


class GalleryImage(Document):
    def validate(self):
        self.make_image_public()

    def make_image_public(self):
        """Gallery photos are shown to anonymous visitors, so the attached File
        must be public.

        Frappe's upload dialog can save an attachment as private, which lands
        the file under /private/files/. Guests can't fetch that path, so the
        photo renders as a broken image on the website while looking perfectly
        fine in the Desk — the manager hit exactly this in 2026-09. Flipping
        is_private moves the file and rewrites file_url, so we re-read it.
        """
        if not self.image or not self.image.startswith("/private/files/"):
            return

        name = frappe.db.get_value("File", {"file_url": self.image}, "name")
        if not name:
            return

        f = frappe.get_doc("File", name)
        f.is_private = 0
        f.save(ignore_permissions=True)
        self.image = f.file_url
