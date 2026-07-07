"""Build & publish the Blarberinė Builder pages from the in-app generator.

The site's pages are DB records (Builder Page / Builder Client Script), so a
code deploy alone can't change them — and restoring a DB over the live site
would destroy real bookings. This loader is the deploy path instead: the
generator emits fresh page JSON into a temp dir and this module upserts the
records in place. Run locally with
    bench execute blarberine.website_build.loader.rebuild
and on Frappe Cloud via a one-line patch per page batch (see patches.txt).
"""

import json
import os
import tempfile

import frappe

from . import build_page

ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
MARKER_JS = "Blarberine booking wizard"
MARKER_CSS = "bl-navitem"
MARKER_INT = "Blarberine interactive widgets"
OWNER = "yogaselvansaravanan557@gmail.com"


def _ensure_script(marker, content, script_type):
    """Upsert the Builder Client Script whose body contains `marker`."""
    target = None
    for cs in frappe.get_all("Builder Client Script", fields=["name", "script"]):
        if marker in (cs.get("script") or ""):
            target = cs["name"]
            break
    if target:
        d = frappe.get_doc("Builder Client Script", target)
        d.script = content
        d.script_type = script_type
        d.save(ignore_permissions=True)
    else:
        d = frappe.get_doc({"doctype": "Builder Client Script",
                            "script_type": script_type, "script": content})
        d.insert(ignore_permissions=True)
    return d.name


def _ensure_page(route, title):
    name = frappe.db.get_value("Builder Page", {"route": route}, "name")
    if name:
        return name
    doc = frappe.get_doc({"doctype": "Builder Page", "page_title": title, "route": route})
    doc.insert(ignore_permissions=True)
    return doc.name


def rebuild(email=OWNER):
    out = tempfile.mkdtemp(prefix="blarberine_pages_")
    build_page.generate(out)

    js = open(os.path.join(ASSETS, "booking.js")).read()
    interactive = open(os.path.join(ASSETS, "interactive.js")).read()
    css = open(os.path.join(out, "nav.css")).read()
    script_names = (
        _ensure_script(MARKER_JS, js, "JavaScript"),
        _ensure_script(MARKER_CSS, css, "CSS"),
        _ensure_script(MARKER_INT, interactive, "JavaScript"),
    )

    ds_cache = {}

    def data_script(fname):
        if fname not in ds_cache:
            ds_cache[fname] = open(os.path.join(out, fname)).read()
        return ds_cache[fname]

    manifest = json.load(open(os.path.join(out, "pages", "manifest.json")))
    for e in manifest:
        name = _ensure_page(e["route"], e["title"])
        blocks = open(os.path.join(out, "pages", e["file"])).read()
        doc = frappe.get_doc("Builder Page", name)
        doc.draft_blocks = blocks
        doc.blocks = blocks
        doc.page_data_script = data_script(e["data_script"])
        doc.published = 1
        doc.route = e["route"]
        doc.page_title = e["seo_title"]
        doc.meta_description = e["seo_desc"]
        doc.meta_image = e["seo_image"]
        doc.favicon = e["seo_favicon"]
        have = [r.builder_script for r in (doc.get("client_scripts") or [])]
        for sname in script_names:
            if sname not in have:
                doc.append("client_scripts", {"builder_script": sname})
        doc.save(ignore_permissions=True)
        frappe.db.set_value("Builder Page", name, "owner", email, update_modified=False)
        print("PUBLISHED %-2s %-8s -> /%s" % (e["lang"], e["key"], e["route"]))

    bs = frappe.get_doc("Builder Settings", "Builder Settings")
    bs.favicon = "/assets/blarberine/images/favicon.png"
    bs.save(ignore_permissions=True)

    # blog post pages copy the home page's nav/footer — refresh them too
    from blarberine.blarberine.blog_render import render_post
    n = 0
    for r in frappe.get_all("Blog Post", pluck="name"):
        render_post(frappe.get_doc("Blog Post", r))
        n += 1
    frappe.db.commit()
    print("re-rendered %d blog pages" % n)
