// Settings: dropdowns that change the game without a rebuild. They persist
// in S.settings (the same localStorage record as progress) and apply at once.
// config/camp.toml still sets the defaults for a fresh browser; these override them.
// They belong to this browser and not to the journey: the progress code carries
// the stops, so an import never moves a setting.
const SETTINGS_DEFAULTS={experience:"islands",difficulty:"config",map:"big",vault:"config",live:"config",pairings:"config",shadows:"high",motion:"auto",speed:"normal",zoom:CAM.zoom.start,
  text:"normal",spacing:"normal",contrast:"auto",hand:"right",run:"hold",haptics:"on",saver:"auto",awake:"on",toasts:"all",breaks:"on"};
const SETTINGS_OPTIONS={
  experience:[["islands","Islands: walk the camp"],["galaxy","Galaxy: follow programming history"]],
  difficulty:[["config","From config/camp.toml ("+CONFIG.difficulty+")"],["beginner","Beginner: commands open, lenient"],["easy","Easy: commands open"],["normal","Normal: commands open, real checks"],["hard","Hard: commands folded, strict"],["expert","Expert: folded, tests must pass"],["god","God: folded, just verify must be green"]],
  map:[["compact","Compact (56% of the window)"],["big","Big (84% of the window)"],["tall","Tall (the whole window)"]],
  vault:[["config","From config/camp.toml ("+((CONFIG.vault&&CONFIG.vault.mode)||"full")+")"],["full","Full: every note in the graph"],["grow","Grow: notes unlock as you play"]],
  live:[["config","From config/camp.toml ("+((CONFIG.news&&CONFIG.news.live===false)?"off":"on")+")"],["on","On: what the sources published lately"],["off","Off: nothing from the feeds"]],
  pairings:[["config","From the theme"],["on","Show the pairings"],["off","Hide the pairings"]],
  shadows:[["high","Soft shadows"],["low","Cheap shadows"],["off","No shadows (fastest)"]],
  motion:[["auto","Follow the system setting"],["off","No animations"]],
  speed:[["slow","Stroll"],["normal","Walk"],["fast","Hurry"]],
  text:[["normal","Normal"],["large","Large"],["larger","Larger"]],
  spacing:[["normal","Normal"],["comfortable","Comfortable"]],
  contrast:[["auto","Follow the system setting"],["more","More contrast"],["off","The usual contrast"]],
  hand:[["right","Stick on the left"],["left","Stick on the right"]],
  run:[["hold","Hold to hurry"],["toggle","Tap to hurry"]],
  haptics:[["on","A short buzz"],["off","No buzzing"]],
  saver:[["auto","Pause when you look away"],["off","Keep running"]],
  awake:[["on","Keep the screen awake"],["off","Let the screen dim"]],
  toasts:[["all","Show them"],["quiet","Quiet: none shown"]],
  breaks:[["on","Suggest a break"],["off","No break card"]]
};
const SETTINGS_LABELS={experience:"Experience",difficulty:"Difficulty",map:"Map size",vault:"Vault",live:"Live world",pairings:"Pairings",shadows:"Shadows",motion:"Motion",speed:"Walking speed",
  text:"Text size",spacing:"Line spacing",contrast:"Contrast",hand:"Handedness",run:"Hurrying",haptics:"Buzz",saver:"Battery saver",awake:"Screen",toasts:"Toasts",breaks:"Break card"};
// The rows in the order a player looks for them. A key outside a group has no
// dropdown: zoom is written by the wheel, the pinch and the stage buttons.
const SETTINGS_GROUPS=[
  ["The game",["experience","difficulty","vault","live","pairings"]],
  ["Reading",["text","spacing","contrast"]],
  ["Controls",["hand","speed","run","haptics"]],
  ["The screen",["map","shadows","motion","saver","awake"]],
  ["Interruptions",["toasts","breaks"]]
];
// A row the platform cannot obey is not offered: neither the buzz nor the
// screen wake lock exists everywhere, and iOS has no vibration at all.
const SETTINGS_WHEN={haptics:()=>typeof navigator.vibrate==="function",awake:()=>!!(navigator.wakeLock&&navigator.wakeLock.request)};
function settingShown(k){const f=SETTINGS_WHEN[k];return !f||f()}
function settings(){if(!S.settings)S.settings={};return Object.assign({},SETTINGS_DEFAULTS,S.settings)}
function speedMult(){return {slow:.7,normal:1,fast:1.5}[settings().speed]||1}
function motionOff(){return settings().motion==="off"}
// High contrast raises the token values and nothing else, so black stays the
// brand. The platform's own answer is the default; Settings insists either
// way. Forced colours means the system is already repainting the page, so the
// raised tokens go with it.
function contrastMore(){const c=settings().contrast;if(c!=="auto")return c==="more";
  return matchMedia("(prefers-contrast: more)").matches||matchMedia("(forced-colors: active)").matches}
function applySettings(){const s=settings();
  const st=$("stage");st.classList.remove("map-compact","map-big","map-tall");st.classList.add("map-"+s.map);
  if(typeof renderer!=="undefined"&&renderer){renderer.shadowMap.enabled=s.shadows!=="off";if(typeof dirL!=="undefined"&&dirL){dirL.castShadow=s.shadows!=="off";dirL.shadow.mapSize.set(s.shadows==="high"?CONFIG.shadowMap:1024,s.shadows==="high"?CONFIG.shadowMap:1024);if(dirL.shadow.map){dirL.shadow.map.dispose();dirL.shadow.map=null}}
    fitRenderer()}
  // The zoom is a setting without a dropdown: the wheel, a pinch and the
  // buttons on the stage write it, and the defaults reset it with the rest.
  if(typeof syncZoom==="function")syncZoom();
  const showPair=s.pairings==="config"?CONFIG.theme.showPairings:s.pairings==="on";document.querySelectorAll(".pairing").forEach(el=>el.style.display=showPair?"":"none");
  document.body.classList.toggle("no-motion",s.motion==="off");
  // Reading comfort, handedness and contrast are the stylesheet's business:
  // the body carries the answer and every rule reads it from there.
  document.body.dataset.text=s.text;document.body.dataset.spacing=s.spacing;
  document.body.classList.toggle("hand-left",s.hand==="left");
  document.body.classList.toggle("contrast-more",contrastMore());
  // Quiet suppresses the toast, never the event behind it: the dashboard and
  // the achievements still count what happened.
  document.body.classList.toggle("quiet",s.toasts==="quiet");
  // Off means nothing from the feeds appears and nothing is fetched: the
  // stylesheet hides every element marked live-feed, loadNews checks the same.
  if(typeof liveNews==="function"){document.body.classList.toggle("no-live",!liveNews());if(liveNews())renderNews()}
  if(typeof difficulty==="function"){document.body.dataset.difficulty=difficulty();syncCmds()}
  // Difficulty gates the bridges, so the island answers the setting at once.
  if(typeof refreshBridges==="function")refreshBridges();
  if(activeExperience().layout)activeExperience().layout();
  const sel=$("s-settings");if(sel&&sel.classList.contains("on"))renderSettings();
}
window.setSetting=function(key,value,control){const focus=(control&&control.id)||(document.activeElement&&document.activeElement.id),before=key==="experience"?activeExperience():null;if(!S.settings)S.settings={};S.settings[key]=value;
  if(key==="experience"){const url=new URL(location.href);url.searchParams.delete("experience");history.replaceState(null,"",url)}save();
  if(key==="experience"&&before!==activeExperience()){before.dispose();activeExperience().build();announceExperience()}
  applySettings();if(focus&&$(focus)){$(focus).focus();requestAnimationFrame(()=>{if($(focus))$(focus).focus()})}if(key==="vault"&&$("vault").classList.contains("on"))openVault()};
function settingRow(k,s){return `<div class="setting"><label for="set-${k}">${SETTINGS_LABELS[k]}</label><select id="set-${k}" onchange="setSetting('${k}',this.value,this)">${SETTINGS_OPTIONS[k].map(([v,l])=>`<option value="${v}"${s[k]===v?" selected":""}>${l}</option>`).join("")}</select></div>`}
// A first-time hint shows once and records its id, so the way back to them is
// a button that empties the record. Offered only once there is one to show.
function hintsRow(){return (S.hints&&S.hints.length)?`<button onclick="showHintsAgain()">Show the hints again</button>`:""}
window.showHintsAgain=function(){S.hints=[];save();renderSettings()};
function renderSettings(){const s=settings();
  $("s-settings").innerHTML=`<h2>Settings</h2><p class="small muted">Changes apply at once and stay in this browser. The defaults come from config/camp.toml in your camp.</p>`+
    SETTINGS_GROUPS.map(([title,keys])=>{const rows=keys.filter(settingShown).map(k=>settingRow(k,s)).join("");return rows?`<h3>${title}</h3>`+rows:""}).join("")+
    petPicker()+
    `<div class="setting wide"><label>What you want to learn</label>${interestChips()}<p class="small muted">${interestSummary()}</p>${presetRow()}</div>`+
    `<div class="row"><button class="fs-only" data-icon="maximize" onclick="goFullscreen()">Full screen</button><button onclick="resetSettings()">Back to the defaults</button>${hintsRow()}<button onclick="resetProgress(this)">Reset progress</button><button onclick="closeSheet()">${esc(backLabel())}</button></div>`+
    `<p class="small muted">Persona and theme live in config/camp.toml (uv run vibe persona, theme). They are baked into the game when it is built, so a hosted game keeps the theme it was published with. Difficulty here changes the folding of the commands and the copy; the terminal's checks follow vibe difficulty.</p>`;
  iconize($("s-settings"))}
window.openSettings=function(){renderSettings();openSheet("s-settings")};
// Fullscreen takes the whole document: the sheet and the vault live outside
// #stage, so asking for the stage alone hides every panel behind the canvas.
// iPhone Safari has no Fullscreen API, so the control that asks for it is not
// offered there. One class on the body, so every entry obeys the same fact.
document.body.classList.toggle("no-fullscreen",
  !(document.fullscreenEnabled||document.webkitFullscreenEnabled));
window.goFullscreen=function(){const el=document.documentElement;if(document.fullscreenElement||document.webkitFullscreenElement){(document.exitFullscreen||document.webkitExitFullscreen).call(document)}
  else if(el.requestFullscreen){el.requestFullscreen().catch(()=>{})}else if(el.webkitRequestFullscreen){el.webkitRequestFullscreen()}};
window.resetSettings=function(){S.settings={};save();applySettings()};
// Back to the start of the roadmap: every stop undone, artifacts and mentor
// choices cleared; the name, the chosen look and play mode, and the settings kept. Two clicks, no dialog,
// then a reload so the island rebuilds from the empty state. The hosted
// game does the same from ?reset in the URL.
let resetArmed=null;
window.resetProgress=function(btn){if(btn&&resetArmed!==btn){resetArmed=btn;const old=btn.textContent;btn.textContent="Really start over? Click again";btn.classList.add("danger");setTimeout(()=>{if(resetArmed===btn){resetArmed=null;btn.textContent=old;btn.classList.remove("danger")}},5000);return}
  const keep={name:S.name,look:S.look,mode:S.mode,settings:S.settings||{},interests:S.interests,pet:S.pet};try{localStorage.removeItem(KEY);localStorage.removeItem(OLD_KEY)}catch(e){}
  S={name:keep.name,done:[],doneW:{campus:[],winter:[],desert:[],prod:[]},path:{},pitch:"",versions:[],bridges:{},date:null,wine:null,artifacts:[],look:keep.look,mode:keep.mode,settings:keep.settings,interests:keep.interests,pet:keep.pet};save();
  location.replace(location.pathname)};
document.addEventListener("fullscreenchange",()=>{if(typeof renderer!=="undefined"&&renderer)fitRenderer()});
// The platform's contrast setting can change while the game is open, and at
// auto the game follows it without a reload.
["(prefers-contrast: more)","(forced-colors: active)"].forEach(q=>{const m=matchMedia(q);
  if(m&&m.addEventListener)m.addEventListener("change",()=>applySettings())});
