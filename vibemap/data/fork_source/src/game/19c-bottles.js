// Messages in a bottle: a few notes washed up on each island's shore, each a
// lesson from the building of this game (ITEMS.bottles). They are deliberately
// not part of the forty collectibles: no count, badge or progress code knows
// them, so finding none of them costs a player nothing.

// Where a bottle lies: on the bearing it names, just inside the shoreline. A
// bearing that falls on a bridge deck or off the land is turned a little until
// it does not, so a new layout cannot strand a bottle in the sea.
function bottleSpot(deg){
  for(const off of [0,10,-10,20,-20,35,-35]){
    const a=(deg+off)*Math.PI/180,r=landReach(W,deg+off)-1.4;
    const x=Math.cos(a)*r,z=Math.sin(a)*r;
    if(r>0&&onLandW(x,z)&&!onBridge(x,z))return {x,z,face:a}}
  return null}

// Two draw calls a bottle: the glass, which has to stay its own transparent
// mesh, and the roll of paper with the cork baked into one. Geometry and
// materials are shared by every bottle.
// Larger than life on purpose: at the fitted camera a real bottle is three pixels.
const BOTTLE_SCALE=2;
let BOTTLEG=null;
function bottleParts(){if(BOTTLEG)return BOTTLEG;
  const pts=[[0,0],[.13,0],[.14,.04],[.14,.3],[.06,.42],[.055,.54],[.07,.55],[.07,.58],[0,.58]]
    .map(([x,y])=>new T.Vector2(x,y));
  BOTTLEG={
    glass:new T.LatheGeometry(pts,9),
    paper:new T.CylinderGeometry(.05,.05,.3,6),
    cork:new T.CylinderGeometry(.05,.05,.07,6),
    glassMat:mat(PALETTE.greenBright,{transparent:true,opacity:.5,roughness:.25,depthWrite:false,
      emissive:PALETTE.greenBright,emissiveIntensity:.3}),
    paperMat:mat(PALETTE.text),corkMat:mat(PALETTE.orange)};
  return BOTTLEG}
function bottleMesh(){const P=bottleParts(),g=new T.Group();
  const paper=new T.Mesh(P.paper,P.paperMat);paper.position.y=.2;
  const cork=new T.Mesh(P.cork,P.corkMat);cork.position.y=.6;
  g.add(paper,cork);mergeStatic(g);
  g.add(new T.Mesh(P.glass,P.glassMat));
  return g}

// Idempotent, like placeItems: it only adds what is missing and not yet found.
function placeBottles(){
  // A rebuilt island has thrown its meshes away: forget what is no longer in
  // the scene, so the bottles of the new island are placed afresh.
  props.bottles=(props.bottles||[]).filter(b=>b.m.parent===scene);
  const got=sl("bottles");
  (ITEMS.bottles||[]).filter(b=>b.world===(S.world||"campus")).forEach(b=>{
    if(got.includes(b.id)||props.bottles.some(x=>x.id===b.id))return;
    const sp=bottleSpot(b.deg);if(!sp)return;
    const m=bottleMesh();
    // Lying on its side, neck towards the sea, half dug into the sand.
    m.rotation.set(0,-sp.face,Math.PI/2-.35);m.position.set(sp.x,.3,sp.z);m.scale.setScalar(BOTTLE_SCALE);
    scene.add(m);props.bottles.push({id:b.id,m,x:sp.x,z:sp.z,p:props.bottles.length})})}

function openBottle(it){const data=(ITEMS.bottles||[]).find(x=>x.id===it.id);
  scene.remove(it.m);props.bottles=props.bottles.filter(x=>x!==it);
  if(!data)return;
  sl("bottles").push(data.id);save();
  toast(icon("compass")+"A message in a bottle: "+esc(data.title),
    esc(data.lesson)+` <a href="#" onclick="openTopic('${esc(data.topic)}');return false">Read the topic</a>`);
  if(typeof track==="function")track("bottle",data.id)}

// A bottle rocks where it lies; it never bobs in the air like a collectible,
// so the two read as different things from a distance.
function tickBottles(dt,t){
  const pos=chars.lotte&&chars.lotte.g.position;if(!pos)return;
  const still=reducedMotion();
  (props.bottles||[]).slice().forEach(it=>{
    if(!still)it.m.rotation.x=Math.sin(t*1.3+it.p*2)*.12;
    if(Math.hypot(pos.x-it.x,pos.z-it.z)<1.1)openBottle(it)})}

// The Backpack keeps what was read, so a lesson can be found again.
function bottlesCard(){const got=sl("bottles"),all=ITEMS.bottles||[];
  if(!got.length)return "";
  return `<div class="card" id="bottlescard"><h3>Messages in a bottle</h3>`+
    `<p class="small muted">${got.length} of ${all.length} found on the shores. Washed up from the building of this game; every one of them happened.</p>`+
    all.filter(b=>got.includes(b.id)).map(b=>`<div class="pathrow"><span><b>${esc(b.title)}</b><br><span class="muted small">${esc(b.lesson)}</span></span>`+
      `<button onclick="openTopic('${esc(b.topic)}')" style="padding:4px 10px;font-size:12px">Topic</button></div>`).join("")+`</div>`}

window.__bottles=()=>({all:(ITEMS.bottles||[]).map(b=>b.id),found:sl("bottles").slice(),
  here:(props.bottles||[]).map(b=>({id:b.id,x:b.x,z:b.z,land:onLandW(b.x,b.z),bridge:!!onBridge(b.x,b.z),
    shore:landReach(W,Math.atan2(b.z,b.x)*180/Math.PI)-Math.hypot(b.x,b.z),
    screen:new T.Vector3(b.x,.3,b.z).project(camera).toArray().slice(0,2)}))});
