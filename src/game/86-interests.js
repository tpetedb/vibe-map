// What you want to learn: the eleven shelves of the tech tree as a choice.
// State is data. S.interests holds the chosen shelf ids; null means the
// player has not answered yet, so config/camp.toml (CONFIG.interests) speaks.
// An empty array is a real answer and means everything.
//
// Nothing is ever hidden or locked by a choice. Interests only change what is
// offered first: the tree and the search put chosen shelves in front and dim
// the rest, the Roadmap suggests topics from them, grow mode gives their
// basics a head start, and matching artifacts, mentors and items get a dot.
// The thirty-two stops stay the spine for everyone.
function interestList(){const s=S.interests;return Array.isArray(s)?s:((CONFIG&&CONFIG.interests)||[])}
function interestsAll(){return interestList().length===0}
function wantsShelf(c){return interestsAll()||interestList().indexOf(c)>=0}
function interestAnswered(){return Array.isArray(S.interests)}
function shelfName(c){const row=(typeof CATS==="undefined"?[]:CATS).find(x=>x[0]===c);return row?row[1]:c}
// The shelf a tree topic sits on, by its note title. TREE is the generated
// map of shelf to topics, so this never needs a second list.
function shelfOfTopic(title){if(typeof TREE==="undefined")return null;
  const keys=Object.keys(TREE);for(let i=0;i<keys.length;i++){if(TREE[keys[i]].some(t=>t.n===title))return keys[i]}
  return null}
// The first chosen shelf a thing touches, for the small marker. `links` is a
// list of note titles (artifacts), `shelf` a shelf id (mentors), `topic` a
// tree id (items, resolved through its note title by the caller).
function matchedShelf(titles){if(interestsAll())return null;
  for(let i=0;i<titles.length;i++){const c=shelfOfTopic(titles[i]);if(c&&wantsShelf(c))return c}
  return null}
function interestDot(c){return c?`<span class="idot" title="On your shelf: ${shelfName(c)}" style="background:${CAT_COL[c]||"var(--accent)"}"></span>`:""}
function setInterests(list){S.interests=list.slice();save();track("interests",list.join(",")||"all");
  if(typeof renderOnboarding==="function"&&$("onboard"))renderOnboarding();
  if($("s-settings")&&$("s-settings").classList.contains("on"))renderSettings();
  if($("vtree")&&$("vtree").classList.contains("on"))renderTree()}
window.toggleInterest=function(c){const cur=interestList().slice();const at=cur.indexOf(c);
  if(at>=0)cur.splice(at,1);else cur.push(c);setInterests(cur)};
window.clearInterests=function(){setInterests([])};
window.presetInterests=function(){setInterests((CONFIG&&CONFIG.personaInterests)||[])};
// The chips, one per shelf plus Everything, used on the title screen and in
// Settings so the two can never drift.
function interestChips(){const all=interestsAll();
  return `<div class="choices shelves"><button class="choice${all?" on":""}" onclick="clearInterests()">Everything</button>`+
    (typeof CATS==="undefined"?[]:CATS).map(([c,n])=>`<button class="choice${!all&&wantsShelf(c)?" on":""}" onclick="toggleInterest('${c}')" title="${esc(n)}"><i style="background:${CAT_COL[c]}"></i>${esc(n)}</button>`).join("")+
    `</div>`}
function interestSummary(){return interestsAll()?"Everything. Nothing is hidden either way; a choice only changes what comes first.":
  interestList().map(shelfName).join(", ")+". The rest stays open, just dimmed."}
function presetRow(){const p=(CONFIG&&CONFIG.personaInterests)||[];if(!p.length)return "";
  return `<p class="small muted">Your persona (${esc(CONFIG.persona)}) usually picks ${p.map(shelfName).join(", ")}. <button class="link" onclick="presetInterests()">Use that preset</button></p>`}
// Where to start on the shelves you chose: the shallowest topics first, six
// at most. Derived from TREE every time, so a new topic appears here by itself.
// The Roadmap card: what you chose and where to start on it. Every button
// opens the topic's vault note, so the card adds no state of its own.
function interestCard(){const start=interestStarters(6);
  return `<div class="card"><h3>${icon("git-branch")}What you want to learn</h3>`+
    `<p class="small muted">${interestSummary()}</p>`+interestChips()+
    `<p class="small muted">Start here:</p><div class="choices">`+
    start.map(t=>`<button class="choice" onclick="openNote('${t.n.replace(/'/g,"\\'")}')"><i style="background:${CAT_COL[t.c]}"></i>${esc(t.n)}</button>`).join("")+
    `</div></div>`}
function interestStarters(n){const out=[];
  (typeof CATS==="undefined"?[]:CATS).filter(([c])=>wantsShelf(c)).forEach(([c])=>{
    (TREE[c]||[]).forEach(t=>out.push({c:c,n:t.n,d:t.d}))});
  out.sort((a,b)=>a.d-b.d);return out.slice(0,n||6)}
