def execute():
    """Manager fix batch, 2026-07-07: centered FAQ, full-opacity gold logo,
    real brand logos in the strip, redundant '+ Add treatment' button removed,
    footer contact lines de-linked."""
    from blarberine.website_build.loader import rebuild
    rebuild()
