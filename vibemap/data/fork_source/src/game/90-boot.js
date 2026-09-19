// Resume is offered to anyone who has been here before, but only when there is
// something to resume with: start() refuses an empty name, so a saved look on
// its own would be a button that turns you down. Once a stop is done the five
// steps fold into their disclosure and the resume button is the first thing.
if(load()){$("name").value=S.name;if(S.name)$("btn-continue").style.display="";
  if(S.done.length){$("title").classList.add("returning");$("obfold").open=false}}
// ?reset must run after load(), or it saves the defaults over the real record.
if(new URLSearchParams(location.search).has("reset"))resetProgress();
// Pairings are written for wine. Any other theme gets its own one-line pairing
// from the theme data; a theme without pairings loses the blocks altogether.
function themePairings(){const th=CONFIG.theme;if(th.pairing==="wine")return;
  const blocks=[...document.querySelectorAll(".pairing")];
  if(!(th.pairings||[]).length){blocks.forEach(el=>el.remove());return}
  const kind=th.pairing.charAt(0).toUpperCase()+th.pairing.slice(1);
  // The go-live block is the whole stack in one sentence. The items carry
  // commas of their own, so they are separated by semicolons and the last one
  // gets an "and", which is the only way the list reads as a sentence.
  const stack=th.pairings.length===1?th.pairings[0]
    :th.pairings.slice(0,-1).join("; ")+" and "+th.pairings[th.pairings.length-1];
  blocks.forEach((el,i)=>{if(i<th.pairings.length)el.innerHTML=`<b>${kind}, ${CH[i]?CH[i].h:"go-live"}</b>${th.pairings[i]}`;
    else el.innerHTML=`<b>${kind}, go-live</b>The stack for the evening, in order: ${stack}.`})}
// Theme, dates and repo come from config/camp.toml through CONFIG. Labels apply to
// every theme; the wine-night preset alone keeps the handwritten framing, and
// any other theme swaps it and rewrites the pairings. Difficulty and persona
// are exposed on <body> for CSS.
function applyTheme(){const th=CONFIG.theme;document.body.dataset.theme=th.id;document.body.dataset.difficulty=CONFIG.difficulty;document.body.dataset.persona=CONFIG.persona;
  const tp=$("tplink");if(tp&&CONFIG.repo){tp.href=CONFIG.repo;tp.textContent=CONFIG.repo.replace(/^https?:\/\//,"")}
  // The title screen and the HUD speak the theme's language: the second line
  // of the tagline, the two buttons, the word for a stop, the four KPIs.
  $("tagline").textContent="From intern to expert in one evening. "+th.taglineSuffix;
  $("btn-go").textContent=th.goLabel;
  $("btn-continue").textContent=th.resumeLabel;
  $("hud-stoplabel").textContent=th.stopLabel;
  th.kpiLabels.forEach((l,i)=>{const el=$("k"+(i+1)+"l");if(el)el.textContent=l});
  themePairings();
  if(!th.showPairings)document.querySelectorAll(".pairing").forEach(el=>el.style.display="none");
  // Over http the vault folder is not on disk, so the button is honest about
  // where it goes.
  const ob=$("vobs");if(ob&&location.protocol!=="file:"){ob.textContent="Vault on GitHub";ob.dataset.icon="book-open";ob.title="The vault folder on GitHub"}
  if(th.id==="wine-night")return;
  $("intro").textContent=th.intro;
  $("roles").textContent=`Tom is your ${th.hostRole}. Rolinda is ${th.guideRole}, and the only one who is allowed to ask the simple question. ${th.signOff}`}
function stamp(){$("stamp-ver").textContent=`vibe-map v${CONFIG.version} · ${CONFIG.theme.id}`;$("t-done").textContent=String(S.done.length)}
applyTheme();stamp();wrapCommands();renderOnboarding();iconize();say("title");hud();renderWorldPicker();applySettings();
// The island is the backdrop of the title, so the scene builds at once;
// start() only flips the flag. A failure here is reported again by start().
try{if(typeof THREE!=="undefined")init3d();applySettings()}catch(e){}
