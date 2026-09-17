window.start=function(){S.name=$("name").value.trim()||"Lotte";save();$("title").classList.add("off");if(!started){try{if(!inited){if(typeof THREE==="undefined")throw new Error("three.js not loaded");init3d()}started=true}catch(e){__err("3D failed: "+(e&&e.message||e)+". Falling back to the Roadmap list.");openSheet("s-map")}}hud();say(S.done.length===8?"fin":"walk")};
window.openSheet=function(id){closeVault();document.querySelectorAll("#sheet .screen").forEach(s=>s.classList.remove("on"));$(id).classList.add("on");$("sheet").classList.add("on");fx($("sheet"));if(id==="s-map")renderMap();setTimeout(()=>$("sheet").scrollIntoView({behavior:"smooth",block:"start"}),30)};
window.closeSheet=function(){$("sheet").classList.remove("on");window.scrollTo({top:0,behavior:"smooth"})};
window.enterNear=function(){if(typeof nearK==="string"&&nearK.startsWith("m:"))openMentor(nearK.slice(2));else if(typeof nearK==="string"&&nearK.startsWith("a:"))openArtifact(nearK.slice(2));else if(nearK)open(nearK)};
window.openCh=open;
function renderEveningDone(){const t=CAMPAIGN[S.world];$("s-gen").innerHTML=`<div class="evening">${t.title}</div><h2>Island complete</h2><p>All eight stops on this island are done. Rolinda is opening something. Your path through the mentors is recorded under Roadmap, and every note is in the Vault. Pick another environment from the World button to continue the campaign, or export your progress to the CLI so the vault on your Mac catches up.</p><div class="row"><button class="primary" onclick="nextWorld();closeSheet()">Next environment</button><button onclick="openSheet('s-map')">Roadmap</button></div>`}
window.openMentor=function(id){const m=MENTORS.find(x=>x.id===id);if(!m)return;const st=S.path[id];
  const ideas=m.ideas.map(i=>`<li>${i}</li>`).join("");const src=m.src.map(([t,u])=>`<a href="${u}" target="_blank" rel="noopener">${t}</a>`).join(" · ");
  $("s-mentor").innerHTML=`<div class="mentor-head">${mentorFace(m.look)}<div><h2 style="margin:0">${m.name}</h2><div class="role">${m.role}</div></div></div>
   <p>${m.bio}</p><h3>What they would tell you tonight</h3><ul class="ideas small">${ideas}</ul>
   <div class="deep${st==="deep"?" on":""}" id="deep"><h3>Going deeper</h3><p class="small">${m.deep}</p><p class="small"><b>Sources:</b> ${src}</p></div>
   <div class="rolinda"><b>Rolinda asks</b>${m.ask}</div>
   <div class="row"><button class="primary" onclick="choosePath('${id}','deep')">${st==="deep"?"Keep on my path":"Tell me more"}</button><button onclick="choosePath('${id}','skip')">${st==="skip"?"Still not now":"Not interested for now"}</button><button onclick="closeSheet()">Back</button></div>
   <p class="small muted">Your choice is saved to your path (Roadmap) and to the vault. You can come back and change it.</p>`;
  $("bub-face").innerHTML=FACE.tom;$("bub-who").textContent="Tom, Site Reliability Engineer";$("bub-text").textContent=m.name+" is on the island. Ask, or walk on. Either is a valid product decision.";openSheet("s-mentor")};
window.choosePath=function(id,v){S.path[id]=v;save();if(props.mentors){const c=props.mentors.find(x=>x.id===id);if(c)c.ring.material.color.set(v==="deep"?"#0088CC":"#F04923")}if(v==="deep"){$("deep").classList.add("on");$("deep").scrollIntoView({behavior:"smooth",block:"nearest"})}else closeSheet();hud()};
function mentorFace(lk){return `<svg viewBox="0 0 40 40"><rect x="6" y="8" width="28" height="28" rx="6" fill="#F5D7BC"/><rect x="4" y="4" width="32" height="10" rx="4" fill="${lk.hair}"/>${lk.glasses?'<rect x="9" y="19" width="9" height="5" rx="2" fill="none" stroke="#111" stroke-width="1.5"/><rect x="22" y="19" width="9" height="5" rx="2" fill="none" stroke="#111" stroke-width="1.5"/>':'<circle cx="14" cy="21" r="2" fill="#333"/><circle cx="26" cy="21" r="2" fill="#333"/>'}${lk.beard?'<rect x="10" y="27" width="20" height="8" rx="3" fill="'+lk.hair+'"/>':'<path d="M15 29 Q20 33 25 29" stroke="#B0534B" stroke-width="2" fill="none"/>'}</svg>`}
function open(n){
  if(n===0){openSheet("s-0");return}
  if(S.world!=="campus"){if(n===9){renderEveningDone();say("fin");openSheet("s-gen");return}const w=CH[n-1];const done=S.done.includes(n);
    $("s-gen").innerHTML=`<div class="evening">${CAMPAIGN[S.world].title}</div><div class="hour">${w.h}</div><h2>${w.n}</h2>${w.html}<div class="row"><button class="primary" onclick="claim(${n})">${done?"Back to the island":"Mark as done and unlock the OKR"}</button><button onclick="closeSheet()">Back to the island</button></div>`;
    $("bub-face").innerHTML=FACE.rolinda;$("bub-who").textContent="Rolinda, Head of Hospitality Operations";$("bub-text").textContent="Same rule as always: explain it to me in one sentence when you are done.";openSheet("s-gen");return}
  if(n===1&&!S.mascot)spinUp();
  if(n===2)renderMascot("mascot2");if(n===3)drawChart();if(n===4)renderVersions();if(n===5)renderBridges();if(n===9)renderFinale();
  say(n);openSheet("s-"+n);
}
function renderMap(){const ok=S.done.length===8;const ev=CAMPAIGN[S.world];
  // Pre-flight (workstream 0) only exists on the campus; the other islands start at stop 1.
  const preflight=S.world==="campus"?`<button class="date" onclick="openCh(0)">Before the evening, Pre-flight<br><span class="small" style="opacity:.75">Install Claude Code, git, Obsidian. 20 minutes, alone.</span></button>`:"";
  $("plotlist").innerHTML=`<div class="evening">${ev.title}</div><p class="small muted">${ev.blurb}</p>`+preflight+CH.map((c,i)=>{const k=i+1,done=S.done.includes(k),locked=k>1&&!S.done.includes(k-1);
    return `<button class="date${done?' pick':''}" ${locked?'disabled':''} onclick="openCh(${k})">${done?icon("check"):""}${c.h}, ${c.n}${done?" (delivered)":locked?" (blocked by dependency)":""}<br><span class="small" style="opacity:.75">${c.d}</span></button>`}).join("")+
    (S.world==="campus"?`<button class="date" ${ok?'':'disabled'} onclick="openCh(9)">${icon("milestone")}Calendar alignment${ok?"":" (pending eight OKRs)"}</button>`:"")+
    `<div class="card"><h3>${icon("users")}Your path: the mentors</h3><p class="small muted">People you met on the islands, and what you chose. Tap to revisit or change your mind.</p>`+MENTORS.map(m=>{const st=S.path[m.id];return `<div class="pathrow"><span><b>${m.name}</b> <span class="muted">· ${WORLDS[m.world].name}</span></span><span style="display:flex;gap:6px;align-items:center"><span class="st ${st||''}">${st==="deep"?"on path":st==="skip"?"skipped":"not met"}</span><button onclick="openMentor('${m.id}')" style="padding:4px 10px;font-size:12px">Open</button></span></div>`}).join("")+`</div>`+
    `<div class="card"><h3>${icon("compass")}Artifacts on the island</h3><p class="small muted">Ten things that each explain one idea. Walk up to a yellow ring, or open one here.</p>`+ARTIFACTS.map(a=>`<div class="pathrow"><span><b>${a.name}</b> <span class="muted">· ${a.concept}</span></span><span style="display:flex;gap:6px;align-items:center"><span class="st ${S.artifacts.includes(a.id)?'deep':''}">${S.artifacts.includes(a.id)?"found":"not yet"}</span><button onclick="openArtifact('${a.id}')" style="padding:4px 10px;font-size:12px">Open</button></span></div>`).join("")+`</div>`+
    `<div class="card"><h3>${icon("flag")}The campaign</h3>`+Object.keys(CAMPAIGN).map(k=>`<div class="pathrow"><span><b>${CAMPAIGN[k].title}</b><br><span class="muted small">${WORLDS[k].name}</span></span><span style="display:flex;gap:6px;align-items:center"><span class="st ${(S.doneW[k]||[]).length===8?'deep':''}">${(S.doneW[k]||[]).length}/8</span><button onclick="setWorld('${k}');closeSheet()" style="padding:4px 10px;font-size:12px">Go</button></span></div>`).join("")+`</div>`;
}
window.claim=function(n){
  if(!S.done.includes(n)){S.done.push(n);save();placeBuilding(n,true);applySky(S.done.length,false);hud();closeSheet();say(S.done.length===8?"fin":"done");lastSay="done";return}
  closeSheet()};


/* ---------------- vault (mini Obsidian) ---------------- */
