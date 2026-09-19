window.start=function(){const nm=$("name").value.trim();if(!nm){refuseEmptyName();return}S.name=nm;save();if(typeof chars!=="undefined"&&chars.lotte&&typeof rebuildPlayer==="function")rebuildPlayer();$("title").classList.add("off");if(!started){try{if(!inited){if(typeof THREE==="undefined")throw new Error("three.js not loaded");init3d()}started=true}catch(e){__err("3D failed: "+(e&&e.message||e)+". Falling back to the Roadmap list.");openSheet("s-map")}}hud();track("session","start");say(S.done.length>=stopCount()?"fin":"walk")};
// The world feed: real organisations, projects and people by name, each line
// their own headline and their own words with the link next to it. Never a
// logo, never a sentence written for them (docs/adr/0010). NEWS is baked in at
// build time from data/news.json; the version travels with it so a file of a
// shape this build does not know is refused rather than half read.
const NEWS_VERSION=2;
let newsData=(typeof NEWS==="object"&&NEWS&&NEWS.version===NEWS_VERSION)?NEWS:{fetched_at:"",items:[]};
let newsLoaded=false;
// The one place that answers "does anything from the feed appear": the
// Settings dropdown wins, config/camp.toml [news] live is the default.
function liveNews(){const v=(typeof settings==="function"?settings().live:"config");
  if(v==="off")return false;if(v==="on")return true;return !(CONFIG.news&&CONFIG.news.live===false)}
// The feed comes from other people's machines, so every string in a row is
// text and the link is checked: an item with no usable link keeps its title
// as plain words rather than becoming an anchor we cannot vouch for.
function newsRow(i){const tag=i.kind==="release"?"release":"";const t=esc(i.title),u=safeUrl(i.link);
  return `<div class="pathrow"><span>${u?`<a href="${esc(u)}" target="_blank" rel="noopener noreferrer">${t}</a>`:t}<br><span class="muted small">${esc(i.name)}${tag?" · "+tag:""}</span>${i.summary?`<br><span class="muted small">${esc(i.summary)}</span>`:""}</span><span class="st">${esc((i.date||"").slice(0,10))}</span></div>`}
function renderNews(){const msg=$("newsmsg"),list=$("newslist");if(!msg||!liveNews())return;
  const items=(newsData.items||[]).slice(0,12);
  if(!items.length){msg.textContent="Nothing pulled yet. Run uv run vibe news, then just build; a forked repo does it every day.";list.innerHTML="";return}
  msg.textContent="Pulled "+(newsData.fetched_at||"").slice(0,10)+" from the sources in vibemap/data/sources.json. Unofficial, not affiliated; every line links to the publisher.";
  list.innerHTML=items.map(newsRow).join("")}
// Same origin only: ./news.json sits next to the page the Pages workflow
// publishes, never a third party feed read from the browser. A file:// game
// has no origin to ask, and a camp may host the page without the file, so a
// failure leaves the baked copy in place and says nothing.
function refreshNews(){if(!liveNews()||location.protocol==="file:")return;
  fetch("./news.json?t="+Date.now(),{cache:"no-store"})
    .then(r=>r.ok?r.json():null)
    .then(d=>{if(!d||d.version!==NEWS_VERSION||!Array.isArray(d.items))return;newsData=d;renderNews()})
    .catch(()=>{})}
function loadNews(){renderNews();if(newsLoaded)return;newsLoaded=true;refreshNews()}
// How long a screen stayed open is the one thing the dashboard cannot derive
// afterwards, so the panel that opens is remembered and closing records it.
let sheetOpen=null;
// The sheet is an overlay over the HUD, so the screen a player was reading is
// remembered after it closes: the chat asks about that one when the walker is
// not standing next to anything of its own.
let lastScreen=null;
function sheetDwell(){if(!sheetOpen)return;const s=(Date.now()-sheetOpen.at)/1000;const id=sheetOpen.id;sheetOpen=null;if(s>=2)track("dwell",id,s)}
// A lesson is long, so the row that closes it (Mark as done, and the way back)
// sticks to the bottom of the scroll container. Only that row: a list screen
// would have its own items sitting under a bar that never scrolls away.
function stickyActions(screen){
  const rows=[...screen.querySelectorAll(".row")];
  rows.forEach(r=>r.classList.remove("actions"));
  const bar=rows.reverse().find(r=>[...r.querySelectorAll("button")].some(b=>(b.getAttribute("onclick")||"").indexOf("claim(")===0));
  if(bar)bar.classList.add("actions")}
window.openSheet=function(id){closeVault();sheetDwell();sheetOpen={id:id,at:Date.now()};lastScreen=id;document.querySelectorAll("#sheet .screen").forEach(s=>s.classList.remove("on"));const sc=$(id);sc.classList.add("on");stickyActions(sc);$("sheet").classList.add("on");fx($("sheet"));if(id==="s-map"){renderMap();loadNews()}
  // The sheet has its own scroll container, so a new screen starts at the top
  // of it and the page behind the overlay never moves.
  $("sheet").querySelector(".inner").scrollTop=0;
  setTimeout(()=>{const x=$("sheet").querySelector(".x");if(x)x.focus({preventScroll:true})},30)};
window.closeSheet=function(){sheetDwell();$("sheet").classList.remove("on")};
// Both panels are role=dialog, so Escape has to close them; the palette sits
// on top of everything, then the vault, then the sheet.
addEventListener("keydown",e=>{if(e.key!=="Escape")return;
  if($("pal").classList.contains("on")){closePalette();e.preventDefault()}
  else if($("hud-more").classList.contains("open")){closeHudMenu();e.preventDefault()}
  else if($("vault").classList.contains("on")){closeVault();e.preventDefault()}
  else if($("sheet").classList.contains("on")){closeSheet();e.preventDefault()}});
/* ---------------- the HUD menu ---------------- */
// Everything but Roadmap and Search lives behind one button; which of them the
// menu actually shows is the stylesheet's business, not this function's.
window.toggleHudMenu=function(){const on=!$("hud-more").classList.contains("open");
  $("hud-more").classList.toggle("open",on);$("hud-more-btn").setAttribute("aria-expanded",String(on))};
window.closeHudMenu=function(){$("hud-more").classList.remove("open");$("hud-more-btn").setAttribute("aria-expanded","false")};
// A click anywhere else closes it, and so does picking an item in it.
addEventListener("pointerdown",e=>{if(!$("hud-more").classList.contains("open"))return;if(!$("hud-more").contains(e.target))closeHudMenu()},true);
$("hud-menu").addEventListener("click",e=>{if(e.target.closest("button"))closeHudMenu()});
window.enterNear=function(){if(typeof nearK==="string"&&nearK.startsWith("m:"))openMentor(nearK.slice(2));else if(typeof nearK==="string"&&nearK.startsWith("a:"))openArtifact(nearK.slice(2));else if(nearK)open(nearK)};
window.openCh=open;
function renderEveningDone(){const id=S.world||"campus",t=CAMPAIGN[id],ids=Object.keys(WORLDS),last=ids.indexOf(id)===ids.length-1;
  $("s-gen").innerHTML=`<div class="evening">${t.title}</div><h2>${last?"Campaign complete":"Island complete"}</h2><p>Every stop on this island is done. Your path through the mentors is recorded under Roadmap, and every note is in the Vault. ${last?"That was the last environment of the campaign, so there is nothing left to deploy tonight.":"Pick the next environment from the World button, or walk the bridge."} Export your progress to the CLI so the vault on your Mac catches up.</p><div class="row">${last?"":`<button class="primary" onclick="nextWorld();closeSheet()">Next environment</button>`}<button class="${last?"primary":""}" onclick="openSheet('s-map')">Roadmap</button></div>`}
// The way back out of a stop, in the words of the island you are on.
const backLabel=()=>(S.world||"campus")==="campus"?"Back to the campus":"Back to the island";
// The claim row is a view over S.done: a delivered stop offers one way back,
// so no two buttons in the row ever carry the same name and the primary is
// never a button that does nothing.
function syncClaimRow(sc,n){const b=sc.querySelector('button[onclick^="claim("]');
  if(!b||!S.done.includes(n))return;
  const row=b.closest(".row"),others=row?[...row.querySelectorAll("button")].filter(x=>x!==b):[];
  b.textContent=others.length?others[0].textContent:backLabel();
  b.removeAttribute("onclick");b.onclick=closeSheet;others.forEach(x=>x.remove());
  if(row)row.classList.add("actions")}

// The encounter: the dialogue the learner walks through one exchange at a
// time, then the exercise. Every mentor line paraphrases a recorded idea and
// carries the link it came from; nothing here is a quote. The summary list of
// ideas stays in the vault note, so the screen says each thing once.
function mentorTalk(m){const d=m.encounter.dialogue;const seen=Math.min(d.length,S.met[m.id]||1);
  return d.slice(0,seen).map(x=>`<div class="mturn"><p class="you">${x.you}</p><p class="them"><b>${m.name}:</b> ${x.m} <a class="cite" href="${m.src[x.src][1]}" target="_blank" rel="noopener">${m.src[x.src][0]}</a></p></div>`).join("")}
// The second check of a mentor quest, mirrored from vibemap/quests.py: it runs
// at a strict difficulty, so the card only promises it there.
const MENTOR_NOTE="notes.md",MENTOR_SECTION="## What I learned",MENTOR_WORDS=25;
const strictChecks=()=>["hard","expert","god"].indexOf(typeof difficulty==="function"?difficulty():CONFIG.difficulty)>=0;
function mentorExercise(m){const ex=m.encounter.exercise;const done=S.mentors.includes(m.id);
  return `<div class="card"><h3>${icon("compass")}Your exercise: ${ex.title}</h3>
   <p class="small muted">About ${ex.minutes} minutes, in <code>${ex.dir}/</code> in your camp.</p>
   <ol class="small">${ex.steps.map(s=>`<li>${s}</li>`).join("")}</ol>
   <p class="small"><b>Checked by</b> <code>vibe check --mentor ${m.id}</code>: ${ex.done}${strictChecks()?`, and your note in <code>${ex.dir}/${MENTOR_NOTE}</code> with a ${MENTOR_SECTION} section of at least ${MENTOR_WORDS} words`:""}.</p>
   <p class="small ${done?"":"muted"}">${done?"Verified. The plaque on their spot reads: "+m.encounter.plaque:"Not verified yet. Run the check in your camp, then bring the progress code back here."}</p></div>`}
window.talkMore=function(id){const m=MENTORS.find(x=>x.id===id);if(!m)return;const d=m.encounter.dialogue;
  S.met[id]=Math.min(d.length,(S.met[id]||1)+1);save();$("mtalk").innerHTML=mentorTalk(m);
  const b=$("talkmore");if(b&&S.met[id]>=d.length)b.remove()};
window.openMentor=function(id){const m=MENTORS.find(x=>x.id===id);if(!m)return;const st=S.path[id];
  if(!S.met[id]){S.met[id]=1;save();track("mentor",id)}
  const src=m.src.map(([t,u])=>`<a href="${u}" target="_blank" rel="noopener">${t}</a>`).join(" · ");
  $("s-mentor").innerHTML=`<div class="mentor-head">${mentorFace(m.look)}<div><h2 style="margin:0">${m.name}</h2><div class="role">${m.role}</div></div></div>
   <p>${m.bio}</p><h3>The encounter</h3><div class="mtalk" id="mtalk">${mentorTalk(m)}</div>
   ${S.met[id]>=m.encounter.dialogue.length?"":`<button id="talkmore" onclick="talkMore('${id}')">Ask the next question</button>`}
   ${mentorExercise(m)}
   <div class="deep${st==="deep"?" on":""}" id="deep"><h3>Going deeper</h3><p class="small">${m.deep}</p><p class="small"><b>Sources:</b> ${src}</p></div>
   <div class="rolinda"><b>Rolinda asks</b>${m.ask}</div>
   <div class="row"><button class="primary" onclick="choosePath('${id}','deep')">${st==="deep"?"Keep on my path":"Tell me more"}</button><button onclick="choosePath('${id}','skip')">${st==="skip"?"Still not now":"Not interested for now"}</button><button onclick="closeSheet()">Back</button></div>
   <p class="small muted">Your choice is saved to your path (Roadmap) and to the vault. You can come back and change it.</p>`;
  bubble("tom",m.name+" is on the island. Ask, or walk on. Either is a valid product decision.");openSheet("s-mentor")};
window.choosePath=function(id,v){S.path[id]=v;save();if(props.mentors&&!S.mentors.includes(id)){const c=props.mentors.find(x=>x.id===id);if(c)c.ring.material.color.set(v==="deep"?"#0088CC":"#F04923")}if(v==="deep"){$("deep").classList.add("on");$("deep").scrollIntoView({behavior:"smooth",block:"nearest"})}else closeSheet();hud()};
function mentorFace(lk){return `<svg viewBox="0 0 40 40"><rect x="6" y="8" width="28" height="28" rx="6" fill="#F5D7BC"/><rect x="4" y="4" width="32" height="10" rx="4" fill="${lk.hair}"/>${lk.glasses?'<rect x="9" y="19" width="9" height="5" rx="2" fill="none" stroke="#111" stroke-width="1.5"/><rect x="22" y="19" width="9" height="5" rx="2" fill="none" stroke="#111" stroke-width="1.5"/>':'<circle cx="14" cy="21" r="2" fill="#333"/><circle cx="26" cy="21" r="2" fill="#333"/>'}${lk.beard?'<rect x="10" y="27" width="20" height="8" rx="3" fill="'+lk.hair+'"/>':'<path d="M15 29 Q20 33 25 29" stroke="#B0534B" stroke-width="2" fill="none"/>'}</svg>`}
function open(n){
  track("open",n);
  if(n===0){openSheet("s-0");return}
  const sc=$("s-"+n);
  // The campus lessons are sections written into the page; every other stop,
  // including one a camp adds to an island, is rendered from the island's ws.
  if((S.world||"campus")==="campus"&&sc){
    if(n===1)renderPitch();if(n===2)renderCard();if(n===3)renderSchema();if(n===4)renderVersions();
    if(n===5)renderBridges();if(n===6)weave();if(n===finaleStop())renderFinale();
    say(n);openSheet("s-"+n);syncClaimRow(sc,n);return}
  const w=CH[n-1];
  if(!w){renderEveningDone();say("fin");openSheet("s-gen");return}
  const done=S.done.includes(n);
  $("s-gen").innerHTML=`<div class="evening">${CAMPAIGN[S.world||"campus"].title}</div><div class="hour">${w.h}</div><h2>${w.n}</h2>${w.html||`<p>${w.d}</p>`}<div class="row"><button class="primary" onclick="claim(${n})">Mark as done and unlock the OKR</button><button onclick="closeSheet()">${backLabel()}</button></div>`;
  bubble("rolinda","Same rule as always: explain it to me in one sentence when you are done.");
  openSheet("s-gen");syncClaimRow($("s-gen"),n);
}
function renderMap(){const ok=S.done.length>=stopCount();const ev=CAMPAIGN[S.world||"campus"];
  // Pre-flight (workstream 0) only exists on the campus; the other islands start at stop 1.
  const preflight=(S.world||"campus")==="campus"?`<button class="date" onclick="openCh(0)">Before the evening, Pre-flight<br><span class="small" style="opacity:.75">Install Claude Code, git, Obsidian. 20 minutes, alone.</span></button>`:"";
  $("plotlist").innerHTML=`<div class="evening">${ev.title}</div><p class="small muted">${ev.blurb}</p>`+preflight+CH.map((c,i)=>{const k=i+1,done=S.done.includes(k),locked=k>1&&!S.done.includes(k-1);
    return `<button class="date${done?' pick':''}" ${locked?'disabled':''} onclick="openCh(${k})">${done?icon("check"):""}${c.h}, ${c.n}${done?" (delivered)":locked?" (blocked by dependency)":""}<br><span class="small" style="opacity:.75">${c.d}</span></button>`}).join("")+
    ((S.world||"campus")==="campus"?`<button class="date" ${ok?'':'disabled'} onclick="openCh(${finaleStop()})">${icon("milestone")}Calendar alignment${ok?"":" (pending "+stopCount()+" OKRs)"}</button>`:"")+
    interestCard()+
    `<div class="card"><h3>${icon("users")}Your path: the mentors</h3><p class="small muted">People you met on the islands, and what you chose. Tap to revisit or change your mind.</p>`+MENTORS.map(m=>{const st=S.path[m.id];return `<div class="pathrow"><span>${interestDot(!interestsAll()&&wantsShelf(m.shelf)?m.shelf:null)}<b>${m.name}</b> <span class="muted">· ${WORLDS[m.world].name}</span></span><span style="display:flex;gap:6px;align-items:center"><span class="st ${st||''}">${st==="deep"?"on path":st==="skip"?"skipped":S.met[m.id]?"met":"not met"}</span><button onclick="openMentor('${m.id}')" aria-label="Open ${m.name}" style="padding:4px 10px;font-size:12px">Open</button></span></div>`}).join("")+`</div>`+
    `<div class="card"><h3>${icon("compass")}Artifacts on the islands</h3><p class="small muted">Twenty-one things across the four islands that each explain one idea. Walk up to a yellow ring, or open one here.</p>`+ARTIFACTS.map(a=>`<div class="pathrow"><span>${interestDot(matchedShelf(a.links))}<b>${a.name}</b> <span class="muted">· ${a.concept}</span></span><span style="display:flex;gap:6px;align-items:center"><span class="st ${S.artifacts.includes(a.id)?'deep':''}">${S.artifacts.includes(a.id)?"found":"not yet"}</span><button onclick="openArtifact('${a.id}')" aria-label="Open ${a.name}" style="padding:4px 10px;font-size:12px">Open</button></span></div>`).join("")+`</div>`+
    `<div class="card"><h3>${icon("flag")}The campaign</h3>`+Object.keys(CAMPAIGN).map(k=>`<div class="pathrow"><span><b>${CAMPAIGN[k].title}</b><br><span class="muted small">${WORLDS[k].name}</span></span><span style="display:flex;gap:6px;align-items:center"><span class="st ${(S.doneW[k]||[]).length>=CAMPAIGN[k].ws.length?'deep':''}">${(S.doneW[k]||[]).length}/${CAMPAIGN[k].ws.length}</span><button onclick="setWorld('${k}');closeSheet()" aria-label="Go to ${WORLDS[k].name}" style="padding:4px 10px;font-size:12px">Go</button></span></div>`).join("")+`</div>`;
}
window.claim=function(n){
  if(!S.done.includes(n)){S.done.push(n);save();track("claim",n);
    // A stop a camp added has data but no plot of its own on the island, so
    // there is nothing to build on it.
    if(PLOT_POS[n-1])placeBuilding(n,true);applySky(S.done.length,false);hud();closeSheet();say(S.done.length>=stopCount()?"fin":"done");lastSay="done";return}
  closeSheet()};


/* ---------------- vault (mini Obsidian) ---------------- */
