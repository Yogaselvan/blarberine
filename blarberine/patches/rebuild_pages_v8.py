def execute():
    """v8 (2026-07-08): "Our work" gallery is now manager-editable via the new
    Gallery Image DocType (falls back to placeholder photos when empty).
    Rebuilds all Builder pages so the gallery renders from the repeater."""
    from blarberine.website_build.loader import rebuild
    rebuild()
