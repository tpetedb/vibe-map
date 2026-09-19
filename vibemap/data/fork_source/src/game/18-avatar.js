// The avatar: what a character can do (a pose, a laptop, something to wear)
// and what the player earns for doing it (achievements, wearables).
// State is data: S.items, S.ach and S.wear are the whole record and the scene,
// the backpack panel and the progress code are rebuilt from them. A character
// only carries a pose and a wardrobe; the behaviour lives here.

// Every list this module keeps lives under its own key in S, created on first
// use so an older save, or a reset, never has to be migrated.
function sl(k){if(!Array.isArray(S[k]))S[k]=[];return S[k]}
function totalDone(){return Object.values(S.doneW||{}).reduce((n,v)=>n+(v||[]).length,0)}

/* ---------------- poses ---------------- */
// A pose is a name. poseChar puts the limbs where the name says, once a frame,
// and answers true when it has taken the frame over from the walk cycle.
// A timed pose (wave, cheer) falls back to standing on its own.
const POSE_MS={wave:1.6,cheer:2.2};
// Sitting on the ground, and on a seat; the walker's hips are at .7 standing.
const GROUND_SEAT=.34,HIP=.7;
function setPose(c,p,seat){if(!c)return;c.pose=p;c.poseT=0;c.seatH=seat===undefined?c.seatH:seat;
  if(p==="sit")return;
  // Standing again clears what only a pose ever touches, so the walk cycle
  // starts from the same body every time.
  c.poseY=0;c.head.rotation.x=0;c.rArm.rotation.z=0;if(c.lap)c.lap.visible=false}
function isSitting(c){return !!c&&c.pose==="sit"}
function poseChar(c,dt,t){
  const p=c.pose;
  if(p==="sit"){
    const h=(c.seatH||GROUND_SEAT)-HIP;c.poseY=h;c.g.position.y=h;
    c.lLeg.rotation.x=-1.5;c.rLeg.rotation.x=-1.5;
    const lap=c.lap||addLaptop(c);lap.visible=true;
    // Typing: both forearms tap out of phase, a hand's width apart.
    const k=Math.sin(t*9+(c.g.position.x||0))*.07;
    c.lArm.rotation.x=-1.2+k;if(!c.raised)c.rArm.rotation.x=-1.2-k;
    c.head.rotation.x=.2;c.head.rotation.y=Math.sin(t*.6)*.06;
    return true}
  if(p==="wave"||p==="cheer"){
    c.poseT+=dt;if(c.poseT>POSE_MS[p]){setPose(c,"stand");return false}
    const s=Math.sin(c.poseT*9);
    if(p==="wave"){c.rArm.rotation.x=-2.6;c.rArm.rotation.z=s*.35;c.lArm.rotation.x=Math.sin(t*2)*.08}
    else{c.lArm.rotation.x=-2.7;c.rArm.rotation.x=-2.7;c.g.position.y=Math.abs(s)*.22}
    c.head.rotation.y=Math.sin(t*3)*.2;return true}
  if(p==="carry"){
    // Rolinda serving: one arm out, the tray steady, a slow shift of weight.
    c.rArm.rotation.x=-1.5;c.lArm.rotation.x=Math.sin(t*1.4)*.1;
    c.g.position.y=Math.sin(t*1.6)*.02;c.head.rotation.y=Math.sin(t*.5)*.25;return true}
  return false;
}
window.wave=function(){setPose(chars.lotte,"wave")};
// The cheer the whole party does when a stop lands.
function cheer(){setPose(chars.lotte,"cheer");setPose(chars.tom,"cheer")}

/* ---------------- the laptop ---------------- */
// An original low-poly clamshell: two thin slabs in aluminium grey with a lit
// panel between them, no marks on the lid. The geometries and the three
// materials are built once and shared by every character that sits down, so a
// second laptop costs no memory and no new material.
let LAPTOP=null;
function laptopParts(){if(LAPTOP)return LAPTOP;
  LAPTOP={
    base:new T.BoxGeometry(.62,.04,.44),
    lid:new T.BoxGeometry(.62,.42,.03),
    screen:new T.PlaneGeometry(.54,.34),
    keys:new T.BoxGeometry(.46,.012,.22),
    shell:mat(PALETTE.muted,{roughness:.35,metalness:.5}),
    dark:mat(PALETTE.black),
    lit:mat(PALETTE.blueBright,{emissive:PALETTE.blueBright,emissiveIntensity:.9}),
  };return LAPTOP}
// lite is the version an onlooker gets: the lid is the lit panel and the keys
// are left off, which is two draw calls instead of four at the distance a
// mentor is ever seen from.
function laptop(lite){const P=laptopParts(),g=new T.Group();
  const base=new T.Mesh(P.base,P.shell);base.castShadow=true;g.add(base);
  const lid=new T.Mesh(P.lid,lite?P.lit:P.shell);lid.position.set(0,.2,-.24);lid.rotation.x=-.18;lid.castShadow=true;g.add(lid);
  if(lite)return g;
  const keys=new T.Mesh(P.keys,P.dark);keys.position.set(0,.028,.06);g.add(keys);
  const scr=new T.Mesh(P.screen,P.lit);scr.position.set(0,.2,-.21);scr.rotation.x=-.18;g.add(scr);
  // After dark the screen is what lights the face, which is the joke. A light
  // costs no draw call, and the lid hides it from everything behind.
  const glow=new T.PointLight(PALETTE.blueBright,.9,3.2);glow.position.set(0,.34,-.08);g.add(glow);
  return g}
// The lap: where the clamshell sits once the thighs are horizontal.
function addLaptop(c){const g=laptop(c!==chars.lotte);g.position.set(0,.9,.42);c.g.add(g);c.lap=g;return g}

/* ---------------- wearables ---------------- */
// One per slot, unlocked by an achievement. The mesh is built from the same
// boxes as the walker, in the palette, so a hat reads at a glance from above.
const WEAR=ITEMS.wearables;
function wearOwned(id){const w=WEAR.find(x=>x.id===id);return !!w&&sl("ach").includes(w.by)}
function wearMesh(id){const g=new T.Group();
  if(id==="cap"){g.add(box(.86,.18,.86,PALETTE.blue,0,2.54,0));g.add(box(.52,.06,.36,PALETTE.blue,0,2.48,.5))}
  else if(id==="beanie"){g.add(box(.88,.32,.88,PALETTE.red,0,2.56,0));g.add(sph(.14,PALETTE.text,0,2.78,0,6))}
  else if(id==="shades"){g.add(box(.78,.16,.08,PALETTE.black,0,2.12,.44))}
  else if(id==="jacket"){g.add(box(.98,.94,.58,PALETTE.green,0,1.15,0))}
  else if(id==="backpack"){g.add(box(.62,.72,.28,PALETTE.orange,0,1.25,-.4));[-.26,.26].forEach(x=>g.add(box(.1,.8,.1,PALETTE.orangeBright,x,1.3,.2)))}
  else if(id==="lanyard"){[-.2,.2].forEach(x=>g.add(box(.07,.44,.07,PALETTE.yellow,x,1.5,.2)));g.add(box(.34,.24,.05,PALETTE.text,0,1.22,.28))}
  else return null;
  return g}
// A character's wardrobe is rebuilt from the list, never patched in place.
function applyWear(c,ids){if(!c)return;if(c.wearG)c.g.remove(c.wearG);
  const g=new T.Group();(ids||[]).forEach(id=>{const m=wearMesh(id);if(m)g.add(m)});
  c.g.add(g);c.wearG=g;fixColors(g)}
window.toggleWear=function(id){const w=WEAR.find(x=>x.id===id);if(!w||!wearOwned(id))return;
  const worn=sl("wear");const i=worn.indexOf(id);
  if(i>=0)worn.splice(i,1);
  else{WEAR.filter(x=>x.slot===w.slot).forEach(x=>{const j=worn.indexOf(x.id);if(j>=0)worn.splice(j,1)});worn.push(id)}
  save();applyWear(chars.lotte,worn);renderPack("wardrobe");if(typeof renderOnboarding==="function")renderOnboarding()};

/* ---------------- achievements ---------------- */
// Six mirror the CLI's badges (vibemap/quests.py) so the two agree on what an
// evening was worth; the rest are the island's own. Each answers when() from
// state, except the ones only the moment knows, which unlock() records.
let speedRun=false,lastClaimAt=0;
const ACH=[
  {id:"first-light",name:"First light",what:"The first stop delivered.",when:()=>totalDone()>=1},
  {id:"full-evening",name:"Full evening",what:"Eight of eight on one island.",when:()=>Object.values(S.doneW||{}).some(v=>(v||[]).length>=8)},
  {id:"campaign",name:"Campaign",what:"All thirty-two stops across the four islands.",when:()=>totalDone()>=32},
  {id:"collector",name:"Collector",what:"Every artifact inspected.",when:()=>(S.artifacts||[]).length>=ARTIFACTS.length},
  {id:"builder",name:"Builder",what:"Every artifact built for real, not only inspected.",when:()=>(S.artifactsBuilt||[]).length>=ARTIFACTS.length},
  {id:"mentored",name:"Mentored",what:"Every mentor's exercise verified.",when:()=>(S.mentors||[]).length>=MENTORS.length},
  {id:"mentor-verified",name:"Verified",what:"A mentor's exercise checked in your camp.",when:()=>(S.mentors||[]).length>=1},
  {id:"first-sit",name:"First sit",what:"You sat down and opened the laptop.",when:()=>false},
  {id:"ten-items",name:"Ten things",what:"Ten collectibles picked up.",when:()=>sl("items").length>=10},
  {id:"island-items",name:"Clean sweep",what:"Every collectible on one island.",when:()=>Object.keys(WORLDS).some(w=>{const all=ITEMS.items.filter(i=>i.world===w);return all.length>0&&all.every(i=>sl("items").includes(i.id))})},
  {id:"night-owl",name:"Night owl",what:"On the island after eleven at night.",when:()=>new Date().getHours()>=23},
  {id:"speed-run",name:"Speed run",what:"Two stops inside five minutes.",when:()=>speedRun},
];
function unlock(id){const a=ACH.find(x=>x.id===id);if(!a||sl("ach").includes(id))return false;
  sl("ach").push(id);save();
  const w=WEAR.find(x=>x.by===id);
  toast(icon("trophy")+"Achievement: "+a.name,a.what+(w?" Unlocked: the "+w.name.toLowerCase()+", in the Backpack.":""));
  if(typeof track==="function")track("achievement",id);
  return true}
function achCheck(){ACH.forEach(a=>{if(a.when()&&!sl("ach").includes(a.id))unlock(a.id)})}

/* ---------------- toast ---------------- */
// One stack, created on demand so the page keeps its markup. A toast is a
// message, never state: it says what just happened and goes away.
// The count is what a test waits for: a toast removes itself after a few
// seconds, so looking for the element is a race on a loaded machine.
let toastN=0;
window.__toasts=()=>toastN;
function toast(title,body){
  toastN++;
  let el=$("toast");
  if(!el){el=document.createElement("div");el.id="toast";el.setAttribute("aria-live","polite");document.body.appendChild(el)}
  const n=document.createElement("div");n.className="tst";
  n.innerHTML=`<b>${title}</b><span>${body}</span>`;el.appendChild(n);fx(n);
  setTimeout(()=>n.remove(),5000)}

/* ---------------- the backpack panel ---------------- */
// The tech tree topic a collectible points at, by its note title.
function topicName(id){for(const k in TREE){const t=TREE[k].find(x=>x.id===id);if(t)return t.n}return null}
window.openTopic=function(id){const n=topicName(id);if(n)openNote(n)};
let packTab="inventory";
window.openPack=function(tab){renderPack(tab||packTab);openSheet("s-pack")};
window.renderPack=renderPack;
function renderPack(tab){packTab=tab||packTab;const got=sl("items"),ach=sl("ach"),worn=sl("wear");
  const tabs=[["inventory","Inventory"],["achievements","Achievements"],["wardrobe","Wardrobe"]]
    .map(([k,l])=>`<button class="${packTab===k?"pick":""}" onclick="renderPack('${k}')">${l}</button>`).join("");
  let body="";
  if(packTab==="inventory"){
    body=`<p class="small muted">${got.length} of ${ITEMS.items.length} picked up. Walk over one to collect it; each explains one idea and opens its topic in the tech tree.</p>`+
      Object.keys(WORLDS).map(w=>{const list=ITEMS.items.filter(i=>i.world===w);
        const mine=list.filter(i=>got.includes(i.id));
        return `<div class="card"><h3>${WORLDS[w].name}</h3><p class="small muted">${mine.length} of ${list.length}</p>`+
          mine.map(i=>`<div class="pathrow"><span><b>${i.name}</b><br><span class="muted small">${i.concept}</span></span><button onclick="openTopic('${i.topic}')" style="padding:4px 10px;font-size:12px">Topic</button></div>`).join("")+
          (mine.length<list.length?`<div class="pathrow"><span class="muted small">${list.length-mine.length} still out there, along the paths and on the annexes.</span></div>`:"")+`</div>`}).join("")}
  else if(packTab==="achievements"){
    body=`<p class="small muted">${ach.length} of ${ACH.length} unlocked. Six of them are the badges the terminal hands out, so a progress code keeps the two in step.</p>`+
      ACH.map(a=>`<div class="pathrow"><span><b>${a.name}</b><br><span class="muted small">${a.what}</span></span><span class="st ${ach.includes(a.id)?"deep":""}">${ach.includes(a.id)?"unlocked":"locked"}</span></div>`).join("")}
  else{
    body=`<p class="small muted">Earned by achievements, worn one per slot. What you wear shows on the walker, on the title screen and in the terminal.</p>`+
      WEAR.map(w=>`<div class="pathrow"><span><b>${w.name}</b><br><span class="muted small">${w.slot} · from ${(ACH.find(a=>a.id===w.by)||{}).name}</span></span>`+
        (wearOwned(w.id)
          ?`<button class="${worn.includes(w.id)?"primary":""}" onclick="toggleWear('${w.id}')" style="padding:4px 10px;font-size:12px">${worn.includes(w.id)?"Worn":"Wear"}</button>`
          :`<span class="st">locked</span>`)+`</div>`).join("")}
  $("s-pack").innerHTML=`<h2>Backpack</h2><div class="row packtabs">${tabs}</div>${body}`;
  iconize($("s-pack"))}

/* ---------------- the frame ---------------- */
// One call a frame from the animation loop: sitting, picking things up and the
// achievements that follow. Everything it needs is already computed there.
let wantSit=false,avatarWired=false,achT=0;
function wireAvatar(){if(avatarWired)return;avatarWired=true;
  // The key is caught on its own event rather than sampled in the loop: a tap
  // can start and end between two frames on a slow machine.
  addEventListener("keydown",e=>{if(e.key.toLowerCase()!=="x"||e.metaKey||e.ctrlKey)return;
    const el=document.activeElement;if(el&&/^(input|textarea|select)$/i.test(el.tagName))return;
    wantSit=true});
  // A claim is the party's moment, so the cheer hangs off the real entry point
  // rather than off a copy of the rule that decides a stop is done.
  const claimed=window.claim;
  window.claim=function(n){const before=(S.done||[]).includes(n);claimed.apply(this,arguments);
    if(before||!(S.done||[]).includes(n))return;
    const now=Date.now();if(lastClaimAt&&now-lastClaimAt<300000)speedRun=true;lastClaimAt=now;
    cheer();achCheck()};
  const h=$("hint");if(h&&h.textContent.indexOf("sit")<0)h.textContent+=" · x to sit";
  setPose(chars.rolinda,"carry");
  applyWear(chars.lotte,sl("wear"));
}
function toggleSit(){const L=chars.lotte;if(!L)return;
  if(isSitting(L)){setPose(L,"stand");return}
  // Sitting is a full stop: with no speed left the frame loop skips the
  // collision push, so a walker on a bench stays on it.
  if(L.vel)L.vel.set(0,0,0);hasTarget=false;if(marker)marker.material.opacity=0;
  const s=nearestSeat(L.g.position);
  if(s){L.g.position.set(s.x,0,s.z);L.g.rotation.y=s.face;setPose(L,"sit",s.h)}
  else setPose(L,"sit",GROUND_SEAT);
  unlock("first-sit")}
function tickAvatar(dt,t,sp){
  wireAvatar();
  const L=chars.lotte;if(!L)return;
  if(wantSit){wantSit=false;if(started)toggleSit()}
  // Standing again is decided on the speed the frame ends with, not the speed
  // it began with: sitting down is a full stop, so the walk that carried the
  // walker to the seat must not stand him straight back up in the same frame.
  const speed=L.vel?Math.hypot(L.vel.x,L.vel.z):sp;
  if(isSitting(L)&&(speed>.35||wantJump||L.jy>0))setPose(L,"stand");
  // Mentors work at their spot: the animation loop moves them, so their pose
  // is applied here, where the loop has not yet touched them this frame.
  (props.mentors||[]).forEach(c=>{if(isSitting(c))poseChar(c,dt,t)});
  tickItems(dt,t);
  // The derived achievements read the whole state, so they are answered about
  // once a second rather than every frame; the earned-by-a-moment ones unlock
  // where they happen.
  achT+=dt;if(achT>1){achT=0;achCheck()}
}
