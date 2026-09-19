// Onboarding: the title screen is a five-step form on a first visit. Who you
// are (a preset walker or your own name), how hard, what you want to learn,
// how you want to play (browser only, or the full experience with the terminal
// and Obsidian), go. Everything it decides lives in S: S.name, S.look,
// S.settings.difficulty, S.interests.
// Returning players get the resume button first; the steps fold away.
const LOOKS={
  lotte:{label:"Lotte",role:"CoS",blurb:"Chief of Staff. The default; the copy is written to her.",kind:"lotte",body:"#FFFFFF",legs:"#C9C1B8",arms:"#F5D7BC"},
  frank:{label:"Frank",role:"Platform",blurb:"Platform engineer. Glasses, blue shirt, no patience for dashboards.",kind:"mentor",body:"#0067A5",legs:"#2B2B2B",arms:"#F5D7BC",look:{hair:"#3B2A1E",glasses:true}},
  max:{label:"Max",role:"Data",blurb:"Data engineer. Beard, green shirt, brings the DuckDB.",kind:"mentor",body:"#00A86B",legs:"#3A3A3A",arms:"#F5D7BC",look:{hair:"#1A1A1A",beard:true}},
  rolinda:{label:"Rolinda",role:"Ops",blurb:"Head of Hospitality. Plays herself; the hub keeps its own Rolinda on duty.",kind:"rolinda",body:"#8FD18A",legs:"#9CC4E8",arms:"#8FD18A"},
  own:{label:"Your own name",role:"Player",blurb:"Type it in the box below. Orange shirt, brown hair.",kind:"mentor",body:"#FF8C1A",legs:"#3A3A3A",arms:"#F5D7BC",look:{hair:"#6B4A2B"}}
};
const DIFFS=[
  ["beginner","Beginner","Every command spelled out and open. Lenient checks."],
  ["easy","Easy","Commands open, a little less hand-holding."],
  ["normal","Normal","Commands open. Checks look at what you built."],
  ["hard","Hard","Command blocks folded (one click opens them). Strict checks."],
  ["expert","Expert","Command blocks folded. Tests must exist and pass."],
  ["god","God","Command blocks folded. just verify must be green to claim."]
];
// The walker spec for the current player. Unknown or missing looks fall back
// to Lotte for a saved game that was played as her, else to your own look.
function playerLook(){return LOOKS[S.look]||(S.name==="Lotte"?LOOKS.lotte:LOOKS.own)}
// What to call the player before a name is typed: the chosen preset, else
// nothing. Never the placeholder.
function playerLabel(){return S.name||(LOOKS[S.look]&&S.look!=="own"?LOOKS[S.look].label:"")}
function playerSpec(){const l=playerLook();const n=playerLabel();return {kind:l.kind,body:l.body,legs:l.legs,arms:l.arms,look:l.look,wear:sl("wear"),label:n?n+", "+l.role:l.role}}
function difficulty(){const d=(S.settings&&S.settings.difficulty)||"config";return d==="config"?CONFIG.difficulty:d}
function cmdsOpen(){return ["beginner","easy","normal"].indexOf(difficulty())>=0}
// Every command block in a lesson becomes a <details>: open at beginner, easy
// and normal, folded at hard and up, always one click away. Runs once at boot;
// syncCmds re-applies the fold whenever the difficulty changes.
function wrapCommands(){document.querySelectorAll(".lesson pre").forEach(pre=>{if(pre.parentElement.classList.contains("cmds"))return;const d=document.createElement("details");d.className="cmds";d.innerHTML="<summary>Commands</summary>";pre.replaceWith(d);d.appendChild(pre)})}
let cmdsLevel=null;
function syncCmds(){const open=cmdsOpen();if(cmdsLevel===open)return;cmdsLevel=open;document.querySelectorAll("details.cmds").forEach(d=>d.open=open)}
// The naming convention for a local camp: your name, vibe-map, the date.
// Accents fold rather than disappear: Jorg and the accented spelling get the
// same camp directory. Mirrors camp_dir_name in the CLI.
function fold(s){return String(s||"").normalize("NFD").replace(/[\u0300-\u036f]/g,"")}
function slug(s){return fold(s||"player").toLowerCase().replace(/[^a-z0-9]+/g,"-").replace(/^-|-$/g,"")||"player"}
// A name goes into a shell command as one single-quoted word, so a quote or
// a space in it cannot end the argument.
function shq(s){return "'"+String(s).replace(/'/g,"'\\''")+"'"}
function campDir(){const d=new Date();const ymd=d.getFullYear()+"-"+String(d.getMonth()+1).padStart(2,"0")+"-"+String(d.getDate()).padStart(2,"0");return "~/vibe-map-"+slug(S.name)+"-"+ymd}
// The camp's own repository, from config/camp.toml. It becomes an anchor and a
// command, so it is held to the same rule as any other link: http or https.
function repoUrl(){return safeUrl(CONFIG.repo)||"https://github.com/tpetedb/vibe-map"}
// The setup guide: the exact commands for the full experience. Rendered on the
// title screen (step 3) and on its own screen from the Roadmap, from one
// template so the two never drift. The commands are always open here,
// whatever the difficulty: setup is not the game.
function setupHtml(){const dir=campDir();const repo=esc(repoUrl());return `
<p class="small">Three windows side by side: this game, a terminal, Obsidian. The game is where you get the story and claim stops. The terminal is where the work happens and the checks run. Obsidian is where the notes land. Fifteen minutes to set up, then <code>just start</code> every session.</p>
<h4>1. Get the tools</h4>
<p class="small">Open <a href="${repo}" target="_blank" rel="noopener">${repo.replace(/^https?:\/\//,"")}</a> and press <b>Use this template</b> if you want your own copy on GitHub, or skip that and clone below. Then open a terminal (on a Mac: Cmd+Space, type Terminal, or install Ghostty).</p>
<pre><code>brew install uv git just gh
brew install --cask obsidian</code></pre>
<p class="small muted">You should see: a list of installed formulae, and <code>uv --version</code> printing a number.</p>
<h4>2. Install the command and make your camp</h4>
<p class="small">The folder name is the convention: your name, vibe-map, today's date. It sorts by date in a listing and tells you which camp a note came from.</p>
<pre><code>uv tool install git+${repo}
vibe new ${dir}
cd ${dir}
just setup</code></pre>
<p class="small muted">You should see: <code>Installed 1 executable: vibe</code>, then a new folder with <code>config/camp.toml</code>, <code>workspace/</code> and <code>vault/</code> in it.</p>
<p class="small muted">Own GitHub copy instead? <code>vibe new ${dir} --github YOU/vibe-map-${slug(playerLabel())}</code> (needs <code>gh auth login</code> first).</p>
<h4>3. Tell it who you are</h4>
<pre><code>vibe name ${esc(shq(playerLabel()||"player"))}
vibe difficulty ${esc(difficulty())}
just start</code></pre>
<p class="small muted">You should see: the camp menu, with your name at the top and 0 of 8 stops done.</p>
<p class="small muted"><code>just start</code> is the terminal menu: checks, the pet, the launchers. It stays open in one terminal tab; open a second tab for Claude Code.</p>
<h4>4. Open the vault in Obsidian</h4>
<p class="small">Obsidian, <b>Open folder as vault</b>, pick <code>${dir}/vault</code>. Obsidian asks whether to trust the vault's own plugin config; it is the folder <code>vibe</code> just wrote, so yes. Press Cmd+G for the graph.</p>
<pre><code>vibe vault mode grow     # optional: start empty and watch the graph fill as you play
vibe vault build</code></pre>
<p class="small muted">You should see: <code>vault/Camp/Tonight.md</code> on disk, and a graph with notes in it in Obsidian.</p>
<h4>5. Keep the two in sync</h4>
<p class="small">Progress here and progress in the terminal are one code. After a session in either place, carry it across:</p>
<pre><code>vibe export                                # prints a code; paste it in the game under Roadmap, Sync
vibe import &lt;code from the game&gt;           # the other way round</code></pre>
<p class="small muted">You should see: a long code on export, and a line naming the stops that were added on import.</p>
<h4>6. Confirm the whole thing</h4>
<pre><code>vibe status</code></pre>
<p class="small muted">You should see: your name, your difficulty, your stops and your XP. That one line is the check that setup worked.</p>
<p class="small muted">Two terminals help: one with <code>just start</code> or <code>claude</code>, one for the commands the lessons give you. The full walk-through with screenshots is in <a href="${repo}/blob/main/docs/LONG-GAME.md" target="_blank" rel="noopener">docs/LONG-GAME.md</a>.</p>`}
window.openSetup=function(){$("s-setup").innerHTML=`<h2>Setup guide</h2><p class="small muted">The full experience: this game, your terminal and Obsidian on one desk.</p>`+setupHtml();openSheet("s-setup")};
// The title form. Re-rendered on every choice so the highlighted buttons and
// the setup commands (which carry the name and the difficulty) stay current.
// A preset's label is the picker's own writing, never something the player
// typed, so it is the one value "Your own name" is allowed to clear.
function presetLabel(v){return Object.keys(LOOKS).some(k=>k!=="own"&&LOOKS[k].label===v)}
window.pickLook=function(id){S.look=id;const nm=$("name");
  if(id!=="own")nm.value=LOOKS[id].label;else{if(presetLabel(nm.value))nm.value="";nm.focus()}
  S.name=nm.value.trim();clearNameError();save();renderOnboarding();if(typeof chars!=="undefined"&&chars.lotte&&typeof rebuildPlayer==="function")rebuildPlayer()};
window.pickDifficulty=function(d){if(!S.settings)S.settings={};S.settings.difficulty=d;save();applySettings();renderOnboarding()};
window.pickMode=function(m){S.mode=m;save();renderOnboarding();if(m==="full"){const el=$("ob-setup");if(el)el.scrollIntoView({block:"start",behavior:motionOff()?"auto":"smooth"})}};
// The walker carries the name on a sprite, so it is rebuilt after typing
// stops rather than on every keystroke.
let nameT=null;
window.nameTyped=function(v){S.name=v.trim();if(S.look!=="own"&&LOOKS[S.look]&&LOOKS[S.look].label!==S.name)S.look="own";clearNameError();save();hud();const el=$("ob-setup");if(el&&el.style.display!=="none")el.innerHTML=setupHtml();
  clearTimeout(nameT);nameT=setTimeout(()=>{if(typeof chars!=="undefined"&&chars.lotte&&typeof rebuildPlayer==="function")rebuildPlayer()},400)};
// The name is the one thing the title screen insists on: no placeholder gets
// saved, so an empty box sends you back to it instead of starting as nobody.
const NAME_HINT="Type your name plainly.";
function clearNameError(){const h=$("namehint");if(h){h.classList.remove("err");h.textContent=NAME_HINT}}
window.refuseEmptyName=function(){const nm=$("name"),h=$("namehint");if(h){h.textContent="Type your name first, then kick off.";h.classList.add("err")}
  if(nm){nm.classList.remove("shake");void nm.offsetWidth;nm.classList.add("shake");nm.focus()}};
// What you have earned to wear, on the look picker: nothing until the first
// achievement unlocks something, then one button a piece.
function wardrobeRow(){const owned=WEAR.filter(w=>wearOwned(w.id));if(!owned.length)return "";
  const worn=sl("wear");
  return `<div class="choices">${owned.map(w=>`<button class="choice${worn.includes(w.id)?" on":""}" onclick="toggleWear('${w.id}')" title="${w.slot}">${w.name}</button>`).join("")}</div>
<p class="small muted">Yours to wear, earned on the islands. The Backpack has the rest.</p>`}
function renderOnboarding(){const box=$("onboard");if(!box)return;const look=LOOKS[S.look]?S.look:(S.name==="Lotte"?"lotte":"own");const diff=difficulty();const mode=S.mode||"";
  box.innerHTML=`<div class="step"><b>1</b><span>Who are you?</span></div>
<div class="choices">${Object.keys(LOOKS).map(k=>`<button class="choice${look===k?" on":""}" onclick="pickLook('${k}')" title="${LOOKS[k].blurb}"><i style="background:${LOOKS[k].body}"></i>${LOOKS[k].label}</button>`).join("")}</div>
<p class="small muted">${LOOKS[look].blurb}</p>
${wardrobeRow()}
${petPicker('ob-pet')}
<div class="step"><b>2</b><span>How hard?</span></div>
<div class="choices">${DIFFS.map(([k,l])=>`<button class="choice${diff===k?" on":""}" onclick="pickDifficulty('${k}')">${l}</button>`).join("")}</div>
<p class="small muted">${(DIFFS.find(d=>d[0]===diff)||DIFFS[2])[2]} You can change this any time under Settings.</p>
<div class="step"><b>3</b><span>What do you want to learn?</span></div>
${interestChips()}
<p class="small muted">${interestSummary()}</p>
${presetRow()}
<div class="step"><b>4</b><span>How do you want to play?</span></div>
<div class="choices modes"><button class="choice${mode==="online"?" on":""}" onclick="pickMode('online')"><b>Just the game</b><span>In this browser. Nothing to install. The lessons still show every command.</span></button><button class="choice${mode==="full"?" on":""}" onclick="pickMode('full')"><b>The full experience</b><span>Everything, synced. Add a terminal and Obsidian so your work is checked and your notes are saved. You can switch to this later; nothing is lost.</span></button></div>
<p class="small muted" id="prereq">Honest prerequisites for the full experience: a Mac or Linux terminal, about fifteen minutes to install the tools, a GitHub account, and a paid plan for Claude, Codex or Gemini. Without those, pick just the game; you can switch later and nothing is lost.</p>
<div class="step"><b>5</b><span>Your name, then go</span></div>`;
  const setup=$("ob-setup");if(setup){setup.style.display=mode==="full"?"":"none";setup.innerHTML=mode==="full"?setupHtml():""}
  const nm=$("name");if(nm&&nm.value!==S.name)nm.value=S.name;
  document.body.dataset.mode=mode}
// The title is modal: until Start the campus behind it is not there. The
// stylesheet takes away the HUD's tab stops and its clicks; this takes away the
// global keys, so c, Cmd K and Escape cannot open a panel over the form or
// claim a stop before the game has begun. A key aimed at the form is swallowed
// on its way out, after the field or the button it was aimed at has had it; a
// key aimed at nothing is swallowed on the window, before the handlers there.
function swallowKey(e){if(!$("title").classList.contains("off"))e.stopPropagation()}
$("title").addEventListener("keydown",swallowKey);
addEventListener("keydown",e=>{if(!$("title").contains(e.target))swallowKey(e)},true);
