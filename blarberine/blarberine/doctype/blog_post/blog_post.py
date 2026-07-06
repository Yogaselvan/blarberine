import re

import frappe
from frappe.model.document import Document
from frappe.utils import today

from blarberine.blarberine.blog_render import render_post, remove_post
from blarberine.blarberine.blog_translate import sync_translation

# transliterate Lithuanian diacritics -> ASCII for clean URLs
_LT_MAP = str.maketrans("ąčęėįšųūžĄČĘĖĮŠŲŪŽ", "aceeisuuzACEEISUUZ")


def _slugify(s):
    s = (s or "post").translate(_LT_MAP).lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s or "post"


class BlogPost(Document):
    def validate(self):
        # route lives under the language tree (LT: blog/…, EN: en/blog/…), ASCII-clean
        prefix = "blog/" if (self.language or "lt") == "lt" else "en/blog/"
        if not self.route:
            self.route = prefix + _slugify(self.title)
        else:
            slug = _slugify(self.route.rstrip("/").split("/")[-1])
            self.route = prefix + slug
        if self.published and not self.published_on:
            self.published_on = today()

    def on_update(self):
        # 1) keep this post's Builder Page in sync
        try:
            render_post(self)
        except Exception:
            frappe.log_error(frappe.get_traceback(), "Blog Post render failed")
        # 2) if this is a source post set to auto-translate, sync its paired post
        if self.translate_automatically and not self.source_post:
            try:
                sync_translation(self)
            except Exception as e:
                frappe.log_error(frappe.get_traceback(), "Blog Post auto-translate failed")
                frappe.msgprint("Auto-translation skipped: {0}".format(e),
                                indicator="orange", alert=True)

    def on_trash(self):
        # remove this post's page, and any paired translation it generated
        remove_post(self.route)
        for child in frappe.get_all("Blog Post", filters={"source_post": self.name}, fields=["name"]):
            frappe.delete_doc("Blog Post", child.name, ignore_permissions=True, force=True)
