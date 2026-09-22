const ray=new T.Raycaster(),ndc=new T.Vector2(),target=new T.Vector3(),keys={};let hasTarget=false,downPos=null,marker=null;
// The walk that is on: the corners still to be turned on the way to target,
// the scene it was taken on, what it is a walk to when a panel asked for it,
// and how near it has got and for how long it has got no nearer.
let route=[],aimOn=null,aimFor="",aimBest=0,aimStall=0;
let joy={x:0,y:0,on:false},wantJump=false;
// When the player last did anything, anywhere on the page: a key, a tap on the
// island, a press on a button, the wheel, the stick. The battery saver in
// 31-animate.js is the only reader, and it is listened for on the window in
// the capture phase rather than added to each control, so a control added
// later cannot forget to say that somebody is there.
// The clock starts when the page does: a browser that has just opened the
// island is not a browser nobody is at, however long the first frames took.
let lastInput=performance.now();
function noteInput(){lastInput=performance.now()}
function idleMs(){return performance.now()-lastInput}
// Hurrying: hold the key, or push the stick to its rim. Holding a key is more
// motor ability than pressing one, so Settings keeps the alternative: at
// "Tap to hurry" the same key turns it on and leaves it on.
const RUN_MULT=1.5,RUN_RIM=.92;
let runOn=false,shiftAlone=false;
function running(){return (settings().run==="toggle"?runOn:!!keys.shift)||(joy.on&&Math.hypot(joy.x,joy.y)>RUN_RIM)}
function runMult(){return running()?RUN_MULT:1}
// The keys that steer, in one list, because a destination lets go of them and
// the frame loop reads them.
const STEER=["arrowup","arrowdown","arrowleft","arrowright","w","a","s","d"];
// A key typed into a field belongs to the field: the caret moves, the walker
// does not. One test for it, because the walk, the jump and the zoom all ask.
function inField(el){return !!el&&(el.isContentEditable||/^(input|textarea|select)$/i.test(el.tagName||""))}
// A walk ends here, however it ended: arrived, steered away from, given up on
// or carried onto another island. The marker goes out with it, because a lit
// marker means a walk is still on its way.
function clearAim(){hasTarget=false;route.length=0;if(marker)marker.material.opacity=0;hidePath()}
// One place writes a destination: the tap on the ground, the tap on the map
// and walkTo all land here, so the marker, the way to it and the arrival are
// one path. Whatever was steering is let go, or the walk would fight it.
function aim(x,z,name){target.set(x,0,z);hasTarget=true;aimOn=scene;aimFor=name||"";
  joy={x:0,y:0,on:false};const kn=$("knob");if(kn)kn.style.transform="";
  STEER.forEach(k=>{keys[k]=false});
  const p=chars.lotte.g.position;route=planRoute(p.x,p.z,x,z);aimBest=1e9;aimStall=0;
  marker.position.set(x,.06,z);marker.material.opacity=1}
// A destination is a point on the island it was picked on. Leaving that island
// ends the walk, whichever way it is left: over a bridge, by the flight, or by
// the cut that reduced motion makes of the flight. The frame loop asks once,
// so no way of leaving has to remember to say so.
function aimStale(){return hasTarget&&(!!flight||aimOn!==scene)}

/* ---------------- the way there ---------------- */
// A destination a few paces off is a straight line. One across the island has
// the hub, the lake and a bay between it and the walker, and a walker steered
// straight at it ends up pinned against the first of them. So the way is
// worked out once, when the destination is taken: a grid over the island, a
// cell free where the walker has room to stand, the shortest way over free
// cells, and then every corner the walker can see past taken out again. The
// frame loop only steers at the next corner; nothing here runs in it.
//
// WALK_R is how near the frame loop lets the walker come to an obstacle. A
// corner keeps ROUTE_ROOM from it, so the walker rounds it without rubbing,
// and a straight stretch keeps ROUTE_PASS, which is still more than WALK_R: a
// gap the way goes through is a gap the walker fits through. The shore is kept
// at ROUTE_SHORE on every side, because a walker carries its speed round a
// corner and the island is circles: where two of them meet there is a notch
// of water a walker that drifts into it does not steer out of.
const WALK_R=.45,ROUTE_CELL=1,ROUTE_ROOM=WALK_R+.35,ROUTE_PASS=WALK_R+.05,ROUTE_SHORE=.6,ROUTE_NEAR=.9;
function roomAt(x,z,r){const s=ROUTE_SHORE;
  if(!onLandW(x,z)||!onLandW(x-s,z)||!onLandW(x+s,z)||!onLandW(x,z-s)||!onLandW(x,z+s))return false;
  for(let i=0;i<obstacles.length;i++){const o=obstacles[i];if(Math.hypot(x-o[0],z-o[1])<o[2]+r)return false}
  return true}
// Whether the straight line between two points stays on land, asked of the
// two stretches that have no room to keep: from wherever the walker happens
// to stand onto the way, and off the way to wherever the destination is.
function landWay(ax,az,bx,bz){const d=Math.hypot(bx-ax,bz-az),n=Math.max(1,Math.ceil(d/.25));
  for(let i=0;i<=n;i++){const t=i/n;if(!onLandW(ax+(bx-ax)*t,az+(bz-az)*t))return false}
  return true}
// Whether the straight line between two points can be walked: a sample every
// half pace, which is finer than anything that stands on the island.
function clearWay(ax,az,bx,bz){const d=Math.hypot(bx-ax,bz-az),n=Math.max(1,Math.ceil(d/.5));
  for(let i=0;i<=n;i++){const t=i/n;if(!roomAt(ax+(bx-ax)*t,az+(bz-az)*t,ROUTE_PASS))return false}
  return true}
// The corners between the walker and the destination, nearest first, without
// either end. Empty when the way is straight, and empty when there is no way
// over land at all: then the walk is the straight line it always was, and
// walkWatch() is what ends it.
function planRoute(fx,fz,tx,tz){
  if(clearWay(fx,fz,tx,tz))return [];
  let x0=Math.min(fx,tx),x1=Math.max(fx,tx),z0=Math.min(fz,tz),z1=Math.max(fz,tz);
  W.land.forEach(b=>{x0=Math.min(x0,b[0]-b[2]);x1=Math.max(x1,b[0]+b[2]);z0=Math.min(z0,b[1]-b[2]);z1=Math.max(z1,b[1]+b[2])});
  const C=ROUTE_CELL,nx=Math.ceil((x1-x0)/C)+1,nz=Math.ceil((z1-z0)/C)+1,N=nx*nz;
  // Asked of a cell the first time the search reaches it and kept: most of
  // the grid is never looked at.
  const room=new Int8Array(N),ok=i=>{if(!room[i])room[i]=roomAt(x0+(i%nx)*C,z0+((i/nx)|0)*C,ROUTE_ROOM)?1:-1;return room[i]>0};
  // Either end may stand where a corner may not: at a signpost by the shore,
  // or pressed against the hub. The search runs between the free cells
  // nearest to them that can be reached from them over land.
  const near=(x,z)=>{const cx=Math.round((x-x0)/C),cz=Math.round((z-z0)/C);let best=-1,bd=1e9;
    for(let dz=-4;dz<=4;dz++)for(let dx=-4;dx<=4;dx++){const ix=cx+dx,iz=cz+dz;
      if(ix<0||iz<0||ix>=nx||iz>=nz||!ok(iz*nx+ix))continue;
      const px=x0+ix*C,pz=z0+iz*C,d=Math.hypot(px-x,pz-z);if(d<bd&&landWay(x,z,px,pz)){bd=d;best=iz*nx+ix}}
    return best};
  const start=near(fx,fz),goal=near(tx,tz);if(start<0||goal<0)return [];
  // A* over eight neighbours. A diagonal step needs both cells beside it
  // free, or the way would cut the corner of whatever stands in one of them.
  const cost=new Float32Array(N).fill(Infinity),from=new Int32Array(N).fill(-1),heap=[];
  const gx=goal%nx,gz=(goal/nx)|0,far=i=>{const dx=Math.abs(i%nx-gx),dz=Math.abs(((i/nx)|0)-gz);return Math.max(dx,dz)+.414*Math.min(dx,dz)};
  const push=(f,i)=>{let k=heap.length;heap.push([f,i]);
    while(k>0){const up=(k-1)>>1;if(heap[up][0]<=heap[k][0])break;[heap[up],heap[k]]=[heap[k],heap[up]];k=up}};
  const pop=()=>{const top=heap[0],last=heap.pop();if(heap.length){heap[0]=last;let k=0;
      for(;;){const l=2*k+1,r=l+1;let m=k;if(l<heap.length&&heap[l][0]<heap[m][0])m=l;if(r<heap.length&&heap[r][0]<heap[m][0])m=r;
        if(m===k)break;[heap[m],heap[k]]=[heap[k],heap[m]];k=m}}
    return top};
  cost[start]=0;push(far(start),start);let found=false;
  while(heap.length){const [f,i]=pop();if(i===goal){found=true;break}
    if(f>cost[i]+far(i)+1e-6)continue;
    const ix=i%nx,iz=(i/nx)|0;
    for(let dz=-1;dz<=1;dz++)for(let dx=-1;dx<=1;dx++){if(!dx&&!dz)continue;
      const jx=ix+dx,jz=iz+dz;if(jx<0||jz<0||jx>=nx||jz>=nz)continue;
      const j=jz*nx+jx;if(!ok(j)||(dx&&dz&&(!ok(iz*nx+jx)||!ok(jz*nx+ix))))continue;
      const c=cost[i]+(dx&&dz?1.414:1);if(c<cost[j]){cost[j]=c;from[j]=i;push(c+far(j),j)}}}
  if(!found)return [];
  // The cells from the walker's end to the destination's, then the ends
  // themselves, then every point the one before it can see past is dropped.
  const pts=[];for(let i=goal;i>=0;i=from[i])pts.push(new T.Vector3(x0+(i%nx)*C,0,z0+((i/nx)|0)*C));
  pts.push(new T.Vector3(fx,0,fz));pts.reverse();pts.push(new T.Vector3(tx,0,tz));
  const out=[];let a=0;
  while(a<pts.length-1){let b=a+1;
    while(b+1<pts.length&&clearWay(pts[a].x,pts[a].z,pts[b+1].x,pts[b+1].z))b++;
    if(b<pts.length-1)out.push(pts[b]);a=b}
  return out}
// Where the frame loop steers: the next corner, or the destination once the
// last corner is behind. A corner counts as turned a pace before it, so the
// walker rounds it instead of stopping on it.
function routeNext(pos){
  while(route.length&&Math.hypot(route[0].x-pos.x,route[0].z-pos.z)<ROUTE_NEAR)route.shift();
  return route.length?route[0]:target}
// A walk that has stopped getting nearer is over, and says so: a destination
// inside the hub, across a shut bridge or behind something that was not there
// when the way was planned is otherwise a walker pressed against it for good,
// under a marker that stays lit. Measured along the way that is left, and on
// the game's clock, so a slow renderer is not mistaken for a wall.
const STALL_S=1.2;
function walkWatch(pos,dt){
  let left=0,x=pos.x,z=pos.z;
  for(let i=0;i<route.length;i++){left+=Math.hypot(route[i].x-x,route[i].z-z);x=route[i].x;z=route[i].z}
  left+=Math.hypot(target.x-x,target.z-z);
  if(left<aimBest-.05){aimBest=left;aimStall=0;return}
  aimStall+=dt;if(aimStall>STALL_S)stopShort()}
function stopShort(){const name=aimFor;clearAim();
  toast(icon("compass")+"Stopped short",name?esc("The way to "+name+" is blocked from here. Steer round it and ask again."):"This is as near as the walker gets.")}
// Walk me there: the seam a panel calls to send the walker to a stop of this
// island. It refuses what cannot be reached from here rather than half
// obeying, and says so, so that a caller can offer something else.
window.walkTo=function(n){const p=PLOT_POS[n-1];
  // The flight to another island owns the frame while it lasts and lands on
  // an island this one's coordinates say nothing about.
  if(!started||flight||!marker||!p||!onLandW(p.x,p.z))return false;
  const c=CH[n-1],name=c?c.h+", "+c.n:"stop "+n;aim(p.x,p.z,name);
  // Said as well as drawn: the toast is the announcement for anyone who
  // cannot see the marker land, and the quiet setting still silences it.
  toast(icon("compass")+"Walking there",esc(name));
  return true};
function setupInput(){
  const c=$("c");
  // Presence, before anything else and however the event is later handled or
  // stopped: a press, a key, a wheel. Anyone pressing the zoom buttons or
  // reading a panel is here, and the saver's minute is about nobody being.
  ["pointerdown","keydown","wheel"].forEach(k=>addEventListener(k,noteInput,true));
  c.addEventListener("pointerdown",e=>{downPos=[e.clientX,e.clientY]});
  c.addEventListener("pointerup",e=>{if(experienceId()!=="islands"){downPos=null;return}if(pinching()){downPos=null;return}if(!downPos)return;const d=Math.hypot(e.clientX-downPos[0],e.clientY-downPos[1]);downPos=null;if(d>10)return;
    const rc=$("c").getBoundingClientRect();ndc.set((e.clientX-rc.left)/rc.width*2-1,-((e.clientY-rc.top)/rc.height)*2+1);ray.setFromCamera(ndc,camera);const hit=ray.intersectObjects(island.userData.parts)[0];if(!hit)return;
    aim(hit.point.x,hit.point.z)});
  addEventListener("keydown",e=>{if(inField(e.target))return;const k=e.key.toLowerCase();keys[k]=true;if(k===" "){wantJump=true;if(document.activeElement===document.body)e.preventDefault()}if(["arrowup","arrowdown","arrowleft","arrowright"].includes(k))e.preventDefault()
    // The toggle is Shift on its own, down and up again with no other key in
    // between: the Shift of Shift and Tab belongs to the Tab, and somebody
    // moving through the page by keyboard is not asking to hurry.
    if(k==="shift"){if(!e.repeat)shiftAlone=true}else shiftAlone=false;
    // Enter is the keyboard twin of the proximity button, so it only fires
    // while the page itself has focus and nothing is standing in front of it:
    // a form field and an open panel keep their own Enter.
    if(k==="enter"&&nearK&&document.activeElement===document.body&&!document.querySelector("#sheet.on,#vault.on,#pal.on,#title:not(.off)")){enterNear();e.preventDefault()}});
  addEventListener("keyup",e=>{const k=e.key.toLowerCase();keys[k]=false;
    if(k!=="shift"||!shiftAlone)return;shiftAlone=false;
    if(settings().run!=="toggle")return;runOn=!runOn;
    // A latch nobody can see is a walker that is fast for no reason, so it
    // says which way it went.
    toast(icon("rocket")+(runOn?"Hurrying":"Walking"),"Shift changes it back.")});
  // A key held while the focus moves into a field never sends its keyup here.
  addEventListener("focusin",e=>{if(inField(e.target))for(const k in keys)keys[k]=false});
  // Key releases may go to another app after the window loses focus.
  addEventListener("blur",()=>{for(const k in keys)keys[k]=false;shiftAlone=false});
  const j=$("joy"),kn=$("knob");let jid=null;
  j.addEventListener("pointerdown",e=>{jid=e.pointerId;j.setPointerCapture(jid);joy.on=true;jm(e)});
  j.addEventListener("pointermove",e=>{if(e.pointerId===jid)jm(e)});
  const je=e=>{if(e.pointerId!==jid)return;jid=null;joy={x:0,y:0,on:false};kn.style.transform=""};
  j.addEventListener("pointerup",je);j.addEventListener("pointercancel",je);
  // A finger already down and still steering is somebody there, and its move
  // is the only input that is not a press of its own.
  function jm(e){const r=j.getBoundingClientRect();let dx=(e.clientX-r.left-r.width/2)/(r.width/2),dy=(e.clientY-r.top-r.height/2)/(r.height/2);const l=Math.hypot(dx,dy);if(l>1){dx/=l;dy/=l}joy.x=dx;joy.y=dy;kn.style.transform=`translate(${dx*30}px,${dy*30}px)`;noteInput()}
  $("jump").addEventListener("pointerdown",e=>{e.preventDefault();wantJump=true});
  $("c").addEventListener("dblclick",()=>{wantJump=true});
}
function nearestPlot(){let best=-1,bd=99;PLOT_POS.forEach((p,i)=>{const d=p.distanceTo(chars.lotte.g.position);if(d<bd){bd=d;best=i}});return {i:best,d:bd}}
let nearK=0,started=false,inited=false,lastSay="";
// What the walk is doing, for the tests: the destination, whether one is set,
// how lit its marker is, and whether the walker is hurrying.
window.__walk=()=>({target:[target.x,target.z],has:hasTarget,
  marker:marker?Math.round(marker.material.opacity*1000)/1000:0,
  run:running(),mult:runMult(),line:pathShown(),idle:Math.round(idleMs()),
  corners:route.map(p=>[p.x,p.z]),dashes:pathDashes()});
// Where a point of the ground is on the screen, for the tests: a tap is a real
// click, and a click needs somewhere to land.
window.__groundAt=(x,z)=>{const v=new T.Vector3(x,0,z).project(camera),rc=$("c").getBoundingClientRect();
  return [rc.left+(v.x+1)/2*rc.width,rc.top+(1-v.y)/2*rc.height]};
