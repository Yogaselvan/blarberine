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
KEYS = ["home", "services", "team", "about"]

def _routes(lang):
    p = "" if lang == DEFAULT_LANG else "en/"
    return {"home": p+"blarberine", "services": p+"blarberine/services",
            "team": p+"blarberine/team", "about": p+"blarberine/about"}
ROUTES = {l: _routes(l) for l in LANGS}

# palette (sampled from Treatwell)
# Dark luxury brand palette (manager's brand board): black + gold + cream.
BG="#0d0d0d"; ALT="#141414"; INK="#f2ede4"; BODY="#c9c3b8"; MUTED="#948c7a"
BORDER="#2b2820"; CORAL="#d4af37"; NAVY="#050505"; GOLD="#d4af37"; CARD="#1a1a1a"
BAR_Y,BAR_B,BAR_T="#d4af37","#8a6f22","#e7d29a"
FONT="'Montserrat', system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
HEAD="'Playfair Display', Georgia, 'Times New Roman', serif"

GALLERY=[
 "https://images.unsplash.com/photo-1599351431202-1e0f0137899a?auto=format&fit=crop&w=900&q=80",
 "https://images.unsplash.com/photo-1503951914875-452162b0f3f1?auto=format&fit=crop&w=900&q=80",
 "https://images.unsplash.com/photo-1585747860715-2ba37e788b70?auto=format&fit=crop&w=900&q=80"]
WORK=[
 "https://images.unsplash.com/photo-1605497788044-5a32c7078486?auto=format&fit=crop&w=600&q=80",
 "https://images.unsplash.com/photo-1622286342621-4bd786c2447c?auto=format&fit=crop&w=600&q=80",
 "https://images.unsplash.com/photo-1503443207922-dff7d543fd0e?auto=format&fit=crop&w=600&q=80",
 "https://images.unsplash.com/photo-1521119989659-a83eee488004?auto=format&fit=crop&w=600&q=80",
 "https://images.unsplash.com/photo-1593702275687-f8b402bf1fb5?auto=format&fit=crop&w=600&q=80",
 "https://images.unsplash.com/photo-1517832606299-7ae9b720a186?auto=format&fit=crop&w=600&q=80"]
PROMO=[
 "https://images.unsplash.com/photo-1621605815971-fbc98d665033?auto=format&fit=crop&w=500&q=80",
 "https://images.unsplash.com/photo-1622287162716-f311baa1a2b8?auto=format&fit=crop&w=500&q=80"]

# ---------------------------------------------------------------- i18n
T = {
 "nav_services":{"en":"Services","lt":"Paslaugos"},
 "nav_barbers":{"en":"Barbers","lt":"Kirpėjai"},
 "nav_about":{"en":"About","lt":"Apie"},
 "book_now":{"en":"Book now","lt":"Rezervuoti"},
 "book_appt":{"en":"Book an appointment","lt":"Rezervuoti vizitą"},
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
 "address_line":{"en":"Kurpių g. 7, Kaunas, Lithuania","lt":"Kurpių g. 7, Kaunas, Lietuva"},
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
 "am_loc1":{"en":"Close to the Cathedral","lt":"Netoli Katedros"},
 "am_loc2":{"en":"Street parking nearby","lt":"Vietos automobiliams gatvėje"},
 "am_loc3":{"en":"Bus stop nearby","lt":"Netoli autobusų stotelė"},
 "see_all_amenities":{"en":"See all 10 amenities","lt":"Rodyti visus 10 patogumų"},
 "about_desc":{"en":"Blarberinė is a neighbourhood barbershop built on craft and good conversation. For years we've kept Kaunas sharp with classic cuts, skin fades, beard sculpting and traditional hot-towel shaves. Walk-ins are welcome and bookings are recommended — payment is taken at the venue, cash or card.",
               "lt":"Blarberinė — kvartalo kirpykla, sukurta iš meistrystės ir gerų pokalbių. Jau daugelį metų palaikome kauniečius tvarkingus: klasikiniai kirpimai, perėjimai, barzdos modeliavimas ir tradicinis skutimas karštu rankšluosčiu. Laukiame ir be registracijos, tačiau rekomenduojame rezervuoti — atsiskaitoma vietoje, grynaisiais arba kortele."},
 "getting_here":{"en":"Getting here","lt":"Kaip mus rasti"},
 "getting_here_txt":{"en":"A short walk from the Cathedral. Street parking nearby.",
                     "lt":"Vos kelios minutės pėsčiomis nuo Katedros. Netoliese – vietos automobiliams gatvėje."},
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
 "foot_city":{"en":"Kurpių g. 7, Kaunas","lt":"Kurpių g. 7, Kaunas"},
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
R_HOME=R_SERVICES=R_TEAM=R_ABOUT=BOOK_HREF=None
def set_lang(lang):
    global LANG,R_HOME,R_SERVICES,R_TEAM,R_ABOUT,BOOK_HREF
    LANG=lang
    r=ROUTES[lang]
    R_HOME,R_SERVICES,R_TEAM,R_ABOUT="/"+r["home"],"/"+r["services"],"/"+r["team"],"/"+r["about"]
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
    if solid: bg,col,bd=GOLD,"#0d0d0d","none"
    else: bg,col,bd="transparent",GOLD,"1px solid "+GOLD
    return link(label,href,{"display":"inline-flex","alignItems":"center","justifyContent":"center",
        "backgroundColor":bg,"color":col,"border":bd,"fontWeight":"600",
        "fontSize":"14px" if small else "15px",
        "paddingTop":"9px" if small else "12px","paddingBottom":"9px" if small else "12px",
        "paddingLeft":"18px" if small else "26px","paddingRight":"18px" if small else "26px",
        "borderRadius":"8px","cursor":"pointer","flexShrink":"0"})

def stars(size=16,color=GOLD):
    return text("★★★★★",{"fontSize":"%dpx"%size,"color":color,"letterSpacing":"2px","lineHeight":"1"})

def kicker(l): return text(l,{"fontSize":"12px","letterSpacing":"0.16em","textTransform":"uppercase","color":CORAL,"fontWeight":"700","marginBottom":"8px"})
def h2(l): return text(l,{"fontFamily":HEAD,"fontSize":"30px","color":INK,"fontWeight":"600","marginBottom":"20px","letterSpacing":"0.01em"},tag="h2",mob={"fontSize":"23px","marginBottom":"16px"})

def tri_bar(mt="0",mb="0"):
    seg=lambda c: blk("div",styles={"backgroundColor":c,"height":"4px","flex":"1"})
    return blk("div",children=[seg(BAR_Y),seg(BAR_B),seg(BAR_T)],styles={"display":"flex","flexDirection":"row","width":"100%","marginTop":mt,"marginBottom":mb,"flexShrink":0})

def section(children,*,bg=BG,pad="56px",width="1040px",attributes=None,name=None,align="center"):
    inner=blk("div",children=children,styles=container(width))
    return blk("section",children=[inner],attributes=attributes,name=name,styles={
        "display":"flex","flexDirection":"column","alignItems":align,"width":"100%","flexShrink":0,
        "backgroundColor":bg,"paddingTop":pad,"paddingBottom":pad,"paddingLeft":"24px","paddingRight":"24px"},
        mobileStyles={"paddingTop":"40px","paddingBottom":"40px","paddingLeft":"16px","paddingRight":"16px"})

def u(path): return path

def _menu_link(label,href,key=None):
    return link(label,href,{"fontSize":"14px","color":INK,"fontWeight":"500","padding":"9px 10px",
        "borderRadius":"8px","width":"100%"},classes=["bl-menu-link"])

def _menu_panel(children,width="260px"):
    return blk("div",classes=["bl-menu"],children=children,styles={
        "position":"absolute","top":"100%","right":"0","minWidth":width,
        "backgroundColor":CARD,"borderRadius":"14px","border":"1px solid "+BORDER,
        "boxShadow":"0 18px 50px rgba(0,0,0,0.6)","padding":"14px","zIndex":"60",
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
            "borderRadius":"12px","border":"1px solid "+BORDER,"boxShadow":"0 18px 50px rgba(0,0,0,0.6)",
            "padding":"8px","zIndex":"60","display":"flex","flexDirection":"column","gap":"2px"})
    return blk("div",classes=["bl-navitem"],children=[trig,panel],
        styles={"position":"relative","display":"flex","flexDirection":"row","alignItems":"center"})

def nav(active="home"):
    brand=blk("a",attributes={"href":R_HOME},children=[
        text("Blarberinė",{"fontFamily":HEAD,"fontSize":"22px","color":GOLD,"fontWeight":"600",
            "letterSpacing":"0.12em","lineHeight":"1","whiteSpace":"nowrap"},mob={"fontSize":"18px"}),
        text("KAUNAS",{"fontFamily":FONT,"fontSize":"8px","color":MUTED,"fontWeight":"600",
            "letterSpacing":"0.42em","marginTop":"3px"})],
        styles={"textDecoration":"none","display":"flex","flexDirection":"column",
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

    barber_rep=blk("div",children=[_menu_link("Barber",R_TEAM,key="barber_name")],isRepeater=True,
        dataKey={"key":"barbers","comesFrom":"dataScript"},
        styles={"display":"flex","flexDirection":"column","width":"100%"})
    barbers_panel=_menu_panel([
        text(t("our_barbers"),{"fontSize":"12px","color":MUTED,"fontWeight":"700","letterSpacing":"0.08em","textTransform":"uppercase","padding":"4px 10px 8px"}),
        barber_rep,_menu_link(t("meet_team_arrow"),R_TEAM)],width="240px")

    about_link=link(t("nav_about"),R_ABOUT,{"fontSize":"13px","color":INK,"fontWeight":"600",
        "letterSpacing":"0.06em","textTransform":"uppercase","padding":"8px 2px","display":"inline-flex","alignItems":"center"})

    center=blk("div",classes=["bl-navlinks"],children=[
        navitem(t("nav_services"),R_SERVICES,services_panel),
        navitem(t("nav_barbers"),R_TEAM,barbers_panel),
        about_link, lang_dropdown(active)],
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
        mlink(t("nav_services"),R_SERVICES),mlink(t("nav_barbers"),R_TEAM),mlink(t("nav_about"),R_ABOUT),
        blk("div",children=[lang_switcher(active)],styles={"display":"flex","paddingTop":"12px","paddingBottom":"6px"}),
        blk("div",children=[pill(t("book_now"),BOOK_HREF)],styles={"display":"flex","width":"100%","paddingTop":"6px","paddingBottom":"6px"})],
        styles={"display":"none","position":"absolute","top":"100%","left":"0","right":"0","width":"100%","flexDirection":"column",
            "backgroundColor":CARD,"borderBottom":"1px solid "+BORDER,"boxShadow":"0 14px 34px rgba(0,0,0,0.6)",
            "paddingLeft":"20px","paddingRight":"20px","paddingBottom":"10px","zIndex":"55"})
    return blk("header",children=[row,mobile_menu],name="nav",classes=["bl-nav"],styles={
        "display":"flex","flexDirection":"row","justifyContent":"center","alignItems":"center","width":"100%",
        "flexShrink":0,"position":"sticky","top":"0","zIndex":"50","paddingTop":"14px","paddingBottom":"14px",
        "paddingLeft":"24px","paddingRight":"24px","backgroundColor":"rgba(13,13,13,0.9)",
        "backdropFilter":"blur(10px)","borderBottom":"1px solid "+BORDER},
        mobileStyles={"paddingLeft":"16px","paddingRight":"16px"})

# ================================================================= FOOTER
def footer():
    def col(title,items):
        ch=[text(title,{"fontSize":"12px","color":GOLD,"fontWeight":"600","letterSpacing":"0.14em","textTransform":"uppercase","marginBottom":"14px"})]
        for label,href in items:
            ch.append(link(label,href,{"fontSize":"14px","color":"#b3ab98","marginBottom":"10px"}))
        return blk("div",children=ch,styles={"display":"flex","flexDirection":"column","flex":"1","minWidth":"180px"})
    brand_col=blk("div",children=[
        text("Blarberinė",{"fontFamily":HEAD,"fontSize":"25px","color":GOLD,"fontWeight":"600","letterSpacing":"0.1em","marginBottom":"2px"}),
        text("KAUNAS",{"fontFamily":FONT,"fontSize":"9px","color":MUTED,"fontWeight":"600","letterSpacing":"0.42em","marginBottom":"14px"}),
        text(t("footer_tag"),{"fontSize":"14px","color":"#b3ab98","lineHeight":"1.6","marginBottom":"16px","width":"auto","maxWidth":"260px"}),
        blk("div",children=[text(g,{"fontSize":"16px","color":GOLD}) for g in ["f","ig","in"]],
            styles={"display":"flex","flexDirection":"row","gap":"14px"})],
        styles={"display":"flex","flexDirection":"column","flex":"1.4","minWidth":"220px"})
    cols=blk("div",children=[brand_col,
        col(t("foot_explore"),[(t("nav_services"),R_SERVICES),(t("nav_barbers"),R_TEAM),(t("nav_about"),R_ABOUT),(t("book_now"),BOOK_HREF)]),
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
    return blk("footer",children=[tri_bar(),blk("div",children=[inner],styles={
        "display":"flex","flexDirection":"column","alignItems":"center","width":"100%",
        "paddingTop":"52px","paddingBottom":"40px","paddingLeft":"24px","paddingRight":"24px"},
        mobileStyles={"paddingLeft":"16px","paddingRight":"16px"})],
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
    photo=img(WORK[0],{"width":"100%","height":"260px","objectFit":"cover","borderRadius":"12px","flexShrink":"0"},key="photo")
    name=text("Barber",{"fontSize":"18px","color":INK,"fontWeight":"700","marginTop":"14px"},key="barber_name",tag="h3")
    bio=text("Bio",{"fontSize":"14px","color":MUTED,"lineHeight":"1.55","marginTop":"6px","width":"auto"},key="bio")
    return blk("div",children=[photo,name,bio],styles={"display":"flex","flexDirection":"column","width":"100%"})

def barbers_grid():
    return blk("div",children=[barber_card()],isRepeater=True,dataKey={"key":"barbers","comesFrom":"dataScript"},
        styles={"display":"grid","gridTemplateColumns":"repeat(3, 1fr)","gap":"28px","width":"100%"},
        mobileStyles={"gridTemplateColumns":"1fr"})

# ================================================================= HERO
def hero():
    name=text("Blarberinė",{"fontFamily":HEAD,"fontSize":"46px","color":INK,"fontWeight":"600","letterSpacing":"0.08em","textTransform":"uppercase","marginBottom":"12px"},tag="h1",mob={"fontSize":"32px"})
    rating=blk("div",children=[stars(18),text(t("trusted"),{"fontSize":"14px","color":MUTED,"fontWeight":"500"}),
        text(t("vilnius"),{"fontSize":"14px","color":MUTED})],
        styles={"display":"flex","flexDirection":"row","alignItems":"center","gap":"10px","marginBottom":"18px"},
        mobileStyles={"flexWrap":"wrap","gap":"6px"})
    tag=text(t("hero_tag"),{"fontSize":"17px","color":BODY,"lineHeight":"1.6","maxWidth":"520px","marginBottom":"24px","width":"100%"})
    cta=blk("div",children=[pill(t("book_appt"),BOOK_HREF,solid=True),
        link(t("view_services"),R_SERVICES,{"fontSize":"15px","color":CORAL,"fontWeight":"600","padding":"12px 6px"})],
        styles={"display":"flex","flexDirection":"row","alignItems":"center","gap":"14px","flexWrap":"wrap"})
    left=blk("div",children=[name,rating,tag,cta],styles={"display":"flex","flexDirection":"column","flex":"1","minWidth":"280px"})
    big=img(GALLERY[0],{"width":"46%","height":"340px","objectFit":"cover","borderRadius":"16px","flexShrink":"0"})
    big["mobileStyles"]={"width":"100%","height":"240px"}
    row=blk("div",children=[left,big],styles={"display":"flex","flexDirection":"row","gap":"40px","width":"100%","maxWidth":"1080px","alignItems":"center"},
        mobileStyles={"flexDirection":"column","gap":"24px"})
    return blk("section",children=[row],styles={"display":"flex","flexDirection":"column","alignItems":"center","width":"100%",
        "flexShrink":0,"backgroundColor":BG,"paddingTop":"56px","paddingBottom":"40px","paddingLeft":"24px","paddingRight":"24px"},
        mobileStyles={"paddingTop":"32px","paddingBottom":"28px","paddingLeft":"16px","paddingRight":"16px"})

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
    pop=blk("div",children=[service_row()],isRepeater=True,dataKey={"key":"popular_services","comesFrom":"dataScript"},
        styles={"display":"flex","flexDirection":"column","width":"100%"})
    popular=section([blk("div",children=[
        blk("div",children=[h2(t("popular_services")),link(t("see_all_services"),R_SERVICES,{"fontSize":"14px","color":CORAL,"fontWeight":"600"})],
            styles={"display":"flex","flexDirection":"row","justifyContent":"space-between","alignItems":"center","width":"100%","flexWrap":"wrap","gap":"8px"}),
        rows_shrinkwrap(pop)],styles=container("760px"))],width="760px")
    team=section([kicker(t("the_team")),h2(t("meet_barbers")),barbers_grid(),
        blk("div",children=[pill(t("meet_team_btn"),R_TEAM,solid=False)],styles={"display":"flex","justifyContent":"center","width":"100%","marginTop":"28px"})],
        bg=ALT)
    return _body([nav("home"),hero(),info_bar(),popular,team,booking_section(),footer()])

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

def about_page():
    gmaps="https://www.google.com/maps/search/?api=1&query=Kurpi%C5%B3+g.+7+Kaunas+Lithuania"
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
        text("Kurpių g. 7",{"fontSize":"15px","color":BODY}),text(t("addr_city"),{"fontSize":"15px","color":BODY}),
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
    card=blk("div",children=[head,app],styles={"display":"flex","flexDirection":"column","alignItems":"center","width":"100%","maxWidth":"720px",
        "backgroundColor":CARD,"border":"1px solid "+BORDER,"borderRadius":"16px","paddingTop":"40px","paddingBottom":"40px","paddingLeft":"32px","paddingRight":"32px"},
        mobileStyles={"paddingTop":"28px","paddingBottom":"28px","paddingLeft":"16px","paddingRight":"16px","borderRadius":"14px"})
    return blk("section",children=[card],attributes={"id":"booking"},name="booking",styles={"display":"flex","flexDirection":"column","alignItems":"center","width":"100%","flexShrink":0,
        "backgroundColor":ALT,"paddingTop":"56px","paddingBottom":"56px","paddingLeft":"24px","paddingRight":"24px"},
        mobileStyles={"paddingTop":"40px","paddingBottom":"40px","paddingLeft":"12px","paddingRight":"12px"})

# ================================================================= NAV CSS
NAV_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600;700&family=Montserrat:wght@300;400;500;600;700&display=swap');
html,body{background:#0d0d0d;}
::selection{background:#d4af37;color:#0d0d0d;}
a, a:link, a:visited, a:hover, a:focus, a:active { text-decoration: none !important; }
.bl-menu{opacity:0;visibility:hidden;transform:translateY(10px);transition:opacity .18s ease,transform .18s ease,visibility .18s ease;pointer-events:none;}
.bl-navitem:hover .bl-menu{opacity:1;visibility:visible;transform:translateY(0);pointer-events:auto;}
.bl-menu-link{transition:background .12s ease,color .12s ease;}
.bl-menu-link:hover{background:#242017;color:#d4af37;}
.bl-promo:hover{opacity:.9;}
.bl-navitem>div:first-child:hover{color:#d4af37;}
@media (min-width:577px){ .bl-mobile-menu{display:none !important;} }
.bl-mobile-menu a:hover{ color:#d4af37; }
.bl-lang a:hover{ color:#d4af37; }
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
    return '''# Blarberine shared page data (%s) — live from DocTypes.
%s
def trx(s, TR=TR):
    return TR.get(s, s) if s else s
def eur(p):
    p = p or 0
    return ("€%%d" %% int(p)) if float(p) == int(p) else ("€%%.2f" %% p)

barbers = frappe.db.get_all("Barber", filters={"is_active": 1},
    fields=["name","barber_name","bio","photo","phone","email"], order_by="barber_name asc")
fb=["https://images.unsplash.com/photo-1503443207922-dff7d543fd0e?auto=format&fit=crop&w=600&q=80",
    "https://images.unsplash.com/photo-1622286342621-4bd786c2447c?auto=format&fit=crop&w=600&q=80",
    "https://images.unsplash.com/photo-1605497788044-5a32c7078486?auto=format&fit=crop&w=600&q=80",
    "https://images.unsplash.com/photo-1521119989659-a83eee488004?auto=format&fit=crop&w=600&q=80"]
for i,b in enumerate(barbers):
    if not b.get("photo"): b["photo"]=fb[i%%len(fb)]
    b["bio"]=trx(b.get("bio") or "")
data.barbers=barbers

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
            cc+=1
    brk.append({"label":"%%d"%%st,"stars":"★"*st,"count":"%%d"%%cc,"pct":("%%d%%%%"%%int(100*cc/n)) if n else "0%%"})
data.review_breakdown=brk
''' % (lang, tr_src, mins, ("nuo" if lang=="lt" else "from"),
       ("atsiliepimai" if lang=="lt" else "reviews"))

PAGES={"home":home,"services":services_page,"team":team_page,"about":about_page}

if __name__=="__main__":
    os.makedirs(PAGES_DIR,exist_ok=True)
    manifest=[]
    for lang in LANGS:
        set_lang(lang)
        for key in KEYS:
            _c[0]=0
            tree=PAGES[key]()
            fn="%s__%s.json"%(lang,key)
            with open(os.path.join(PAGES_DIR,fn),"w") as f: json.dump(tree,f)
            manifest.append({"lang":lang,"key":key,"route":ROUTES[lang][key],"file":fn,
                             "data_script":"page_data_%s.py"%lang,"title":"Blarberinė — %s (%s)"%(key,lang)})
        with open(os.path.join(SCRATCH,"page_data_%s.py"%lang),"w") as f: f.write(make_data_script(lang))
    with open(os.path.join(SCRATCH,"nav.css"),"w") as f: f.write(NAV_CSS)
    with open(os.path.join(PAGES_DIR,"manifest.json"),"w") as f: json.dump(manifest,f,indent=1)
    print("generated %d pages"%len(manifest))
