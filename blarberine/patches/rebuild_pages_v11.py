def execute():
    """v11 (2026-09, manager task 1 — corrected): the team page's "Our work"
    section was a hardcoded grid of stock photos, which is what the manager saw
    as "random placeholder pictures" on the barber pages. It now repeats over
    data.gallery_images (Gallery Image DocType), so it shows the same photos as
    the home page.

    Supersedes v10, which had instead added a second gallery inside the barber
    detail panel; the manager asked for the photos in the lower "Our work"
    section rather than under the barber, so that panel gallery is removed.
    Rebuilds all Builder pages/scripts to ship both changes."""
    from blarberine.website_build.loader import rebuild
    rebuild()
