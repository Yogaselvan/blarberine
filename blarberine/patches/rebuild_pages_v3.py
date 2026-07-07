def execute():
    """Rebuild pages: removed 'Services' from the nav and the 'Popular services'
    section (both redundant with the booking widget); moved the 'Book an
    appointment' widget up into the popular-services slot."""
    from blarberine.website_build.loader import rebuild
    rebuild()
