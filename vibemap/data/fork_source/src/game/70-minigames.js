// The demos that survived the audit in docs/adr/0005-mini-games.md. Each one
// leaves the player with something they keep: a prompt they can paste, the
// difference a scoped ask makes, a schema that breaks when you rename a
// column, a rollback, a connector, a graph. Nothing here rolls dice.

/* ---- Workstream 1: the three sentences become a prompt ---- */
// The guardrail is the one Tom imposes in the lesson, so the panel and the
// lesson cannot drift apart.
const GUARDRAIL = "Keep it to a single file called index.html, no external libraries, no frameworks. Keep score. When you are done, tell me how to open it.";
window.pitchTyped=function(v){S.pitch=v;save();renderPitch()};
// One copy helper for every Copy button. A refused clipboard is not silence:
// the text is selected so it can be copied by hand, and the button says so.
// srcEl is the element holding the text, so the fallback can select it.
function copyText(text,btn,label,srcEl){
  const done=msg=>{btn.textContent=msg;setTimeout(()=>{btn.textContent=label},2500)};
  const fallback=()=>{if(srcEl&&window.getSelection){const r=document.createRange();r.selectNodeContents(srcEl);
      const sel=getSelection();sel.removeAllRanges();sel.addRange(r)}
    done("Selected, press Cmd C")};
  if(navigator.clipboard&&navigator.clipboard.writeText)
    navigator.clipboard.writeText(text).then(()=>done("Copied"),fallback);
  else fallback()}
window.copyPitch=function(){copyText($("pitch-out").textContent,$("pitch-copy"),"Copy the prompt",$("pitch-out"))};
function renderPitch(){const out=$("pitch-out");if(!out)return;const box=$("pitch");if(box&&box.value!==(S.pitch||""))box.value=S.pitch||"";
  const v=(S.pitch||"").trim();
  out.textContent=v?`Build a small browser game. ${v}\n\n${GUARDRAIL}`:"Type your three sentences above and the prompt appears here, with the guardrail already attached.";
  const n=v?v.split(/[.!?]+/).filter(x=>x.trim()).length:0;
  $("pitch-note").textContent=!v?"":n<3?`That is ${n} sentence${n===1?"":"s"}. Three is the ask: what it is, who plays it, how you win.`:"Three sentences and one hard constraint. That is the whole prompt; the rest is watching it land.";}

/* ---- Workstream 2: the same card, asked for two ways ---- */
// One demo component, two change requests. The precise one changes exactly
// what it named; the vague one is free to change everything else too.
const CARD0={title:"Tonight's scores",accent:"#0067A5",cols:["Player","Score"],badge:false,serif:false};
let card=Object.assign({},CARD0);
// Both asks start from the same card, which is what makes them comparable:
// the precise one changes the one thing it named, the vague one everything
// it was not told to leave alone.
window.speak=function(precise){
  card=precise?Object.assign({},CARD0,{badge:true})
    :{title:"Impactful Scores Experience",accent:"#FF8C1A",cols:["Player"],badge:false,serif:true};
  $("speak-out").textContent=precise
    ?"One change, delivered as scoped: a badge. Title, colour, columns and font untouched, and a one-line summary back."
    :"It maximised impact against its own idea of impact: new title, new colour, a decorative font, and the score column gone. Nothing was out of scope, because you put nothing out of scope.";
  renderCard()};
window.resetCard=function(){card=Object.assign({},CARD0);$("speak-out").textContent="Back to the version you started from.";renderCard()};
function renderCard(){const el=$("card-demo");if(!el)return;
  el.innerHTML=`<div class="demo-card${card.serif?" serif":""}" style="border-color:${card.accent}">
<h4 style="color:${card.accent}">${card.title}${card.badge?'<span class="demo-badge">new</span>':""}</h4>
<table><thead><tr>${card.cols.map(c=>`<th>${c}</th>`).join("")}</tr></thead>
<tbody>${[["Lotte",1240],["Frank",980],["Rolinda",1810]].map(r=>`<tr>${card.cols.map((c,i)=>`<td>${r[i]}</td>`).join("")}</tr>`).join("")}</tbody></table></div>`}

/* ---- Workstream 3: the column names are the contract ---- */
// The schema demo runs the same query against the same rows; renaming one
// column is enough to break it, with the error DuckDB actually prints.
const SCHEMA=["played_at","player","score","duration_s"];
const ROWS=[["2026-09-17T20:10","Lotte",1240,95],["2026-09-17T20:19","Frank",980,71],["2026-09-17T20:31","Rolinda",1810,120]];
const QUERY="select player, max(score) as best\nfrom 'workspace/data/scores.csv'\ngroup by player order by best desc";
let scoreCol="score";
window.renameColumn=function(to){scoreCol=to;renderSchema()};
function renderSchema(){const el=$("schema");if(!el)return;const broken=scoreCol!=="score";
  const cols=SCHEMA.map(c=>c==="score"?scoreCol:c);
  el.innerHTML=`<table class="csv"><thead><tr>${cols.map(c=>`<th${c===scoreCol&&broken?' class="changed"':""}>${c}</th>`).join("")}</tr></thead>
<tbody>${ROWS.map(r=>`<tr>${r.map(v=>`<td>${v}</td>`).join("")}</tr>`).join("")}</tbody></table>
<pre class="sql">${QUERY}</pre>
<pre class="out${broken?" err":""}" id="schema-out">${broken
  ?`Binder Error: Referenced column "score" not found in FROM clause!\nCandidate bindings: "${scoreCol}"`
  :"player    best\nRolinda   1810\nLotte     1240\nFrank      980"}</pre>
<p class="small muted">${broken
  ?"One rename, every query downstream red. Nothing is corrupt; the contract simply changed and nobody was told."
  :"Four column names, in this order, are the contract. The game writes them, the queries read them."}</p>`}

/* ---- Workstream 4: commits are snapshots, rollback is always on ---- */
// An empty box is a refusal with a reason, never a button that does nothing.
function releaseMsg(t){const el=$("release-msg");if(el)el.textContent=t||""}
window.commit=function(){const t=$("release").value.trim();
  if(!t){releaseMsg("Nothing to commit: the release note is empty. Say what this release is, then tag it.");return}
  releaseMsg("");S.versions.push({t,at:new Date().toLocaleTimeString([],{hour:"2-digit",minute:"2-digit"})});save();renderVersions();hud()};
window.ruin=function(){$("release").value="A smal scorng board that rnks the team by cofee consmption and also everything is now in Comic Sans. Sev 1. Paging Tom."};
window.revert=function(i){$("release").value=S.versions[i].t};
function renderVersions(){$("versions").innerHTML=S.versions.length?S.versions.map((v,i)=>`<li><span class="muted">v${i+1}, ${esc(v.at)}: ${esc(String(v.t).slice(0,44))}${v.t.length>44?"…":""}</span><button onclick="revert(${i})">Roll back</button></li>`).join(""):`<li class="muted small">No releases tagged yet. Commit one, trigger a P1, then roll back.</li>`}

/* ---- Workstream 5: a connector is a plug, and unplugging is the point ---- */
const B={cal:"Integrated. It can now read Thursday and pre-populate the 10:00 agenda.",files:"Integrated. It can now surface the deck you lost in March.",mail:"Integrated. It can now distil a 40-message thread into three action items."};
window.bridge=function(k){S.bridges[k]=!S.bridges[k];save();renderBridges();hud()};
function renderBridges(){for(const k in B){const el=$("b-"+k),sp=el.querySelector("span");el.classList.toggle("on",!!S.bridges[k]);sp.textContent=S.bridges[k]?B[k]:"Not integrated";sp.className=S.bridges[k]?"":"muted"}}

/* ---- Workstream 6: notes with links are a graph ---- */
// The player's name is the one node here that is not ours: it can arrive in
// an imported progress code, so it is text like any other field.
window.weave=function(){const nodes=[["Tonight",200,150],[esc(playerLabel()||"You"),90,60],["Playbook",310,60],["Data warehouse",60,220],["Releases",200,275],["Integrations",340,220],["Rolinda's questions",200,25],["Q4 roadmap",330,275]];
  const links=[[0,1],[0,2],[0,3],[0,4],[0,5],[0,6],[1,2],[3,4],[4,7],[2,7],[5,7],[6,2]];const svg=$("web");svg.classList.remove("woven");
  svg.innerHTML=links.map(([a,b])=>`<line x1="${nodes[a][1]}" y1="${nodes[a][2]}" x2="${nodes[b][1]}" y2="${nodes[b][2]}"/>`).join("")+nodes.map((n,i)=>`<g style="animation-delay:${i*.12}s"><circle cx="${n[1]}" cy="${n[2]}" r="${i===0?13:8}"/><text x="${n[1]}" y="${n[2]+(i===6?-16:22)}" text-anchor="middle">${n[0]}</text></g>`).join("");
  requestAnimationFrame(()=>svg.classList.add("woven"))};
