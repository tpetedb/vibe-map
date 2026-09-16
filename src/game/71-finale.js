// Dates and pairings come from vibe.toml through the build (CONFIG); the
// wine-night theme keeps the original beverage stack.
const DATES=CONFIG.dates;
const WINES=CONFIG.theme.id==="wine-night"?["Bourgogne Chardonnay, the arrogant one","Sancerre, chalky, unresolved finish","Barolo, decanted, bureaucratic tannins","Grower Champagne, zero dosage","Whatever Hospitality Operations decants"]:(CONFIG.theme.pairings.length?CONFIG.theme.pairings:["Water, still","Water, sparkling"]);
function renderFinale(){$("dates").innerHTML=DATES.map(d=>`<button class="date${S.date===d?' pick':''}" onclick="pickDate('${d}')">${d}, from 18:00</button>`).join("");$("wines").innerHTML=WINES.map(w=>`<button class="wine${S.wine===w?' pick':''}" onclick="pickWine('${w}')">${w}</button>`).join("");renderMsg()}
window.pickDate=function(d){S.date=d;save();renderFinale()};window.pickWine=function(w){S.wine=w;save();renderFinale()};
function renderMsg(){if(!S.date||!S.wine){$("msgcard").style.display="none";return}const c=S.mascot?S.mascot.name:"an unnamed agent";
  const bev=CONFIG.theme.pairing==="wine"?`Beverage stack, per Hospitality Operations: ${S.wine}, served at the sommelier-mandated temperature.`:`Refreshments: ${S.wine}.`;
  const m=`Hi Tom, per my last message and the ratified roadmap, confirming go-live: ${S.date}, 18:00, at the Hospitality Hub. ${bev} Current state of the campus: one ${c}, ${S.rolls.length} rows in the data warehouse, ${S.versions.length} tagged releases and ${Object.values(S.bridges).filter(Boolean).length} live integrations. Please loop in Rolinda, she will have questions, and they will be the only good ones. Please also confirm she has decanted.\n\nBest,\n${S.name}\nChief of Staff`;
  $("msg").textContent=m;$("wa").href="https://wa.me/?text="+encodeURIComponent(m);$("msgcard").style.display=""}
window.copyMsg=function(){const m=$("msg").textContent;const ok=()=>{$("copybtn").textContent="Copied";setTimeout(()=>$("copybtn").textContent="Copy to clipboard",1500)};if(navigator.clipboard&&navigator.clipboard.writeText)navigator.clipboard.writeText(m).then(ok).catch(()=>{})};
