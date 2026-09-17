if(load()){$("name").value=S.name;if(S.done.length)$("btn-continue").style.display=""}
// Theme, dates and repo come from vibe.toml through CONFIG. The wine-night
// preset keeps the handwritten copy; any other theme swaps the framing and
// hides the pairings. Difficulty and persona are exposed on <body> for CSS.
function applyTheme(){const th=CONFIG.theme;document.body.dataset.theme=th.id;document.body.dataset.difficulty=CONFIG.difficulty;document.body.dataset.persona=CONFIG.persona;
  const tp=$("tplink");if(tp&&CONFIG.repo){tp.href=CONFIG.repo;tp.textContent=CONFIG.repo.replace(/^https?:\/\//,"")}
  if(!th.showPairings)document.querySelectorAll(".pairing").forEach(el=>el.style.display="none");
  if(th.id==="wine-night")return;
  $("tagline").textContent="From intern to expert in one evening. ";
  $("intro").textContent=th.intro;
  $("roles").textContent=`Tom is your ${th.hostRole}. Rolinda is ${th.guideRole}, and the only one who is allowed to ask the simple question. ${th.signOff}`}
function stamp(){$("stamp-ver").textContent=`vibe-map v${CONFIG.version} · ${CONFIG.theme.id}`;$("t-done").textContent=String(S.done.length)}
applyTheme();stamp();iconize();say("title");hud();renderWorldPicker();applySettings();
// The island is the backdrop of the title, so the scene builds at once;
// start() only flips the flag. A failure here is reported again by start().
try{if(typeof THREE!=="undefined")init3d();applySettings()}catch(e){}
