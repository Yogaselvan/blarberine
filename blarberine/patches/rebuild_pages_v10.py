def execute():
    """v10 (2026-09, manager task 1): the barber detail panel on the team page
    (/team?pro=<Barber>) now shows the manager-uploaded "Our work" photos from
    the Gallery Image DocType — the same set the home page renders — instead of
    showing no photos at all. get_booking_data() returns gallery_images and
    interactive.js draws them under the barber's services.
    Rebuilds all Builder pages/scripts to ship the updated JS."""
    from blarberine.website_build.loader import rebuild
    rebuild()
