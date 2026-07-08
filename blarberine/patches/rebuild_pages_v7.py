def execute():
    """v7 LIGHT design + owner tweaks (2026-07-08): location/hours strip moved
    ABOVE the navbar, owner-supplied hero photo, Price-list section removed from
    home, booking service-picker keeps the selected category after '+ Add'.
    Rebuilds all Builder pages from the in-app generator."""
    from blarberine.website_build.loader import rebuild
    rebuild()
