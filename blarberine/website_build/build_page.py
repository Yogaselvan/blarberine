#!/usr/bin/env python3
"""
Blarberine — BILINGUAL multi-page Frappe Builder site (Lithuanian default + English).
Emits 8 pages: {lt,en} x {home,services,team,about}. LT at bare routes, EN under /en/.
Static UI text via a central T dict + t(); dynamic DocType data translated in the
per-language page data script (and mirrored in api.py for the JS widgets).
"""
import json, os
SCRATCH = os.path.dirname(os.path.abspath(__file__))
PAGES_DIR = os.path.join(SCRATCH, "pages")

LANGS = ["lt", "en"]
DEFAULT_LANG = "lt"
KEYS = ["home", "services", "team", "blog"]   # 'about' removed — merged into home contact section

def _routes(lang):
    # clean URLs: LT at root (home/services/team/blog), EN under /en
    if lang == DEFAULT_LANG:
        return {"home": "home", "services": "services", "team": "team", "blog": "blog"}
    return {"home": "en", "services": "en/services", "team": "en/team", "blog": "en/blog"}
ROUTES = {l: _routes(l) for l in LANGS}

# v3 LIGHT PREMIUM (2026-07-07, owner brief: light colors, premium feel,
# animations, simple hero with one Book-now CTA). Ivory canvas, white cards,
# charcoal text, gold-bronze accent, dark footer band for contrast, serif
# display headings. Token ROLES kept: INK/BODY/MUTED are text (dark now),
# BG/ALT/CARD are light surfaces, NAVY is the dark footer/brands band.
BG="#faf8f3"; ALT="#f1ece2"; INK="#26211a"; BODY="#57503f"; MUTED="#8c8271"
BORDER="#e6dfd0"; CORAL="#b3873c"; NAVY="#181410"; GOLD="#b3873c"; CARD="#ffffff"
BAR_Y,BAR_B,BAR_T="#b3873c","#8a6527","#dcc28a"
LBG="#ffffff"; LCARD="#faf8f3"; LINK="#26211a"; LMUT="#8c8271"; LLINE="#e6dfd0"
FONT="'Montserrat', system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
HEAD="'Cormorant Garamond', 'Playfair Display', Georgia, serif"
# High-quality, verified barbershop photography (all return 200 at these
# widths). Placeholders until Mantas supplies the shop's own photos.
_U="https://images.unsplash.com/photo-%s?auto=format&fit=crop&w=%d&q=80"
# owner-supplied hero photo (1920x950, shipped in-app 2026-07-08)
HERO_IMG="/assets/blarberine/images/hero-banner.jpg"
GALLERY=[
 _U % ("1503951914875-452162b0f3f1", 1400),   # hot-towel shave
 _U % ("1622286342621-4bd786c2447c", 1400),   # cut in progress
 _U % ("1599351431202-1e0f0137899a", 1400)]   # skin fade + razor detail
WORK=[
 _U % ("1521119989659-a83eee488004", 1100),   # groomed portrait (barber-card fallback)
 _U % ("1593702275687-f8b402bf1fb5", 1100),   # fade
 _U % ("1596728325488-58c87691e9af", 1100),   # straight-razor
 _U % ("1517832606299-7ae9b720a186", 1100),   # dramatic shave
 _U % ("1605497788044-5a32c7078486", 1100),   # styling / blow-dry
 _U % ("1512690459411-b9245aed614b", 1100)]   # vintage chair detail
PROMO=[
 _U % ("1596728325488-58c87691e9af", 800),
 _U % ("1512690459411-b9245aed614b", 800)]

# PLACEHOLDER pro-barber grooming brands — Mantas to confirm the real ones the shop uses.
BRANDS=[("American Crew","american-crew"),("STMNT Grooming","stmnt"),("Wahl Professional","wahl"),
        ("Joewell","joewell"),("REM","rem"),("Parlux","parlux")]
# PLACEHOLDER before/after pairs (known-good stock) — Mantas to send REAL client before/after photos.
BEFORE_AFTER=[(WORK[2],WORK[0]),(WORK[3],WORK[1]),(WORK[5],WORK[4])]
# DUMMY founder portrait — replace with the real founder's photo.
FOUNDER_PHOTO=_U % ("1521119989659-a83eee488004", 800)

# ---------------------------------------------------------------- i18n
T = {
 "nav_services":{"en":"Services","lt":"Paslaugos"},
 "nav_barbers":{"en":"Barbers","lt":"Kirpėjai"},
 "nav_about":{"en":"About","lt":"Apie"},
 "nav_blog":{"en":"Blog","lt":"Blogas"},
 "book_now":{"en":"Book now","lt":"Rezervuoti"},
 "book_appt":{"en":"Book an appointment","lt":"Rezervuoti vizitą"},
 "hero_head":{"en":"Where tradition meets modern style","lt":"Kur tradicija susitinka su šiuolaikiniu stiliumi"},
 "no_card":{"en":"no card needed","lt":"kortelės nereikia"},
 "works_title":{"en":"Our work","lt":"Mūsų darbai"},
 "works_sub":{"en":"The styles we craft every day.","lt":"Stilius, kurį kuriame kasdien."},
 "prices_title":{"en":"Price list","lt":"Kainoraštis"},
 "prices_sub":{"en":"Most popular services — the full list is in the booking window.",
               "lt":"Populiariausios paslaugos — visą sąrašą rasite rezervacijos lange."},
 "join_title":{"en":"Would you like to join our team?","lt":"Nori prisijungti prie mūsų komandos?"},
 "join_btn":{"en":"Get in touch","lt":"Susisiekite"},
 "menu_services_head":{"en":"Services","lt":"Paslaugos"},
 "see_all_services":{"en":"See all services →","lt":"Visos paslaugos →"},
 "our_barbers":{"en":"Our barbers","lt":"Mūsų kirpėjai"},
 "meet_team_arrow":{"en":"Meet the team →","lt":"Komanda →"},
 "promo1":{"en":"Fresh fades & classic cuts","lt":"Perėjimai ir klasikiniai kirpimai"},
 "promo2":{"en":"Hot-towel shaves","lt":"Skutimas karštu rankšluosčiu"},
 "trusted":{"en":"Trusted local barbershop","lt":"Patikima vietinė kirpykla"},
 "vilnius":{"en":"·  Kaunas","lt":"·  Kaunas"},
 "hero_tag":{"en":"Book a chair with Kaunas' sharpest barbers. Walk-ins welcome, pay at the venue.",
             "lt":"Rezervuokite kėdę pas geriausius Kauno kirpėjus. Ateikite ir be registracijos, atsiskaitoma vietoje."},
 "view_services":{"en":"View services →","lt":"Peržiūrėti paslaugas →"},
 "address_line":{"en":"Utenos g. 16, Kaunas, Lithuania","lt":"Utenos g. 16, Kaunas, Lietuva"},
 "open_today":{"en":"Open today: 09:00 – 19:00","lt":"Šiandien dirbame: 09:00 – 19:00"},
 "show_details":{"en":"Show details","lt":"Plačiau"},
 "popular_services":{"en":"Popular services","lt":"Populiarios paslaugos"},
 "the_team":{"en":"The team","lt":"Komanda"},
 "meet_barbers":{"en":"Meet the barbers","lt":"Susipažinkite su kirpėjais"},
 "meet_team_btn":{"en":"Meet the team","lt":"Susipažinkite su komanda"},
 "reserve_chair":{"en":"Reserve your chair","lt":"Rezervuokite kėdę"},
 "booking_intro":{"en":"Pick a service, a barber, a date and a time. Pay at the venue — no card needed.",
                  "lt":"Pasirinkite paslaugą, kirpėją, datą ir laiką. Atsiskaitoma vietoje — kortelės nereikia."},
 "loading_booking":{"en":"Loading booking…","lt":"Kraunama rezervacija…"},
 "price_list":{"en":"Price list","lt":"Kainoraštis"},
 "our_services":{"en":"Our services","lt":"Mūsų paslaugos"},
 "services_intro":{"en":"Choose a category, add what you fancy, then pick a time. Pay at the venue.",
                   "lt":"Pasirinkite kategoriją, pridėkite norimas paslaugas ir išsirinkite laiką. Atsiskaitoma vietoje."},
 "loading_services":{"en":"Loading services…","lt":"Kraunamos paslaugos…"},
 "our_work":{"en":"Our work","lt":"Mūsų darbai"},
 "loading_team":{"en":"Loading team…","lt":"Kraunama komanda…"},
 "stat_years_num":{"en":"5+","lt":"5+"},                         # PLACEHOLDER — Mantas: real years open
 "stat_years_lbl":{"en":"Years of experience","lt":"Metų patirties"},
 "stat_barbers_lbl":{"en":"Pro barbers","lt":"Profesionalūs kirpėjai"},
 "stat_clients_num":{"en":"3000+","lt":"3000+"},                 # PLACEHOLDER — Mantas: real client count
 "stat_clients_lbl":{"en":"Happy clients","lt":"Patenkintų klientų"},
 "ba_kicker":{"en":"Transformations","lt":"Pokyčiai"},
 "ba_title":{"en":"Before & after","lt":"Prieš ir po"},
 "ba_intro":{"en":"Real cuts from our chairs — a few recent transformations.",
             "lt":"Tikri kirpimai iš mūsų kėdžių — keletas naujausių pokyčių."},
 "ba_before":{"en":"Before","lt":"Prieš"},
 "ba_after":{"en":"After","lt":"Po"},
 "faq_kicker":{"en":"Good to know","lt":"Verta žinoti"},
 "faq_title":{"en":"Frequently asked questions","lt":"Dažniausiai užduodami klausimai"},
 "faq1_q":{"en":"How do I book an appointment?","lt":"Kaip užsiregistruoti vizitui?"},
 "faq1_a":{"en":"Pick a service, a barber, a date and a time right here on the site — it takes under a minute, and you'll get a confirmation with your booking reference.",
           "lt":"Pasirinkite paslaugą, kirpėją, datą ir laiką čia pat svetainėje — tai užtrunka mažiau nei minutę, o jūs gausite patvirtinimą su rezervacijos numeriu."},
 "faq2_q":{"en":"How do I pay?","lt":"Kaip atsiskaityti?"},
 "faq2_a":{"en":"You pay at the venue after your cut — cash or card. No card is needed to book online, and there is no online payment.",
           "lt":"Atsiskaitote vietoje po kirpimo — grynaisiais arba kortele. Registruojantis internetu kortelės nereikia, o mokėjimų internetu nėra."},
 "faq3_q":{"en":"Do you accept walk-ins?","lt":"Ar priimate be išankstinės registracijos?"},
 "faq3_a":{"en":"Walk-ins are welcome whenever a chair is free, but we recommend booking ahead so your preferred barber and time are guaranteed.",
           "lt":"Mielai priimame, kai yra laisva kėdė, tačiau rekomenduojame registruotis iš anksto, kad būtų garantuotas norimas kirpėjas ir laikas."},
 "faq4_q":{"en":"How much does a haircut cost?","lt":"Kiek kainuoja kirpimas?"},
 "faq4_a":{"en":"Haircuts start from €12, with classic cuts and skin fades up to €28. You can see the full price list on the services page.",
           "lt":"Kirpimai prasideda nuo €12, klasikiniai kirpimai ir perėjimai — iki €28. Visą kainoraštį rasite paslaugų puslapyje."},
 "faq5_q":{"en":"Do you cut children's hair?","lt":"Ar kerpate vaikus?"},
 "faq5_a":{"en":"Yes — we offer kids' haircuts and are happy to work with younger clients in a relaxed, friendly setting.",
           "lt":"Taip — turime vaikų kirpimo paslaugą ir mielai kerpame jaunuosius klientus jaukioje, draugiškoje aplinkoje."},
 "faq6_q":{"en":"What languages do you speak?","lt":"Kokiomis kalbomis kalbate?"},
 "faq6_a":{"en":"Our barbers speak Lithuanian and English, so you'll feel at home whether you're local or just visiting.",
           "lt":"Mūsų kirpėjai kalba lietuvių ir anglų kalbomis, todėl jausitės patogiai — ar esate vietinis, ar svečias."},
 "faq7_q":{"en":"Where are you located?","lt":"Kur mus rasti?"},
 "faq7_a":{"en":"You'll find us at Utenos g. 16, Kaunas. Street parking is nearby.",
           "lt":"Esame Utenos g. 16, Kaune. Netoliese — vietos automobiliams gatvėje."},
 # Founder card — DUMMY content, Mantas to replace name/role/quote/bio/photo with the real founder.
 "founder_kicker":{"en":"Founder","lt":"Įkūrėjas"},
 "founder_name":{"en":"Mantas Petrauskas","lt":"Mantas Petrauskas"},
 "founder_role":{"en":"Founder & Head Barber","lt":"Įkūrėjas ir vyriausiasis kirpėjas"},
 "founder_quote":{"en":"We don't chase speed — we chase the perfect cut, every single time.",
                  "lt":"Nesivaikome greičio — siekiame tobulo kirpimo kiekvieną kartą."},
 "founder_bio":{"en":"Mantas opened Blarberinė to bring proper, unhurried barbering to Kaunas. With over a decade behind the chair, he built a team that treats every haircut as craft and every client as a regular.",
                "lt":"Mantas įkūrė Blarberinę, norėdamas Kaunui suteikti tikrą, neskubų kirpimo meną. Turėdamas daugiau nei dešimtmetį patirties, jis subūrė komandą, kuri kiekvieną kirpimą laiko amatu, o kiekvieną klientą — nuolatiniu."},
 # Google rating badge — TEST values, replace with the real Google Business rating + review count + link.
 "google_reviews_count":{"en":"Based on 120 Google reviews","lt":"Pagal 120 „Google“ atsiliepimų"},
 "blog_kicker":{"en":"Blog","lt":"Blogas"},
 "blog_title":{"en":"News & tips","lt":"Naujienos ir patarimai"},
 "blog_intro":{"en":"Grooming tips, style guides and news from the chair.",
               "lt":"Priežiūros patarimai, stiliaus gidai ir naujienos iš mūsų kėdžių."},
 "blog_read":{"en":"Read →","lt":"Skaityti →"},
 "blog_empty":{"en":"No posts yet — check back soon.","lt":"Kol kas įrašų nėra — užsukite netrukus."},
 "contact_kicker":{"en":"Contact","lt":"Kontaktai"},
 "contact_intro":{"en":"Drop by, call ahead, or get directions — we're at Utenos g. 16 in Kaunas.",
                  "lt":"Užsukite, paskambinkite ar nuvykite pagal nuorodą — esame Utenos g. 16, Kaune."},
 "con_address":{"en":"Address","lt":"Adresas"},
 "con_phone":{"en":"Phone","lt":"Telefonas"},
 "con_hours":{"en":"Opening hours","lt":"Darbo laikas"},
 "findus_kicker":{"en":"Visit","lt":"Užsukite"},
 "findus_title":{"en":"Find us in Kaunas","lt":"Raskite mus Kaune"},
 "findus_sub":{"en":"Utenos g. 16, Kaunas, Lithuania.",
               "lt":"Utenos g. 16, Kaunas, Lietuva."},
 "craft_kicker":{"en":"Our craft","lt":"Kirpimo menas"},
 "craft_title":{"en":"The art of a proper cut","lt":"Tikro kirpimo menas"},
 "craft_intro":{"en":"We don't rush. Every visit is an experience, not just a service — precise, clean and built to last.",
                "lt":"Neskubame. Kiekvienas apsilankymas — tai patirtis, ne tik paslauga: tikslu, švaru ir sukurta išlikti."},
 "craft_p1_t":{"en":"Precision","lt":"Tikslumas"},
 "craft_p1_d":{"en":"Every cut is targeted, clean and shaped to grow out well. We chase perfection, not speed.",
               "lt":"Kiekvienas kirpimas tikslingas, švarus ir suformuotas taip, kad gražiai atželtų. Siekiame tobulumo, ne greitumo."},
 "craft_p2_t":{"en":"Experience","lt":"Patirtis"},
 "craft_p2_d":{"en":"Years behind the chair and an eye for detail — you're in steady, practised hands.",
               "lt":"Metų metai prie kėdės ir dėmesys detalėms — esate patyrusiose rankose."},
 "craft_p3_t":{"en":"Tradition","lt":"Tradicija"},
 "craft_p3_d":{"en":"Classic methods paired with modern tools. We respect the craft and keep refining it.",
               "lt":"Klasikiniai metodai su moderniais įrankiais. Gerbiame amatą ir nuolat jį tobuliname."},
 "brands_kicker":{"en":"Products we use","lt":"Naudojami produktai"},
 "brands_title":{"en":"Highest-quality cosmetics","lt":"Aukščiausios kokybės kosmetika"},
 "brands_intro":{"en":"The professional brands we trust for every cut, shave and finish — so you leave looking your best.",
                 "lt":"Profesionalūs prekės ženklai, kuriais pasitikime kiekvienam kirpimui, skutimui ir stiliui — kad išeitumėte atrodydami puikiai."},
 "reviews_kicker":{"en":"Reviews","lt":"Atsiliepimai"},
 "reviews_title":{"en":"What our clients say","lt":"Ką sako mūsų klientai"},
 "good_to_know":{"en":"Good to know","lt":"Verta žinoti"},
 "about_shop":{"en":"About the shop","lt":"Apie kirpyklą"},
 "get_directions":{"en":"Get directions →","lt":"Kaip nuvykti →"},
 "addr_city":{"en":"Kaunas, Lithuania","lt":"Kaunas, Lietuva"},
 "amenities_title":{"en":"Amenities","lt":"Patogumai"},
 "am_products":{"en":"Products","lt":"Produktai"},
 "am_payment":{"en":"Payment methods","lt":"Atsiskaitymo būdai"},
 "am_location":{"en":"Location","lt":"Vieta"},
 "am_p1":{"en":"Locally-made products","lt":"Vietinės gamybos produktai"},
 "am_p2":{"en":"Organic products","lt":"Ekologiški produktai"},
 "am_pay1":{"en":"Cash accepted","lt":"Priimame grynuosius"},
 "am_pay2":{"en":"Credit card accepted","lt":"Priimame kredito korteles"},
 "am_pay3":{"en":"Debit card accepted","lt":"Priimame debeto korteles"},
 "am_loc1":{"en":"Easy to reach","lt":"Patogiai pasiekiama"},
 "am_loc2":{"en":"Street parking nearby","lt":"Vietos automobiliams gatvėje"},
 "am_loc3":{"en":"Bus stop nearby","lt":"Netoli autobusų stotelė"},
 "see_all_amenities":{"en":"See all 10 amenities","lt":"Rodyti visus 10 patogumų"},
 "about_desc":{"en":"Blarberinė is a neighbourhood barbershop built on craft and good conversation. For years we've kept Kaunas sharp with classic cuts, skin fades, beard sculpting and traditional hot-towel shaves. Walk-ins are welcome and bookings are recommended — payment is taken at the venue, cash or card.",
               "lt":"Blarberinė — kvartalo kirpykla, sukurta iš meistrystės ir gerų pokalbių. Jau daugelį metų palaikome kauniečius tvarkingus: klasikiniai kirpimai, perėjimai, barzdos modeliavimas ir tradicinis skutimas karštu rankšluosčiu. Laukiame ir be registracijos, tačiau rekomenduojame rezervuoti — atsiskaitoma vietoje, grynaisiais arba kortele."},
 "getting_here":{"en":"Getting here","lt":"Kaip mus rasti"},
 "getting_here_txt":{"en":"Utenos g. 16, Kaunas. Street parking nearby.",
                     "lt":"Utenos g. 16, Kaunas. Netoliese – vietos automobiliams gatvėje."},
 "opening_hours":{"en":"Opening hours","lt":"Darbo laikas"},
 "closed":{"en":"Closed","lt":"Uždaryta"},
 "ready_fresh":{"en":"Ready for a fresh cut?","lt":"Pasiruošę naujam kirpimui?"},
 "book_min":{"en":"Book online in under a minute — pay at the venue.","lt":"Rezervuokite internetu per minutę — atsiskaitoma vietoje."},
 "footer_tag":{"en":"Classic cuts, hot-towel shaves and sharp fades in the heart of Kaunas.",
               "lt":"Klasikiniai kirpimai, skutimas karštu rankšluosčiu ir tikslūs perėjimai pačiame Kauno centre."},
 "foot_explore":{"en":"Explore","lt":"Naršyti"},
 "foot_visit":{"en":"Visit","lt":"Aplankykite"},
 "foot_hours":{"en":"Hours","lt":"Darbo laikas"},
 "foot_hours_wk":{"en":"Mon–Fri  09:00–19:00","lt":"I–V  09:00–19:00"},
 "foot_hours_sat":{"en":"Saturday  09:00–17:00","lt":"VI  09:00–17:00"},
 "foot_hours_sun":{"en":"Sunday  Closed","lt":"VII  Uždaryta"},
 "pay_at_venue":{"en":"Pay at venue","lt":"Atsiskaitymas vietoje"},
 "foot_city":{"en":"Utenos g. 16, Kaunas","lt":"Utenos g. 16, Kaunas"},
 "foot_country":{"en":"Lithuania","lt":"Lietuva"},
 "foot_bottom":{"en":"Pay-at-venue only · Cash & card","lt":"Tik atsiskaitymas vietoje · Grynaisiais ir kortele"},
 "copyright":{"en":"© 2026 Blarberinė","lt":"© 2026 Blarberinė"},
 "days":{"en":["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"],
         "lt":["Pirmadienis","Antradienis","Trečiadienis","Ketvirtadienis","Penktadienis","Šeštadienis","Sekmadienis"]},
}

# DocType-data translation (English base -> LT). Mirrored in api.py for JS widgets.
DATA_TR_LT = {
 # categories
 "Add-ons":"Papildomos paslaugos","Beard":"Barzda","Haircuts":"Kirpimai","Shaves":"Skutimas",
 "Quick extras to finish the look.":"Greitos papildomos paslaugos įvaizdžiui užbaigti.",
 "Beard trims, shaping and styling.":"Barzdos kirpimas, formavimas ir modeliavimas.",
 "Cuts, fades and styling for all hair types.":"Kirpimai, perėjimai ir modeliavimas visų tipų plaukams.",
 "Traditional hot-towel and head shaves.":"Tradicinis skutimas karštu rankšluosčiu ir galvos skutimas.",
 # service names
 "Beard Sculpt & Style":"Barzdos modeliavimas","Beard Trim":"Barzdos formavimas","Buzz Cut":"Kirpimas mašinėle",
 "Classic Haircut":"Klasikinis kirpimas","Eyebrow Trim":"Antakių korekcija","Hair Wash":"Plaukų plovimas",
 "Head Shave":"Galvos skutimas","Hot Towel Shave":"Skutimas karštu rankšluosčiu","Kids Haircut":"Vaikų kirpimas",
 "Skin Fade":"Perėjimas (skin fade)",
 # service descriptions
 "Full beard shaping, trim and conditioning.":"Pilnas barzdos formavimas, kirpimas ir priežiūra.",
 "Tidy-up and line-up of the beard.":"Barzdos tvarkymas ir kontūrų formavimas.",
 "Single-guard all-over clipper cut.":"Vientisas kirpimas mašinėle vienu antgaliu.",
 "Scissor and clipper cut, washed and styled.":"Kirpimas žirklėmis ir mašinėle, plovimas ir modeliavimas.",
 "Quick eyebrow tidy-up.":"Greita antakių korekcija.",
 "Shampoo, conditioner and blow-dry.":"Plovimas, kondicionierius ir džiovinimas.",
 "Smooth razor head shave.":"Švarus galvos skutimas skustuvu.",
 "Traditional straight-razor shave with hot towels.":"Tradicinis skutimas skustuvu su karštais rankšluosčiais.",
 "Haircut for children under 12.":"Kirpimas vaikams iki 12 metų.",
 "Clean skin fade with a sharp finish.":"Švarus perėjimas iki odos su tiksliu užbaigimu.",
 # bios
 "Fast, friendly and great with kids. Your go-to for buzz cuts and quick refreshes.":
   "Greitas, draugiškas ir puikiai sutaria su vaikais. Geriausias pasirinkimas kirpimui mašinėle ir greitam atsinaujinimui.",
 "Master barber with 12 years behind the chair. Specialises in fades and classic cuts.":
   "Meistras kirpėjas, turintis 12 metų patirtį. Specializuojasi perėjimuose ir klasikiniuose kirpimuose.",
 "Beard specialist who loves a precise line-up and a sharp scissor cut.":
   "Barzdos specialistas, mėgstantis tikslius kontūrus ir preciziškus kirpimus žirklėmis.",
}

LANG = DEFAULT_LANG
R_HOME=R_SERVICES=R_TEAM=R_ABOUT=R_BLOG=BOOK_HREF=None
def set_lang(lang):
    global LANG,R_HOME,R_SERVICES,R_TEAM,R_ABOUT,R_BLOG,BOOK_HREF
    LANG=lang
    r=ROUTES[lang]
    R_HOME = "/" if lang==DEFAULT_LANG else "/en"          # LT home at root, EN at /en
    R_SERVICES="/"+r["services"]; R_TEAM="/"+r["team"]; R_BLOG="/"+r["blog"]
    R_ABOUT=R_HOME                                          # about removed; keep var harmless
    BOOK_HREF=R_HOME+"#booking"
def t(k):
    v=T.get(k,{})
    return v.get(LANG, v.get("en", k))

_c=[0]
def bid():
    _c[0]+=1; return "b%04d"%_c[0]

def blk(el="div",*,children=None,styles=None,name=None,innerHTML=None,attributes=None,
        dataKey=None,dynamicValues=None,originalElement=None,blockId=None,mobileStyles=None,
        isRepeater=False,classes=None):
    b={"blockId":blockId or bid(),"element":el}
    if name is not None: b["blockName"]=name
    if originalElement is not None: b["originalElement"]=originalElement
    if innerHTML is not None: b["innerHTML"]=innerHTML
    if attributes is not None: b["attributes"]=attributes
    if dataKey is not None: b["dataKey"]=dataKey
    if dynamicValues is not None: b["dynamicValues"]=dynamicValues
    if classes is not None: b["classes"]=classes
    if isRepeater: b["isRepeaterBlock"]=True
    b["baseStyles"]=styles or {}
    if mobileStyles is not None: b["mobileStyles"]=mobileStyles
    b["children"]=children or []
    return b

def text(content,styles,key=None,tag="p",mob=None,classes=None):
    s={"fontFamily":FONT,"width":"fit-content","height":"fit-content"}; s.update(styles)
    dk={"key":key,"type":"key","property":"innerHTML"} if key else None
    return blk(tag,innerHTML=content,styles=s,dataKey=dk,mobileStyles=mob,classes=classes)

def img(src,styles,key=None,classes=None):
    dv=[{"key":key,"type":"attribute","property":"src","comesFrom":"dataScript"}] if key else None
    return blk("img",attributes={"src":src,"alt":""},dynamicValues=dv,styles=styles,classes=classes)

def link(label,href,styles,tag="a",mob=None,classes=None):
    s={"fontFamily":FONT,"textDecoration":"none","width":"fit-content","height":"fit-content"}; s.update(styles)
    return blk(tag,innerHTML=label,attributes={"href":href},styles=s,mobileStyles=mob,classes=classes)

def container(width="1040px",**extra):
    s={"display":"flex","flexDirection":"column","width":"100%","maxWidth":width,"flexShrink":0}; s.update(extra); return s

def pill(label,href,*,solid=True,small=False):
    if solid: bg,col,bd=GOLD,"#ffffff","none"
    else: bg,col,bd="transparent",GOLD,"1px solid "+GOLD
    return link(label,href,{"display":"inline-flex","alignItems":"center","justifyContent":"center",
        "backgroundColor":bg,"color":col,"border":bd,"fontWeight":"600",
        "fontSize":"14px" if small else "15px",
        "paddingTop":"9px" if small else "12px","paddingBottom":"9px" if small else "12px",
        "paddingLeft":"18px" if small else "26px","paddingRight":"18px" if small else "26px",
        "borderRadius":"8px","cursor":"pointer","flexShrink":"0"})

def stars(size=16,color=GOLD):
    return text("★★★★★",{"fontSize":"%dpx"%size,"color":color,"letterSpacing":"2px","lineHeight":"1"})

def kicker(l,color=CORAL): return text(l,{"fontSize":"12px","letterSpacing":"0.22em","textTransform":"uppercase","color":color,"fontWeight":"700","marginBottom":"12px"})
def h2(l,color=INK): return text(l,{"fontFamily":HEAD,"fontSize":"44px","color":color,"fontWeight":"600","marginBottom":"20px","letterSpacing":"0.01em","lineHeight":"1.12"},tag="h2",mob={"fontSize":"31px","marginBottom":"16px","lineHeight":"1.18"})

def tri_bar(mt="0",mb="0"):
    seg=lambda c: blk("div",styles={"backgroundColor":c,"height":"4px","flex":"1"})
    return blk("div",children=[seg(BAR_Y),seg(BAR_B),seg(BAR_T)],styles={"display":"flex","flexDirection":"row","width":"100%","marginTop":mt,"marginBottom":mb,"flexShrink":0})

def section(children,*,bg=BG,pad="56px",width="1040px",attributes=None,name=None,align="center"):
    inner=blk("div",children=children,styles=container(width))
    # bl-reveal: fade/slide-in on scroll (activated by interactive.js; without
    # JS the class is inert and everything stays visible)
    return blk("section",children=[inner],attributes=attributes,name=name,classes=["bl-reveal"],styles={
        "display":"flex","flexDirection":"column","alignItems":align,"width":"100%","flexShrink":0,
        "backgroundColor":bg,"paddingTop":pad,"paddingBottom":pad,"paddingLeft":"24px","paddingRight":"24px"},
        mobileStyles={"paddingTop":"40px","paddingBottom":"40px","paddingLeft":"16px","paddingRight":"16px"})

def u(path): return path

def _menu_link(label,href,key=None,href_key=None):
    b=link(label,href,{"fontSize":"14px","color":INK,"fontWeight":"500","padding":"9px 10px",
        "borderRadius":"8px","width":"100%"},classes=["bl-menu-link"])
    if key: b["dataKey"]={"key":key,"type":"key","property":"innerHTML"}
    # bind the href per repeated item (e.g. each barber -> /team?pro=<name>)
    if href_key: b["dynamicValues"]=[{"key":href_key,"type":"attribute","property":"href","comesFrom":"dataScript"}]
    return b

def _menu_panel(children,width="260px"):
    return blk("div",classes=["bl-menu"],children=children,styles={
        "position":"absolute","top":"100%","right":"0","minWidth":width,
        "backgroundColor":CARD,"borderRadius":"14px","border":"1px solid "+BORDER,
        "boxShadow":"0 18px 50px rgba(38,33,26,0.14)","padding":"14px","zIndex":"60",
        "display":"flex","flexDirection":"column","gap":"2px"})

def lang_switcher(active):
    def one(code,lbl):
        on=(code==LANG)
        return link(lbl,"/"+ROUTES[code][active],{"fontSize":"13px","fontWeight":"700",
            "color":CORAL if on else MUTED,"padding":"4px 6px","letterSpacing":"0.04em"})
    return blk("div",classes=["bl-lang"],children=[one("lt","LT"),text("/",{"fontSize":"12px","color":MUTED}),one("en","EN")],
        styles={"display":"flex","flexDirection":"row","alignItems":"center","gap":"4px"})

def lang_dropdown(active):
    trig=blk("div",children=[
        text("🌐",{"fontSize":"13px"}),
        text(LANG.upper(),{"fontSize":"13px","color":INK,"fontWeight":"700","letterSpacing":"0.04em"}),
        text("▾",{"fontSize":"10px","color":MUTED})],
        styles={"display":"flex","flexDirection":"row","alignItems":"center","gap":"5px","cursor":"pointer","padding":"8px 2px"})
    def opt(code,label):
        on=(code==LANG)
        return link(label,"/"+ROUTES[code][active],
            {"fontSize":"14px","color":(CORAL if on else INK),"fontWeight":("700" if on else "500"),
             "padding":"9px 12px","borderRadius":"8px","width":"100%"},classes=["bl-menu-link"])
    panel=blk("div",classes=["bl-menu"],children=[opt("lt","Lietuvių"),opt("en","English")],
        styles={"position":"absolute","top":"100%","right":"0","minWidth":"150px","backgroundColor":CARD,
            "borderRadius":"12px","border":"1px solid "+BORDER,"boxShadow":"0 18px 50px rgba(38,33,26,0.14)",
            "padding":"8px","zIndex":"60","display":"flex","flexDirection":"column","gap":"2px"})
    return blk("div",classes=["bl-navitem"],children=[trig,panel],
        styles={"position":"relative","display":"flex","flexDirection":"row","alignItems":"center"})

def nav(active="home"):
    _navlogo=img("/assets/blarberine/images/logo-dark.png",{"height":"42px","width":"auto","display":"block"})
    _navlogo["attributes"]["alt"]="Blarberinė Kaunas"
    _navlogo["mobileStyles"]={"height":"30px"}
    brand=blk("a",attributes={"href":R_HOME},children=[_navlogo],
        styles={"textDecoration":"none","display":"flex","alignItems":"center",
            "flexShrink":"1","minWidth":"0","overflow":"hidden"})

    def navitem(label,href,panel):
        lab=link(label,href,{"fontSize":"13px","color":INK,"fontWeight":"600","letterSpacing":"0.06em",
            "textTransform":"uppercase","display":"inline-flex","alignItems":"center"})
        cap=text("▾",{"fontSize":"10px","color":MUTED})
        row=blk("div",children=[lab,cap],styles={"display":"flex","flexDirection":"row","alignItems":"center","gap":"5px","cursor":"pointer","padding":"8px 2px"})
        return blk("div",classes=["bl-navitem"],children=[row,panel],
            styles={"position":"relative","display":"flex","flexDirection":"row","alignItems":"center"})

    cat_rep=blk("div",children=[_menu_link("Category",R_SERVICES,key="category_name")],isRepeater=True,
        dataKey={"key":"service_categories","comesFrom":"dataScript"},
        styles={"display":"flex","flexDirection":"column","width":"100%"})
    left_col=blk("div",children=[
        text(t("menu_services_head"),{"fontSize":"12px","color":MUTED,"fontWeight":"700","letterSpacing":"0.08em","textTransform":"uppercase","padding":"4px 10px 8px"}),
        cat_rep,_menu_link(t("see_all_services"),R_SERVICES)],
        styles={"display":"flex","flexDirection":"column","width":"220px","flexShrink":"0"})
    def promo(imgsrc,title,href):
        return blk("a",attributes={"href":href},classes=["bl-promo"],children=[
            img(imgsrc,{"width":"150px","height":"96px","objectFit":"cover","borderRadius":"10px"}),
            text(title,{"fontSize":"13px","color":INK,"fontWeight":"600","marginTop":"8px","lineHeight":"1.3"})],
            styles={"textDecoration":"none","display":"flex","flexDirection":"column","width":"150px","flexShrink":"0"})
    promos=blk("div",children=[promo(PROMO[0],t("promo1"),R_SERVICES),promo(PROMO[1],t("promo2"),R_SERVICES)],
        styles={"display":"flex","flexDirection":"row","gap":"12px","paddingLeft":"14px","borderLeft":"1px solid "+BORDER})
    services_panel=_menu_panel([blk("div",children=[left_col,promos],styles={"display":"flex","flexDirection":"row","gap":"14px"})],width="520px")

    barber_rep=blk("div",children=[_menu_link("Barber",R_TEAM,key="barber_name",href_key="href")],isRepeater=True,
        dataKey={"key":"barbers","comesFrom":"dataScript"},
        styles={"display":"flex","flexDirection":"column","width":"100%"})
    barbers_panel=_menu_panel([
        text(t("our_barbers"),{"fontSize":"12px","color":MUTED,"fontWeight":"700","letterSpacing":"0.08em","textTransform":"uppercase","padding":"4px 10px 8px"}),
        barber_rep,_menu_link(t("meet_team_arrow"),R_TEAM)],width="240px")

    _plain_link=lambda label,href:link(label,href,{"fontSize":"13px","color":INK,"fontWeight":"600",
        "letterSpacing":"0.06em","textTransform":"uppercase","padding":"8px 2px","display":"inline-flex","alignItems":"center"})
    blog_link=_plain_link(t("nav_blog"),R_BLOG)

    # "Services" removed from the nav 2026-07-07 (redundant — booking widget picks services)
    center=blk("div",classes=["bl-navlinks"],children=[
        navitem(t("nav_barbers"),R_TEAM,barbers_panel),
        blog_link, lang_dropdown(active)],
        styles={"display":"flex","flexDirection":"row","gap":"22px","alignItems":"center"},
        mobileStyles={"display":"none"})

    book=pill(t("book_now"),BOOK_HREF,small=True)
    burger=blk("button",innerHTML="☰",classes=["bl-burger"],
        styles={"display":"none","background":"none","border":"none","cursor":"pointer","fontSize":"26px","lineHeight":"1","color":INK,"padding":"2px 4px"},
        mobileStyles={"display":"inline-flex","alignItems":"center"})
    right=blk("div",children=[center,book,burger],styles={"display":"flex","flexDirection":"row","gap":"22px","alignItems":"center","flexShrink":"0"},
        mobileStyles={"gap":"14px"})
    row=blk("div",children=[brand,right],styles={"display":"flex","flexDirection":"row","alignItems":"center",
        "justifyContent":"space-between","width":"100%","maxWidth":"1180px","minWidth":"0","gap":"12px","boxSizing":"border-box"})
    def mlink(label,href):
        return link(label,href,{"fontSize":"15px","color":INK,"fontWeight":"600","padding":"15px 4px","width":"100%","borderBottom":"1px solid "+BORDER,"display":"block"})
    mobile_menu=blk("div",classes=["bl-mobile-menu"],children=[
        mlink(t("nav_barbers"),R_TEAM),mlink(t("nav_blog"),R_BLOG),
        blk("div",children=[lang_switcher(active)],styles={"display":"flex","paddingTop":"12px","paddingBottom":"6px"}),
        blk("div",children=[pill(t("book_now"),BOOK_HREF)],styles={"display":"flex","width":"100%","paddingTop":"6px","paddingBottom":"6px"})],
        styles={"display":"none","position":"absolute","top":"100%","left":"0","right":"0","width":"100%","flexDirection":"column",
            "backgroundColor":CARD,"borderBottom":"1px solid "+BORDER,"boxShadow":"0 14px 34px rgba(38,33,26,0.14)",
            "paddingLeft":"20px","paddingRight":"20px","paddingBottom":"10px","zIndex":"55"})
    # slim location/hours strip ABOVE the navbar (owner 2026-07-08 — replaces
    # the info bar that sat under the hero)
    def _titem(icon,label):
        return blk("div",children=[text(icon,{"fontSize":"12px","color":CORAL}),
            text(label,{"fontSize":"12.5px","color":BODY,"fontWeight":"500"})],
            styles={"display":"flex","flexDirection":"row","alignItems":"center","gap":"6px"})
    _tstrip_row=blk("div",children=[_titem("📍",t("address_line")),_titem("🕑",t("open_today"))],
        styles={"display":"flex","flexDirection":"row","alignItems":"center","gap":"26px","width":"100%",
            "maxWidth":"1180px","flexWrap":"wrap"},mobileStyles={"gap":"10px"})
    top_strip=blk("div",classes=["bl-topstrip"],children=[_tstrip_row],styles={
        "display":"flex","flexDirection":"row","justifyContent":"center","width":"100%","flexShrink":0,
        "backgroundColor":ALT,"borderBottom":"1px solid "+BORDER,"paddingTop":"7px","paddingBottom":"7px",
        "paddingLeft":"24px","paddingRight":"24px"},mobileStyles={"paddingLeft":"16px","paddingRight":"16px"})
    navrow=blk("div",children=[row,mobile_menu],styles={
        "display":"flex","flexDirection":"row","justifyContent":"center","alignItems":"center","width":"100%",
        "position":"relative","paddingTop":"14px","paddingBottom":"14px",
        "paddingLeft":"24px","paddingRight":"24px","backgroundColor":"rgba(250,248,243,0.92)",
        "backdropFilter":"blur(10px)","borderBottom":"1px solid "+BORDER},
        mobileStyles={"paddingLeft":"16px","paddingRight":"16px"})
    return blk("header",children=[top_strip,navrow],name="nav",classes=["bl-nav"],styles={
        "display":"flex","flexDirection":"column","alignItems":"center","width":"100%",
        "flexShrink":0,"position":"sticky","top":"0","zIndex":"50"})

# ================================================================= FOOTER
# ---- Social links (both CONFIRMED by Mantas 2026-07-06) ----
IG_URL="https://www.instagram.com/blarberine"
FB_URL="https://www.facebook.com/blarberine"

def _social(url,svg,label):
    return blk("a",attributes={"href":url,"target":"_blank","rel":"noopener","aria-label":label},
        innerHTML=svg,classes=["bl-social"],
        styles={"display":"inline-flex","alignItems":"center","justifyContent":"center","width":"38px","height":"38px",
            "borderRadius":"50%","border":"1px solid "+BORDER,"color":GOLD,"textDecoration":"none","flexShrink":"0"})

def social_row(gap="12px"):
    fb=('<svg width="17" height="17" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">'
        '<path d="M22 12c0-5.52-4.48-10-10-10S2 6.48 2 12c0 4.84 3.44 8.87 8 9.8v-6.93H7.9V12H10V9.8'
        'c0-2.07 1.23-3.22 3.12-3.22.9 0 1.85.16 1.85.16v2.03h-1.04c-1.03 0-1.35.64-1.35 1.29V12h2.3'
        'l-.37 2.87h-1.93V21.8c4.56-.93 8-4.96 8-9.8z"/></svg>')
    ig=('<svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" aria-hidden="true">'
        '<rect x="3.2" y="3.2" width="17.6" height="17.6" rx="5"/><circle cx="12" cy="12" r="3.8"/>'
        '<circle cx="17.4" cy="6.6" r="1.1" fill="currentColor" stroke="none"/></svg>')
    return blk("div",children=[_social(FB_URL,fb,"Facebook — Blarberinė | Kaunas"),
                               _social(IG_URL,ig,"Instagram — @blarberine")],
        styles={"display":"flex","flexDirection":"row","gap":gap})

def footer():
    def col(title,items):
        ch=[text(title,{"fontSize":"12px","color":GOLD,"fontWeight":"600","letterSpacing":"0.14em","textTransform":"uppercase","marginBottom":"14px"})]
        for label,href in items:
            if href=="#":  # informational line, not a destination — render as plain text
                ch.append(text(label,{"fontSize":"14px","color":"#b3ab98","marginBottom":"10px","width":"auto"}))
            else:
                ch.append(link(label,href,{"fontSize":"14px","color":"#b3ab98","marginBottom":"10px"}))
        return blk("div",children=ch,styles={"display":"flex","flexDirection":"column","flex":"1","minWidth":"180px"})
    # small, and alignSelf/flexShrink/objectFit stop the flex column from stretching
    # the emblem into an "egg" (the manager's note)
    _footlogo=img("/assets/blarberine/images/logo-cream.png",{"height":"38px","width":"auto","display":"block",
        "marginBottom":"18px","alignSelf":"flex-start","flexShrink":"0","objectFit":"contain","maxWidth":"100%"})
    _footlogo["attributes"]["alt"]="Blarberinė Kaunas"
    brand_col=blk("div",children=[
        _footlogo,
        text(t("footer_tag"),{"fontSize":"14px","color":"#b3ab98","lineHeight":"1.6","marginBottom":"18px","width":"auto","maxWidth":"260px"}),
        social_row()],
        styles={"display":"flex","flexDirection":"column","flex":"1.4","minWidth":"220px"})
    cols=blk("div",children=[brand_col,
        col(t("foot_explore"),[(t("nav_services"),R_SERVICES),(t("nav_barbers"),R_TEAM),(t("nav_blog"),R_BLOG),(t("book_now"),BOOK_HREF)]),
        col(t("foot_visit"),[(t("foot_city"),"#"),(t("foot_country"),"#"),("+370 600 00000","#"),("hello@blarberine.lt","#")]),
        col(t("foot_hours"),[(t("foot_hours_wk"),"#"),(t("foot_hours_sat"),"#"),(t("foot_hours_sun"),"#"),(t("pay_at_venue"),"#")])],
        styles={"display":"flex","flexDirection":"row","gap":"40px","width":"100%","maxWidth":"1080px","flexWrap":"wrap"},
        mobileStyles={"flexDirection":"column","gap":"28px"})
    bottom=blk("div",children=[
        text(t("copyright"),{"fontSize":"13px","color":"#8a8272"}),
        text(t("foot_bottom"),{"fontSize":"13px","color":"#8a8272"})],
        styles={"display":"flex","flexDirection":"row","justifyContent":"space-between","width":"100%","maxWidth":"1080px",
            "borderTop":"1px solid rgba(212,175,55,0.16)","paddingTop":"20px","marginTop":"36px","flexWrap":"wrap","gap":"8px"})
    inner=blk("div",children=[cols,bottom],styles=container("1080px"))
    # Mantas's "little touch" — a subtle classic barber-pole stripe under the footer.
    barberpole=blk("div",classes=["bl-barberpole"],styles={"width":"100%","height":"6px","flexShrink":"0"})
    return blk("footer",children=[tri_bar(),blk("div",children=[inner],styles={
        "display":"flex","flexDirection":"column","alignItems":"center","width":"100%",
        "paddingTop":"52px","paddingBottom":"40px","paddingLeft":"24px","paddingRight":"24px"},
        mobileStyles={"paddingLeft":"16px","paddingRight":"16px"}),barberpole],
        styles={"display":"flex","flexDirection":"column","alignItems":"center","width":"100%","flexShrink":0,"backgroundColor":NAVY})

# ================================================================= shared bits
def service_row():
    name=text("Service name",{"fontSize":"16px","color":INK,"fontWeight":"600"},key="service_name")
    meta=blk("div",children=[text("30 mins",{"fontSize":"13px","color":MUTED},key="duration_display"),
        text("·",{"fontSize":"13px","color":MUTED}),
        text(t("show_details"),{"fontSize":"13px","color":CORAL,"fontWeight":"500"})],
        styles={"display":"flex","flexDirection":"row","alignItems":"center","gap":"8px","marginTop":"4px"})
    left=blk("div",children=[name,meta],styles={"display":"flex","flexDirection":"column","flexShrink":1,"minWidth":"0"})
    price=text("€25",{"fontSize":"16px","color":INK,"fontWeight":"700"},key="price_display")
    sel=pill(t("book_now"),BOOK_HREF,solid=False,small=True)
    right=blk("div",children=[price,sel],styles={"display":"flex","flexDirection":"row","alignItems":"center","gap":"18px","flexShrink":"0"},mobileStyles={"gap":"10px"})
    return blk("div",children=[left,right],styles={"display":"flex","flexDirection":"row","justifyContent":"space-between",
        "alignItems":"center","gap":"20px","width":"100%","paddingTop":"16px","paddingBottom":"16px","borderBottom":"1px solid "+BORDER},
        mobileStyles={"gap":"12px"})

def rows_shrinkwrap(rep):
    colw=blk("div",children=[rep],styles={"display":"flex","flexDirection":"column","flex":"1","minWidth":"0","width":"100%"})
    return blk("div",children=[colw],styles={"display":"flex","flexDirection":"row","width":"100%","minWidth":"0"})

def barber_card():
    # light "experts" card (reference style): photo card on paper background
    photo=img(WORK[0],{"width":"100%","height":"280px","objectFit":"cover","borderRadius":"12px","flexShrink":"0"},key="photo")
    name=text("Barber",{"fontFamily":HEAD,"fontSize":"22px","color":LINK,"fontWeight":"600","marginTop":"16px",
        "textTransform":"uppercase","letterSpacing":"0.03em"},key="barber_name",tag="h3")
    bio=text("Bio",{"fontSize":"14px","color":LMUT,"lineHeight":"1.55","marginTop":"6px","width":"auto"},key="bio")
    return blk("div",children=[photo,name,bio],classes=["bl-lift"],styles={"display":"flex","flexDirection":"column","width":"100%",
        "backgroundColor":LCARD,"border":"1px solid "+LLINE,"borderRadius":"16px",
        "paddingTop":"14px","paddingBottom":"22px","paddingLeft":"14px","paddingRight":"14px"})

def barbers_grid():
    return blk("div",children=[barber_card()],isRepeater=True,dataKey={"key":"barbers","comesFrom":"dataScript"},
        styles={"display":"grid","gridTemplateColumns":"repeat(3, 1fr)","gap":"28px","width":"100%"},
        mobileStyles={"gridTemplateColumns":"1fr"})

# ============================================== redesign: cream sections
def works_gallery():
    head=blk("div",children=[
        blk("div",children=[kicker(t("works_title")),h2(t("works_title"),color=LINK),
            text(t("works_sub"),{"fontSize":"15px","color":LMUT,"lineHeight":"1.6","width":"auto"})],
            styles={"display":"flex","flexDirection":"column"})],
        styles={"display":"flex","flexDirection":"row","justifyContent":"space-between","alignItems":"flex-end",
                "width":"100%","marginBottom":"28px"})
    # manager-editable gallery: repeats over data.gallery_images (Gallery Image
    # DocType at /app/gallery-image); the data script falls back to built-in
    # placeholder photos when none are uploaded.
    ph=img(GALLERY[0],{"width":"100%","height":"250px","objectFit":"cover","display":"block"},key="image")
    cell=blk("div",children=[ph],classes=["bl-zoom"],
        styles={"borderRadius":"14px","overflow":"hidden","width":"100%"})
    grid=blk("div",children=[cell],isRepeater=True,dataKey={"key":"gallery_images","comesFrom":"dataScript"},
        styles={"display":"grid","gridTemplateColumns":"repeat(3, 1fr)","gap":"22px","width":"100%"},
        mobileStyles={"gridTemplateColumns":"1fr","gap":"14px"})
    return section([head,grid],bg=LBG)

def prices_strip():
    left=blk("div",children=[kicker(t("prices_title")),h2(t("prices_title"),color=LINK),
        text(t("prices_sub"),{"fontSize":"14px","color":LMUT,"lineHeight":"1.6","maxWidth":"280px","width":"auto","marginBottom":"18px"}),
        pill(t("book_now"),BOOK_HREF,solid=True)],
        styles={"display":"flex","flexDirection":"column","width":"320px","flexShrink":"0"},
        mobileStyles={"width":"100%"})
    nm=text("Service",{"fontSize":"16px","color":LINK,"fontWeight":"600"},key="service_name")
    dur=text("30 min",{"fontSize":"12px","color":LMUT,"marginTop":"2px"},key="duration_display")
    lcol=blk("div",children=[nm,dur],styles={"display":"flex","flexDirection":"column","minWidth":"0"})
    pr=text("€25",{"fontFamily":HEAD,"fontSize":"26px","color":CORAL,"fontWeight":"600","flexShrink":"0"},key="price_display")
    prow=blk("div",children=[lcol,pr],styles={"display":"flex","flexDirection":"row","justifyContent":"space-between",
        "alignItems":"center","gap":"16px","width":"100%","paddingTop":"14px","paddingBottom":"14px","borderBottom":"1px solid "+LLINE})
    rep=blk("div",children=[prow],isRepeater=True,dataKey={"key":"popular_services","comesFrom":"dataScript"},
        styles={"display":"flex","flexDirection":"column","flex":"1","minWidth":"280px"})
    row=blk("div",children=[left,rep],styles={"display":"flex","flexDirection":"row","gap":"56px","width":"100%","alignItems":"flex-start"},
        mobileStyles={"flexDirection":"column","gap":"28px"})
    return section([row],bg=LBG,pad="48px")

def join_strip():
    title=text(t("join_title"),{"fontFamily":HEAD,"fontSize":"26px","color":LINK,"fontWeight":"600",
        "textTransform":"uppercase","letterSpacing":"0.03em"})
    btn=pill(t("join_btn"),"#contact",solid=False,small=True)
    row=blk("div",children=[title,btn],styles={"display":"flex","flexDirection":"row","justifyContent":"space-between",
        "alignItems":"center","gap":"20px","width":"100%","backgroundColor":LCARD,"border":"1px solid "+LLINE,
        "borderRadius":"16px","paddingTop":"26px","paddingBottom":"26px","paddingLeft":"32px","paddingRight":"32px","flexWrap":"wrap"})
    return blk("div",children=[row],styles={"display":"flex","width":"100%","marginTop":"28px"})

# ================================================================= HERO
def hero():
    # Full-bleed background photo, text overlaid on top (owner brief). Text is
    # light against the photo; a left-weighted dark gradient keeps it legible
    # while the image stays visible on the right.
    HW="#ffffff"; HSUB="#ece5d8"
    rating=blk("div",children=[stars(15,color="#e2b988"),text(t("trusted")+" · Kaunas",{"fontSize":"13px","color":HSUB,
        "fontWeight":"600","letterSpacing":"0.14em","textTransform":"uppercase"})],
        styles={"display":"flex","flexDirection":"row","alignItems":"center","gap":"10px","marginBottom":"22px"},
        mobileStyles={"flexWrap":"wrap","gap":"6px"})
    headline=text(t("hero_head"),{"fontFamily":HEAD,"fontSize":"72px","color":HW,"fontWeight":"600",
        "lineHeight":"1.05","letterSpacing":"0.005em","maxWidth":"640px","width":"auto","marginBottom":"22px",
        "textShadow":"0 2px 30px rgba(0,0,0,0.35)"},tag="h1",mob={"fontSize":"42px","lineHeight":"1.1"})
    tag=text(t("hero_tag"),{"fontSize":"18px","color":HSUB,"lineHeight":"1.7","maxWidth":"480px","marginBottom":"36px","width":"auto"})
    cta=pill(t("book_now"),BOOK_HREF,solid=True)
    cta["baseStyles"].update({"fontSize":"16px","paddingLeft":"42px","paddingRight":"42px","paddingTop":"16px","paddingBottom":"16px",
        "boxShadow":"0 14px 36px rgba(179,135,60,0.5)"})
    cta["classes"]=["bl-cta"]
    inner=blk("div",children=[rating,headline,tag,cta],styles={"display":"flex","flexDirection":"column",
        "width":"100%","maxWidth":"1180px","alignItems":"flex-start"})
    return blk("section",children=[inner],classes=["bl-reveal"],styles={"display":"flex","flexDirection":"column",
        "justifyContent":"center","alignItems":"center","width":"100%","flexShrink":0,"minHeight":"88vh",
        "paddingTop":"96px","paddingBottom":"96px","paddingLeft":"48px","paddingRight":"48px",
        "backgroundImage":"linear-gradient(90deg, rgba(20,16,12,0.82) 0%, rgba(20,16,12,0.5) 48%, rgba(20,16,12,0.22) 100%), url('"+HERO_IMG+"')",
        "backgroundSize":"cover","backgroundPosition":"center","backgroundRepeat":"no-repeat"},
        mobileStyles={"minHeight":"78vh","paddingTop":"64px","paddingBottom":"64px","paddingLeft":"22px","paddingRight":"22px",
            "backgroundImage":"linear-gradient(180deg, rgba(20,16,12,0.5) 0%, rgba(20,16,12,0.8) 100%), url('"+HERO_IMG+"')"})

def info_bar():
    def item(icon,label):
        return blk("div",children=[text(icon,{"fontSize":"16px","color":CORAL}),text(label,{"fontSize":"15px","color":BODY,"fontWeight":"500"})],
            styles={"display":"flex","flexDirection":"row","alignItems":"center","gap":"8px"})
    row=blk("div",children=[item("📍",t("address_line")),item("🕑",t("open_today"))],
        styles={"display":"flex","flexDirection":"row","gap":"32px","width":"100%","maxWidth":"1080px","flexWrap":"wrap"},
        mobileStyles={"flexDirection":"column","gap":"8px"})
    wrap=blk("div",children=[row,tri_bar(mt="20px")],styles={"display":"flex","flexDirection":"column","alignItems":"center","width":"100%","maxWidth":"1080px"})
    return blk("section",children=[wrap],styles={"display":"flex","flexDirection":"column","alignItems":"center","width":"100%",
        "flexShrink":0,"backgroundColor":BG,"paddingTop":"8px","paddingBottom":"0","paddingLeft":"24px","paddingRight":"24px"},
        mobileStyles={"paddingLeft":"16px","paddingRight":"16px"})

# ================================================================= PAGES
def _body(children):
    b=blk("div",originalElement="body",blockId="root",styles={"display":"flex","flexDirection":"column","alignItems":"center",
        "flexWrap":"nowrap","flexShrink":0,"position":"static","backgroundColor":BG,"width":"100%","minHeight":"100vh",
        "maxWidth":"100%","overflowX":"hidden","fontFamily":FONT},children=children)
    b["draggable"]=False
    return [b]

def home():
    # light "experts" section per the reference, with the join-the-team card
    team=section([kicker(t("the_team")),h2(t("meet_barbers"),color=LINK),barbers_grid(),join_strip()],bg=LBG)
    # Redesign composition (cloned from reference #1): dark hero w/ booking card
    # -> info strip -> real booking widget (dark) -> cream works/prices/team ->
    # dark brands strip -> cream FAQ -> dark contact + footer. before_after
    # dropped (placeholder stock pairs; works_gallery covers it until Mantas
    # sends real photos).
    # info_bar moved into the header top strip; prices_strip removed from home
    # (owner 2026-07-08) — full price list stays inside the booking widget.
    return _body([nav("home"),hero(),booking_section(),works_gallery(),team,
                  brands_strip(),faq_section(),contact_section(),footer()])

def services_page():
    app=blk("div",attributes={"id":"services-app"},
        innerHTML='<p style="font-family:'+FONT+';color:'+MUTED+';text-align:center">'+t("loading_services")+'</p>',
        styles={"display":"flex","flexDirection":"column","width":"100%"})
    head=blk("div",children=[kicker(t("price_list")),h2(t("our_services")),
        text(t("services_intro"),{"fontSize":"15px","color":MUTED,"marginBottom":"20px","width":"auto"})],
        styles={"display":"flex","flexDirection":"column"})
    sec=blk("section",children=[blk("div",children=[head,app],styles=container("880px"))],
        styles={"display":"flex","flexDirection":"column","alignItems":"center","width":"100%","flexShrink":0,
            "backgroundColor":BG,"paddingTop":"48px","paddingBottom":"72px","paddingLeft":"24px","paddingRight":"24px"},
        mobileStyles={"paddingTop":"32px","paddingBottom":"56px","paddingLeft":"16px","paddingRight":"16px"})
    return _body([nav("services"),sec,footer()])

def team_page():
    app=blk("div",attributes={"id":"team-app"},
        innerHTML='<p style="font-family:'+FONT+';color:'+MUTED+';text-align:center">'+t("loading_team")+'</p>',
        styles={"display":"flex","flexDirection":"column","width":"100%"})
    work=[img(u2,{"width":"100%","height":"200px","objectFit":"cover","borderRadius":"10px"}) for u2 in WORK]
    grid=blk("div",children=work,styles={"display":"grid","gridTemplateColumns":"repeat(3, 1fr)","gap":"16px","width":"100%"},mobileStyles={"gridTemplateColumns":"repeat(2, 1fr)"})
    return _body([nav("team"),
        section([kicker(t("the_team")),h2(t("meet_barbers")),app]),
        section([h2(t("our_work")),grid],bg=ALT),
        reviews_section(),
        booking_cta(),footer()])

def blog_card():
    cover=blk("img",attributes={"src":WORK[0],"alt":""},
        dynamicValues=[{"key":"cover_image","type":"attribute","property":"src","comesFrom":"dataScript"}],
        styles={"width":"100%","height":"200px","objectFit":"cover","display":"block"})
    meta=text("meta",{"fontSize":"11px","letterSpacing":"0.12em","textTransform":"uppercase","color":GOLD,"fontWeight":"700","marginBottom":"8px"},key="meta")
    title=text("Title",{"fontFamily":HEAD,"fontSize":"20px","color":INK,"fontWeight":"600","lineHeight":"1.3","marginBottom":"8px","width":"auto"},key="title",tag="h3")
    excerpt=text("Excerpt",{"fontSize":"14px","color":BODY,"lineHeight":"1.6","marginBottom":"14px","width":"auto"},key="excerpt")
    read=text(t("blog_read"),{"fontSize":"13px","color":GOLD,"fontWeight":"700"})
    body=blk("div",children=[meta,title,excerpt,read],styles={"display":"flex","flexDirection":"column","padding":"20px"})
    return blk("a",children=[cover,body],classes=["bl-blogcard"],attributes={"href":"#"},
        dynamicValues=[{"key":"href","type":"attribute","property":"href","comesFrom":"dataScript"}],
        styles={"display":"flex","flexDirection":"column","backgroundColor":CARD,"border":"1px solid "+BORDER,
            "borderRadius":"14px","overflow":"hidden","textDecoration":"none","width":"100%"})

def blog_list():
    grid=blk("div",children=[blog_card()],isRepeater=True,dataKey={"key":"blog_posts","comesFrom":"dataScript"},
        styles={"display":"grid","gridTemplateColumns":"repeat(3, 1fr)","gap":"22px","width":"100%"},
        mobileStyles={"gridTemplateColumns":"1fr"})
    head=blk("div",children=[kicker(t("blog_kicker")),h2(t("blog_title")),
        text(t("blog_intro"),{"fontSize":"15px","color":MUTED,"lineHeight":"1.6","width":"auto","marginBottom":"28px"})],
        styles={"display":"flex","flexDirection":"column","width":"100%"})
    return _body([nav("blog"),section([head,grid]),footer()])

def about_page():
    gmaps="https://www.google.com/maps/search/?api=1&query=Utenos+g.+16+Kaunas+Lithuania"
    Z, cx, cy = 15, 18557, 10380
    tiles=[]
    for y in (cy, cy+1):
        for x in (cx-1, cx, cx+1):
            tiles.append(blk("img",attributes={"src":"https://tile.openstreetmap.org/%d/%d/%d.png"%(Z,x,y),"alt":"","loading":"lazy"},
                styles={"width":"256px","height":"256px","display":"block"}))
    mosaic=blk("div",children=tiles,styles={"position":"absolute","top":"50%","left":"50%","transform":"translate(-50%,-50%)",
        "width":"768px","height":"512px","display":"grid","gridTemplateColumns":"repeat(3,256px)","gridTemplateRows":"repeat(2,256px)"})
    pin=blk("div",innerHTML="📍",styles={"position":"absolute","top":"calc(50% - 22px)","left":"50%","transform":"translate(-50%,-100%)","fontSize":"30px","zIndex":"2","lineHeight":"1"})
    map_inner=blk("div",children=[mosaic,pin],styles={"position":"relative","width":"100%","height":"340px","overflow":"hidden",
        "borderRadius":"14px","border":"1px solid "+BORDER,"backgroundColor":ALT},mobileStyles={"height":"240px"})
    map_embed=blk("a",attributes={"href":gmaps,"target":"_blank"},children=[map_inner],
        styles={"width":"55%","flexShrink":"0","display":"block","textDecoration":"none"},mobileStyles={"width":"100%"})
    directions=blk("a",innerHTML=t("get_directions"),attributes={"href":gmaps,"target":"_blank"},
        styles={"fontFamily":FONT,"fontSize":"14px","color":CORAL,"fontWeight":"600","textDecoration":"none","marginTop":"14px","width":"fit-content"})
    addr=blk("div",children=[
        text("Blarberinė",{"fontFamily":HEAD,"fontSize":"20px","color":GOLD,"fontWeight":"600","letterSpacing":"0.04em","marginBottom":"6px"}),
        text("Utenos g. 16",{"fontSize":"15px","color":BODY}),text(t("addr_city"),{"fontSize":"15px","color":BODY}),
        text("+370 600 00000",{"fontSize":"15px","color":BODY,"marginTop":"10px"}),
        directions],
        styles={"display":"flex","flexDirection":"column","flex":"1","minWidth":"220px"})
    maprow=blk("div",children=[map_embed,addr],styles={"display":"flex","flexDirection":"row","gap":"32px","width":"100%","alignItems":"flex-start"},mobileStyles={"flexDirection":"column","gap":"20px"})
    desc=text(t("about_desc"),{"fontSize":"16px","color":BODY,"lineHeight":"1.7","width":"auto","marginBottom":"24px"})
    days=T["days"][LANG]
    def hrow(d,h):
        return blk("div",children=[text(d,{"fontSize":"15px","color":BODY}),text(h,{"fontSize":"15px","color":MUTED})],
            styles={"display":"flex","justifyContent":"space-between","width":"100%","paddingTop":"10px","paddingBottom":"10px","borderBottom":"1px solid "+BORDER})
    hours=[hrow(days[i],"09:00 – 19:00") for i in range(5)]+[hrow(days[5],"09:00 – 17:00"),hrow(days[6],t("closed"))]
    hbox=blk("div",children=[text(t("opening_hours"),{"fontSize":"18px","color":INK,"fontWeight":"700","marginBottom":"6px"}),*hours],styles={"display":"flex","flexDirection":"column","flex":"1","minWidth":"260px"})
    tbox=blk("div",children=[desc,text(t("getting_here"),{"fontSize":"15px","color":INK,"fontWeight":"700","marginBottom":"6px"}),
        text(t("getting_here_txt"),{"fontSize":"15px","color":MUTED,"width":"auto"})],
        styles={"display":"flex","flexDirection":"column","flex":"1.3","minWidth":"260px"})
    tworow=blk("div",children=[tbox,hbox],styles={"display":"flex","flexDirection":"row","gap":"56px","width":"100%","flexWrap":"wrap"},mobileStyles={"flexDirection":"column"})
    return _body([nav("about"),
        craft_philosophy(),
        founder_section(),
        section([kicker(t("good_to_know")),h2(t("about_shop")),maprow]),
        amenities(),
        section([tworow],bg=ALT),
        booking_cta(),footer()])

def amenities():
    def group(title,items):
        ch=[text(title,{"fontSize":"13px","color":MUTED,"fontWeight":"700","letterSpacing":"0.06em","textTransform":"uppercase","marginBottom":"14px"})]
        for it in items:
            ch.append(blk("div",children=[text("✓",{"fontSize":"14px","color":CORAL}),text(it,{"fontSize":"15px","color":BODY})],
                styles={"display":"flex","flexDirection":"row","alignItems":"center","gap":"10px","marginBottom":"10px"}))
        return blk("div",children=ch,styles={"display":"flex","flexDirection":"column","flex":"1","minWidth":"200px"})
    row=blk("div",children=[
        group(t("am_products"),[t("am_p1"),t("am_p2")]),
        group(t("am_payment"),[t("am_pay1"),t("am_pay2"),t("am_pay3")]),
        group(t("am_location"),[t("am_loc1"),t("am_loc2"),t("am_loc3")])],
        styles={"display":"flex","flexDirection":"row","gap":"48px","width":"100%","flexWrap":"wrap"},
        mobileStyles={"flexDirection":"column","gap":"24px"})
    note=blk("div",children=[pill(t("see_all_amenities"),R_ABOUT,solid=False)],
        styles={"display":"flex","justifyContent":"center","width":"100%","marginTop":"28px"})
    return section([h2(t("amenities_title")),row,note])

def reviews_section():
    avg=text("5.0",{"fontFamily":HEAD,"fontSize":"50px","color":GOLD,"fontWeight":"600","lineHeight":"1"},key="review_avg")
    sstars=text("★★★★★",{"fontSize":"20px","color":GOLD,"letterSpacing":"2px","marginTop":"8px"},key="review_stars")
    cnt=text("0 reviews",{"fontSize":"14px","color":MUTED,"marginTop":"6px"},key="review_count_display")
    summary=blk("div",children=[avg,sstars,cnt],styles={"display":"flex","flexDirection":"column","width":"180px","flexShrink":"0"})
    lbl=text("★★★★★",{"fontSize":"12px","color":GOLD,"letterSpacing":"1px","width":"72px","whiteSpace":"nowrap","flexShrink":"0"},key="stars")
    bar=blk("div",dataKey={"key":"pct","type":"style","property":"width","comesFrom":"dataScript"},
        styles={"height":"8px","backgroundColor":GOLD,"borderRadius":"4px","width":"0%"})
    track=blk("div",children=[bar],styles={"flex":"1","height":"8px","backgroundColor":"#2a2a2a","borderRadius":"4px","overflow":"hidden"})
    bcount=text("0",{"fontSize":"13px","color":MUTED,"width":"28px","textAlign":"right"},key="count")
    brow=blk("div",children=[lbl,track,bcount],styles={"display":"flex","flexDirection":"row","alignItems":"center","gap":"10px","width":"100%","marginBottom":"8px"})
    brk=blk("div",children=[brow],isRepeater=True,dataKey={"key":"review_breakdown","comesFrom":"dataScript"},
        styles={"display":"flex","flexDirection":"column","flex":"1","minWidth":"200px","maxWidth":"320px"})
    top=blk("div",children=[summary,brk],styles={"display":"flex","flexDirection":"row","gap":"48px","width":"100%","alignItems":"center","marginBottom":"12px","flexWrap":"wrap"})
    r_stars=text("★★★★★",{"fontSize":"15px","color":GOLD,"letterSpacing":"2px","marginBottom":"10px"},key="stars")
    r_text=text("Great cut.",{"fontSize":"15px","color":BODY,"lineHeight":"1.6","marginBottom":"14px","width":"auto"},key="review_text")
    r_auth=text("Author",{"fontSize":"14px","color":INK,"fontWeight":"700"},key="author_name")
    r_meta=text("Service · Google",{"fontSize":"13px","color":MUTED,"marginTop":"2px"},key="meta")
    card=blk("div",children=[r_stars,r_text,r_auth,r_meta],styles={"display":"flex","flexDirection":"column",
        "backgroundColor":CARD,"border":"1px solid "+BORDER,"borderRadius":"14px","padding":"22px","width":"100%"})
    cards=blk("div",children=[card],isRepeater=True,dataKey={"key":"reviews","comesFrom":"dataScript"},
        styles={"display":"grid","gridTemplateColumns":"repeat(3, 1fr)","gap":"20px","width":"100%"},
        mobileStyles={"gridTemplateColumns":"1fr"})
    return section([kicker(t("reviews_kicker")),h2(t("reviews_title")),top,tri_bar(mt="8px",mb="28px"),cards],bg=BG)

def stats_bar():
    def item(num,label,num_key=None):
        n=text(num,{"fontFamily":HEAD,"fontSize":"46px","color":GOLD,"fontWeight":"600","lineHeight":"1"},
            key=num_key,tag="div",mob={"fontSize":"36px"})
        l=text(label,{"fontSize":"12px","color":MUTED,"fontWeight":"700","letterSpacing":"0.12em",
            "textTransform":"uppercase","marginTop":"12px","textAlign":"center","width":"auto"})
        return blk("div",children=[n,l],styles={"display":"flex","flexDirection":"column","alignItems":"center",
            "flex":"1","minWidth":"130px"})
    items=[item(t("stat_years_num"),t("stat_years_lbl")),
           item("0",t("stat_barbers_lbl"),num_key="stat_barbers"),
           item(t("stat_clients_num"),t("stat_clients_lbl"))]
    row=blk("div",children=items,styles={"display":"flex","flexDirection":"row","justifyContent":"center",
        "alignItems":"flex-start","gap":"24px","width":"100%","flexWrap":"wrap"},mobileStyles={"gap":"28px"})
    return section([row],bg=ALT,pad="40px")

def before_after():
    def half(src,lbl):
        im=img(src,{"width":"100%","height":"280px","objectFit":"cover","display":"block"})
        tag=text(lbl,{"position":"absolute","top":"12px","left":"12px","fontFamily":FONT,"fontSize":"11px",
            "fontWeight":"700","letterSpacing":"0.14em","textTransform":"uppercase","color":INK,
            "backgroundColor":"rgba(13,13,13,0.72)","paddingTop":"5px","paddingBottom":"5px",
            "paddingLeft":"11px","paddingRight":"11px","borderRadius":"6px"})
        return blk("div",children=[im,tag],styles={"position":"relative","flex":"1","minWidth":"0","overflow":"hidden"})
    def pair(b,a):
        return blk("div",children=[half(b,t("ba_before")),half(a,t("ba_after"))],
            styles={"display":"flex","flexDirection":"row","gap":"2px","backgroundColor":GOLD,
                "borderRadius":"14px","overflow":"hidden","border":"1px solid "+BORDER,"width":"100%"})
    cards=[pair(b,a) for (b,a) in BEFORE_AFTER]
    grid=blk("div",children=cards,styles={"display":"grid","gridTemplateColumns":"repeat(3, 1fr)","gap":"18px","width":"100%"},
        mobileStyles={"gridTemplateColumns":"1fr","gap":"16px"})
    head=blk("div",children=[kicker(t("ba_kicker")),h2(t("ba_title")),
        text(t("ba_intro"),{"fontSize":"15px","color":MUTED,"lineHeight":"1.6","maxWidth":"620px","width":"auto","marginBottom":"24px"})],
        styles={"display":"flex","flexDirection":"column","width":"100%"})
    return section([head,grid],bg=BG)

def founder_section():
    photo=img(FOUNDER_PHOTO,{"width":"40%","height":"440px","objectFit":"cover","borderRadius":"16px","flexShrink":"0"})
    photo["mobileStyles"]={"width":"100%","height":"320px"}
    name=text(t("founder_name"),{"fontFamily":HEAD,"fontSize":"27px","color":INK,"fontWeight":"600","marginBottom":"4px"},tag="h3")
    role=text(t("founder_role"),{"fontSize":"12px","color":GOLD,"fontWeight":"700","letterSpacing":"0.14em","textTransform":"uppercase","marginBottom":"20px"})
    quote=text("“"+t("founder_quote")+"”",{"fontFamily":HEAD,"fontSize":"23px","color":INK,"fontStyle":"italic","lineHeight":"1.4","marginBottom":"18px","width":"auto"})
    bio=text(t("founder_bio"),{"fontSize":"15px","color":BODY,"lineHeight":"1.7","width":"auto"})
    txt=blk("div",children=[kicker(t("founder_kicker")),name,role,quote,bio],
        styles={"display":"flex","flexDirection":"column","flex":"1.2","minWidth":"280px","justifyContent":"center"})
    row=blk("div",children=[photo,txt],styles={"display":"flex","flexDirection":"row","gap":"48px","width":"100%","alignItems":"center"},
        mobileStyles={"flexDirection":"column","gap":"24px"})
    return section([row],bg=BG)

def google_badge():
    goog=[("G","#4285F4"),("o","#EA4335"),("o","#FBBC05"),("g","#4285F4"),("l","#34A853"),("e","#EA4335")]
    letters=[text(ch,{"fontFamily":FONT,"fontSize":"21px","fontWeight":"700","color":c,"lineHeight":"1"}) for ch,c in goog]
    wordmark=blk("div",children=letters,styles={"display":"flex","flexDirection":"row","alignItems":"center"})
    st=text("★★★★★",{"fontSize":"18px","color":"#fbbc05","letterSpacing":"2px","lineHeight":"1"})
    rating=text("5.0",{"fontFamily":FONT,"fontSize":"20px","fontWeight":"700","color":"#ffffff","lineHeight":"1"})
    cnt=text(t("google_reviews_count"),{"fontSize":"13px","color":"#5f6368","fontWeight":"500"})
    inner=blk("div",children=[wordmark,st,rating,cnt],styles={"display":"flex","flexDirection":"row","alignItems":"center",
        "gap":"14px","flexWrap":"wrap","justifyContent":"center"})
    link_="https://www.google.com/maps/search/?api=1&query=Blarberin%C4%97+Kaunas"  # TEST link
    card=blk("a",attributes={"href":link_,"target":"_blank"},children=[inner],
        styles={"display":"inline-flex","alignItems":"center","backgroundColor":"#ffffff","borderRadius":"12px",
        "paddingTop":"14px","paddingBottom":"14px","paddingLeft":"24px","paddingRight":"24px","textDecoration":"none",
        "boxShadow":"0 2px 18px rgba(0,0,0,0.35)"})
    wrap=blk("div",children=[card],styles={"display":"flex","justifyContent":"center","width":"100%"})
    return section([wrap],bg=BG,pad="30px")

def craft_philosophy():
    def pillar(num,title,desc):
        n=text(num,{"fontFamily":HEAD,"fontSize":"34px","color":GOLD,"fontWeight":"600","lineHeight":"1","marginBottom":"14px"})
        tt=text(title,{"fontFamily":HEAD,"fontSize":"21px","color":INK,"fontWeight":"600","marginBottom":"8px","letterSpacing":"0.01em"})
        dd=text(desc,{"fontSize":"15px","color":BODY,"lineHeight":"1.65","width":"auto"})
        return blk("div",children=[n,tt,dd],styles={"display":"flex","flexDirection":"column","flex":"1","minWidth":"220px",
            "paddingTop":"18px","borderTop":"2px solid rgba(212,175,55,0.4)"})
    row=blk("div",children=[pillar("01",t("craft_p1_t"),t("craft_p1_d")),
        pillar("02",t("craft_p2_t"),t("craft_p2_d")),
        pillar("03",t("craft_p3_t"),t("craft_p3_d"))],
        styles={"display":"flex","flexDirection":"row","gap":"40px","width":"100%","flexWrap":"wrap"},
        mobileStyles={"flexDirection":"column","gap":"28px"})
    head=blk("div",children=[kicker(t("craft_kicker")),h2(t("craft_title")),
        text(t("craft_intro"),{"fontSize":"16px","color":MUTED,"lineHeight":"1.65","maxWidth":"640px","width":"auto","marginBottom":"32px"})],
        styles={"display":"flex","flexDirection":"column","width":"100%"})
    return section([head,row],bg=ALT)

def faq_section():
    items=[]
    for i in range(1,8):
        qt=text(t("faq%d_q"%i),{"fontSize":"16px","color":LINK,"fontWeight":"600","lineHeight":"1.4",
            "flex":"1","minWidth":"0","width":"auto"},tag="span",classes=["bl-faq-qt"])
        plus=text("+",{"fontSize":"24px","color":CORAL,"fontWeight":"300","lineHeight":"1",
            "flexShrink":"0","marginLeft":"18px"},tag="span",classes=["bl-faq-plus"])
        summary=blk("summary",children=[qt,plus],classes=["bl-faq-q"],styles={"display":"flex","flexDirection":"row",
            "justifyContent":"space-between","alignItems":"center","width":"100%","cursor":"pointer",
            "paddingTop":"18px","paddingBottom":"18px","listStyle":"none"})
        ans=text(t("faq%d_a"%i),{"fontSize":"15px","color":LMUT,"lineHeight":"1.7","width":"auto",
            "paddingBottom":"20px","maxWidth":"680px"})
        det=blk("details",children=[summary,ans],classes=["bl-faq"],
            styles={"borderBottom":"1px solid "+LLINE,"width":"100%"},
            attributes=({"open":"open"} if i==1 else None))
        items.append(det)
    head=blk("div",children=[kicker(t("faq_kicker")),h2(t("faq_title"),color=LINK)],
        styles={"display":"flex","flexDirection":"column","alignItems":"center","textAlign":"center","width":"100%"})
    col=blk("div",children=items,styles={"display":"flex","flexDirection":"column","width":"100%","maxWidth":"760px","alignSelf":"center"})
    return section([head,col],bg=LBG)

def brands_strip():
    # dark band on the light site — gives the page rhythm and the cream-tinted
    # brand logos need a dark surface
    logos=[]
    for nm,slug in BRANDS:
        lg=img("/assets/blarberine/images/brands/%s.png"%slug,
            {"height":"34px","width":"auto","display":"block","objectFit":"contain"})
        lg["attributes"]["alt"]=nm
        lg["attributes"]["loading"]="lazy"
        logos.append(blk("div",children=[lg],classes=["bl-brand"],
            styles={"display":"flex","alignItems":"center","justifyContent":"center","flexShrink":"0"}))
    row=blk("div",children=logos,styles={"display":"flex","flexDirection":"row","flexWrap":"wrap",
        "justifyContent":"center","alignItems":"center","columnGap":"48px","rowGap":"22px","width":"100%","marginTop":"8px"},
        mobileStyles={"columnGap":"28px","rowGap":"18px"})
    head=blk("div",children=[kicker(t("brands_kicker")),h2(t("brands_title"),color="#f3ede3"),
        text(t("brands_intro"),{"fontSize":"15px","color":"#b3a893","lineHeight":"1.6","maxWidth":"620px","width":"auto","marginBottom":"6px"})],
        styles={"display":"flex","flexDirection":"column","alignItems":"center","textAlign":"center","width":"100%","marginBottom":"26px"})
    return section([head,row],bg=NAVY)

def contact_section():
    q="Utenos+g.+16+Kaunas"
    directions_url="https://www.google.com/maps/dir/?api=1&destination="+q
    # interactive google map
    iframe=blk("iframe",attributes={"src":"https://maps.google.com/maps?q="+q+"&z=16&output=embed",
        "loading":"lazy","title":"Blarberinė — Utenos g. 16, Kaunas","allowfullscreen":""},
        styles={"width":"100%","height":"100%","border":"0","display":"block"})
    box=blk("div",children=[iframe],styles={"width":"100%","height":"380px","overflow":"hidden",
        "borderRadius":"16px","border":"1px solid "+BORDER,"flex":"1.25","minWidth":"300px"},mobileStyles={"height":"300px"})
    # contact details column
    def line(label,value):
        return blk("div",children=[
            text(label,{"fontSize":"12px","color":MUTED,"fontWeight":"700","letterSpacing":"0.1em","textTransform":"uppercase","marginBottom":"5px"}),
            text(value,{"fontSize":"16px","color":BODY,"width":"auto","lineHeight":"1.5"})],
            styles={"display":"flex","flexDirection":"column","marginBottom":"22px"})
    hours_val=t("foot_hours_wk")+" · "+t("foot_hours_sat")+" · "+t("foot_hours_sun")
    directions=link(t("get_directions"),directions_url,{"fontSize":"15px","color":GOLD,"fontWeight":"700","marginTop":"2px","width":"fit-content"})
    directions["attributes"]["target"]="_blank"
    details=blk("div",children=[
        text("Blarberinė",{"fontFamily":HEAD,"fontSize":"22px","color":GOLD,"fontWeight":"600","letterSpacing":"0.04em","marginBottom":"20px"}),
        line(t("con_address"),t("address_line")),
        line(t("con_phone"),"+370 600 00000"),
        line(t("con_hours"),hours_val),
        directions],
        styles={"display":"flex","flexDirection":"column","flex":"1","minWidth":"260px","justifyContent":"center"})
    row=blk("div",children=[details,box],styles={"display":"flex","flexDirection":"row","gap":"44px","width":"100%","alignItems":"stretch"},
        mobileStyles={"flexDirection":"column","gap":"26px"})
    head=blk("div",children=[kicker(t("contact_kicker")),h2(t("findus_title")),
        text(t("contact_intro"),{"fontSize":"15px","color":MUTED,"lineHeight":"1.6","width":"auto","marginBottom":"30px"})],
        styles={"display":"flex","flexDirection":"column","width":"100%"})
    return section([head,row],bg=ALT,width="1120px",attributes={"id":"contact"},name="contact")

def booking_cta():
    card=blk("div",children=[kicker(t("reserve_chair")),h2(t("ready_fresh")),
        text(t("book_min"),{"fontSize":"16px","color":BODY,"marginBottom":"20px","textAlign":"center","width":"100%","maxWidth":"460px"}),
        pill(t("book_appt"),BOOK_HREF,solid=True)],
        styles={"display":"flex","flexDirection":"column","alignItems":"center","width":"100%"})
    return section([card],bg=BG,align="center")

def booking_section():
    head=blk("div",children=[kicker(t("reserve_chair")),h2(t("book_appt")),
        text(t("booking_intro"),{"fontSize":"15px","color":MUTED,"lineHeight":"1.6","maxWidth":"560px","width":"100%","textAlign":"center","marginBottom":"24px"})],
        styles={"display":"flex","flexDirection":"column","alignItems":"center","width":"100%"})
    app=blk("div",attributes={"id":"booking-app"},innerHTML='<p style="font-family:'+FONT+';color:'+MUTED+';text-align:center">'+t("loading_booking")+'</p>',
        styles={"display":"flex","flexDirection":"column","width":"100%"})
    card=blk("div",children=[head,app],styles={"display":"flex","flexDirection":"column","alignItems":"center","width":"100%","maxWidth":"960px",
        "backgroundColor":CARD,"border":"1px solid "+BORDER,"borderRadius":"16px","paddingTop":"40px","paddingBottom":"40px","paddingLeft":"36px","paddingRight":"36px"},
        mobileStyles={"paddingTop":"28px","paddingBottom":"28px","paddingLeft":"16px","paddingRight":"16px","borderRadius":"14px"})
    return blk("section",children=[card],attributes={"id":"booking"},name="booking",styles={"display":"flex","flexDirection":"column","alignItems":"center","width":"100%","flexShrink":0,
        "backgroundColor":ALT,"paddingTop":"56px","paddingBottom":"56px","paddingLeft":"24px","paddingRight":"24px"},
        mobileStyles={"paddingTop":"40px","paddingBottom":"40px","paddingLeft":"12px","paddingRight":"12px"})

# ================================================================= NAV CSS
NAV_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600;700&family=Montserrat:wght@300;400;500;600;700&display=swap');
html,body{background:#faf8f3;}
html{scroll-behavior:smooth;}
body,input,button,textarea,select{-webkit-font-smoothing:antialiased;-moz-osx-font-smoothing:grayscale;text-rendering:optimizeLegibility;}
::selection{background:#b3873c;color:#ffffff;}
a, a:link, a:visited, a:hover, a:focus, a:active { text-decoration: none !important; }
.bl-menu{opacity:0;visibility:hidden;transform:translateY(10px);transition:opacity .18s ease,transform .18s ease,visibility .18s ease;pointer-events:none;}
.bl-navitem:hover .bl-menu{opacity:1;visibility:visible;transform:translateY(0);pointer-events:auto;}
.bl-menu-link{transition:background .12s ease,color .12s ease;}
.bl-menu-link:hover{background:#f3eee2;color:#b3873c;}
.bl-promo:hover{opacity:.9;}
.bl-brand{transition:opacity .15s ease;opacity:.7;}
.bl-brand:hover{opacity:1;}
.bl-faq>summary{list-style:none;}
.bl-faq>summary::-webkit-details-marker{display:none;}
.bl-faq-plus{transition:transform .2s ease;}
.bl-faq[open] .bl-faq-plus{transform:rotate(45deg);}
.bl-faq-qt{transition:color .15s ease;}
.bl-faq:hover .bl-faq-qt{color:#b3873c;}
.bl-barberpole{background:repeating-linear-gradient(-45deg,#c8102e 0 10px,#f5f5f5 10px 20px,#0a3161 20px 30px,#f5f5f5 30px 40px);}
.bl-social{transition:background .15s ease,color .15s ease,border-color .15s ease;}
.bl-social:hover{background:#b3873c;color:#ffffff;border-color:#b3873c;}
#booking-app select option{background:#ffffff;color:#26211a;}
.bl-timegrid{display:flex;gap:28px;align-items:flex-start;width:100%;}
.bl-timegrid .bl-cal{flex:0 0 330px;max-width:330px;}
.bl-timegrid .bl-slots{flex:1 1 auto;min-width:0;}
@media (max-width:760px){ .bl-timegrid{flex-direction:column;gap:22px;} .bl-timegrid .bl-cal,.bl-timegrid .bl-slots{flex:1 1 auto;max-width:100%;width:100%;} }
#booking-app select:focus{outline:none;border-color:#b3873c;}
.bl-blogcard{transition:transform .15s ease,border-color .15s ease;}
.bl-blogcard:hover{transform:translateY(-3px);border-color:#b3873c;box-shadow:0 14px 34px rgba(38,33,26,.10);}
.bl-blog-content{font-size:16px;line-height:1.8;color:#57503f;}
.bl-blog-content p{margin:0 0 18px;}
.bl-blog-content h2{font-family:'Cormorant Garamond',Georgia,serif;color:#26211a;font-size:27px;font-weight:600;margin:32px 0 12px;letter-spacing:.005em;}
.bl-blog-content h3{font-family:'Cormorant Garamond',Georgia,serif;color:#26211a;font-size:21px;font-weight:600;margin:26px 0 10px;}
.bl-blog-content a{color:#b3873c;text-decoration:underline !important;}
.bl-blog-content ul,.bl-blog-content ol{margin:0 0 18px;padding-left:22px;}
.bl-blog-content li{margin-bottom:8px;}
.bl-blog-content img{max-width:100%;border-radius:12px;margin:18px 0;}
.bl-blog-content strong,.bl-blog-content b{color:#26211a;}
.bl-navitem>div:first-child:hover{color:#b3873c;}
@media (min-width:577px){ .bl-mobile-menu{display:none !important;} }
.bl-mobile-menu a:hover{ color:#b3873c; }
.bl-lang a:hover{ color:#b3873c; }
.bl-anim .bl-reveal{opacity:0;transform:translateY(26px);transition:opacity .7s ease,transform .7s ease;}
.bl-anim .bl-reveal.bl-inview{opacity:1;transform:translateY(0);}
@media (prefers-reduced-motion: reduce){.bl-anim .bl-reveal{opacity:1 !important;transform:none !important;transition:none !important;}}
.bl-lift{transition:transform .25s ease,box-shadow .25s ease;}
.bl-lift:hover{transform:translateY(-5px);box-shadow:0 16px 40px rgba(38,33,26,.12);}
.bl-zoom img{transition:transform .6s ease;}
.bl-zoom:hover img{transform:scale(1.06);}
.bl-cta{transition:transform .2s ease,box-shadow .2s ease,opacity .2s ease;}
.bl-cta:hover{transform:translateY(-2px);box-shadow:0 14px 34px rgba(179,135,60,.45);}
img[src*="tile.openstreetmap"]{filter:grayscale(.35) brightness(.82) contrast(1.05);}
"""

def make_data_script(lang):
    # LT reads the editable Translation DocType at render time (add/edit at
    # /app/translation — no rebuild needed); EN shows source strings as-is.
    if lang == "lt":
        tr_src = ('TR = {}\n'
                  'for row in frappe.db.get_all("Translation", filters={"language": "lt"},\n'
                  '        fields=["source_text", "translated_text"]):\n'
                  '    TR[row["source_text"]] = row["translated_text"]')
    else:
        tr_src = "TR = {}"
    mins = "min" if lang == "lt" else "mins"
    blog_src = ('posts = frappe.db.get_all("Blog Post", filters={"published": 1, "language": "%s"},\n'
                '    fields=["title","route","excerpt","cover_image","author","published_on"], order_by="published_on desc")\n'
                'for p in posts:\n'
                '    p["href"] = "/" + p["route"]\n'
                '    mb = []\n'
                '    if p.get("published_on"): mb.append(str(p["published_on"]))\n'
                '    if p.get("author"): mb.append(p["author"])\n'
                '    p["meta"] = " · ".join(mb)\n'
                '    if not p.get("cover_image"): p["cover_image"] = "%s"\n'
                'data.blog_posts = posts') % (lang, GALLERY[0])
    # extra social/OG tags safe for every page in this language (Builder merges page_data.metatags)
    _locale = "lt_LT" if lang == "lt" else "en_US"
    blog_src += '\ndata.metatags = {"og:site_name": "Blarberinė", "og:locale": "%s"}' % _locale
    script = '''# Blarberine shared page data (%s) — live from DocTypes.
%s
def trx(s, TR=TR):
    return TR.get(s, s) if s else s
def eur(p):
    p = p or 0
    return ("€%%d" %% int(p)) if float(p) == int(p) else ("€%%.2f" %% p)

barbers = frappe.db.get_all("Barber", filters={"is_active": 1},
    fields=["name","barber_name","bio","photo","phone","email"], order_by="barber_name asc")
fb=["https://images.unsplash.com/photo-1521119989659-a83eee488004?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1622286342621-4bd786c2447c?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1605497788044-5a32c7078486?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1593702275687-f8b402bf1fb5?auto=format&fit=crop&w=800&q=80"]
for i,b in enumerate(barbers):
    if not b.get("photo"): b["photo"]=fb[i%%len(fb)]
    b["bio"]=trx(b.get("bio") or "")
data.barbers=barbers
data.stat_barbers="%%d"%%len(barbers)

categories=frappe.db.get_all("Service Category", fields=["name","category_name","description"], order_by="category_name asc")
popular=[]
for c in categories:
    svcs=frappe.db.get_all("Service", filters={"service_category":c["name"]},
        fields=["name","service_name","duration","price","description"], order_by="price asc")
    for s in svcs:
        s["price_display"]=eur(s.get("price"))
        s["duration_display"]="%%d %s"%%int(s.get("duration") or 0)
        s["description"]=trx(s.get("description") or "")
        s["service_name"]=trx(s.get("service_name"))
    c["services"]=svcs; c["count"]=len(svcs); c["count_display"]="(%%d)"%%len(svcs)
    c["price_from_display"]=("%s "+eur(min(x["price"] for x in svcs))) if svcs else ""
    c["category_name"]=trx(c.get("category_name"))
    popular.extend(svcs)
data.service_categories=[c for c in categories if c["services"]]
popular.sort(key=lambda s:s["price"]); data.popular_services=popular[:5]
data.hero_services=popular[:3]

revs=frappe.db.get_all("Testimonial", fields=["author_name","rating","service","source","review_text"], order_by="creation desc")
for r in revs:
    rt=int(r.get("rating") or 5)
    r["stars"]="★"*rt
    bits=[]
    if r.get("service"): bits.append(trx(r["service"]))
    if r.get("source"): bits.append(r["source"])
    r["meta"]=" · ".join(bits)
data.reviews=revs
n=len(revs)
avg=(sum(int(x.get("rating") or 0) for x in revs)/n) if n else 0
data.review_avg="%%.1f"%%avg
data.review_count_display="%%d %s"%%n
data.review_stars="★"*int(round(avg)) if n else ""
brk=[]
for st in [5,4,3,2,1]:
    cc=0
    for x in revs:
        if int(x.get("rating") or 0)==st:
            cc=cc+1
    brk.append({"label":"%%d"%%st,"stars":"★"*st,"count":"%%d"%%cc,"pct":("%%d%%%%"%%int(100*cc/n)) if n else "0%%"})
data.review_breakdown=brk
%s
''' % (lang, tr_src, mins, ("nuo" if lang=="lt" else "from"),
       ("atsiliepimai" if lang=="lt" else "reviews"), blog_src)
    # per-barber deep link for the nav dropdown: /team?pro=<Barber Name>
    # (appended outside the %-template so the literal "%20" survives; note the
    # loop var must NOT start with "_" — RestrictedPython forbids that)
    script += ('\nfor nb in data.barbers:\n'
               '    nb["href"] = ' + repr(R_TEAM) + ' + "?pro=" + nb["name"].replace(" ", "%20")\n')
    # gallery: manager-uploaded Gallery Image docs, else built-in placeholders
    gfallback = [GALLERY[0], WORK[1], GALLERY[1], WORK[4], WORK[3], GALLERY[2]]
    gfb_literal = "[" + ",".join(repr(u) for u in gfallback) + "]"
    script += ('\ngimgs = frappe.db.get_all("Gallery Image", fields=["image"], order_by="display_order asc, creation asc")\n'
               'gimgs = [{"image": gi["image"]} for gi in gimgs if gi.get("image")]\n'
               'if not gimgs:\n'
               '    gimgs = [{"image": gu} for gu in ' + gfb_literal + ']\n'
               'data.gallery_images = gimgs\n')
    return script

PAGES={"home":home,"services":services_page,"team":team_page,"blog":blog_list}

# ---- SEO: preview image (1200x630) + favicon shipped in the app so they deploy with the code ----
OG_IMAGE="/assets/blarberine/images/blarberine-og.jpg"
FAVICON="/assets/blarberine/images/favicon.png"

# ---- SEO: (title, meta description) per page & language ----
SEO={
 "home":{
   "lt":("Blarberinė – Barbershop Kaune | Kirpimai, barzdos, skutimas",
         "Vyriška kirpykla Kaune (Utenos g. 16). Klasikiniai kirpimai, perėjimai, barzdos formavimas ir skutimas karštu rankšluosčiu. Registruokitės internetu — atsiskaitoma vietoje."),
   "en":("Blarberinė – Barbershop Kaunas | Cuts, Beards & Shaves",
         "Men's barbershop in Kaunas (Utenos g. 16). Classic cuts, skin fades, beard shaping and hot-towel shaves. Book online — pay at the venue.")},
 "services":{
   "lt":("Paslaugos ir kainos — Blarberinė Kaunas",
         "Blarberinės kainoraštis: vyriški kirpimai nuo €12, barzdos priežiūra, perėjimai ir skutimas. Registruokitės internetu, atsiskaitoma vietoje."),
   "en":("Services & Prices — Blarberinė Kaunas",
         "Blarberinė price list: men's haircuts from €12, beard care, skin fades and shaves. Book online, pay at the venue in Kaunas.")},
 "team":{
   "lt":("Kirpėjai — Blarberinė Kaunas",
         "Susipažinkite su Blarberinės kirpėjais Kaune. Patyrę meistrai, klasikiniai ir modernūs kirpimai. Rezervuokite savo meistrą internetu."),
   "en":("Our Barbers — Blarberinė Kaunas",
         "Meet the barbers at Blarberinė in Kaunas — experienced masters, classic and modern cuts. Book your barber online.")},
 "about":{
   "lt":("Apie mus — Blarberinė Kaunas",
         "Blarberinė — kvartalo kirpykla Kaune. Meistrystė, tradicijos ir dėmesys detalėms. Utenos g. 16, Kaunas."),
   "en":("About — Blarberinė Kaunas",
         "Blarberinė — a neighbourhood barbershop in Kaunas. Craft, tradition and attention to detail. Utenos g. 16, Kaunas.")},
 "blog":{
   "lt":("Blogas — patarimai ir naujienos | Blarberinė Kaunas",
         "Vyriškos priežiūros patarimai, stiliaus gidai ir naujienos iš Blarberinės kirpyklos Kaune."),
   "en":("Blog — grooming tips & news | Blarberinė Kaunas",
         "Men's grooming tips, style guides and news from Blarberinė barbershop in Kaunas.")},
}

def generate(outdir):
    """Emit page JSON + manifest + data scripts + nav.css into `outdir`."""
    pages_dir=os.path.join(outdir,"pages")
    os.makedirs(pages_dir,exist_ok=True)
    manifest=[]
    for lang in LANGS:
        set_lang(lang)
        for key in KEYS:
            _c[0]=0
            tree=PAGES[key]()
            fn="%s__%s.json"%(lang,key)
            with open(os.path.join(pages_dir,fn),"w") as f: json.dump(tree,f)
            seo_title,seo_desc=SEO[key][lang]
            manifest.append({"lang":lang,"key":key,"route":ROUTES[lang][key],"file":fn,
                             "data_script":"page_data_%s.py"%lang,"title":seo_title,
                             "seo_title":seo_title,"seo_desc":seo_desc,"seo_image":OG_IMAGE,
                             "seo_favicon":FAVICON})
        with open(os.path.join(outdir,"page_data_%s.py"%lang),"w") as f: f.write(make_data_script(lang))
    with open(os.path.join(outdir,"nav.css"),"w") as f: f.write(NAV_CSS)
    with open(os.path.join(pages_dir,"manifest.json"),"w") as f: json.dump(manifest,f,indent=1)
    return manifest

if __name__=="__main__":
    print("generated %d pages"%len(generate(SCRATCH)))
