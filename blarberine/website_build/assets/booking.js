/* Blarberine booking wizard — Treatwell-style multi-service flow.
   basket -> select time (professional + week strip) -> checkout -> done.
   Consumes localStorage['bl_basket'] (shared with interactive.js). Calls the
   whitelisted guest API: get_booking_data, get_basket_slots,
   get_week_availability, create_basket_booking. Pay-at-venue only. */
(function () {
  "use strict";
  var CORAL="#d4af37", NAVY="#050505", INK="#f2ede4", MUTED="#948c7a",
      BORDER="#2b2820", ALT="#141414", GREEN="#3fbf7a", CARD="#1a1a1a", DARK="#0d0d0d";
  var API="/api/method/blarberine.blarberine.api.";
  var FONT="'Montserrat', system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif";
  var LANG=/^\/en(\/|$)/.test(location.pathname)?"en":"lt";
  var MONTHS_ALL={en:["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"],
    lt:["saus.","vas.","kov.","bal.","geg.","birž.","liep.","rugp.","rugs.","spal.","lapkr.","gruod."]};
  var DOW_ALL={en:["Sun","Mon","Tue","Wed","Thu","Fri","Sat"],lt:["Sk","Pr","An","Tr","Kt","Pn","Št"]};
  var MONTHS=MONTHS_ALL[LANG]||MONTHS_ALL.lt, DOW=DOW_ALL[LANG]||DOW_ALL.lt;
  // Monday-first column labels (European calendars) + full weekday names, indexed by getDay() 0=Sun
  var DOW_MON={en:["Mon","Tue","Wed","Thu","Fri","Sat","Sun"],lt:["Pr","An","Tr","Kt","Pn","Št","Sk"]};
  var DOW_FULL={en:["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"],
    lt:["Sekmadienis","Pirmadienis","Antradienis","Trečiadienis","Ketvirtadienis","Penktadienis","Šeštadienis"]};
  var I18N={
   en:{back:"← Back",all:"All",add:"+ Add",added:"✓ Added",yourAppt:"Your appointment",
    basketSubHas:"Choose a time next — pay at the venue.",basketSubEmpty:"Pick a treatment to get started.",
    totalPay:"Total · pay at venue",hideTreat:"− Hide treatments",addAnother:"+ Add another treatment",addTreat:"+ Add treatment",
    choose:"Choose time",selectTime:"Select time",anyPro:"Any professional",loadingAvail:"Loading availability…",
    fullyBooked:"Fully booked",nextAvail:"Next availability on",goTo:"Go to",finding:"Finding times…",noTimes:"No times left this day.",
    noneThisMonth:"No availability this month — try the next one ›",pickDate:"Pick a date to see available times.",
    checkout:"Checkout",checkoutSub:"Pay at the venue — no card needed to book.",withw:"With ",firstAvail:"first available professional",
    payVenue:"Pay at venue",fullName:"Full name",email:"Email (optional)",phone:"Phone",guest:"Check out as guest",payment:"Payment",
    cancelNote:"You won't be charged now — you'll pay at the venue after your appointment. If you cancel less than 24 hours before or don't show up, the venue may charge you.",
    promoNote:"Unable to add promo codes or gift cards when paying at venue.",venuePolicies:"Venue policies",
    pol1:"Cancellations: please give at least 24 hours' notice. Late cancellations or no-shows may be charged in full.",
    pol2:"Please arrive 5 minutes early. Payment is taken in-store by cash or card.",
    consent1:"I'd like to receive news and offers from Blarberinė by email. You can unsubscribe anytime.",
    consent2:"I'd like updates about my booking and offers from the salon by email & SMS.",
    complete:"Complete booking",terms:"By continuing you agree to our Booking Terms.",errName:"Please enter your name and phone number.",
    booking:"Booking…",errGeneric:"Something went wrong. Please try again.",errNet:"Network error. Please try again.",
    booked:"You're booked!",reference:"Reference:",bookAnother:"Book another",loadingBooking:"Loading booking…",errBooking:"Could not load booking. Please refresh."},
   lt:{back:"← Atgal",all:"Visos",add:"+ Pridėti",added:"✓ Pridėta",yourAppt:"Jūsų vizitas",
    basketSubHas:"Toliau pasirinkite laiką — atsiskaitoma vietoje.",basketSubEmpty:"Pasirinkite paslaugą, kad pradėtumėte.",
    totalPay:"Iš viso · atsiskaitoma vietoje",hideTreat:"− Slėpti paslaugas",addAnother:"+ Pridėti dar paslaugą",addTreat:"+ Pridėti paslaugą",
    choose:"Pasirinkti laiką",selectTime:"Pasirinkite laiką",anyPro:"Bet kuris meistras",loadingAvail:"Kraunamas laisvas laikas…",
    fullyBooked:"Viskas užimta",nextAvail:"Artimiausias laisvas laikas:",goTo:"Eiti į",finding:"Ieškoma laikų…",noTimes:"Šią dieną laisvų laikų nėra.",
    noneThisMonth:"Šį mėnesį laisvų laikų nėra — pabandykite kitą ›",pickDate:"Pasirinkite dieną, kad matytumėte laisvus laikus.",
    checkout:"Rezervacija",checkoutSub:"Atsiskaitoma vietoje — rezervuojant kortelės nereikia.",withw:"Su ",firstAvail:"pirmu laisvu meistru",
    payVenue:"Atsiskaitymas vietoje",fullName:"Vardas ir pavardė",email:"El. paštas (nebūtina)",phone:"Telefonas",guest:"Užsakymas be paskyros",payment:"Apmokėjimas",
    cancelNote:"Dabar nebūsite apmokestinti — sumokėsite vietoje po vizito. Jei atšauksite likus mažiau nei 24 val. arba neatvyksite, kirpykla gali pritaikyti mokestį.",
    promoNote:"Atsiskaitant vietoje nuolaidų kodų ir dovanų kuponų pridėti negalima.",venuePolicies:"Kirpyklos taisyklės",
    pol1:"Atšaukimas: praneškite likus bent 24 val. Vėlyvi atšaukimai ar neatvykimai gali būti apmokestinti visa suma.",
    pol2:"Prašome atvykti 5 min. anksčiau. Atsiskaitoma vietoje grynaisiais arba kortele.",
    consent1:"Noriu gauti naujienas ir pasiūlymus iš Blarberinė el. paštu. Bet kada galiu atsisakyti.",
    consent2:"Noriu gauti pranešimus apie savo rezervaciją ir kirpyklos pasiūlymus el. paštu ir SMS.",
    complete:"Patvirtinti rezervaciją",terms:"Tęsdami sutinkate su mūsų rezervacijos sąlygomis.",errName:"Įveskite vardą ir telefono numerį.",
    booking:"Rezervuojama…",errGeneric:"Kažkas nepavyko. Bandykite dar kartą.",errNet:"Tinklo klaida. Bandykite dar kartą.",
    booked:"Rezervacija patvirtinta!",reference:"Nr.:",bookAnother:"Rezervuoti dar",loadingBooking:"Kraunama rezervacija…",errBooking:"Nepavyko įkelti rezervacijos. Atnaujinkite puslapį."}
  };
  var L=I18N[LANG]||I18N.lt;

  function ready(fn){ if(document.readyState!=="loading") fn(); else document.addEventListener("DOMContentLoaded",fn); }
  function csrf(){ return (window.frappe&&window.frappe.csrf_token)||""; }
  function el(tag,style,props){
    var n=document.createElement(tag); if(style) n.style.cssText=style;
    if(props) for(var k in props){ if(k==="text")n.textContent=props[k]; else if(k==="html")n.innerHTML=props[k];
      else if(k==="on")for(var ev in props.on)n.addEventListener(ev,props.on[ev]); else n.setAttribute(k,props[k]); }
    return n;
  }
  function clear(n){ while(n.firstChild) n.removeChild(n.firstChild); }
  function get(url){ return fetch(url,{headers:{"X-Frappe-CSRF-Token":csrf()}}).then(function(r){return r.json();}).then(function(j){return j.message;}); }
  function post(path,body){ return fetch(API+path,{method:"POST",headers:{"Content-Type":"application/json","X-Frappe-CSRF-Token":csrf()},body:JSON.stringify(body)}).then(function(r){return r.json();}).then(function(j){return j.message;}); }
  function q(o){ return Object.keys(o).map(function(k){return encodeURIComponent(k)+"="+encodeURIComponent(o[k]);}).join("&"); }
  function eur(v){ v=v||0; return (v===Math.round(v))?("€"+Math.round(v)):("€"+v.toFixed(2)); }

  function loadBasket(){ try{ return JSON.parse(localStorage.getItem("bl_basket"))||[]; }catch(e){ return []; } }
  function saveBasket(b){ try{ localStorage.setItem("bl_basket",JSON.stringify(b)); }catch(e){} }

  function iso(d){ return d.getFullYear()+"-"+("0"+(d.getMonth()+1)).slice(-2)+"-"+("0"+d.getDate()).slice(-2); }
  function parseISO(s){ var p=s.split("-"); return new Date(+p[0],+p[1]-1,+p[2]); }
  function addDays(d,n){ var x=new Date(d.getTime()); x.setDate(x.getDate()+n); return x; }

  var BTN="font-family:"+FONT+";display:inline-flex;align-items:center;justify-content:center;background:"+CORAL+
    ";color:#0d0d0d;font-weight:700;font-size:15px;padding:13px 26px;border:none;border-radius:8px;cursor:pointer;text-decoration:none;";
  var GHOST="font-family:"+FONT+";background:"+CARD+";color:"+MUTED+";font-weight:600;font-size:14px;padding:9px 18px;border:1px solid "+BORDER+";border-radius:8px;cursor:pointer;";

  ready(function(){
    var root=document.getElementById("booking-app");
    if(!root) return;
    var DATA={cats:[],barbers:[]};
    var state={step:"basket", pro:"", weekStart:new Date(new Date().getFullYear(),new Date().getMonth(),new Date().getDate()),
               date:null, slot:null, showPicker:false, result:null};

    function total(){ return loadBasket().reduce(function(s,x){return s+(x.price||0);},0); }
    function names(){ return loadBasket().map(function(x){return x.name;}); }

    function h(title,sub){
      var w=el("div","text-align:center;margin-bottom:20px;");
      w.appendChild(el("h3","font-family:"+FONT+";font-size:22px;color:"+INK+";font-weight:700;margin:0 0 4px;",{text:title}));
      if(sub) w.appendChild(el("p","font-family:"+FONT+";font-size:14px;color:"+MUTED+";margin:0;",{text:sub}));
      return w;
    }
    function back(to){ return el("button",GHOST+"margin-top:18px;",{text:L.back,on:{click:function(){ state.step=to; render(); }}}); }

    // ---------- BASKET ----------
    function servicePicker(){
      var wrap=el("div","border:1px solid "+BORDER+";border-radius:12px;padding:16px;margin-top:12px;");
      var active=L.all;
      var chips=el("div","display:flex;flex-wrap:wrap;gap:8px;margin-bottom:14px;");
      var list=el("div","");
      function drawChips(){ clear(chips);
        [L.all].concat(DATA.cats.map(function(c){return c.category_name;})).forEach(function(l){
          var on=l===active;
          chips.appendChild(el("button","font-family:"+FONT+";font-size:13px;font-weight:600;padding:7px 14px;border-radius:999px;cursor:pointer;"+
            (on?("background:"+CORAL+";color:#0d0d0d;border:1px solid "+CORAL+";"):("background:"+CARD+";color:"+INK+";border:1px solid "+BORDER+";")),
            {text:l,on:{click:function(){active=l;drawChips();drawList();}}}));
        });
      }
      function drawList(){ clear(list);
        DATA.cats.forEach(function(c){ if(active!==L.all&&c.category_name!==active) return;
          (c.services||[]).forEach(function(s){
            var inB=names().indexOf(s.name)>-1;
            var row=el("div","display:flex;justify-content:space-between;align-items:center;gap:12px;padding:12px 0;border-bottom:1px solid "+BORDER+";");
            var left=el("div"); left.appendChild(el("div","font-family:"+FONT+";font-size:15px;color:"+INK+";font-weight:600;",{text:s.service_name}));
            left.appendChild(el("div","font-family:"+FONT+";font-size:12px;color:"+MUTED+";margin-top:2px;",{text:s.duration_display+"  ·  "+s.price_display}));
            var add=el("button","font-family:"+FONT+";font-size:13px;font-weight:600;padding:6px 14px;border-radius:8px;cursor:pointer;flex-shrink:0;"+
              (inB?("background:#13291c;color:"+GREEN+";border:1px solid "+GREEN+";"):("background:"+CARD+";color:"+CORAL+";border:1px solid "+CORAL+";")),
              {text:inB?L.added:L.add});
            // single service per booking: selecting one replaces any previous choice
            add.addEventListener("click",function(){ var sel=names().indexOf(s.name)>-1;
              saveBasket(sel?[]:[{name:s.name,service_name:s.service_name,price:s.price,price_display:s.price_display}]);
              render(); });
            row.appendChild(left); row.appendChild(add); list.appendChild(row);
          });
        });
      }
      drawChips(); drawList(); wrap.appendChild(chips); wrap.appendChild(list); return wrap;
    }

    function renderBasket(){
      var b=loadBasket();
      root.appendChild(h(L.yourAppt, b.length?L.basketSubHas:L.basketSubEmpty));
      // one service per booking: always show the picker (single-select highlights the
      // chosen service); once one is picked, offer "Choose time". No add-more button.
      root.appendChild(servicePicker());
      if(b.length){
        var go=el("button",BTN+"width:100%;margin-top:16px;",{text:L.choose,on:{click:function(){ state.step="time"; state.date=null; state.slot=null; render(); }}});
        root.appendChild(go);
      }
    }

    // ---------- TIME (Treatwell-style: month calendar + time list) ----------
    function startOfMonth(d){ return new Date(d.getFullYear(),d.getMonth(),1); }
    function firstAvail(map){ var ks=Object.keys(map||{}).filter(function(k){return map[k]>0;}).sort(); return ks[0]||null; }

    function renderTime(){
      root.appendChild(h(L.selectTime));

      // professional selector — full width, centred
      var selWrap=el("div","width:100%;max-width:460px;margin:0 auto 24px;");
      var sel=el("select","font-family:"+FONT+";font-size:15px;padding:13px 16px;border:1px solid "+BORDER+";border-radius:10px;width:100%;color:"+INK+";background:"+CARD+";display:block;cursor:pointer;");
      sel.appendChild(el("option","",{value:"",text:L.anyPro}));
      DATA.barbers.forEach(function(bb){ sel.appendChild(el("option","",{value:bb.name,text:bb.barber_name})); });
      sel.value=state.pro;
      sel.addEventListener("change",function(){ state.pro=sel.value; state.date=null; state.slot=null; loadMonth(); });
      selWrap.appendChild(sel); root.appendChild(selWrap);

      // two panels: calendar (left) + times (right); stack on mobile via .bl-timegrid
      var layout=el("div"); layout.className="bl-timegrid";
      var calPanel=el("div","border:1px solid "+BORDER+";border-radius:14px;padding:18px;"); calPanel.className="bl-cal";
      var slotPanel=el("div",""); slotPanel.className="bl-slots";
      layout.appendChild(calPanel); layout.appendChild(slotPanel);
      root.appendChild(layout);

      var monthCursor=startOfMonth(state.date?parseISO(state.date):new Date());
      var monthData=null;

      function loadMonth(){
        clear(calPanel); clear(slotPanel);
        calPanel.appendChild(el("p","font-family:"+FONT+";text-align:center;color:"+MUTED+";font-size:14px;padding:40px 0;",{text:L.loadingAvail}));
        get(API+"get_month_availability?"+q({services:JSON.stringify(names()),month_start:iso(monthCursor),barber:state.pro})).then(function(days){
          monthData={}; days.forEach(function(x){ monthData[x.date]=x.count; });
          var inMonth=state.date&&parseISO(state.date).getMonth()===monthCursor.getMonth()&&parseISO(state.date).getFullYear()===monthCursor.getFullYear();
          if(!inMonth||(monthData[state.date]||0)===0) state.date=firstAvail(monthData);
          drawCalendar(); drawSlots();
        });
      }

      function drawCalendar(){
        clear(calPanel);
        var now=new Date();
        var atMin=monthCursor.getFullYear()<now.getFullYear()||(monthCursor.getFullYear()===now.getFullYear()&&monthCursor.getMonth()<=now.getMonth());
        var head=el("div","display:flex;align-items:center;justify-content:space-between;margin-bottom:16px;");
        var prev=el("button","background:"+CARD+";border:1px solid "+BORDER+";border-radius:8px;width:34px;height:34px;cursor:pointer;font-size:18px;color:"+INK+";"+(atMin?"opacity:.3;cursor:default;":""),{html:"‹"});
        if(!atMin) prev.addEventListener("click",function(){ monthCursor=new Date(monthCursor.getFullYear(),monthCursor.getMonth()-1,1); loadMonth(); });
        var next=el("button","background:"+CARD+";border:1px solid "+BORDER+";border-radius:8px;width:34px;height:34px;cursor:pointer;font-size:18px;color:"+INK+";",{html:"›",on:{click:function(){ monthCursor=new Date(monthCursor.getFullYear(),monthCursor.getMonth()+1,1); loadMonth(); }}});
        head.appendChild(prev);
        head.appendChild(el("div","font-family:"+FONT+";font-size:16px;font-weight:700;color:"+INK+";text-transform:capitalize;",{text:MONTHS[monthCursor.getMonth()]+" "+monthCursor.getFullYear()}));
        head.appendChild(next);
        calPanel.appendChild(head);

        var wl=el("div","display:grid;grid-template-columns:repeat(7,1fr);gap:5px;margin-bottom:7px;");
        (DOW_MON[LANG]||DOW_MON.lt).forEach(function(d){ wl.appendChild(el("div","font-family:"+FONT+";font-size:11px;color:"+MUTED+";text-align:center;font-weight:600;letter-spacing:.04em;",{text:d})); });
        calPanel.appendChild(wl);

        var grid=el("div","display:grid;grid-template-columns:repeat(7,1fr);gap:5px;");
        var startCol=(monthCursor.getDay()+6)%7;   // Monday-first offset
        for(var i=0;i<startCol;i++) grid.appendChild(el("div",""));
        var dim=new Date(monthCursor.getFullYear(),monthCursor.getMonth()+1,0).getDate();
        var todayI=iso(now);
        for(var day=1;day<=dim;day++){
          (function(dnum){
            var di=iso(new Date(monthCursor.getFullYear(),monthCursor.getMonth(),dnum));
            var count=(monthData&&monthData[di])||0, past=di<todayI, avail=count>0&&!past, on=state.date===di, isToday=di===todayI;
            var st="display:flex;align-items:center;justify-content:center;height:40px;border-radius:10px;font-family:"+FONT+";font-size:14px;font-weight:600;"+
              (on?("background:"+CORAL+";color:#0d0d0d;"):(avail?("color:"+INK+";background:"+CARD+";cursor:pointer;"):("color:#4a473f;")))+
              (isToday&&!on?("box-shadow:inset 0 0 0 1px "+CORAL+";"):"");
            var cell=el("div",st,{text:(""+dnum)});
            if(avail&&!on) cell.addEventListener("click",function(){ state.date=di; state.slot=null; drawCalendar(); drawSlots(); });
            grid.appendChild(cell);
          })(day);
        }
        calPanel.appendChild(grid);
      }

      function drawSlots(){
        clear(slotPanel);
        if(!state.date){
          slotPanel.appendChild(el("div","font-family:"+FONT+";text-align:center;color:"+MUTED+";font-size:14px;padding:48px 16px;line-height:1.6;",{text:L.noneThisMonth}));
          return;
        }
        var dt=parseISO(state.date);
        slotPanel.appendChild(el("div","font-family:"+FONT+";font-size:15px;font-weight:700;color:"+INK+";margin-bottom:14px;text-transform:capitalize;",{text:(DOW_FULL[LANG]||DOW_FULL.lt)[dt.getDay()]+", "+dt.getDate()+" "+MONTHS[dt.getMonth()]}));
        var box=el("div","max-height:360px;overflow-y:auto;"); slotPanel.appendChild(box);
        box.appendChild(el("p","font-family:"+FONT+";text-align:center;color:"+MUTED+";font-size:13px;padding:16px 0;",{text:L.finding}));
        get(API+"get_basket_slots?"+q({services:JSON.stringify(names()),date:state.date,barber:state.pro})).then(function(res){
          clear(box);
          var slots=(res&&res.slots)||[];
          if(!slots.length){ box.appendChild(el("p","font-family:"+FONT+";text-align:center;color:"+MUTED+";padding:24px 0;",{text:L.noTimes})); return; }
          var grid=el("div","display:grid;grid-template-columns:repeat(auto-fill,minmax(78px,1fr));gap:10px;");
          slots.forEach(function(s){
            grid.appendChild(el("button","font-family:"+FONT+";font-size:15px;font-weight:600;color:"+INK+";background:"+CARD+";border:1px solid "+BORDER+";border-radius:9px;padding:11px 0;cursor:pointer;transition:border-color .12s,color .12s;",
              {text:s.time,on:{click:function(){ state.slot=s; state.step="checkout"; render(); },
                mouseover:function(e){e.currentTarget.style.borderColor=CORAL;e.currentTarget.style.color=CORAL;},
                mouseout:function(e){e.currentTarget.style.borderColor=BORDER;e.currentTarget.style.color=INK;}}}));
          });
          box.appendChild(grid);
        });
      }

      loadMonth();
      root.appendChild(back("basket"));
    }

    // ---------- CHECKOUT ----------
    function field(label,type,ph){
      var w=el("div","margin-bottom:14px;text-align:left;");
      w.appendChild(el("label","font-family:"+FONT+";font-size:13px;font-weight:600;color:"+INK+";display:block;margin-bottom:6px;",{text:label}));
      var i=el("input","font-family:"+FONT+";font-size:15px;padding:11px 14px;border:1px solid "+BORDER+";border-radius:8px;width:100%;box-sizing:border-box;background:"+CARD+";color:"+INK+";",{type:type,placeholder:ph||""});
      w.appendChild(i); w._input=i; return w;
    }
    function check(label){
      var w=el("label","display:flex;gap:10px;align-items:flex-start;margin-bottom:12px;cursor:pointer;");
      var c=el("input","margin-top:3px;flex-shrink:0;",{type:"checkbox"});
      w.appendChild(c); w.appendChild(el("span","font-family:"+FONT+";font-size:13px;color:"+MUTED+";line-height:1.5;",{text:label})); return w;
    }
    function renderCheckout(){
      root.appendChild(h(L.checkout,L.checkoutSub));
      var b=loadBasket();
      // summary
      var sum=el("div","border:1px solid "+BORDER+";border-radius:12px;padding:16px;margin-bottom:20px;background:"+ALT+";");
      var dt=parseISO(state.date);
      var when=state.slot.time+"  ·  "+DOW[dt.getDay()]+" "+dt.getDate()+" "+MONTHS[dt.getMonth()];
      sum.appendChild(el("div","font-family:"+FONT+";font-size:16px;font-weight:700;color:"+INK+";margin-bottom:2px;",{text:when}));
      sum.appendChild(el("div","font-family:"+FONT+";font-size:13px;color:"+MUTED+";margin-bottom:12px;",{text:L.withw+(state.pro?proName(state.pro):L.firstAvail)}));
      b.forEach(function(x){ var r=el("div","display:flex;justify-content:space-between;padding:4px 0;");
        r.appendChild(el("span","font-family:"+FONT+";font-size:14px;color:"+INK+";",{text:x.service_name}));
        r.appendChild(el("span","font-family:"+FONT+";font-size:14px;color:"+INK+";",{text:x.price_display})); sum.appendChild(r); });
      var tr=el("div","display:flex;justify-content:space-between;border-top:1px solid "+BORDER+";margin-top:8px;padding-top:10px;");
      tr.appendChild(el("span","font-family:"+FONT+";font-size:15px;font-weight:700;color:"+INK+";",{text:L.payVenue}));
      tr.appendChild(el("span","font-family:"+FONT+";font-size:15px;font-weight:800;color:"+INK+";",{text:eur(total())}));
      sum.appendChild(tr);
      root.appendChild(sum);

      var box=el("div","max-width:460px;margin:0 auto;text-align:left;");
      var fName=field(L.fullName,"text","Jonas Jonaitis"), fEmail=field(L.email,"email","you@example.com"), fPhone=field(L.phone,"tel","+370 …");
      box.appendChild(el("div","font-family:"+FONT+";font-size:15px;font-weight:700;color:"+INK+";margin-bottom:12px;",{text:L.guest}));
      box.appendChild(fName); box.appendChild(fPhone); box.appendChild(fEmail);

      // payment
      box.appendChild(el("div","font-family:"+FONT+";font-size:15px;font-weight:700;color:"+INK+";margin:18px 0 8px;",{text:L.payment}));
      box.appendChild(el("div","font-family:"+FONT+";font-size:14px;color:"+INK+";border:1px solid "+CORAL+";border-radius:8px;padding:12px 14px;",{text:"◉  "+L.payVenue}));
      box.appendChild(el("div","font-family:"+FONT+";font-size:12px;color:"+MUTED+";margin:8px 0 4px;",{text:L.cancelNote}));
      box.appendChild(el("div","font-family:"+FONT+";font-size:12px;color:"+MUTED+";background:#241d0c;border-radius:8px;padding:8px 12px;margin:8px 0 4px;",{text:L.promoNote}));

      // venue policies (collapsible)
      var polWrap=el("div","border:1px solid "+BORDER+";border-radius:8px;margin:14px 0;overflow:hidden;");
      var polBody=el("div","font-family:"+FONT+";font-size:13px;color:"+MUTED+";line-height:1.6;padding:0 14px;max-height:0;overflow:hidden;transition:max-height .2s ease,padding .2s ease;");
      polBody.appendChild(el("p","margin:0 0 8px;",{text:L.pol1}));
      polBody.appendChild(el("p","margin:0 0 12px;",{text:L.pol2}));
      var polHead=el("button","width:100%;display:flex;justify-content:space-between;align-items:center;background:"+CARD+";border:none;padding:14px;cursor:pointer;font-family:"+FONT+";font-size:15px;font-weight:700;color:"+INK+";",{});
      polHead.appendChild(el("span","",{text:L.venuePolicies})); var caret=el("span","color:"+MUTED+";",{text:"▾"});
      polHead.appendChild(caret);
      polHead.addEventListener("click",function(){ var open=polBody.style.maxHeight&&polBody.style.maxHeight!=="0px"; polBody.style.maxHeight=open?"0":"200px"; polBody.style.padding=open?"0 14px":"4px 14px 12px"; caret.textContent=open?"▾":"▴"; });
      polWrap.appendChild(polHead); polWrap.appendChild(polBody); box.appendChild(polWrap);

      // consent
      box.appendChild(check(L.consent1));
      box.appendChild(check(L.consent2));

      var err=el("p","font-family:"+FONT+";color:"+CORAL+";font-size:14px;margin:6px 0;display:none;"); box.appendChild(err);
      var confirm=el("button",BTN+"width:100%;margin-top:8px;",{text:L.complete}); box.appendChild(confirm);
      box.appendChild(el("p","font-family:"+FONT+";font-size:12px;color:"+MUTED+";text-align:center;margin:12px 0 0;",{text:L.terms}));
      box.appendChild(back("time"));
      root.appendChild(box);

      confirm.addEventListener("click",function(){
        var name=fName._input.value.trim(), phone=fPhone._input.value.trim(), email=fEmail._input.value.trim();
        err.style.display="none";
        if(!name||!phone){ err.textContent=L.errName; err.style.display="block"; return; }
        confirm.disabled=true; confirm.textContent=L.booking;
        post("create_basket_booking",{customer_name:name,phone:phone,email:email,services:JSON.stringify(names()),
          date:state.date,start_time:state.slot.time,barber:state.pro||state.slot.barber||""}).then(function(res){
          if(res&&res.success){ state.result=res; saveBasket([]); state.step="done"; render(); }
          else { err.textContent=(res&&res.error)||L.errGeneric; err.style.display="block"; confirm.disabled=false; confirm.textContent=L.complete; }
        }).catch(function(){ err.textContent=L.errNet; err.style.display="block"; confirm.disabled=false; confirm.textContent=L.complete; });
      });
    }
    function proName(nm){ var b=DATA.barbers.filter(function(x){return x.name===nm;})[0]; return b?b.barber_name:nm; }

    // ---------- DONE ----------
    function renderDone(){
      var r=state.result||{};
      var w=el("div","text-align:center;padding:12px 0;");
      w.appendChild(el("div","width:64px;height:64px;border-radius:50%;background:"+ALT+";color:"+CORAL+";display:flex;align-items:center;justify-content:center;font-size:32px;margin:0 auto 16px;",{text:"✓"}));
      w.appendChild(el("h3","font-family:"+FONT+";font-size:24px;color:"+INK+";font-weight:700;margin:0 0 8px;",{text:L.booked}));
      var dt=parseISO(state.date);
      w.appendChild(el("p","font-family:"+FONT+";font-size:15px;color:"+INK+";margin:0 0 4px;",{text:(r.start_time||"")+" · "+DOW[dt.getDay()]+" "+dt.getDate()+" "+MONTHS[dt.getMonth()]}));
      w.appendChild(el("p","font-family:"+FONT+";font-size:15px;color:"+MUTED+";margin:0 0 4px;",{text:L.withw+proName(r.barber||"")}));
      w.appendChild(el("p","font-family:"+FONT+";font-size:13px;color:"+MUTED+";margin:8px 0 0;",{text:L.reference+" "+((r.appointments||[]).join(", "))+" · "+L.payVenue}));
      w.appendChild(el("button",GHOST+"margin-top:20px;",{text:L.bookAnother,on:{click:function(){ state=Object.assign(state,{step:"basket",pro:"",date:null,slot:null,showPicker:false,result:null}); render(); }}}));
      root.appendChild(w);
    }

    function render(){
      clear(root);
      // the time step uses the full widened card (two panels); the rest read
      // better as a single centred column
      root.style.marginLeft="auto"; root.style.marginRight="auto";
      root.style.maxWidth=(state.step==="time")?"none":"600px";
      if(state.step==="basket") renderBasket();
      else if(state.step==="time") renderTime();
      else if(state.step==="checkout") renderCheckout();
      else if(state.step==="done") renderDone();
    }

    root.innerHTML='<p style="font-family:'+FONT+';color:'+MUTED+';text-align:center">'+L.loadingBooking+'</p>';
    get(API+"get_booking_data?lang="+LANG).then(function(d){ DATA.cats=(d&&d.service_categories)||[]; DATA.barbers=(d&&d.barbers)||[];
      if(loadBasket().length && /[?&]choose=1/.test(location.search)) state.step="time";
      render(); })
      .catch(function(){ root.innerHTML='<p style="font-family:'+FONT+';color:'+CORAL+';text-align:center">'+L.errBooking+'</p>'; });
  });
})();
