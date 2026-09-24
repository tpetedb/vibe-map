// The command palette: one box over the lists the game already holds, so a
// stop, a note, a tree topic, a mentor, an artifact or an item is two
// keystrokes away. Cmd K or Ctrl K, and the Search button in the HUD.
// Nothing here is state: the index is derived from the same data the panels
// render, every time the box opens.
let PAL=[],PALHITS=[],palSel=0;
function palIndex(){
  const out=[];
  const stopLabel=CONFIG.theme.stopLabel||"Stop";
  // n is the stop's number on this island: the row that has one can be walked
  // to as well as opened.
  CH.forEach((c,i)=>out.push({k:stopLabel,t:c.h+", "+c.n,s:c.d,go:()=>openCh(i+1),n:i+1}));
  const unlocked=typeof computeUnlocked==="function"?computeUnlocked():null;
  const topics={};
  if(typeof TREE!=="undefined")Object.keys(TREE).forEach(c=>TREE[c].forEach(t=>topics[t.n]=c));
  Object.keys(typeof NOTES==="undefined"?{}:NOTES).forEach(n=>{
    if(unlocked&&!unlocked.has(n))return;
    out.push({k:topics[n]?"Topic":"Note",s:topics[n]?"Tech tree":"Vault note",t:n,go:()=>openNote(n),c:topics[n]||null})});
  MENTORS.forEach(m=>out.push({k:"Mentor",t:m.name,s:m.role+" · "+WORLDS[m.world].name,go:()=>openMentor(m.id),c:m.shelf||null}));
  (typeof ARTIFACTS==="undefined"?[]:ARTIFACTS).forEach(a=>out.push({k:"Artifact",t:a.name,s:a.concept,go:()=>openArtifact(a.id),c:matchedShelf(a.links)}));
  (typeof ITEMS==="undefined"?{items:[]}:ITEMS).items.forEach(i=>out.push({k:"Item",t:i.name,s:i.concept,go:()=>openTopic(i.topic)}));
  return out}
// A row on a chosen shelf sorts ahead of an equally good one that is not.
// It is a tie-break, never a filter: everything stays in the list.
function palShelf(row){return row.c&&!interestsAll()&&wantsShelf(row.c)?0:1}
// Ranking, shortest rule that reads right: a match at the start beats a match
// in the middle, a match in the title beats one in the line under it.
function palScore(row,q){
  const t=row.t.toLowerCase(),s=(row.s||"").toLowerCase();
  const i=t.indexOf(q);
  if(i===0)return 0;
  if(i>0)return t[i-1]===" "?1:2;
  return s.indexOf(q)>=0?3:-1}
function palRender(){
  const list=$("pal-list");
  if(!PALHITS.length){list.innerHTML='<p class="pal-empty muted small">Nothing matches. Try a stop, a mentor, a note or an artifact.</p>';palWalkSync();return}
  list.innerHTML=PALHITS.map((r,i)=>`<button class="pal-row${i===palSel?" sel":""}" role="option" aria-selected="${i===palSel}" data-i="${i}"><span class="pal-what">${palShelf(r)===0?interestDot(r.c):""}${esc(r.t)}<span class="pal-sub">${esc(r.s||"")}</span></span><span class="pal-kind">${esc(r.k)}</span></button>`).join("");
  list.querySelectorAll(".pal-row").forEach(b=>b.onclick=()=>palGo(+b.dataset.i));
  const sel=list.querySelector(".pal-row.sel");if(sel)sel.scrollIntoView({block:"nearest"});
  palWalkSync()}
/* ---------------- walk me there ---------------- */
// The palette opens a stop; this walks to it, for when the question is where
// on the island it is rather than what the lesson says. It is a button of its
// own rather than a second control inside a row: the list is a listbox, and
// an option with a button inside it is an option a screen reader cannot read
// out as one thing. Built here, the way the map builds its own chrome,
// because the palette's markup belongs to body.html and this does not.
let palWalk=null;
function palWalkBuild(){
  if(palWalk)return;
  palWalk=document.createElement("button");palWalk.type="button";palWalk.id="pal-walk";
  palWalk.title="Shift and Enter";
  palWalk.style.cssText="display:none;margin:var(--space-3) var(--space-4) 0;min-height:44px;align-self:flex-start";
  palWalk.addEventListener("click",()=>palWalkGo());
  // Before the list, not after it: every result is a button, so a control
  // behind forty of them is a control no keyboard reaches.
  const box=$("pal").querySelector(".pal-box");box.insertBefore(palWalk,$("pal-list"))}
// Shown only when the selected row is a stop of the island being walked on,
// so the control is never there with nothing to do.
function palWalkSync(){
  palWalkBuild();
  const r=PALHITS[palSel],n=r&&r.n;
  const can=!!n&&started&&!!PLOT_POS[n-1];
  palWalk.style.display=can?"block":"none";
  if(!can){palWalk.removeAttribute("aria-label");return}
  palWalk.textContent="Walk there";
  palWalk.setAttribute("aria-label","Walk to "+r.t)}
function palWalkGo(){const r=PALHITS[palSel];if(!r||!r.n)return;
  closePalette();walkTo(r.n)}
window.palTyped=function(){const q=$("pal-q").value.trim().toLowerCase();
  PALHITS=(q?PAL.map(r=>[palScore(r,q),r]).filter(([s])=>s>=0).sort((a,b)=>a[0]-b[0]||palShelf(a[1])-palShelf(b[1])).map(([,r])=>r):PAL.slice()).slice(0,40);
  palSel=0;palRender()};
function palGo(i){const r=PALHITS[i];if(!r)return;closePalette();r.go()}
window.palKey=function(e){
  if(e.key==="ArrowDown"||e.key==="ArrowUp"){e.preventDefault();
    if(!PALHITS.length)return;
    palSel=(palSel+(e.key==="ArrowDown"?1:PALHITS.length-1))%PALHITS.length;palRender();return}
  // Shift and Enter walks there instead of opening it, for the hand that is
  // already on the keyboard; the button under the box is the other way.
  if(e.key==="Enter"&&e.shiftKey){e.preventDefault();palWalkGo();return}
  if(e.key==="Enter"){e.preventDefault();palGo(palSel)}};
window.openPalette=function(){closeHudMenu();PAL=palIndex();$("pal-q").value="";palTyped();
  $("pal").classList.add("on");fx($("pal").querySelector(".pal-box"));$("pal-q").focus()};
window.closePalette=function(){$("pal").classList.remove("on")};
// The backdrop is a click target too, so the box closes the way every overlay
// in the game closes.
$("pal").addEventListener("pointerdown",e=>{if(e.target===$("pal"))closePalette()});
addEventListener("keydown",e=>{
  if((e.metaKey||e.ctrlKey)&&e.key.toLowerCase()==="k"){e.preventDefault();
    $("pal").classList.contains("on")?closePalette():openPalette()}});
