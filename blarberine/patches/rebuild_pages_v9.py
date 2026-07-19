def execute():
    """v9 (2026-07-08, manager feedback round 2): lean checkout (name + phone
    only, both required), sticky basket bar hidden on pages that embed the
    booking widget, and cross-script basket sync so the bar never goes stale.
    Rebuilds all Builder pages/scripts to ship the updated JS."""
    from blarberine.website_build.loader import rebuild
    rebuild()
