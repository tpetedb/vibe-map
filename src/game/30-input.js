const ray=new T.Raycaster(),ndc=new T.Vector2(),target=new T.Vector3(),keys={};let hasTarget=false,downPos=null,marker=null;
let joy={x:0,y:0,on:false},wantJump=false;
// When the player last did anything, anywhere on the page: a key, a tap on the
// island, a press on a button, the wheel, the stick. The battery saver in
// 31-animate.js is the only reader, and it is listened for on the window in
// the capture phase rather than added to each control, so a control added
// later cannot forget to say that somebody is there.
let lastInput=0;
function touched(){lastInput=performance.now()}
function idleMs(){return performance.now()-lastInput}
// Hurrying: hold the key, or push the stick to its rim. Holding a key is more
// motor ability than pressing one, so Settings keeps the alternative: at
// "Tap to hurry" the same key turns it on and leaves it on.
const RUN_MULT=1.5,RUN_RIM=.92;
let runOn=false;
function running(){return (settings().run==="toggle"?runOn:!!keys.shift)||(joy.on&&Math.hypot(joy.x,joy.y)>RUN_RIM)}
function runMult(){return running()?RUN_MULT:1}
// The keys that steer, in one list, because a destination lets go of them and
// the frame loop reads them.
const STEER=["arrowup","arrowdown","arrowleft","arrowright","w","a","s","d"];
// A key typed into a field belongs to the field: the caret moves, the walker
// does not. One test for it, because the walk, the jump and the zoom all ask.
function inField(el){return !!el&&(el.isContentEditable||/^(input|textarea|select)$/i.test(el.tagName||""))}
// A walk ends here, however it ended: arrived, steered away from, walked into
// the sea or carried onto another island. The marker goes out with it,
// because a lit marker means a walk is still on its way.
function clearAim(){hasTarget=false;if(marker)marker.material.opacity=0}
// One place writes a destination: the tap on the ground, the tap on the map
// and walkTo all land here, so the marker, the line to it and the arrival are
// one path. Whatever was steering is let go, or the walk would fight it.
function aim(x,z){target.set(x,0,z);hasTarget=true;
  joy={x:0,y:0,on:false};const kn=$("knob");if(kn)kn.style.transform="";
  STEER.forEach(k=>{keys[k]=false});
  marker.position.set(x,.06,z);marker.material.opacity=1}
// Walk me there: the seam a panel calls to send the walker to a stop of this
// island. It refuses what cannot be reached from here rather than half
// obeying, and says so, so that a caller can offer something else.
window.walkTo=function(n){const p=PLOT_POS[n-1];
  // The flight to another island owns the frame while it lasts and lands on
  // an island this one's coordinates say nothing about.
  if(!started||flight||!marker||!p||!onLandW(p.x,p.z))return false;
  aim(p.x,p.z);const c=CH[n-1];
  // Said as well as drawn: the toast is the announcement for anyone who
  // cannot see the marker land, and the quiet setting still silences it.
  toast(icon("compass")+"Walking there",esc(c?c.h+", "+c.n:"stop "+n));
  return true};
function setupInput(){
  const c=$("c");
  // Presence, before anything else and however the event is later handled or
  // stopped: a press, a key, a wheel. Anyone pressing the zoom buttons or
  // reading a panel is here, and the saver's minute is about nobody being.
  ["pointerdown","keydown","wheel"].forEach(k=>addEventListener(k,touched,true));
  c.addEventListener("pointerdown",e=>{downPos=[e.clientX,e.clientY]});
  c.addEventListener("pointerup",e=>{if(pinching()){downPos=null;return}if(!downPos)return;const d=Math.hypot(e.clientX-downPos[0],e.clientY-downPos[1]);downPos=null;if(d>10)return;
    const rc=$("c").getBoundingClientRect();ndc.set((e.clientX-rc.left)/rc.width*2-1,-((e.clientY-rc.top)/rc.height)*2+1);ray.setFromCamera(ndc,camera);const hit=ray.intersectObjects(island.userData.parts)[0];if(!hit)return;
    aim(hit.point.x,hit.point.z)});
  addEventListener("keydown",e=>{if(inField(e.target))return;const k=e.key.toLowerCase();keys[k]=true;if(k===" "){wantJump=true;if(document.activeElement===document.body)e.preventDefault()}if(["arrowup","arrowdown","arrowleft","arrowright"].includes(k))e.preventDefault()
    // A held key repeats, so the toggle listens to the press and not to the
    // repeat: otherwise hurrying would flicker while the key is down.
    if(k==="shift"&&!e.repeat&&settings().run==="toggle")runOn=!runOn;
    // Enter is the keyboard twin of the proximity button, so it only fires
    // while the page itself has focus and nothing is standing in front of it:
    // a form field and an open panel keep their own Enter.
    if(k==="enter"&&nearK&&document.activeElement===document.body&&!document.querySelector("#sheet.on,#vault.on,#pal.on,#title:not(.off)")){enterNear();e.preventDefault()}});
  addEventListener("keyup",e=>{keys[e.key.toLowerCase()]=false});
  // A key held while the focus moves into a field never sends its keyup here.
  addEventListener("focusin",e=>{if(inField(e.target))for(const k in keys)keys[k]=false});
  const j=$("joy"),kn=$("knob");let jid=null;
  j.addEventListener("pointerdown",e=>{jid=e.pointerId;j.setPointerCapture(jid);joy.on=true;jm(e)});
  j.addEventListener("pointermove",e=>{if(e.pointerId===jid)jm(e)});
  const je=e=>{if(e.pointerId!==jid)return;jid=null;joy={x:0,y:0,on:false};kn.style.transform=""};
  j.addEventListener("pointerup",je);j.addEventListener("pointercancel",je);
  // A finger already down and still steering is somebody there, and its move
  // is the only input that is not a press of its own.
  function jm(e){const r=j.getBoundingClientRect();let dx=(e.clientX-r.left-r.width/2)/(r.width/2),dy=(e.clientY-r.top-r.height/2)/(r.height/2);const l=Math.hypot(dx,dy);if(l>1){dx/=l;dy/=l}joy.x=dx;joy.y=dy;kn.style.transform=`translate(${dx*30}px,${dy*30}px)`;touched()}
  $("jump").addEventListener("pointerdown",e=>{e.preventDefault();wantJump=true});
  $("c").addEventListener("dblclick",()=>{wantJump=true});
}
function nearestPlot(){let best=-1,bd=99;PLOT_POS.forEach((p,i)=>{const d=p.distanceTo(chars.lotte.g.position);if(d<bd){bd=d;best=i}});return {i:best,d:bd}}
let nearK=0,started=false,inited=false,lastSay="";
// What the walk is doing, for the tests: the destination, whether one is set,
// how lit its marker is, and whether the walker is hurrying.
window.__walk=()=>({target:[target.x,target.z],has:hasTarget,
  marker:marker?Math.round(marker.material.opacity*1000)/1000:0,
  run:running(),mult:runMult(),line:pathShown(),idle:Math.round(idleMs())});
