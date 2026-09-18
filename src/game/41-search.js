// The command palette: one box over the lists the game already holds, so a
// stop, a note, a tree topic, a mentor, an artifact or an item is two
// keystrokes away. Cmd K or Ctrl K, and the Search button in the HUD.
// Nothing here is state: the index is derived from the same data the panels
// render, every time the box opens.
let PAL=[],PALHITS=[],palSel=0;
function palIndex(){
  const out=[];
  const stopLabel=CONFIG.theme.stopLabel||"Stop";
  CH.forEach((c,i)=>out.push({k:stopLabel,t:c.h+", "+c.n,s:c.d,go:()=>openCh(i+1)}));
  const unlocked=typeof computeUnlocked==="function"?computeUnlocked():null;
  const topics={};
  if(typeof TREE!=="undefined")Object.keys(TREE).forEach(c=>TREE[c].forEach(t=>topics[t.n]=c));
  Object.keys(typeof NOTES==="undefined"?{}:NOTES).forEach(n=>{
    if(unlocked&&!unlocked.has(n))return;
    out.push({k:topics[n]?"Topic":"Note",s:topics[n]?"Tech tree":"Vault note",t:n,go:()=>openNote(n)})});
  MENTORS.forEach(m=>out.push({k:"Mentor",t:m.name,s:m.role+" · "+WORLDS[m.world].name,go:()=>openMentor(m.id)}));
  (typeof ARTIFACTS==="undefined"?[]:ARTIFACTS).forEach(a=>out.push({k:"Artifact",t:a.name,s:a.concept,go:()=>openArtifact(a.id)}));
  (typeof ITEMS==="undefined"?{items:[]}:ITEMS).items.forEach(i=>out.push({k:"Item",t:i.name,s:i.concept,go:()=>openTopic(i.topic)}));
  return out}
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
  if(!PALHITS.length){list.innerHTML='<p class="pal-empty muted small">Nothing matches. Try a stop, a mentor, a note or an artifact.</p>';return}
  list.innerHTML=PALHITS.map((r,i)=>`<button class="pal-row${i===palSel?" sel":""}" role="option" aria-selected="${i===palSel}" data-i="${i}"><span class="pal-what">${esc(r.t)}<span class="pal-sub">${esc(r.s||"")}</span></span><span class="pal-kind">${esc(r.k)}</span></button>`).join("");
  list.querySelectorAll(".pal-row").forEach(b=>b.onclick=()=>palGo(+b.dataset.i));
  const sel=list.querySelector(".pal-row.sel");if(sel)sel.scrollIntoView({block:"nearest"})}
window.palTyped=function(){const q=$("pal-q").value.trim().toLowerCase();
  PALHITS=(q?PAL.map(r=>[palScore(r,q),r]).filter(([s])=>s>=0).sort((a,b)=>a[0]-b[0]).map(([,r])=>r):PAL.slice()).slice(0,40);
  palSel=0;palRender()};
function palGo(i){const r=PALHITS[i];if(!r)return;closePalette();r.go()}
window.palKey=function(e){
  if(e.key==="ArrowDown"||e.key==="ArrowUp"){e.preventDefault();
    if(!PALHITS.length)return;
    palSel=(palSel+(e.key==="ArrowDown"?1:PALHITS.length-1))%PALHITS.length;palRender();return}
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
