const T=THREE;
let CH=[
  {h:"18:00",n:"Innovation Hub",d:"Ship an MVP before the first glass is empty"},
  {h:"19:00",n:"Centre of Excellence",d:"Well-scoped asks, and your first playbook"},
  {h:"20:00",n:"Data Warehouse",d:"Persisted scores and a dashboard"},
  {h:"21:00",n:"Business Continuity Tower",d:"Git, rollback, and one automated control"},
  {h:"21:30",n:"Stakeholder Alignment Bridge",d:"Connectors and MCP"},
  {h:"22:00",n:"Knowledge Management Tree",d:"Obsidian and the graph"},
  {h:"22:30",n:"Go-to-Market Tower",d:"GitHub and GitHub Pages: a real URL"},
  {h:"23:00",n:"Autonomous Operations Plant",d:"Headless Claude on a schedule, and a subagent"},
];
// Two voices for the same beats: the wine-night original, and the plain set
// every other theme uses. Rolinda asks the simple question in both.
const SAY_WINE={
  title:["tom","Welcome aboard, and thank you for prioritising this. Confirm your preferred name, then we kick off. I have blocked four hours, one bottle, and a contingency bottle."],
  walk:["rolinda","Chardonnay is poured, 11 degrees, arrogant on the cheek, galloping nicely against the uvula. Walk to the 18:00 signpost before it warms up."],
  near:["rolinda","Go on then. Tap Enter. Swirl first, it needs air, like most of your MVP."],
  1:["tom","Let's not boil the ocean here. Three sentences, press the button, ship it. Zero enablement this hour, that is a feature, not a gap."],
  2:["rolinda","So why did 'more impactful' break it? It did what you said, no? Also this Chardonnay is opening up. Notes of hazelnut and mild regret."],
  3:["rolinda","Where do the numbers live? In the game, or somewhere else? Sancerre is up. Chalky. Try the goat cheese, ash side first."],
  4:["rolinda","What happens if you delete it by accident? Barolo has been breathing for ninety minutes, which is longer than Tom on call."],
  5:["rolinda","Can it see my email now? I want to be clear about this. Grüner in the glass. Peppery. Pairs with everything, apparently including your calendar."],
  7:["rolinda","Can my mother open it on her iPad? Tokaji is poured, five puttonyos, sweet but earned."],
  8:["rolinda","So it works while you sleep? Armagnac. Last orders. I mean it."],
  6:["rolinda","Is that a mind map? I have opened the Champagne. Zero dosage. Do not add cassis, I will notice."],
  9:["tom","Campus is live, error budget intact, and I am officially off call. Pick the date, pick the beverage stack, circulate the message."],
  done:["tom","OKR unlocked. Tremendous synergy. The campus just scaled horizontally. Rolinda is pouring the next pairing, please proceed to the next signpost with your glass."],
  fin:["rolinda","All eight built. Come back to the inn, we still need to pick a date, and I am not decanting for a maybe."]
};
const SAY_PLAIN={
  title:["tom","Welcome. Confirm your name and we start. Four hours are blocked, the coffee is on, and nothing on this island can break in a way we cannot undo."],
  walk:["rolinda","Coffee is poured. Walk to the 18:00 signpost; the first stop is the one where you build something."],
  near:["rolinda","Go on, tap Enter. Read the definition of done first, then do the thing, then tell me in one sentence what happened."],
  1:["tom","Three sentences, one file, ship it. We fix the loop before we fix the game."],
  2:["rolinda","So why did 'more impactful' break it? It did what you said, no? Write that down; that is the whole lesson."],
  3:["rolinda","Where do the numbers live? In the game, or somewhere you can query? Second coffee, by the way."],
  4:["rolinda","What happens if you delete it by accident? Show me the way back before you show me the way forward."],
  5:["rolinda","Can it see my email now? I want to be clear about this before I say yes."],
  6:["rolinda","Is that a mind map? Click a node and read me what it says, in your own words."],
  7:["rolinda","Can my mother open it on her iPad? A link is not a link until someone else opens it."],
  8:["rolinda","So it works while you sleep? Then show me what it did this morning."],
  9:["tom","Campus is live and I am off call. Pick the date, pick what we drink, circulate the message."],
  done:["tom","OKR unlocked. Next signpost. Bring the coffee."],
  fin:["rolinda","All eight built. Come back to the hub; we still need a date, and I want it in writing."]
};
const SAY=CONFIG.theme.pairing==="wine"?SAY_WINE:SAY_PLAIN;
let S={name:"<your_name>",done:[],doneW:{campus:[],winter:[],desert:[],prod:[]},path:{},rolls:[],versions:[],bridges:{},date:null,wine:null,mascot:null,artifacts:[]};
// Progress lives under "vibemap1"; the pre-rename key "grimoire3" is read once so nobody loses an evening.
const KEY="vibemap1",OLD_KEY="grimoire3";
function save(){try{localStorage.setItem(KEY,JSON.stringify(S))}catch(e){}}
function load(){try{const r=localStorage.getItem(KEY)||localStorage.getItem(OLD_KEY);if(r){const d=JSON.parse(r);S=Object.assign(S,d);if(!S.doneW)S.doneW={campus:[],winter:[],desert:[],prod:[]};if(!S.doneW.campus.length&&Array.isArray(d.done)&&d.done.length)S.doneW.campus=d.done.slice();if(!S.path)S.path={};if(!Array.isArray(S.artifacts))S.artifacts=[];S.done=S.doneW[S.world||"campus"];return true}}catch(e){}S.done=S.doneW.campus;return false}
const $=id=>document.getElementById(id);
// Progressive enhancement: with Motion embedded (src/vendor/motion.min.js) panels
// spring in and KPIs count up; without it, or under reduced motion, they just
// appear. Springs are stiff so nothing takes longer than about 400 ms.
const reducedMotion=()=>matchMedia("(prefers-reduced-motion: reduce)").matches||(typeof motionOff==="function"&&motionOff());
function fx(el){if(!window.Motion||reducedMotion())return;Motion.animate(el,{opacity:[0,1],transform:["translateY(16px)","translateY(0px)"]},{type:"spring",stiffness:420,damping:34,mass:.8})}
function countUp(el,to,fmt){if(!window.Motion||reducedMotion()){el.textContent=fmt(to);return}const from=parseFloat(el.textContent)||0;if(from===to){el.textContent=fmt(to);return}Motion.animate(from,to,{duration:.4,ease:"easeOut",onUpdate:v=>{el.textContent=fmt(v)}})}

/* ---------------- faces for bubble (2D) ---------------- */
const FACE={
 tom:`<svg viewBox="0 0 40 40"><rect x="6" y="6" width="28" height="28" rx="6" fill="#F5D7BC"/><rect x="4" y="4" width="32" height="10" rx="4" fill="#1F2A44"/><rect x="2" y="12" width="36" height="4" rx="2" fill="#E8E8E8"/><rect x="4" y="16" width="5" height="12" fill="#6B4A2B"/><rect x="31" y="16" width="5" height="12" fill="#6B4A2B"/><rect x="11" y="21" width="5" height="2" fill="#333"/><circle cx="26" cy="22" r="2" fill="#333"/><rect x="15" y="27" width="10" height="2.5" rx="1" fill="#6B4A2B"/></svg>`,
 rolinda:`<svg viewBox="0 0 40 40"><rect x="8" y="10" width="24" height="24" rx="6" fill="#F5D7BC"/>${[[8,8],[14,4],[20,3],[26,4],[32,8],[6,15],[34,15]].map(p=>`<circle cx="${p[0]}" cy="${p[1]}" r="5" fill="#F2CF6F"/>`).join("")}<circle cx="15" cy="22" r="2" fill="#333"/><circle cx="25" cy="22" r="2" fill="#333"/><path d="M15 28 Q20 32 25 28" stroke="#B0534B" stroke-width="2" fill="none"/></svg>`
};
// Rolinda types (20 ms a character, 1.2 s at most); Tom is instant. Off under reduced motion.
function typeOut(el,text){el.setAttribute("aria-label",text);if(matchMedia("(prefers-reduced-motion: reduce)").matches){el.textContent=text;return}const step=Math.min(20,1200/Math.max(1,text.length));let i=0;el.textContent="";clearInterval(el._tw);el._tw=setInterval(()=>{el.textContent=text.slice(0,++i);if(i>=text.length)clearInterval(el._tw)},step)}
function say(k){const [who,t]=SAY[k];$("bub-face").innerHTML=FACE[who];$("bub-who").textContent=who==="tom"?"Tom, "+CONFIG.theme.hostRole:"Rolinda, "+CONFIG.theme.guideRole;if(who==="rolinda")typeOut($("bub-text"),t);else{clearInterval($("bub-text")._tw);$("bub-text").textContent=t}}

/* ---------------- 3D ---------------- */
