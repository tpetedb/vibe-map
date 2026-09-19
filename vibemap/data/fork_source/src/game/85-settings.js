// Settings: dropdowns that change the game without a rebuild. They persist
// in S.settings (the same localStorage record as progress) and apply at once.
// config/camp.toml still sets the defaults for a fresh browser; these override them.
const SETTINGS_DEFAULTS={difficulty:"config",map:"big",vault:"config",live:"config",pairings:"config",shadows:"high",motion:"auto",speed:"normal",zoom:CAM.zoom.start};
const SETTINGS_OPTIONS={
  difficulty:[["config","From config/camp.toml ("+CONFIG.difficulty+")"],["beginner","Beginner: commands open, lenient"],["easy","Easy: commands open"],["normal","Normal: commands open, real checks"],["hard","Hard: commands folded, strict"],["expert","Expert: folded, tests must pass"],["god","God: folded, just verify must be green"]],
  map:[["compact","Compact (56% of the window)"],["big","Big (84% of the window)"],["tall","Tall (the whole window)"]],
  vault:[["config","From config/camp.toml ("+((CONFIG.vault&&CONFIG.vault.mode)||"full")+")"],["full","Full: every note in the graph"],["grow","Grow: notes unlock as you play"]],
  live:[["config","From config/camp.toml ("+((CONFIG.news&&CONFIG.news.live===false)?"off":"on")+")"],["on","On: what the sources published lately"],["off","Off: nothing from the feeds"]],
  pairings:[["config","From the theme"],["on","Show the pairings"],["off","Hide the pairings"]],
  shadows:[["high","Soft shadows"],["low","Cheap shadows"],["off","No shadows (fastest)"]],
  motion:[["auto","Follow the system setting"],["off","No animations"]],
  speed:[["slow","Stroll"],["normal","Walk"],["fast","Hurry"]]
};
const SETTINGS_LABELS={difficulty:"Difficulty",map:"Map size",vault:"Vault",live:"Live world",pairings:"Pairings",shadows:"Shadows",motion:"Motion",speed:"Walking speed"};
function settings(){if(!S.settings)S.settings={};return Object.assign({},SETTINGS_DEFAULTS,S.settings)}
function speedMult(){return {slow:.7,normal:1,fast:1.5}[settings().speed]||1}
function motionOff(){return settings().motion==="off"}
function applySettings(){const s=settings();
  const st=$("stage");st.classList.remove("map-compact","map-big","map-tall");st.classList.add("map-"+s.map);
  if(typeof renderer!=="undefined"&&renderer){renderer.shadowMap.enabled=s.shadows!=="off";if(typeof dirL!=="undefined"&&dirL){dirL.castShadow=s.shadows!=="off";dirL.shadow.mapSize.set(s.shadows==="high"?CONFIG.shadowMap:1024,s.shadows==="high"?CONFIG.shadowMap:1024);if(dirL.shadow.map){dirL.shadow.map.dispose();dirL.shadow.map=null}}
    fitRenderer()}
  // The zoom is a setting without a dropdown: the wheel, a pinch and the
  // buttons on the stage write it, and the defaults reset it with the rest.
  if(typeof syncZoom==="function")syncZoom();
  const showPair=s.pairings==="config"?CONFIG.theme.showPairings:s.pairings==="on";document.querySelectorAll(".pairing").forEach(el=>el.style.display=showPair?"":"none");
  document.body.classList.toggle("no-motion",s.motion==="off");
  // Off means nothing from the feeds appears and nothing is fetched: the
  // stylesheet hides every element marked live-feed, loadNews checks the same.
  if(typeof liveNews==="function"){document.body.classList.toggle("no-live",!liveNews());if(liveNews())renderNews()}
  if(typeof difficulty==="function"){document.body.dataset.difficulty=difficulty();syncCmds()}
  // Difficulty gates the bridges, so the island answers the setting at once.
  if(typeof refreshBridges==="function")refreshBridges();
  const sel=$("s-settings");if(sel&&sel.classList.contains("on"))renderSettings();
}
window.setSetting=function(key,value){if(!S.settings)S.settings={};S.settings[key]=value;save();applySettings();if(key==="vault"&&$("vault").classList.contains("on"))openVault()};
function renderSettings(){const s=settings();
  $("s-settings").innerHTML=`<h2>Settings</h2><p class="small muted">Changes apply at once and stay in this browser. The defaults come from config/camp.toml in your camp.</p>`+
    Object.keys(SETTINGS_OPTIONS).map(k=>`<div class="setting"><label for="set-${k}">${SETTINGS_LABELS[k]}</label><select id="set-${k}" onchange="setSetting('${k}',this.value)">${SETTINGS_OPTIONS[k].map(([v,l])=>`<option value="${v}"${s[k]===v?" selected":""}>${l}</option>`).join("")}</select></div>`).join("")+
    petPicker()+
    `<div class="setting wide"><label>What you want to learn</label>${interestChips()}<p class="small muted">${interestSummary()}</p>${presetRow()}</div>`+
    `<div class="row"><button data-icon="maximize" onclick="goFullscreen()">Full screen</button><button onclick="resetSettings()">Back to the defaults</button><button onclick="resetProgress(this)">Reset progress</button><button onclick="closeSheet()">Back to the campus</button></div>`+
    `<p class="small muted">Persona and theme live in config/camp.toml (uv run vibe persona, theme). They are baked into the game when it is built, so a hosted game keeps the theme it was published with. Difficulty here changes the folding of the commands and the copy; the terminal's checks follow vibe difficulty.</p>`;
  iconize($("s-settings"))}
window.openSettings=function(){renderSettings();openSheet("s-settings")};
// Fullscreen takes the whole document: the sheet and the vault live outside
// #stage, so asking for the stage alone hides every panel behind the canvas.
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
