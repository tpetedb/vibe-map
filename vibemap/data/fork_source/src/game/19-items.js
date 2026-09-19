// Collectibles and seats, placed from vibemap/data/items.json (ITEMS).
// Every spot in that file is relative to a plot, an annex or the path of its
// island, so a new layout carries the furniture along instead of stranding it
// in the sea. Nothing here holds a world coordinate of its own.

// Where a spot lands: the anchor, then d units outward turned by a radians.
// Outward is the direction from the island's centre, which is what makes the
// same number mean the same thing on a plot on either side of the island.
// A spot that falls off the land is pulled back towards its anchor rather
// than dropped, so every collectible on an island can always be collected.
function itemSpot(at){
  let cx,cz;
  if(at.plot!==undefined){const p=PLOT_POS[at.plot-1];if(!p)return null;cx=p.x;cz=p.z}
  else if(at.annex!==undefined){const a=annexes.find(x=>x.k===at.annex);if(!a)return null;cx=a.x;cz=a.z}
  else if(at.path!==undefined){const c=props.curve;if(!c)return null;const pt=c.getPointAt(Math.min(1,Math.max(0,at.path)));cx=pt.x;cz=pt.z}
  else return null;
  const ang=Math.atan2(cx,cz)+(at.a||0),d=(at.d||0)*WORLD_SCALE;
  for(const f of [1,.6,.3,0]){const x=cx+Math.sin(ang)*d*f,z=cz+Math.cos(ang)*d*f;
    if(onLandW(x,z))return {x,z,face:Math.atan2(cx-x,cz-z)}}
  return null}

/* ---------------- seats ---------------- */
// Every seat on the island is three instanced meshes, whatever the count: one
// for the slabs, one for the backs, one for the legs. A bench and a chair are
// the same model at a different width.
const SEAT_W={bench:1.5,chair:.8},SEAT_H=.6;
let SEATG=null;
function seatParts(){if(SEATG)return SEATG;
  SEATG={slab:new T.BoxGeometry(1,.12,.52),back:new T.BoxGeometry(1,.5,.1),leg:new T.BoxGeometry(.1,.55,.1)};
  return SEATG}
function placeSeats(){
  props.seats=[];
  const list=(ITEMS.seats||[]).filter(s=>s.world===(S.world||"campus"));
  const spots=[];
  list.forEach(s=>{const p=itemSpot(s.at);if(!p)return;
    spots.push({id:s.id,x:p.x,z:p.z,face:p.face,w:SEAT_W[s.kind]||1,h:SEAT_H});
    obstacles.push([p.x,p.z,.5])});
  // A mentor works at their spot, so they get the chair they are sitting on.
  (props.mentors||[]).forEach(c=>{const p=c.g.position;
    spots.push({id:"seat:"+c.id,x:p.x,z:p.z,face:c.g.rotation.y,w:SEAT_W.chair,h:SEAT_H,taken:true});
    setPose(c,"sit",SEAT_H)});
  props.seats=spots;
  if(!spots.length)return;
  const P=seatParts(),d=new T.Object3D();
  const wood=mat(W.bank),metal=mat(PALETTE.muted);
  const slabs=new T.InstancedMesh(P.slab,wood,spots.length);
  const backs=new T.InstancedMesh(P.back,metal,spots.length);
  const legs=new T.InstancedMesh(P.leg,metal,spots.length*4);
  spots.forEach((s,i)=>{
    d.position.set(s.x,SEAT_H-.06,s.z);d.rotation.set(0,s.face,0);d.scale.set(s.w,1,1);d.updateMatrix();slabs.setMatrixAt(i,d.matrix);
    d.position.set(s.x,SEAT_H+.28,s.z);d.translateZ(-.22);d.updateMatrix();backs.setMatrixAt(i,d.matrix);
    [[-.38,.18],[.38,.18],[-.38,-.18],[.38,-.18]].forEach(([lx,lz],j)=>{
      d.position.set(s.x,.28,s.z);d.scale.set(1,1,1);d.translateX(lx*s.w);d.translateZ(lz);d.updateMatrix();legs.setMatrixAt(i*4+j,d.matrix)})});
  slabs.castShadow=backs.castShadow=legs.castShadow=true;slabs.receiveShadow=true;
  scene.add(slabs,backs,legs);props.seatMeshes=[slabs,backs,legs]}
// The seat you would sit on from here, if one is within reach and free.
function nearestSeat(pos){let best=null,bd=2.2*WORLD_SCALE;
  (props.seats||[]).forEach(s=>{if(s.taken)return;const d=Math.hypot(pos.x-s.x,pos.z-s.z);if(d<bd){bd=d;best=s}});
  return best}

/* ---------------- collectibles ---------------- */
// One mesh each, with the geometry and the material of its kind shared across
// the island, so ten collectibles are ten draw calls and no more.
let ITEMG=null;
function itemParts(){if(ITEMG)return ITEMG;
  ITEMG={geo:{
    octa:new T.OctahedronGeometry(.22),
    ring:new T.TorusGeometry(.18,.06,5,10),
    chip:new T.BoxGeometry(.3,.3,.09),
    cube:new T.BoxGeometry(.3,.3,.3),
    slab:new T.BoxGeometry(.34,.24,.06),
    rod:new T.CylinderGeometry(.06,.06,.44,6),
    tube:new T.CylinderGeometry(.11,.11,.4,8),
    bead:new T.SphereGeometry(.17,7,5),
    roll:new T.CylinderGeometry(.09,.09,.42,7),
    ico:new T.IcosahedronGeometry(.21,0),
  },mats:{}};return ITEMG}
function itemMat(colour){const P=itemParts();
  if(!P.mats[colour])P.mats[colour]=mat(PALETTE[colour]||PALETTE.text,{emissive:PALETTE[colour]||PALETTE.text,emissiveIntensity:.35});
  return P.mats[colour]}
// Idempotent: called when the island is built and again when an annex appears,
// and it only ever adds what is missing and not already collected.
function placeItems(){
  if(!props.items)props.items=[];
  const got=sl("items"),P=itemParts();
  ITEMS.items.filter(i=>i.world===(S.world||"campus")).forEach(i=>{
    if(got.includes(i.id)||props.items.some(x=>x.id===i.id))return;
    const sp=itemSpot(i.at);if(!sp)return;
    const k=ITEMS.kinds[i.kind];if(!k)return;
    const m=new T.Mesh(P.geo[k.model]||P.geo.cube,itemMat(k.colour));
    m.position.set(sp.x,.75,sp.z);m.castShadow=true;scene.add(m);
    props.items.push({id:i.id,m,x:sp.x,z:sp.z,p:props.items.length})})}
// Walking over one collects it: a small burst, a line in the backpack, and the
// concept with the tech tree topic it belongs to.
function collect(it){const data=ITEMS.items.find(x=>x.id===it.id);
  scene.remove(it.m);props.items=props.items.filter(x=>x!==it);
  if(!data)return;
  sl("items").push(data.id);save();
  for(let i=0;i<12;i++){const m=new T.Mesh(new T.BoxGeometry(.1,.1,.1),new T.MeshBasicMaterial({color:PALETTE[ITEMS.kinds[data.kind].colour]||PALETTE.text}));
    m.position.set(it.x,.8,it.z);m.userData.v=new T.Vector3((Math.random()-.5)*3,2+Math.random()*2,(Math.random()-.5)*3);m.userData.life=.8;scene.add(m);parts.push(m)}
  toast(icon("compass")+"Picked up: "+data.name,
    data.concept+` <a href="#" onclick="openTopic('${data.topic}');return false">Read the topic</a>`);
  if(typeof track==="function")track("item",data.id);
  achCheck()}
function tickItems(dt,t){
  const pos=chars.lotte&&chars.lotte.g.position;if(!pos)return;
  (props.items||[]).slice().forEach(it=>{
    // t is the ambient clock, which reduced motion stops; the spin stops with it.
    it.m.rotation.y+=(reducedMotion()?0:dt)*1.6;it.m.position.y=.75+Math.sin(t*2+it.p)*.12;
    if(Math.hypot(pos.x-it.x,pos.z-it.z)<1.1)collect(it)})}
