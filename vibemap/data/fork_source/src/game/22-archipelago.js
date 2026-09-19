// The archipelago: the three islands you are not on, the bridges between
// them, the crossing that swaps the active island under your feet, and the
// camera flight the World button does instead of a cut.
//
// Everything here is drawn into instanced meshes on purpose. The scene is
// already close to the phone's draw-call budget (tests/test_game_webkit.py),
// so a bridge costs the same one draw call per part however long it is, and
// the three distant islands together cost one.

// The distant islands: their land blobs and nothing else. No shadows, no
// props, no labels, one instanced mesh for all three.
function buildSilhouettes(from){
  const geo=shape("blob",()=>new T.CylinderGeometry(1,1.12,1,7));
  const mats=[],cols=[];
  WORLD_IDS.filter(id=>id!==from).forEach(id=>{const o=worldOffset(id,from),w=WORLDS[id];
    w.land.forEach(b=>{
      mats.push(xform(o.x+b[0],-1.2,o.z+b[1],0,0,0,new T.Vector3(b[2],2.4,b[2])));cols.push(w.grass);
      mats.push(xform(o.x+b[0],-2.6,o.z+b[1],0,0,0,new T.Vector3(b[2]+1.1,2.2,b[2]+1.1)));cols.push(w.dirt)})});
  const m=new T.MeshStandardMaterial({color:"#ffffff",roughness:.95,metalness:0,flatShading:true});
  m.userData.cs=1;
  const im=instOf(geo,m,mats,false);if(!im)return;
  const c=new T.Color();mats.forEach((_,i)=>{c.set(cols[i]).convertSRGBToLinear();im.setColorAt(i,c)});
  if(im.instanceColor)im.instanceColor.needsUpdate=true;
  props.silhouettes=im}

// Every bridge in the archipelago shares one instanced mesh per part, so the
// count of bridges costs nothing. A bridge that touches the active island
// gets its planks, railings, lamps and rest platform; a far one is a single
// stretched deck, because at that distance it is a line in the fog.
function buildBridges(){
  const deck=[],rail=[],post=[],lampPost=[],bulb=[],rest=[],slab=[],leg=[],barrier=[];
  props.bridgeLamps=null;
  bridges.forEach(b=>{
    const ry=-Math.atan2(b.dir.z,b.dir.x),at=d=>b.pa.clone().addScaledVector(b.dir,d);
    if(!b.near){const c=at(b.len/2);deck.push(xform(c.x,-.02,c.z,0,ry,0,new T.Vector3(b.len,1,1)));return}
    const n=Math.max(2,Math.round(b.len/.62));
    for(let i=0;i<n;i++){const p=at((i+.5)*b.len/n);deck.push(xform(p.x,-.02,p.z,0,ry,0))}
    // Railings run the whole deck; the posts under them are every few paces.
    const c=at(b.len/2);
    [-1,1].forEach(s=>{
      const o=new T.Vector3(-b.dir.z,0,b.dir.x).multiplyScalar(s*(BRIDGE_W-.25));
      rail.push(xform(c.x+o.x,1,c.z+o.z,0,ry,0,new T.Vector3(b.len,1,1)));
      const np=Math.max(2,Math.round(b.len/3.2));
      for(let i=0;i<=np;i++){const p=at(i*b.len/np);post.push(xform(p.x+o.x,.45,p.z+o.z,0,ry,0))}});
    // Lamps alternate sides so the deck is lit from both.
    const nl=Math.max(2,Math.round(b.len/11));
    for(let i=0;i<=nl;i++){const p=at(i*b.len/nl),s=i%2?1:-1;
      const o=new T.Vector3(-b.dir.z,0,b.dir.x).multiplyScalar(s*(BRIDGE_W-.45));
      lampPost.push(xform(p.x+o.x,1,p.z+o.z,0,ry,0));
      bulb.push(xform(p.x+o.x,2.1,p.z+o.z,0,ry,0))}
    // The rest platform at the middle: somewhere to stop, with a bench.
    rest.push(xform(b.mid.x,-.04,b.mid.z,0,ry,0));
    const bo=new T.Vector3(-b.dir.z,0,b.dir.x).multiplyScalar(2.1);
    slab.push(xform(b.mid.x+bo.x,.54,b.mid.z+bo.z,0,ry,0));
    [[-.6,.2],[.6,.2],[-.6,-.2],[.6,-.2]].forEach(([u,v])=>{
      const p=b.mid.clone().addScaledVector(b.dir,u).addScaledVector(bo.clone().normalize(),2.1+v);
      leg.push(xform(p.x,.28,p.z,0,ry,0))});
    // A closed bridge says so with a barrier across both shores.
    if(!b.open)[0,b.len].forEach(d=>{const p=at(d===0?1.2:b.len-1.2);
      barrier.push(xform(p.x,.45,p.z,0,ry,0))})});
  const plank=shape("plank",()=>new T.BoxGeometry(.5,.16,BRIDGE_W*2));
  const decks=instOf(plank,mat(PALETTE.deck),deck,false);
  instOf(shape("rail",()=>new T.BoxGeometry(1,.14,.14)),mat(PALETTE.timber),rail,false);
  instOf(shape("post",()=>new T.BoxGeometry(.14,.9,.14)),mat(PALETTE.timber),post,false);
  instOf(shape("lamppost",()=>new T.CylinderGeometry(.05,.07,2,5)),mat("#334155"),lampPost,false);
  const lamps=instOf(shape("bulb",()=>new T.SphereGeometry(.2,6,6)),
    mat(PALETTE.lamp,{emissive:PALETTE.yellow,emissiveIntensity:0}),bulb,false);
  if(lamps)props.bridgeLamps=lamps.material;
  const platform=instOf(shape("rest",()=>new T.CylinderGeometry(BRIDGE_REST_R,BRIDGE_REST_R,.2,12)),
    mat("#C8A882"),rest,false);
  instOf(shape("bench",()=>new T.BoxGeometry(1.6,.14,.55)),mat(W.bank),slab,false);
  instOf(shape("benchleg",()=>new T.BoxGeometry(.1,.55,.1)),mat(PALETTE.muted),leg,false);
  instOf(shape("barrier",()=>new T.BoxGeometry(.2,.9,BRIDGE_W*2)),mat(PALETTE.red),barrier,false);
  // Tap to walk aims at the ground; a deck and a platform are ground.
  if(island)[decks,platform].forEach(m=>{if(m)island.userData.parts.push(m)})}

// The bridge under a point, if it is open and the point is on its deck or its
// rest platform. One helper, because onLandW, the crossing and the minimap
// all ask the same question.
function onBridge(x,z){for(const b of bridges){if(!b.open)continue;
  if(Math.hypot(x-b.mid.x,z-b.mid.z)<BRIDGE_REST_R-.4)return b;
  if(segDist(x,z,b.pa.x,b.pa.z,b.pb.x,b.pb.z)<BRIDGE_W-.4)return b}
  return null}

// Crossing the middle switches the island under your feet. The walker is
// carried into the new island's coordinates, so the walk does not stop, and
// the island that was left drops to a silhouette. The dead band of a metre
// keeps a walker standing on the middle from flipping back and forth.
function checkCrossing(pos){
  const b=onBridge(pos.x,pos.z);if(!b)return;
  const here=S.world||"campus";if(b.a!==here&&b.b!==here)return;
  const along=new T.Vector3().subVectors(pos,b.pa).dot(b.dir);
  const towards=b.b===here?b.len-along:along;
  if(towards<b.len/2+1)return;
  crossTo(b.b===here?b.a:b.b)}
function crossTo(id){
  const d=worldOffset(id,S.world),L=chars.lotte,p=L.g.position.clone().sub(d);
  camera.position.sub(d);
  buildWorld(id,{x:p.x,z:p.z,rot:L.g.rotation.y,vel:L.vel?L.vel.clone():null});
  if(typeof track==="function")track("world",id);
  toast(icon("globe")+"You are on "+W.name,CAMPAIGN[id].title)}

// Fast travel: the World button flies the camera over the water to the island
// it picks before building it, so the four islands read as one place even
// when the walk is skipped. Under reduced motion it is a cut.
let flight=null;
function startFlight(id){flight={to:id,t:0,dur:.9,from:camera.position.clone(),at:worldOffset(id,S.world)}}
function tickFlight(dt){
  flight.t+=dt;const x=Math.min(1,flight.t/flight.dur),e=x<.5?2*x*x:1-Math.pow(-2*x+2,2)/2;
  const WS=WORLD_SCALE,to=new T.Vector3(flight.at.x,26*WS,flight.at.z+20*WS);
  camera.position.copy(flight.from).lerp(to,e);camera.lookAt(flight.at.x,0,flight.at.z);
  if(x<1)return;
  const id=flight.to;flight=null;
  buildWorld(id);renderWorldPicker();
  camera.position.set(2,20*WS,22*WS)}
