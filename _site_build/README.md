# Site build sources

Source files that generate the Blarberinė Frappe Builder pages and client scripts.

- `build_page.py` — generates the 8 Builder page JSON files (LT + EN), per-language
  page data scripts, and `nav.css`. Run: `python3 build_page.py` (writes to `pages/`).
- `booking.js` — Builder Client Script: the multi-service booking wizard.
- `interactive.js` — Builder Client Script: services filter/basket + team widgets.
- `nav.css` — Builder Client Script (CSS): nav, fonts (Playfair Display + Montserrat), theme.

Deploy helper lives in `../_tmp_build.py` (`run_all`, `setup_features`, `create_manager`).
The live pages/scripts also travel with the site database backup, so a Frappe Cloud
restore brings them across without re-running the generator.
