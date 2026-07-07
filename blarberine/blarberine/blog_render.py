"""Render a Blog Post into an on-brand Builder Page.

Each published Blog Post becomes its own Builder Page at route `blog/<slug>`.
To stay perfectly on-theme we reuse the *real* nav + footer blocks (and the data
script + client scripts) copied from the language's home page, and drop a single
article section in between. No template duplication — the blog inherits the site."""

import json
import frappe

BG = "#faf8f3"; ALT = "#f1ece2"; INK = "#26211a"; BODY = "#57503f"; MUTED = "#8c8271"
BORDER = "#e6dfd0"; GOLD = "#b3873c"; CARD = "#ffffff"
FONT = "'Montserrat', system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
HEAD = "'Cormorant Garamond', 'Playfair Display', Georgia, serif"

_counter = [0]


def _bid():
    _counter[0] += 1
    return "blogb%05d" % _counter[0]


def _blk(el, children=None, styles=None, innerHTML=None, attributes=None, classes=None):
    b = {"blockId": _bid(), "element": el}
    if innerHTML is not None:
        b["innerHTML"] = innerHTML
    if attributes is not None:
        b["attributes"] = attributes
    if classes is not None:
        b["classes"] = classes
    b["baseStyles"] = styles or {}
    b["children"] = children or []
    return b


def _text(content, styles, tag="p", classes=None):
    s = {"fontFamily": FONT, "width": "fit-content", "height": "fit-content"}
    s.update(styles)
    return _blk(tag, innerHTML=content, styles=s, classes=classes)


def _home_route(lang):
    return "home" if (lang or "lt") == "lt" else "en"


def _blog_route(lang):
    return "blog" if (lang or "lt") == "lt" else "en/blog"


def _content_section(doc):
    lang = doc.language or "lt"
    back = _blk("a", innerHTML=("← Blogas" if lang == "lt" else "← Blog"),
                attributes={"href": "/" + _blog_route(lang)},
                styles={"fontFamily": FONT, "fontSize": "14px", "color": GOLD, "fontWeight": "600",
                        "textDecoration": "none", "marginBottom": "22px", "width": "fit-content"})
    bits = []
    if doc.published_on:
        try:
            bits.append(frappe.utils.formatdate(doc.published_on))
        except Exception:
            bits.append(str(doc.published_on))
    if doc.author:
        bits.append(doc.author)
    meta = _text(" · ".join(bits), {"fontSize": "12px", "letterSpacing": "0.14em", "textTransform": "uppercase",
                                    "color": GOLD, "fontWeight": "700", "marginBottom": "12px"})
    title = _text(doc.title or "", {"fontFamily": HEAD, "fontSize": "40px", "color": INK, "fontWeight": "600",
                                    "lineHeight": "1.15", "marginBottom": "26px", "width": "auto"}, tag="h1")
    kids = [back, meta, title]
    if doc.cover_image:
        kids.append(_blk("img", attributes={"src": doc.cover_image, "alt": doc.title or ""},
                         styles={"width": "100%", "height": "420px", "objectFit": "cover",
                                 "borderRadius": "16px", "marginBottom": "32px", "display": "block"}))
    kids.append(_blk("div", innerHTML=doc.content or "", classes=["bl-blog-content"],
                     styles={"width": "100%", "color": BODY, "fontFamily": FONT}))
    inner = _blk("div", children=kids, styles={"display": "flex", "flexDirection": "column",
                                               "width": "100%", "maxWidth": "820px"})
    return _blk("section", children=[inner],
                styles={"display": "flex", "flexDirection": "column", "alignItems": "center", "width": "100%",
                        "flexShrink": 0, "backgroundColor": BG, "paddingTop": "52px", "paddingBottom": "64px",
                        "paddingLeft": "24px", "paddingRight": "24px"})


def render_post(doc):
    """Create/update the Builder Page for this post. Returns the Builder Page name."""
    _counter[0] = 0
    lang = doc.language or "lt"
    src_name = (frappe.db.get_value("Builder Page", {"route": _home_route(lang)}, "name")
                or frappe.db.get_value("Builder Page", {"route": "home"}, "name"))
    if not src_name:
        frappe.throw("No home Builder Page found to inherit nav/footer from.")
    src = frappe.get_doc("Builder Page", src_name)
    root = json.loads(src.blocks)[0]
    ch = root.get("children", [])
    nav, footer = ch[0], ch[-1]
    new_root = dict(root)
    new_root["children"] = [nav, _content_section(doc), footer]
    new_blocks = json.dumps([new_root])

    tgt_name = frappe.db.get_value("Builder Page", {"route": doc.route}, "name")
    page = frappe.get_doc("Builder Page", tgt_name) if tgt_name else frappe.new_doc("Builder Page")
    page.route = doc.route
    page.page_title = doc.title
    page.meta_description = (doc.meta_description or doc.excerpt or "")[:500]
    # per-post preview image = its cover, else the site default OG image
    page.meta_image = doc.cover_image or "/assets/blarberine/images/blarberine-og.jpg"
    page.favicon = "/assets/blarberine/images/favicon.png"
    page.blocks = new_blocks
    page.draft_blocks = new_blocks
    page.page_data_script = src.page_data_script
    page.published = 1 if doc.published else 0
    have = [r.builder_script for r in (page.get("client_scripts") or [])]
    for r in (src.client_scripts or []):
        if r.builder_script not in have:
            page.append("client_scripts", {"builder_script": r.builder_script})
    page.save(ignore_permissions=True)
    return page.name


def remove_post(route):
    name = frappe.db.get_value("Builder Page", {"route": route}, "name")
    if name:
        frappe.delete_doc("Builder Page", name, ignore_permissions=True, force=True)
