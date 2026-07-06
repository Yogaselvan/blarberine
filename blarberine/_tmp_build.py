import frappe

SCRATCH = "/private/tmp/claude-501/-Users-yogaselvan-Desktop-Barber/aefa40bc-6005-4a7e-87bc-25c105d0f6c2/scratchpad"
MARKER_JS = "Blarberine booking wizard"
MARKER_CSS = "bl-navitem"

PAGES = [
    ("home",     "blarberine",          "Blarberine"),
    ("services", "blarberine/services", "Blarberine — Services"),
    ("team",     "blarberine/team",     "Blarberine — Barbers"),
    ("about",    "blarberine/about",    "Blarberine — About"),
]


def _ensure_script(marker, content, script_type):
    target = None
    for cs in frappe.get_all("Builder Client Script", fields=["name", "script"]):
        if marker in (cs.get("script") or ""):
            target = cs["name"]; break
    if target:
        d = frappe.get_doc("Builder Client Script", target)
        d.script = content; d.script_type = script_type; d.save()
    else:
        d = frappe.get_doc({"doctype": "Builder Client Script", "script_type": script_type, "script": content})
        d.insert()
    frappe.db.commit()
    return d.name


def _ensure_page(route, title):
    name = frappe.db.get_value("Builder Page", {"route": route}, "name")
    if name:
        return name
    doc = frappe.get_doc({"doctype": "Builder Page", "page_title": title, "route": route})
    doc.insert()
    frappe.db.commit()
    print("  created page", doc.name, "route", route)
    return doc.name


def reassign_pages(email="yogaselvansaravanan557@gmail.com"):
    """Make all Blarberine Builder Pages owned by the user's account so they
    show up in the Builder home ('My Pages')."""
    for route in ("blarberine", "blarberine/services", "blarberine/team", "blarberine/about"):
        name = frappe.db.get_value("Builder Page", {"route": route}, "name")
        if name:
            frappe.db.set_value("Builder Page", name, "owner", email, update_modified=False)
            print("owner ->", email, "|", name, route)
    frappe.db.commit()


def setup_reviews():
    """Create a Custom 'Testimonial' DocType (DB-only) and seed sample reviews."""
    if not frappe.db.exists("DocType", "Testimonial"):
        frappe.get_doc({
            "doctype": "DocType", "name": "Testimonial", "module": "Blarberine", "custom": 1,
            "autoname": "hash", "track_changes": 0,
            "fields": [
                {"fieldname": "author_name", "label": "Author", "fieldtype": "Data", "reqd": 1, "in_list_view": 1},
                {"fieldname": "rating", "label": "Rating", "fieldtype": "Int", "default": 5, "in_list_view": 1},
                {"fieldname": "service", "label": "Service", "fieldtype": "Data"},
                {"fieldname": "source", "label": "Source", "fieldtype": "Data"},
                {"fieldname": "review_date", "label": "Date", "fieldtype": "Date"},
                {"fieldname": "review_text", "label": "Review", "fieldtype": "Small Text", "reqd": 1, "in_list_view": 1},
            ],
            "permissions": [{"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1}],
        }).insert()
        frappe.db.commit()
        print("created Testimonial DocType")

    samples = [
        ("Marius K.", 5, "Skin Fade", "Google", "Best fade in Vilnius, hands down. Mantas takes his time and it always comes out perfect."),
        ("Tomas B.", 5, "Beard Sculpt & Style", "Google", "Been coming here for two years. The beard trim and hot towel is a proper ritual. Highly recommend."),
        ("Andrius P.", 5, "Classic Haircut", "Treatwell", "Walked in on a Saturday, short wait, sharp cut. Friendly team and great atmosphere."),
        ("Lukas V.", 4, "Buzz Cut", "Google", "Quick, clean and cheap. Exactly what I wanted. Will be back."),
        ("Deividas R.", 5, "Hot Towel Shave", "Treatwell", "The hot towel shave is unreal. So relaxing and the closest shave I've had. Worth every euro."),
        ("Rokas M.", 5, "Classic Haircut", "Google", "Consistently good. Tomas knows exactly what I like now. Pay at venue is handy too."),
        ("Ignas S.", 4, "Kids Haircut", "Google", "Took my son for his first proper haircut. Patient and kind with the little one. Thank you!"),
        ("Paulius Z.", 5, "Skin Fade", "Treatwell", "Clean shop, skilled barbers, fair prices. My go-to now."),
    ]
    existing = set(frappe.get_all("Testimonial", pluck="author_name"))
    added = 0
    for author, rating, service, source, text in samples:
        if author in existing:
            continue
        frappe.get_doc({"doctype": "Testimonial", "author_name": author, "rating": rating,
                        "service": service, "source": source, "review_text": text,
                        "review_date": "2026-05-15"}).insert(ignore_permissions=True)
        added += 1
    frappe.db.commit()
    print("seeded testimonials:", added, "| total:", frappe.db.count("Testimonial"))


def create_manager(email, password, full_name="Shop Manager"):
    """Create a READ-ONLY 'Booking Viewer' login for the manager.

    They can open Appointment + Customer lists (see who booked, when, which
    service/barber) but cannot write/create/delete, and cannot touch the
    website, settings or other users. Safe to hand to a manager.
    """
    import traceback
    try:
        ROLE = "Booking Viewer"

        # 1) Role
        if not frappe.db.exists("Role", ROLE):
            frappe.get_doc({
                "doctype": "Role", "role_name": ROLE,
                "desk_access": 1, "disabled": 0,
            }).insert(ignore_permissions=True)
            print("created role", ROLE)

        # 2) Read-only permissions on the two booking doctypes.
        #    Custom DocPerm so we don't alter the doctype definitions.
        for dt in ("Appointment", "Customer"):
            existing = frappe.db.get_value(
                "Custom DocPerm", {"parent": dt, "role": ROLE, "permlevel": 0}, "name")
            if not existing:
                frappe.get_doc({
                    "doctype": "Custom DocPerm", "parent": dt,
                    "parenttype": "DocType", "parentfield": "permissions",
                    "role": ROLE, "permlevel": 0,
                    "read": 1, "report": 1, "export": 1,
                    "write": 0, "create": 0, "delete": 0,
                    "submit": 0, "cancel": 0, "amend": 0,
                    "share": 0, "print": 1, "email": 0,
                }).insert(ignore_permissions=True)
                print("read-only perm ->", dt)

        # 3) User (System User so they can reach the desk / booking list).
        if frappe.db.exists("User", email):
            u = frappe.get_doc("User", email)
            print("user exists, updating:", email)
        else:
            u = frappe.get_doc({
                "doctype": "User", "email": email,
                "first_name": full_name, "user_type": "System User",
                "send_welcome_email": 0,
            })
        u.enabled = 1
        u.user_type = "System User"
        u.new_password = password
        # exactly the roles we want — nothing powerful.
        u.set("roles", [])
        u.append("roles", {"role": ROLE})
        u.save(ignore_permissions=True)

        frappe.db.commit()
        print("=" * 48)
        print("MANAGER LOGIN READY")
        print("  URL:      /login  (then Bookings at /app/appointment)")
        print("  Email:   ", email)
        print("  Password:", password)
        print("  Access:   READ-ONLY on Appointment + Customer")
        print("=" * 48)
    except Exception:
        print("ERROR:\n" + traceback.format_exc())


# English -> Lithuanian pairs, seeded once into the Translation DocType.
# After seeding, the editable source of truth is /app/translation.
TRANSLATION_SEED_LT = {
    "Add-ons": "Papildomos paslaugos", "Beard": "Barzda", "Haircuts": "Kirpimai", "Shaves": "Skutimas",
    "Beard Sculpt & Style": "Barzdos modeliavimas", "Beard Trim": "Barzdos formavimas", "Buzz Cut": "Kirpimas mašinėle",
    "Classic Haircut": "Klasikinis kirpimas", "Eyebrow Trim": "Antakių korekcija", "Hair Wash": "Plaukų plovimas",
    "Head Shave": "Galvos skutimas", "Hot Towel Shave": "Skutimas karštu rankšluosčiu", "Kids Haircut": "Vaikų kirpimas",
    "Skin Fade": "Perėjimas (skin fade)",
    "Full beard shaping, trim and conditioning.": "Pilnas barzdos formavimas, kirpimas ir priežiūra.",
    "Tidy-up and line-up of the beard.": "Barzdos tvarkymas ir kontūrų formavimas.",
    "Single-guard all-over clipper cut.": "Vientisas kirpimas mašinėle vienu antgaliu.",
    "Scissor and clipper cut, washed and styled.": "Kirpimas žirklėmis ir mašinėle, plovimas ir modeliavimas.",
    "Quick eyebrow tidy-up.": "Greita antakių korekcija.",
    "Shampoo, conditioner and blow-dry.": "Plovimas, kondicionierius ir džiovinimas.",
    "Smooth razor head shave.": "Švarus galvos skutimas skustuvu.",
    "Traditional straight-razor shave with hot towels.": "Tradicinis skutimas skustuvu su karštais rankšluosčiais.",
    "Haircut for children under 12.": "Kirpimas vaikams iki 12 metų.",
    "Clean skin fade with a sharp finish.": "Švarus perėjimas iki odos su tiksliu užbaigimu.",
    "Fast, friendly and great with kids. Your go-to for buzz cuts and quick refreshes.":
        "Greitas, draugiškas ir puikiai sutaria su vaikais. Geriausias pasirinkimas kirpimui mašinėle ir greitam atsinaujinimui.",
    "Master barber with 12 years behind the chair. Specialises in fades and classic cuts.":
        "Meistras kirpėjas, turintis 12 metų patirtį. Specializuojasi perėjimuose ir klasikiniuose kirpimuose.",
    "Beard specialist who loves a precise line-up and a sharp scissor cut.":
        "Barzdos specialistas, mėgstantis tikslius kontūrus ir preciziškus kirpimus žirklėmis.",
}


def setup_features():
    """Scenario 1-3 backend setup: seed Translation records, create the
    Appointment Calendar View, backfill start_dt/end_dt/title."""
    import traceback
    try:
        # 1) Seed Translation records (skip ones that already exist).
        existing = set(frappe.get_all("Translation", filters={"language": "lt"}, pluck="source_text"))
        added = 0
        for src, lt in TRANSLATION_SEED_LT.items():
            if src in existing:
                continue
            frappe.get_doc({"doctype": "Translation", "language": "lt",
                            "source_text": src, "translated_text": lt}).insert(ignore_permissions=True)
            added += 1
        from frappe.translate import clear_cache as tr_clear
        tr_clear()
        print("translations seeded:", added, "| total lt:", frappe.db.count("Translation", {"language": "lt"}))

        # 2) Calendar View for Appointment.
        if not frappe.db.exists("Calendar View", "Appointment Calendar"):
            cv = frappe.get_doc({"doctype": "Calendar View", "reference_doctype": "Appointment",
                                 "subject_field": "title", "start_date_field": "start_dt",
                                 "end_date_field": "end_dt", "all_day": 0})
            cv.name = "Appointment Calendar"
            cv.insert(ignore_permissions=True)
            print("created Calendar View: Appointment Calendar")
        else:
            print("Calendar View already exists")

        # 3) Backfill existing appointments (validate() computes the fields).
        filled = 0
        for name in frappe.get_all("Appointment", pluck="name"):
            doc = frappe.get_doc("Appointment", name)
            doc.save(ignore_permissions=True)
            filled += 1
        frappe.db.commit()
        print("backfilled appointments:", filled)
        sample = frappe.get_all("Appointment", fields=["name", "title", "start_dt", "end_dt"], limit=3)
        for s in sample:
            print("  ", s)
    except Exception:
        print("ERROR:\n" + traceback.format_exc())


def test_features():
    """End-to-end checks for translation inheritance, calendar fields,
    day-off blocking and busy-slot fade-out. Cleans up after itself."""
    import traceback
    from blarberine.blarberine import api
    try:
        # ---- 1) Translation DocType inheritance -------------------------
        data = api.get_booking_data("lt")
        names = [s["service_name"] for c in data["service_categories"] for s in c["services"]]
        assert "Perėjimas (skin fade)" in names, "LT service name missing: %s" % names
        print("PASS translation: get_booking_data(lt) uses Translation records")

        # live-edit round trip: new record -> visible without any code change
        src = "ZZ Test Service"
        frappe.get_doc({"doctype": "Translation", "language": "lt",
                        "source_text": src, "translated_text": "ZZ Bandymas"}).insert(ignore_permissions=True)
        assert api._tr(src, "lt") == "ZZ Bandymas", "live Translation record not picked up"
        frappe.db.delete("Translation", {"source_text": src})
        from frappe.translate import clear_cache as tr_clear
        tr_clear()
        frappe.db.commit()
        print("PASS translation: live add/edit via /app/translation works")

        # ---- 2) Calendar fields on new bookings -------------------------
        test_date = frappe.utils.add_days(frappe.utils.getdate(), 8)
        while test_date.weekday() == 6:  # skip Sunday
            test_date = frappe.utils.add_days(test_date, 1)
        slots = api.get_basket_slots(["Classic Haircut"], str(test_date))["slots"]
        assert slots, "no baseline slots on %s" % test_date
        res = api.create_basket_booking("ZZ Test Customer", ["Classic Haircut"],
                                        str(test_date), slots[0]["time"], phone="+37060000000")
        assert res.get("success"), res
        appt = frappe.get_doc("Appointment", res["appointments"][0])
        assert appt.start_dt and appt.end_dt and appt.title, "calendar fields not set"
        print("PASS calendar: new booking got title ->", appt.title)

        booked_time = slots[0]["time"]
        booked_barber = res["barber"]

        # ---- 4) fade-out: the booked slot must vanish for that barber ---
        after = api.get_basket_slots(["Classic Haircut"], str(test_date), barber=booked_barber)["slots"]
        assert booked_time not in [s["time"] for s in after], "booked slot still shown!"
        print("PASS fade-out: %s no longer offered for %s" % (booked_time, booked_barber))

        # ---- 3) day off blocks a single barber --------------------------
        barbers = frappe.get_all("Barber", filters={"is_active": 1}, pluck="name")
        off_date = frappe.utils.add_days(test_date, 1)
        while off_date.weekday() == 6:
            off_date = frappe.utils.add_days(off_date, 1)
        b0 = barbers[0]
        base_any = len(api.get_basket_slots(["Classic Haircut"], str(off_date))["slots"])
        to1 = frappe.get_doc({"doctype": "Barber Time Off", "barber": b0, "all_day": 1,
                              "from_date": str(off_date), "reason": "test day off"}).insert(ignore_permissions=True)
        own = api.get_basket_slots(["Classic Haircut"], str(off_date), barber=b0)["slots"]
        assert own == [], "day-off barber still has slots: %s" % own[:3]
        print("PASS day off: %s -> 0 slots on %s (had baseline %d any-barber)" % (b0, off_date, base_any))

        # partial time off: block the morning only
        b1 = barbers[1] if len(barbers) > 1 else b0
        to2 = frappe.get_doc({"doctype": "Barber Time Off", "barber": b1, "all_day": 0,
                              "from_date": str(off_date),
                              "start_time": "09:00:00", "end_time": "12:00:00",
                              "reason": "test partial"}).insert(ignore_permissions=True)
        part = api.get_basket_slots(["Classic Haircut"], str(off_date), barber=b1)["slots"]
        morn = [s["time"] for s in part if s["time"] < "12:00"]
        assert not morn, "partial block leaked morning slots: %s" % morn
        print("PASS partial off: %s has no slots before 12:00" % b1)

        # ---- 3+4) ALL barbers off -> customer sees nothing --------------
        extra = []
        for b in barbers:
            if b != b0:
                extra.append(frappe.get_doc({"doctype": "Barber Time Off", "barber": b, "all_day": 1,
                                             "from_date": str(off_date), "reason": "test"}).insert(ignore_permissions=True))
        allslots = api.get_basket_slots(["Classic Haircut"], str(off_date))["slots"]
        week = api.get_week_availability(["Classic Haircut"], str(off_date))
        daycount = [d["count"] for d in week if d["date"] == str(off_date)][0]
        assert allslots == [] and daycount == 0, "all-off day still bookable"
        print("PASS all-off: %s shows 0 slots + greyed day in week strip" % off_date)

        # ---- cleanup -----------------------------------------------------
        for d in [to1, to2] + extra:
            frappe.delete_doc("Barber Time Off", d.name, ignore_permissions=True, force=True)
        for a in res["appointments"]:
            frappe.delete_doc("Appointment", a, ignore_permissions=True, force=True)
        frappe.db.delete("Customer", {"customer_name": "ZZ Test Customer"})
        frappe.db.commit()
        print("cleanup done — ALL TESTS PASSED")
    except Exception:
        frappe.db.rollback()
        print("TEST FAILURE:\n" + traceback.format_exc())


def retitle_appointments():
    """Recompute Appointment calendar title/start_dt/end_dt directly in the DB
    (no full save) so it also fixes legacy rows whose Customer/Barber link was
    later deleted."""
    import traceback
    from frappe.utils import get_datetime
    try:
        rows = frappe.get_all("Appointment", fields=["name", "customer", "barber", "service",
                                                     "appointment_date", "start_time", "end_time"])
        done = 0
        for a in rows:
            if not (a.appointment_date and a.start_time):
                continue
            start = get_datetime("%s %s" % (a.appointment_date, a.start_time))
            end = get_datetime("%s %s" % (a.appointment_date, a.end_time or a.start_time))
            customer = frappe.db.get_value("Customer", a.customer, "customer_name") or a.customer
            barber = frappe.db.get_value("Barber", a.barber, "barber_name") or a.barber
            hhmm = start.strftime("%H:%M")
            title = "%s %s — %s · %s" % (hhmm, customer, barber, a.service)
            label = "%s\n%s\n%s" % (customer, hhmm, barber)
            frappe.db.set_value("Appointment", a.name, {
                "title": title, "calendar_label": label,
                "start_dt": start, "end_dt": end}, update_modified=False)
            done += 1
        # Point the calendar at the stacked label.
        if frappe.db.exists("Calendar View", "Appointment Calendar"):
            frappe.db.set_value("Calendar View", "Appointment Calendar", "subject_field", "calendar_label")
        frappe.db.commit()
        print("retitled:", done)
        for s in frappe.get_all("Appointment", fields=["name", "calendar_label"], limit=4):
            print("  ", repr(s["calendar_label"]))
    except Exception:
        frappe.db.rollback()
        print("ERROR:\n" + traceback.format_exc())


def dbg_timeoff():
    import traceback, datetime
    from blarberine.blarberine import api
    try:
        print("existing rows:", frappe.get_all("Barber Time Off",
              fields=["name", "barber", "from_date", "to_date", "start_time", "end_time"]))
        d = frappe.get_doc({"doctype": "Barber Time Off", "barber": "Lukas Jankauskas",
                            "from_date": "2026-07-11", "reason": "dbg"}).insert(ignore_permissions=True)
        print("inserted:", d.name, "| from:", d.from_date, "| to:", d.to_date, "| controller:", type(d).__name__)
        raw = frappe.db.get_value("Barber Time Off", d.name, ["from_date", "to_date"], as_dict=True)
        print("raw db:", raw)
        print("raw sql:", frappe.db.sql(
            "select start_time, end_time from `tabBarber Time Off` where name=%s", d.name))
        print("doc attrs:", repr(d.start_time), repr(d.end_time))
        print("intervals:", api._time_off_intervals("Lukas Jankauskas", datetime.date(2026, 7, 11)))
        print("busy:", api._busy_intervals("Lukas Jankauskas", datetime.date(2026, 7, 11)))
        frappe.delete_doc("Barber Time Off", d.name, ignore_permissions=True, force=True)
        frappe.db.commit()
    except Exception:
        frappe.db.rollback()
        print("DBG ERROR:\n" + traceback.format_exc())


def inspect_dts():
    import json, traceback
    try:
        for dt in ("Appointment", "Translation", "Calendar View"):
            fields = frappe.get_all("DocField", filters={"parent": dt},
                                    fields=["fieldname", "fieldtype", "label", "options"], order_by="idx")
            print(dt.upper(), "::", json.dumps(fields, default=str))
    except Exception:
        print("ERR:\n" + traceback.format_exc())


def dbg():
    import traceback
    doc = frappe.get_doc("Builder Page", "page-180e8dca")
    try:
        d = doc.get_page_data()
        print("OK keys:", sorted(d.keys()))
        print("popular sample:", (d.get("popular_services") or [{}])[0])
    except Exception:
        print("DATA SCRIPT ERROR:\n" + traceback.format_exc())


def run_all(email="yogaselvansaravanan557@gmail.com"):
    import json
    js = open(SCRATCH + "/booking.js").read()
    css = open(SCRATCH + "/nav.css").read()
    interactive = open(SCRATCH + "/interactive.js").read()
    js_name = _ensure_script(MARKER_JS, js, "JavaScript")
    css_name = _ensure_script(MARKER_CSS, css, "CSS")
    int_name = _ensure_script("Blarberine interactive widgets", interactive, "JavaScript")
    script_names = (js_name, css_name, int_name)
    print("scripts:", script_names)

    ds_cache = {}
    def data_script(fname):
        if fname not in ds_cache:
            ds_cache[fname] = open(SCRATCH + "/" + fname).read()
        return ds_cache[fname]

    manifest = json.load(open(SCRATCH + "/pages/manifest.json"))
    for e in manifest:
        name = _ensure_page(e["route"], e["title"])
        blocks = open(SCRATCH + "/pages/" + e["file"]).read()
        doc = frappe.get_doc("Builder Page", name)
        doc.draft_blocks = blocks
        doc.blocks = blocks
        doc.page_data_script = data_script(e["data_script"])
        doc.published = 1
        doc.route = e["route"]
        if e.get("seo_title"):
            doc.page_title = e["seo_title"]
        if e.get("seo_desc"):
            doc.meta_description = e["seo_desc"]
        if e.get("seo_image"):
            doc.meta_image = e["seo_image"]
        have = [r.builder_script for r in (doc.get("client_scripts") or [])]
        for sname in script_names:
            if sname not in have:
                doc.append("client_scripts", {"builder_script": sname})
        doc.save()
        frappe.db.set_value("Builder Page", name, "owner", email, update_modified=False)
        frappe.db.commit()
        print("PUBLISHED %-2s %-8s -> /%s" % (e["lang"], e["key"], e["route"]))


def rerender_blog():
    """Re-render every Blog Post's Builder Page (refresh nav/footer/meta) — no DeepL calls."""
    from blarberine.blarberine.blog_render import render_post
    n = 0
    for r in frappe.get_all("Blog Post", fields=["name"]):
        render_post(frappe.get_doc("Blog Post", r.name))
        n += 1
    frappe.db.commit()
    print("re-rendered %d blog pages" % n)


def translate_existing():
    """Translate every source Blog Post (translate_automatically on) via the real DeepL key."""
    import traceback
    from blarberine.blarberine.blog_translate import sync_translation, is_configured
    try:
        print("DeepL configured:", is_configured())
        for r in frappe.get_all("Blog Post",
                                filters={"source_post": ["is", "not set"], "translate_automatically": 1},
                                fields=["name", "title", "language"]):
            doc = frappe.get_doc("Blog Post", r.name)
            child_name = sync_translation(doc)
            child = frappe.get_doc("Blog Post", child_name)
            print("SRC [%s]: %s" % (doc.language, doc.title))
            print("  -> [%s]: %s | %s | published=%s" % (child.language, child.title, child.route, child.published))
        frappe.db.commit()
        print("done")
    except Exception:
        traceback.print_exc()


def cleanup_mock_translation():
    """Remove any auto-generated (translated) child posts + their pages (mock cleanup)."""
    import traceback
    try:
        for c in frappe.get_all("Blog Post", filters={"source_post": ["is", "set"]}, fields=["name", "title"]):
            frappe.delete_doc("Blog Post", c.name, ignore_permissions=True, force=True)
            print("deleted child:", c.title)
        frappe.db.commit()
        print("done")
    except Exception:
        traceback.print_exc()


def test_autotranslate():
    """Flip translate_automatically on the LT 'barzda' post and verify the paired EN post
    + its Builder Page get created (uses mock DeepL key -> offline)."""
    import traceback
    try:
        rows = frappe.get_all("Blog Post", filters={"title": "Kaip pasirūpinti barzda: 5 patarimai"}, fields=["name"])
        if not rows:
            print("source post not found"); return
        doc = frappe.get_doc("Blog Post", rows[0].name)
        doc.translate_automatically = 1
        doc.save(ignore_permissions=True)
        frappe.db.commit()
        print("SOURCE:", doc.language, doc.route, "|", doc.title)
        child = frappe.db.get_value("Blog Post", {"source_post": doc.name},
                                    ["name", "language", "route", "title", "published"], as_dict=True)
        print("CHILD :", child)
        if child:
            pg = frappe.db.get_value("Builder Page", {"route": child["route"]}, ["name", "published"], as_dict=True)
            print("CHILD PAGE:", pg)
    except Exception:
        traceback.print_exc()


def seed_blog():
    """Create a couple of sample published Blog Posts (LT). Saving each fires
    on_update -> render_post -> a themed Builder Page at its route. Idempotent by title."""
    import traceback
    posts = [
        {"title": "Kaip pasirūpinti barzda: 5 patarimai",
         "excerpt": "Paprasti žingsniai, kad barzda atrodytų tvarkinga ir sveika kiekvieną dieną.",
         "cover_image": "https://images.unsplash.com/photo-1621605815971-fbc98d665033?auto=format&fit=crop&w=1000&q=80",
         "content": (
            "<p>Tvarkinga barzda – tai ne tik geras kirpimas, bet ir kasdienė priežiūra. "
            "Štai penki paprasti patarimai, kurie padės jūsų barzdai atrodyti puikiai.</p>"
            "<h2>1. Plaukite reguliariai</h2><p>Naudokite švelnų barzdos šampūną 2–3 kartus per "
            "savaitę, kad oda po barzda liktų švari ir sveika.</p>"
            "<h2>2. Naudokite aliejų</h2><p>Barzdos aliejus minkština plaukelius ir maitina odą – "
            "ypač svarbu šaltuoju metų laiku.</p>"
            "<h2>3. Šukuokite kasdien</h2><p>Reguliarus šukavimas nukreipia plaukelius tinkama "
            "kryptimi ir padeda išvengti susivėlimo.</p>"
            "<h2>4. Formuokite reguliariai</h2><p>Užsukite pas meistrą kas 3–4 savaites, kad "
            "kontūrai išliktų aiškūs.</p>"
            "<h2>5. Nepamirškite kaklo linijos</h2><p>Tvarkinga kaklo linija – smulkmena, kuri iš "
            "karto pakelia bendrą įvaizdį.</p>")},
        {"title": "Kaip išsirinkti kirpimą pagal veido formą",
         "excerpt": "Trumpas gidas, padėsiantis pasirinkti kirpimą, kuris pabrėžia jūsų bruožus.",
         "cover_image": "https://images.unsplash.com/photo-1503443207922-dff7d543fd0e?auto=format&fit=crop&w=1000&q=80",
         "content": (
            "<p>Tinkamas kirpimas pabrėžia veido bruožus ir suteikia pasitikėjimo. "
            "Štai kaip pasirinkti kirpimą pagal veido formą.</p>"
            "<h2>Apvalus veidas</h2><p>Rinkitės kirpimą su daugiau apimties viršuje ir trumpesniais "
            "šonais – tai vizualiai pailgina veidą.</p>"
            "<h2>Kvadratinis veidas</h2><p>Tinka beveik viskas, tačiau klasikiniai kirpimai puikiai "
            "pabrėžia stiprų žandikaulį.</p>"
            "<h2>Pailgas veidas</h2><p>Venkite per daug apimties viršuje – rinkitės vidutinio ilgio "
            "šonus, kad proporcijos išliktų darnios.</p>"
            "<p>Nežinote, kas tiktų jums? <strong>Užsukite</strong> – padėsime išsirinkti.</p>")},
    ]
    try:
        for i, p in enumerate(posts):
            # delete any prior version (also removes its Builder Page via on_trash) then recreate clean
            for e in frappe.get_all("Blog Post", filters={"title": p["title"]}, fields=["name"]):
                frappe.delete_doc("Blog Post", e.name, ignore_permissions=True, force=True)
            doc = frappe.new_doc("Blog Post")
            doc.title = p["title"]
            doc.excerpt = p["excerpt"]
            doc.cover_image = p["cover_image"]
            doc.content = p["content"]
            doc.author = "Blarberinė"
            doc.language = "lt"
            doc.published = 1
            doc.published_on = frappe.utils.add_days(frappe.utils.today(), -i)
            doc.save(ignore_permissions=True)
            print("seeded post:", doc.title, "-> route", doc.route)
        frappe.db.commit()
        print("done")
    except Exception:
        traceback.print_exc()


def inspect_barbers():
    import traceback
    try:
        for b in frappe.get_all("Barber", fields=["name", "barber_name", "is_active", "photo", "bio"],
                                order_by="barber_name asc"):
            print("---")
            print("name      :", b.name)
            print("barber    :", b.barber_name, "| active:", b.is_active)
            print("photo     :", repr(b.photo))
            print("bio       :", repr(b.bio))
    except Exception:
        traceback.print_exc()


def fix_lukas():
    """Two real problems: (1) Lukas' photo points at a missing private file -> broken image;
    (2) the LT page shows 'kazkas' because the Translation record for his (correct) English bio
    was set to junk. Fix the photo (clear -> stock fallback like the others) and repair the bio
    translation to proper Lithuanian."""
    import traceback
    try:
        EN_BIO = "Fast, friendly and great with kids. Your go-to for buzz cuts and quick refreshes."
        LT_BIO = ("Greitas, draugiškas ir puikiai sutaria su vaikais. "
                  "Geriausias pasirinkimas kirpimui mašinėle ir greitam atsinaujinimui.")
        # 1) broken photo -> empty so the data-script stock fallback renders (same as Mantas/Tomas)
        for r in frappe.get_all("Barber", filters={"barber_name": "Lukas Jankauskas"}, fields=["name", "photo"]):
            print("was photo:", repr(r.photo))
            frappe.db.set_value("Barber", r.name, "photo", "")
            print("photo cleared for", r.name)
        # 2) repair the LT bio translation (was 'kazkas')
        trs = frappe.get_all("Translation", filters={"language": "lt", "source_text": EN_BIO},
                             fields=["name", "translated_text"])
        for tr in trs:
            print("was translation:", repr(tr.translated_text))
            frappe.db.set_value("Translation", tr.name, "translated_text", LT_BIO)
            print("translation fixed:", tr.name)
        if not trs:
            frappe.get_doc({"doctype": "Translation", "language": "lt",
                            "source_text": EN_BIO, "translated_text": LT_BIO}).insert(ignore_permissions=True)
            print("translation created")
        # sweep any other stray 'kazkas' rows
        for tr in frappe.get_all("Translation", filters={"translated_text": "kazkas"}, fields=["name", "source_text"]):
            print("STRAY kazkas translation still present for source:", repr(tr.source_text))
        frappe.translate.clear_cache()
        frappe.db.commit()
        print("done")
    except Exception:
        traceback.print_exc()
