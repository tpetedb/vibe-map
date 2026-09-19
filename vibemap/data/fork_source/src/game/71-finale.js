// Dates and pairings come from config/camp.toml through the build (CONFIG); the
// wine-night theme keeps the original beverage stack.
const DATES=CONFIG.dates;
const WINES=CONFIG.theme.id==="wine-night"?["Bourgogne Chardonnay, the arrogant one","Sancerre, chalky, unresolved finish","Barolo, decanted, bureaucratic tannins","Grower Champagne, zero dosage","Whatever Hospitality Operations decants"]:(CONFIG.theme.pairings.length?CONFIG.theme.pairings:["Water, still","Water, sparkling"]);
// The finale starts at the same hour whatever the date. The last entry of the
// list is an escape hatch rather than a date, and a date is the entry that
// carries a number, so the time is only added where it means something.
const FINALE_START="18:00";
const isFinaleDate=d=>/\d/.test(d);
const dateLabel=d=>isFinaleDate(d)?d+", from "+FINALE_START:d;
const countOf=(n,one,many)=>n+" "+(n===1?one:many);
// Config text carries whatever the camp wrote, apostrophes and angle brackets
// included, so an option is an element with its handler bound, never an inline
// onclick built out of that text.
function finaleOptions(host,cls,items,label,pick,current){const el=$(host);el.innerHTML="";
  items.forEach(v=>{const b=document.createElement("button");b.className=cls+(v===current?" pick":"");b.textContent=label(v);b.onclick=()=>pick(v);el.appendChild(b)})}
function renderFinale(){
  finaleOptions("dates","date",DATES,dateLabel,pickDate,S.date);
  finaleOptions("wines","wine",WINES,w=>w,pickWine,S.wine);
  renderMsg()}
window.pickDate=function(d){S.date=d;save();renderFinale()};window.pickWine=function(w){S.wine=w;save();renderFinale()};
function renderMsg(){if(!S.date||!S.wine){$("msgcard").style.display="none";return}
  const wine=CONFIG.theme.pairing==="wine";
  const bev=wine?`Beverage stack, per Hospitality Operations: ${S.wine}, served at the sommelier-mandated temperature.`:`Refreshments: ${S.wine}.`;
  const when=isFinaleDate(S.date)?`${S.date}, ${FINALE_START}`:S.date;
  const m=`Hi Tom, per my last message and the ratified roadmap, confirming go-live: ${when}, at the Hospitality Hub. ${bev} Current state of the campus: ${S.done.length} of 8 stops delivered, ${countOf(S.versions.length,"tagged release","tagged releases")} and ${countOf(Object.values(S.bridges).filter(Boolean).length,"live integration","live integrations")}. Please loop in Rolinda, she will have questions, and they will be the only good ones.${wine?" Please also confirm she has decanted.":""}\n\nBest,\n${S.name}\nChief of Staff`;
  $("msg").textContent=m;$("wa").href="https://wa.me/?text="+encodeURIComponent(m);$("msgcard").style.display=""}
window.copyMsg=function(){copyText($("msg").textContent,$("copybtn"),"Copy to clipboard",$("msg"))};
// Read-only seam for the tests: the dates and pairings this camp configured.
window.__finale=()=>({dates:DATES,pairings:WINES,pairing:CONFIG.theme.pairing});
