/* Blarberine interactive widgets — services category-filter + basket, and the
   team (barber -> their services) widget. Renders into #services-app / #team-app.
   Shares a basket in localStorage that Phase 3 booking will consume. */
(function () {
  "use strict";
  var CORAL="#c4803a", NAVY="#140f0a", INK="#f3ede3", MUTED="#9a8e7c",
      BORDER="#3a2f22", ALT="#221a12", GREEN="#3fbf7a", CARD="#241c14", DARK="#1a140e";
  var API="/api/method/blarberine.blarberine.api.";
  var FONT="'Montserrat', system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif";
  var LANG=/^\/en(\/|$)/.test(location.pathname)?"en":"lt";
  var BOOK=(LANG==="en"?"/en":"/")+"?choose=1#booking";
  var I18N={
    en:{select:"Select",selected:"✓ Selected",add:"+ Add",added:"✓ Added",show:"Show details",all:"All",
        pay:"Pay at venue",edit:"▸ Edit",hide:"▾ Hide",remove:"× Remove",choose:"Choose time",
        service:"service",services:"services",svcOf:"'s services",askStore:"Ask in-store for this barber's full menu.",
        noBarbers:"No barbers yet.",errSvc:"Could not load services.",errTeam:"Could not load team.",
        ckTitle:"We value your privacy",ckText:"We use essential cookies to run the site and, with your consent, analytics cookies to understand how it's used. You can change your choice anytime.",
        ckAll:"Accept all",ckEss:"Essential only"},
    lt:{select:"Pasirinkti",selected:"✓ Pasirinkta",add:"+ Pridėti",added:"✓ Pridėta",show:"Plačiau",all:"Visos",
        pay:"Atsiskaitymas vietoje",edit:"▸ Redaguoti",hide:"▾ Slėpti",remove:"× Pašalinti",choose:"Pasirinkti laiką",
        service:"paslauga",services:"paslaugos",svcOf:" paslaugos",askStore:"Pilno meniu teiraukitės vietoje.",
        noBarbers:"Kirpėjų nėra.",errSvc:"Nepavyko įkelti paslaugų.",errTeam:"Nepavyko įkelti komandos.",
        ckTitle:"Gerbiame jūsų privatumą",ckText:"Naudojame būtinuosius slapukus svetainės veikimui ir, su jūsų sutikimu, analitikos slapukus, kad suprastume, kaip ji naudojama. Pasirinkimą galite keisti bet kada.",
        ckAll:"Priimti visus",ckEss:"Tik būtinuosius"}
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
  function getData(){
    return fetch(API+"get_booking_data?lang="+LANG,{headers:{"X-Frappe-CSRF-Token":csrf()}})
      .then(function(r){return r.json();}).then(function(j){return j.message||{};});
  }

  // ---- basket (shared, persisted) ----
  function loadBasket(){ try{ return JSON.parse(localStorage.getItem("bl_basket"))||[]; }catch(e){ return []; } }
  function saveBasket(b){ try{ localStorage.setItem("bl_basket",JSON.stringify(b)); }catch(e){} }
  function inBasket(name){ return loadBasket().some(function(x){return x.name===name;}); }
  function toggleBasket(svc){
    // one service per booking: selecting a service replaces any previous choice
    var was=inBasket(svc.name);
    saveBasket(was?[]:[{name:svc.name, service_name:svc.service_name, price:svc.price, price_display:svc.price_display}]);
    renderBar(); if(CURRENT_REFRESH) CURRENT_REFRESH(); return inBasket(svc.name);
  }
  function eur(v){ v=v||0; return (v===Math.round(v))?("€"+Math.round(v)):("€"+v.toFixed(2)); }

  var CURRENT_REFRESH=null;  // re-renders the visible widget's list so Select states stay in sync
  function removeFromBasket(name){
    saveBasket(loadBasket().filter(function(x){return x.name!==name;}));
    renderBar(); if(CURRENT_REFRESH) CURRENT_REFRESH();
  }

  var bar=null, barOpen=false;
  function renderBar(){
    // Always rebuild from scratch: reusing a cached node meant a bar that got
    // detached from the DOM (never re-appended because `bar` was still set)
    // would render the selection off-screen until a page refresh.
    if(bar){ bar.remove(); bar=null; }
    var b=loadBasket();
    if(!b.length){ barOpen=false; return; }
    var total=b.reduce(function(s,x){return s+(x.price||0);},0);
    bar=el("div","position:fixed;left:0;right:0;bottom:0;z-index:900;background:"+CARD+";border-top:1px solid "+BORDER+
      ";box-shadow:0 -6px 24px rgba(0,0,0,.5);font-family:"+FONT+";");
    if(barOpen){
      var panel=el("div","max-width:1080px;margin:0 auto;padding:12px 24px 0;");
      b.forEach(function(x){
        var r=el("div","display:flex;justify-content:space-between;align-items:center;gap:12px;padding:10px 0;border-bottom:1px solid "+BORDER+";");
        var l=el("div","display:flex;flex-direction:column;min-width:0;");
        l.appendChild(el("div","font-family:"+FONT+";font-size:15px;color:"+INK+";font-weight:600;",{text:x.service_name}));
        l.appendChild(el("div","font-family:"+FONT+";font-size:13px;color:"+MUTED+";",{text:x.price_display}));
        var rm=el("button","font-family:"+FONT+";background:none;border:none;color:"+MUTED+";font-size:13px;font-weight:600;cursor:pointer;flex-shrink:0;",
          {html:"&times; "+L.remove.replace("× ",""),on:{click:function(){ removeFromBasket(x.name); },
            mouseover:function(e){e.target.style.color=CORAL;}, mouseout:function(e){e.target.style.color=MUTED;}}});
        r.appendChild(l); r.appendChild(rm); panel.appendChild(r);
      });
      bar.appendChild(panel);
    }
    var rowWrap=el("div","max-width:1080px;margin:0 auto;display:flex;align-items:center;justify-content:space-between;gap:16px;padding:14px 24px;");
    var info=el("div","display:flex;flex-direction:column;cursor:pointer;",{on:{click:function(){ barOpen=!barOpen; renderBar(); }}});
    var line1=el("div","display:flex;align-items:center;gap:10px;");
    line1.appendChild(el("span","font-family:"+FONT+";font-size:16px;font-weight:700;color:"+INK+";",
      {text:b.length+" "+(b.length===1?L.service:L.services)+"  ·  "+eur(total)}));
    line1.appendChild(el("span","font-family:"+FONT+";font-size:12px;color:"+CORAL+";font-weight:600;",{text:barOpen?L.hide:L.edit}));
    info.appendChild(line1);
    info.appendChild(el("div","font-family:"+FONT+";font-size:12px;color:"+MUTED+";",{text:L.pay}));
    var go=el("a","font-family:"+FONT+";background:"+CORAL+";color:#1a140e;font-weight:700;font-size:15px;"+
      "padding:12px 28px;border-radius:8px;text-decoration:none;cursor:pointer;flex-shrink:0;",{text:L.choose,href:BOOK});
    rowWrap.appendChild(info); rowWrap.appendChild(go);
    bar.appendChild(rowWrap);
    document.body.appendChild(bar);
  }

  function selectBtn(svc){
    function paint(btn){
      var on=inBasket(svc.name);
      btn.textContent=on?L.selected:L.select;
      btn.style.cssText="font-family:"+FONT+";font-size:14px;font-weight:600;padding:7px 18px;border-radius:8px;"+
        "cursor:pointer;flex-shrink:0;transition:all .12s ease;"+
        (on?("background:#13291c;color:"+GREEN+";border:1px solid "+GREEN+";")
           :("background:"+CARD+";color:"+CORAL+";border:1px solid "+CORAL+";"));
    }
    var btn=el("button"); paint(btn);
    btn.addEventListener("click",function(){ toggleBasket(svc); paint(btn); });
    return btn;
  }

  function serviceRow(svc){
    var left=el("div","display:flex;flex-direction:column;flex-shrink:1;min-width:0;");
    left.appendChild(el("div","font-family:"+FONT+";font-size:16px;color:"+INK+";font-weight:600;",{text:svc.service_name}));
    var meta=el("div","display:flex;gap:8px;align-items:center;margin-top:4px;");
    meta.appendChild(el("span","font-family:"+FONT+";font-size:13px;color:"+MUTED+";",{text:svc.duration_display}));
    meta.appendChild(el("span","font-family:"+FONT+";font-size:13px;color:"+MUTED+";",{text:"·"}));
    meta.appendChild(el("span","font-family:"+FONT+";font-size:13px;color:"+CORAL+";font-weight:500;",{text:L.show}));
    left.appendChild(meta);
    var right=el("div","display:flex;align-items:center;gap:16px;flex-shrink:0;");
    right.appendChild(el("div","font-family:"+FONT+";font-size:16px;color:"+INK+";font-weight:700;",{text:svc.price_display}));
    right.appendChild(selectBtn(svc));
    var row=el("div","display:flex;justify-content:space-between;align-items:center;gap:16px;width:100%;"+
      "padding:16px 0;border-bottom:1px solid "+BORDER+";");
    row.appendChild(left); row.appendChild(right);
    return row;
  }

  // ---- Services page ----
  function renderServices(app, cats){
    clear(app);
    var active=L.all;
    var chipRow=el("div","display:flex;flex-wrap:wrap;gap:10px;margin-bottom:26px;");
    var list=el("div","display:flex;flex-direction:column;");
    function drawChips(){
      clear(chipRow);
      [L.all].concat(cats.map(function(c){return c.category_name;})).forEach(function(label){
        var on=(label===active);
        var chip=el("button","font-family:"+FONT+";font-size:14px;font-weight:600;padding:9px 18px;border-radius:999px;"+
          "cursor:pointer;transition:all .12s ease;"+
          (on?("background:"+CORAL+";color:#1a140e;border:1px solid "+CORAL+";")
             :("background:"+CARD+";color:"+INK+";border:1px solid "+BORDER+";")),
          {text:label,on:{click:function(){ active=label; drawChips(); drawList(); }}});
        chipRow.appendChild(chip);
      });
    }
    function drawList(){
      clear(list);
      cats.forEach(function(c){
        if(active!==L.all && c.category_name!==active) return;
        list.appendChild(el("div","font-family:"+FONT+";font-size:19px;color:"+INK+";font-weight:700;margin:18px 0 2px;",{text:c.category_name}));
        (c.services||[]).forEach(function(s){ list.appendChild(serviceRow(s)); });
      });
    }
    drawChips(); drawList();
    CURRENT_REFRESH=drawList;
    app.appendChild(chipRow); app.appendChild(list);
  }

  // ---- Team page ----
  function renderTeam(app, barbers, cats){
    clear(app);
    var svcMap={}, catOf={};
    cats.forEach(function(c){ (c.services||[]).forEach(function(s){ svcMap[s.name]=s; catOf[s.name]=c.category_name; }); });
    if(!barbers.length){ app.appendChild(el("p","font-family:"+FONT+";color:"+MUTED,{text:L.noBarbers})); return; }
    var active=barbers[0];
    // deep link from the nav dropdown: /team?pro=<Barber Name> pre-selects that barber
    try{ var pro=new URLSearchParams(location.search).get("pro");
      if(pro){ var f=barbers.filter(function(b){return b.name===pro;})[0]; if(f) active=f; } }catch(e){}
    var wrap=el("div","display:flex;gap:40px;align-items:flex-start;flex-wrap:wrap;");
    var listCol=el("div","display:flex;flex-direction:column;width:280px;flex-shrink:0;min-width:240px;");
    var panel=el("div","display:flex;flex-direction:column;flex:1;min-width:260px;");
    function drawList(){
      clear(listCol);
      barbers.forEach(function(b){
        var on=(b.name===active.name);
        var item=el("div","display:flex;align-items:center;gap:14px;padding:12px 10px;border-radius:12px;cursor:pointer;"+
          "transition:background .12s ease;border-left:3px solid "+(on?NAVY:"transparent")+";"+(on?"background:"+ALT+";":""),
          {on:{click:function(){ active=b; drawList(); drawPanel(); }}});
        if(b.photo) item.appendChild(el("img","width:44px;height:44px;border-radius:50%;object-fit:cover;flex-shrink:0;",{src:b.photo}));
        item.appendChild(el("div","font-family:"+FONT+";font-size:16px;color:"+INK+";font-weight:600;",{text:b.barber_name}));
        listCol.appendChild(item);
      });
    }
    function drawPanel(){
      clear(panel);
      panel.appendChild(el("h3","font-family:"+FONT+";font-size:22px;color:"+INK+";font-weight:700;margin:0 0 4px;",{text:active.barber_name}));
      if(active.bio) panel.appendChild(el("p","font-family:"+FONT+";font-size:14px;color:"+MUTED+";line-height:1.55;margin:0 0 16px;max-width:520px;",{text:active.bio}));
      var names=active.service_names||[];
      var doneCats={}, chips=el("div","display:flex;flex-wrap:wrap;gap:8px;margin-bottom:20px;");
      names.forEach(function(nm){ var c=catOf[nm]; if(c&&!doneCats[c]){ doneCats[c]=1;
        chips.appendChild(el("span","font-family:"+FONT+";font-size:13px;font-weight:600;color:"+NAVY+";background:"+ALT+";"+
          "padding:6px 14px;border-radius:999px;border:1px solid "+BORDER+";",{text:c})); } });
      if(chips.children.length) panel.appendChild(chips);
      panel.appendChild(el("div","font-family:"+FONT+";font-size:13px;color:"+MUTED+";font-weight:700;letter-spacing:.06em;text-transform:uppercase;margin-bottom:6px;",{text:active.barber_name.split(" ")[0]+L.svcOf}));
      var svcWrap=el("div","display:flex;flex-direction:column;");
      var shown=0;
      names.forEach(function(nm){ var s=svcMap[nm]; if(s){ shown++; svcWrap.appendChild(serviceRow(s)); } });
      if(!shown) svcWrap.appendChild(el("p","font-family:"+FONT+";color:"+MUTED+";font-size:14px;",{text:L.askStore}));
      panel.appendChild(svcWrap);
    }
    drawList(); drawPanel();
    CURRENT_REFRESH=drawPanel;
    wrap.appendChild(listCol); wrap.appendChild(panel);
    app.appendChild(wrap);
  }

  function wireMobileMenu(){
    var burger=document.querySelector(".bl-burger");
    var menu=document.querySelector(".bl-mobile-menu");
    if(!burger || !menu) return;
    burger.addEventListener("click",function(e){
      e.preventDefault();
      var open=(menu.style.display==="flex");
      menu.style.display=open?"none":"flex";
      burger.innerHTML=open?"☰":"✕";
    });
  }

  // ---- GDPR cookie consent + gated analytics ----
  // Analytics (Google Analytics + Microsoft Clarity) load ONLY after the user
  // clicks "Accept all". "Essential only" keeps them off. Choice persists in
  // localStorage, so returning visitors aren't re-prompted and their analytics
  // preference is honoured on every page.
  var GA_ID="G-PQ24G6YJXV", CLARITY_ID="xidoncwq5i", CK_KEY="bl_cookie_consent";
  function loadAnalytics(){
    if(window.__blAnalytics) return; window.__blAnalytics=true;
    var g=document.createElement("script"); g.async=true;
    g.src="https://www.googletagmanager.com/gtag/js?id="+GA_ID;
    document.head.appendChild(g);
    window.dataLayer=window.dataLayer||[];
    function gtag(){ window.dataLayer.push(arguments); }
    window.gtag=gtag; gtag("js",new Date()); gtag("config",GA_ID);
    (function(c,l,a,r,i,t,y){ c[a]=c[a]||function(){(c[a].q=c[a].q||[]).push(arguments)};
      t=l.createElement(r); t.async=1; t.src="https://www.clarity.ms/tag/"+i;
      y=l.getElementsByTagName(r)[0]; y.parentNode.insertBefore(t,y); })(window,document,"clarity","script",CLARITY_ID);
  }
  function ckGet(){ try{ return localStorage.getItem(CK_KEY); }catch(e){ return null; } }
  function ckSet(v){ try{ localStorage.setItem(CK_KEY,v); }catch(e){} }
  function showCookieBanner(){
    if(document.getElementById("bl-cookie")) return;
    var box=el("div","position:fixed;left:20px;bottom:20px;z-index:1000;max-width:410px;width:calc(100% - 40px);"+
      "background:"+CARD+";border:1px solid "+BORDER+";border-radius:14px;box-shadow:0 14px 44px rgba(0,0,0,.55);padding:20px 22px;");
    box.id="bl-cookie";
    box.appendChild(el("div","font-family:"+FONT+";font-size:15px;font-weight:700;color:"+INK+";margin-bottom:8px;",{text:L.ckTitle}));
    box.appendChild(el("div","font-family:"+FONT+";font-size:13px;color:"+MUTED+";line-height:1.55;margin-bottom:16px;",{text:L.ckText}));
    var btns=el("div","display:flex;gap:10px;flex-wrap:wrap;");
    btns.appendChild(el("button","font-family:"+FONT+";flex:1;min-width:130px;background:"+CORAL+";color:#1a140e;font-weight:700;font-size:14px;padding:11px 16px;border:none;border-radius:8px;cursor:pointer;",
      {text:L.ckAll,on:{click:function(){ ckSet("all"); box.remove(); loadAnalytics(); }}}));
    btns.appendChild(el("button","font-family:"+FONT+";flex:1;min-width:130px;background:"+CARD+";color:"+INK+";font-weight:600;font-size:14px;padding:11px 16px;border:1px solid "+BORDER+";border-radius:8px;cursor:pointer;",
      {text:L.ckEss,on:{click:function(){ ckSet("essential"); box.remove(); }}}));
    box.appendChild(btns);
    document.body.appendChild(box);
  }
  function initConsent(){
    var c=ckGet();
    if(c==="all"){ loadAnalytics(); return; }
    if(c==="essential"){ return; }
    showCookieBanner();
  }

  ready(function(){
    initConsent();
    wireMobileMenu();
    var sApp=document.getElementById("services-app");
    var tApp=document.getElementById("team-app");
    if(!sApp && !tApp){ renderBar(); return; }
    getData().then(function(d){
      var cats=d.service_categories||[], barbers=d.barbers||[];
      if(sApp) renderServices(sApp, cats);
      if(tApp) renderTeam(tApp, barbers, cats);
      renderBar();
    }).catch(function(){
      if(sApp) sApp.innerHTML='<p style="font-family:'+FONT+';color:'+CORAL+';text-align:center">'+L.errSvc+'</p>';
      if(tApp) tApp.innerHTML='<p style="font-family:'+FONT+';color:'+CORAL+';text-align:center">'+L.errTeam+'</p>';
    });
  });
})();
