def execute():
    """Rebuild pages for the 2026-07-07 batch: smaller non-stretched footer
    logo, single-service booking flow (add-more removed), removed stats bar +
    reviews badge, Treatwell calendar, cookie consent + gated analytics."""
    from blarberine.website_build.loader import rebuild
    rebuild()
