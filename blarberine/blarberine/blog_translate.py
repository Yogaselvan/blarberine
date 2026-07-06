"""Auto-translate a Blog Post into the other language via DeepL (free API).

A SOURCE post (no `source_post`, `translate_automatically` on) gets a paired
child post in the other language on every save. The child is marked with
`source_post` so it never translates back (no loops) and is treated as generated.

API key: set in site config as `deepl_api_key` (bench set-config deepl_api_key ...).
Set it to a value starting with `mock` to run offline (no real API call) for testing."""

import frappe

DEEPL_URL = "https://api-free.deepl.com/v2/translate"
_TARGET = {"en": "EN-GB", "lt": "LT"}   # DeepL target codes
_SOURCE = {"en": "EN", "lt": "LT"}      # DeepL source codes


def _key():
    return frappe.conf.get("deepl_api_key")


def is_configured():
    return bool(_key())


def translate_text(text, target_lang, source_lang, html=False):
    if not text or not str(text).strip():
        return text
    key = _key()
    if not key:
        raise RuntimeError("DeepL API key not set. Add it with: bench set-config deepl_api_key <key>")
    if key.startswith("mock"):
        # offline test mode — no network call
        return "[%s] %s" % (target_lang.upper(), text)
    import requests
    data = {"text": text, "target_lang": _TARGET[target_lang], "source_lang": _SOURCE[source_lang]}
    if html:
        data["tag_handling"] = "html"
    resp = requests.post(DEEPL_URL, data=data,
                         headers={"Authorization": "DeepL-Auth-Key " + key}, timeout=30)
    resp.raise_for_status()
    return resp.json()["translations"][0]["text"]


def sync_translation(doc):
    """`doc` is a SOURCE Blog Post -> create/update its paired post in the other language."""
    src = doc.language or "lt"
    tgt = "en" if src == "lt" else "lt"
    child_name = frappe.db.get_value("Blog Post", {"source_post": doc.name}, "name")
    child = frappe.get_doc("Blog Post", child_name) if child_name else frappe.new_doc("Blog Post")
    child.source_post = doc.name
    child.language = tgt
    child.translate_automatically = 0
    child.title = translate_text(doc.title, tgt, src)
    child.excerpt = translate_text(doc.excerpt or "", tgt, src)
    child.content = translate_text(doc.content or "", tgt, src, html=True)
    child.meta_description = translate_text(doc.meta_description or "", tgt, src)
    child.cover_image = doc.cover_image
    child.author = doc.author
    child.published = doc.published
    child.published_on = doc.published_on
    # leave child.route for the child's own validate() to generate a language-appropriate slug
    child.save(ignore_permissions=True)
    return child.name
