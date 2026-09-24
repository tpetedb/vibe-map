// Text that is not ours goes into the page through here: the feed, an answer
// from the bridge, an imported name. One helper, early, so every module can
// reach it; the page is built from strings, so escaping is the rule and raw
// interpolation is the exception that has to be one of our own constants.
function esc(s){return String(s==null?"":s).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]))}
// A link from data we did not write. Only an absolute http or https URL may
// become an anchor; javascript:, data: and anything else give "" and the row
// is rendered without a link rather than with a dangerous one.
function safeUrl(u){const s=String(u==null?"":u).trim();if(!/^https?:\/\//i.test(s))return "";
  // A name and a password in front of the host is how a link to one site is
  // made to read like another, so such a link is no link either.
  try{const p=new URL(s);return (p.protocol==="http:"||p.protocol==="https:")&&!p.username&&!p.password?p.href:""}catch(e){return ""}}
// A plain object, which is what JSON calls a map: not null, not a list.
function isMap(o){return !!o&&typeof o==="object"&&!Array.isArray(o)}
// An identifier from data we did not write (a progress code): a short word of
// letters, digits, dot, dash, underscore and colon, which is every id the
// course data uses. Anything else is not an id, whatever it claims to be.
function plainId(v){return typeof v==="string"&&/^[A-Za-z0-9][A-Za-z0-9_.:-]{0,63}$/.test(v)}
// A document published beside the game on the product's site. The site has
// syllabus.html next to the game; a camp, a fork and file:// do not, so
// anywhere but that site the link goes to the product rather than to a 404.
// base is the folder the page is in, and is a parameter so it can be checked.
// The site comes from config/camp.toml and becomes an href, so it is a link
// like any other: not http or https means there is no site.
function siteDoc(name,base){const site=safeUrl(typeof CONFIG!=="undefined"?CONFIG.site:"").replace(/\/*$/,"/").replace(/^\/$/,"");
  const here=base===undefined?location.origin+location.pathname.replace(/[^/]*$/,""):base;
  return !site?name:(here===site?name:site+name)}
// One copy helper for every Copy button, early so every module can reach it.
// A refused clipboard is not silence: the text is selected so it can be copied
// by hand, and the button says so. srcEl is the element holding the text, so
// the fallback can select it; msg is what a copy that worked should say.
// The button is the visible confirmation and #copysay is the spoken one, so a
// screen reader hears the same words a sighted player reads.
// navigator.clipboard.writeText has to be called inside the click handler
// (MDN, Clipboard: writeText), which is why the text is resolved by the caller.
function copyKey(){return /Mac|iPhone|iPad|iPod/.test(navigator.platform||navigator.userAgent||"")?"Cmd C":"Ctrl C"}
function copySay(msg){const el=document.getElementById("copysay");if(el)el.textContent=msg}
function copyText(text,btn,label,srcEl,msg){
  const done=m=>{btn.textContent=m;copySay(m);setTimeout(()=>{btn.textContent=label},2500)};
  const fallback=()=>{if(srcEl&&window.getSelection){const r=document.createRange();r.selectNodeContents(srcEl);
      const sel=getSelection();sel.removeAllRanges();sel.addRange(r)}
    done("Selected, press "+copyKey())};
  if(navigator.clipboard&&navigator.clipboard.writeText)
    navigator.clipboard.writeText(text).then(()=>done(msg||"Copied"),fallback);
  else fallback()}
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
  walk:["rolinda","Chardonnay is poured, 11 degrees, arrogant on the cheek, galloping nicely against the uvula. Walk to the {stop1} signpost before it warms up."],
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
  walk:["rolinda","Coffee is poured. Walk to the {stop1} signpost; the first stop is the one where you build something."],
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
// SAY is the campus voice. An island that is not the campus has no hub and no
// date to pick, and production ends the campaign, so their closing lines and
// their walk line are overrides on the same keys.
const SAY_WORLD={
  winter:{fin:["rolinda","Every stop on this island is done. The next environment is one bridge away; take it when you are ready."]},
  desert:{fin:["rolinda","Every stop on this island is done. One environment left, and it is the one you cannot break gently."]},
  prod:{fin:["rolinda","Every stop on production is done, which is the whole campaign. Nothing left to deploy tonight; go and tell somebody what you built."]}
};
// The one place a line is chosen: the island's override, else the campus line,
// with the first signpost of this island filled in.
function line(k){const w=SAY_WORLD[S.world||"campus"];const l=(w&&w[k])||SAY[k];
  return [l[0],l[1].replace("{stop1}",CH[0]?CH[0].h:"first")]}
// The name stays empty until the player types one: the placeholder is a
// placeholder, never state. playerLabel() is what the UI shows meanwhile.
// One helper, so a saved record and an imported code agree on it: NAME_SLOT
// is the same text an unnamed camp exports and the onboarding prints.
function cleanName(n){const s=String(n==null?"":n).trim().slice(0,80);return s===NAME_SLOT?"":s}
// topics: the tech tree ids the terminal has verified. The game shows the tree
// but never marks it, so this is the terminal's record travelling with the
// progress code: it must survive a round trip through here untouched.
// hints: the ids of the first-time lines already shown. notes: what the toasts
// said, kept because a message that mattered outlives its five seconds.
let S={name:"",done:[],doneW:{campus:[],winter:[],desert:[],prod:[]},path:{},met:{},mentors:[],pitch:"",versions:[],bridges:{},date:null,wine:null,artifacts:[],artifactsBuilt:[],events:[],interests:null,topics:[],pet:"",hints:[],notes:[]};
// Progress lives under "vibemap1"; the pre-rename key "grimoire3" is read once so nobody loses an evening.
const KEY="vibemap1",OLD_KEY="grimoire3";
// S.done is a view: the array doneW[world] under another name. Only the map is
// written, so a reload can never copy one island's stops onto another.
// The mark that says it happened is the view of this write, so it is raised
// only once the record is really in the browser, and never when it is not.
// mark is false for a write the player did not ask for (the log of a message
// that was just shown), so "Saved" stays a word about progress.
function save(mark){let written=false;
  try{const d=Object.assign({},S);delete d.done;localStorage.setItem(KEY,JSON.stringify(d));written=true}catch(e){}
  if(written&&mark!==false&&typeof savedTick==="function")savedTick()}
// The record is JSON in the player's own browser, and a browser is not a
// vault: a half-written save, another tab or an extension can leave anything
// under the key. Every field is checked before it becomes state, so a record
// that is wrong costs the fields it broke and never the evening. loadFault
// names the first field that had to be repaired, for the player and a test.
let loadFault="";
function load(){
  let raw=null;try{raw=localStorage.getItem(KEY)||localStorage.getItem(OLD_KEY)}catch(e){}
  let d=null;if(raw){try{d=JSON.parse(raw)}catch(e){}}
  loadFault="";const bad=k=>{if(!loadFault)loadFault=k};
  if(!isMap(d)){if(raw)bad("the record");S.done=S.doneW.campus;reportLoad();return false}
  S=Object.assign(S,d);delete S.done;S.name=cleanName(S.name);
  if(!isMap(S.doneW)){S.doneW={};if(d.doneW!==undefined)bad("doneW")}
  // An island this game does not have cannot hold stops, and an island it has
  // holds a list of stop numbers: S.done is one of those lists, so anything
  // else here is a blank page one frame later.
  Object.keys(S.doneW).forEach(w=>{if(!CAMPAIGN[w]){delete S.doneW[w];bad("doneW")}
    else if(!Array.isArray(S.doneW[w])){S.doneW[w]=[];bad("doneW")}
    else{const stops=S.doneW[w].filter(n=>typeof n==="number");
      if(stops.length!==S.doneW[w].length)bad("doneW");S.doneW[w]=stops}});
  Object.keys(CAMPAIGN).forEach(w=>{if(!S.doneW[w])S.doneW[w]=[]});
  if(!d.doneW&&Array.isArray(d.done)&&d.done.length)S.doneW.campus=d.done.filter(n=>typeof n==="number");
  // The island the player stands on has to be one this game builds.
  if(S.world&&!CAMPAIGN[S.world]){S.world="campus";bad("world")}
  if(!isMap(S.path)){S.path={};if(d.path!==undefined)bad("path")}
  if(!isMap(S.met)){S.met={};if(d.met!==undefined)bad("met")}
  ["mentors","artifacts","artifactsBuilt","events","hints","notes"].forEach(k=>{
    if(!Array.isArray(S[k])){S[k]=[];if(d[k]!==undefined)bad(k)}});
  // Two lists of our own shapes. A hint id is a short word of ours, and one
  // that is anything else would show an old line again or swallow a new one;
  // a note is what a toast said, a time and two strings, and all three are
  // written back into the panel. Either way the record loses the entries it
  // broke and keeps the rest.
  const only=(k,ok)=>{const v=S[k].filter(ok);if(v.length!==S[k].length)bad(k);S[k]=v};
  only("hints",plainId);
  only("notes",n=>isMap(n)&&typeof n.ts==="number"&&isFinite(n.ts)&&typeof n.t==="string"&&typeof n.b==="string");
  S.notes=S.notes.slice(-NOTE_CAP);
  if(!Array.isArray(S.interests))S.interests=null;
  S.done=S.doneW[S.world||"campus"];reportLoad();return true}
// A record that could not be read whole is not silence: the player is told
// which part started fresh, and the evening runs on everything else.
function reportLoad(){if(loadFault&&typeof toast==="function")
  toast("Saved progress repaired","Part of the record in this browser could not be read ("+esc(loadFault)+"), so that part starts fresh.")}
/* ---------------- the event log ---------------- */
// One shape for the game and for the CLI: {ts, kind, id, world}, plus v for a
// number of seconds when the event measures time. The log is local to this
// browser and never travels in the progress code, so an import merges none of
// it. track() is the only way in; the dashboard derives every number from it.
const EVENT_CAP=600;
function track(kind,id,v){
  if(!Array.isArray(S.events))S.events=[];
  const e={ts:Date.now(),kind:String(kind),id:id==null?"":String(id),world:S.world||"campus"};
  if(typeof v==="number"&&isFinite(v))e.v=Math.round(v);
  S.events.push(e);compactEvents();save();return e}
// Over the cap the minute ticks of a day collapse into one event carrying
// their seconds, so a long evening loses its ticks and keeps its shape;
// only then does the oldest event fall off the front.
function compactEvents(){
  if(S.events.length<=EVENT_CAP)return;
  const day=ts=>new Date(ts).toISOString().slice(0,10),ticks={},kept=[];
  S.events.forEach(e=>{if(e.kind!=="play"){kept.push(e);return}
    const k=day(e.ts);if(ticks[k]){ticks[k].v+=(e.v||60);return}
    ticks[k]={ts:e.ts,kind:"play",id:"day",world:e.world,v:e.v||60};kept.push(ticks[k])});
  S.events=kept.slice(-EVENT_CAP)}
// Other modules (chat, the avatar) record through this one helper.
window.track=track;
/* ---------------- the page, awake and asleep ---------------- */
// Time in another app is not time on the island. The browser already stops the
// frame loop while the page is hidden (MDN, requestAnimationFrame), but the
// clock those frames read keeps running on the wall clock, and the ambient
// animations read it as an absolute phase: the boats, the birds and the beam
// would jump by the whole gap on the way back. So the clock stops where the
// last drawn frame left it and starts again from there, which is also what
// keeps the first frame after a return from being an hour of movement.
// Battery saver off is the player asking for the opposite, so nothing pauses.
let hiddenAt=0,hiddenT=0;
const hasClock=()=>typeof clock!=="undefined"&&!!clock;
function saverOn(){return typeof settings!=="function"||settings().saver!=="off"}
function pageHidden(){if(hiddenAt||!saverOn())return;hiddenAt=Date.now();
  if(!hasClock()||!clock.running)return;
  // start() zeroes the elapsed time, so the clock is restarted by hand rather
  // than left to autoStart, which would call it on the next frame.
  hiddenT=clock.elapsedTime;clock.autoStart=false;clock.stop()}
function pageVisible(){if(!hiddenAt)return;hiddenAt=0;
  if(!hasClock()||clock.running)return;
  clock.start();clock.elapsedTime=hiddenT;clock.autoStart=true}
// One listener, wired in 90-boot.js: the page is what is hidden, so the page's
// own event is what answers for it.
function onVisibility(){if(document.hidden)pageHidden();else pageVisible()}
// Test seam: whether the island is paused, and the clock it is paused at.
window.__awake=()=>({hidden:!!hiddenAt,saver:saverOn(),t:hasClock()&&clock.running?clock.elapsedTime:hiddenT});
const $=id=>document.getElementById(id);
// Progressive enhancement: with Motion embedded (src/vendor/motion.min.js) panels
// spring in and KPIs count up; without it, or under reduced motion, they just
// appear. Springs are stiff so nothing takes longer than about 400 ms.
// Asked several times a frame, so the media query is made once and read live.
const REDUCED=matchMedia("(prefers-reduced-motion: reduce)");
const reducedMotion=()=>REDUCED.matches||(typeof motionOff==="function"&&motionOff());
// How the hosts are named wherever they are named: the role is the theme's.
const roleName=who=>who==="tom"?"Tom, "+CONFIG.theme.hostRole:"Rolinda, "+CONFIG.theme.guideRole;
function fx(el){if(!window.Motion||reducedMotion())return;Motion.animate(el,{opacity:[0,1],transform:["translateY(16px)","translateY(0px)"]},{type:"spring",stiffness:420,damping:34,mass:.8})}
function countUp(el,to,fmt){if(!window.Motion||reducedMotion()){el.textContent=fmt(to);return}const from=parseFloat(el.textContent)||0;if(from===to){el.textContent=fmt(to);return}Motion.animate(from,to,{duration:.4,ease:"easeOut",onUpdate:v=>{el.textContent=fmt(v)}})}

/* ---------------- faces for bubble (2D) ---------------- */
const FACE={
 tom:`<svg viewBox="0 0 40 40"><rect x="6" y="6" width="28" height="28" rx="6" fill="#F5D7BC"/><rect x="4" y="4" width="32" height="10" rx="4" fill="#1F2A44"/><rect x="2" y="12" width="36" height="4" rx="2" fill="#E8E8E8"/><rect x="4" y="16" width="5" height="12" fill="#6B4A2B"/><rect x="31" y="16" width="5" height="12" fill="#6B4A2B"/><rect x="11" y="21" width="5" height="2" fill="#333"/><circle cx="26" cy="22" r="2" fill="#333"/><rect x="15" y="27" width="10" height="2.5" rx="1" fill="#6B4A2B"/></svg>`,
 rolinda:`<svg viewBox="0 0 40 40"><rect x="8" y="10" width="24" height="24" rx="6" fill="#F5D7BC"/>${[[8,8],[14,4],[20,3],[26,4],[32,8],[6,15],[34,15]].map(p=>`<circle cx="${p[0]}" cy="${p[1]}" r="5" fill="#F2CF6F"/>`).join("")}<circle cx="15" cy="22" r="2" fill="#333"/><circle cx="25" cy="22" r="2" fill="#333"/><path d="M15 28 Q20 32 25 28" stroke="#B0534B" stroke-width="2" fill="none"/></svg>`
};
// Rolinda types (20 ms a character, 1.2 s at most); Tom is instant. Off under reduced motion.
function typeOut(el,text){el.setAttribute("aria-label",text);if(reducedMotion()){el.textContent=text;return}const step=Math.min(20,1200/Math.max(1,text.length));let i=0;el.textContent="";clearInterval(el._tw);el._tw=setInterval(()=>{el.textContent=text.slice(0,++i);if(i>=text.length)clearInterval(el._tw)},step)}
// Every line in the bubble goes through here: the face, the role the theme
// gives the speaker, and the running type-out that a new line must cancel.
function bubble(who,t){$("bub-face").innerHTML=FACE[who];$("bub-who").textContent=roleName(who);
  if(who==="rolinda")typeOut($("bub-text"),t);else{clearInterval($("bub-text")._tw);$("bub-text").setAttribute("aria-label",t);$("bub-text").textContent=t}}
function say(k){const [who,t]=line(k);bubble(who,t)}
// A mentor is known by their last name; a team is not a person, so a name that
// starts with "The" keeps all of it.
function shortName(n){return /^The\s/.test(n)?n.charAt(0).toLowerCase()+n.slice(1):n.split(" ").slice(-1)[0]}
// The stops of the island the player is on. CH is the island's ws, so a camp
// that adds a ninth stop has nine, and the stop after the last one is the
// finale on the campus and the end of the island everywhere else.
function stopCount(){return CH.length}
function finaleStop(){return CH.length+1}
// The KPI says Streak, so the number is the one the CLI counts under that
// name (vibemap/quests.py, badge streak-3): stops claimed today.
function streakToday(){const day=new Date().toDateString();
  return (S.events||[]).filter(e=>e.kind==="claim"&&new Date(e.ts).toDateString()===day).length}

/* ---------------- 3D ---------------- */
