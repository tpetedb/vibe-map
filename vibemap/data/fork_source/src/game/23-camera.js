/* ---------------- the camera and its zoom ---------------- */
// One rig, three framings. The zoom level is a single number: at CAM.zoom.min
// the camera is close and frames the walker, at zero it is the fitted view
// that frames the island, at CAM.zoom.max it is far out and frames the
// archipelago with its bridges. Everything between is a blend of those, so
// there is no mode to switch and nothing pops on the way through.
//
// The level is state: it lives in S.settings.zoom, so it survives a reload
// and "Back to the defaults" resets it with the rest. zoomTo is that number
// read once (syncZoom), zoomZ is where the eased camera is right now.

// The canvas in CSS pixels. Read when the window changes and never inside the
// frame loop, where a layout read lands between two DOM writes.
const VIEW={w:1,h:1,dpr:0};
// The one place the renderer is sized: the window, a change of map size, full
// screen and a browser zoom all come through here, which is also why the
// pixel ratio is taken again every time rather than once at the start.
function fitRenderer(){const st=$("stage");VIEW.w=Math.max(1,st.clientWidth);VIEW.h=Math.max(1,st.clientHeight);
  if(!renderer)return;
  VIEW.dpr=devicePixelRatio;renderer.setPixelRatio(Math.min(devicePixelRatio,2));renderer.setSize(VIEW.w,VIEW.h);
  camera.aspect=VIEW.w/VIEW.h;camera.updateProjectionMatrix();camSnap=true}

let zoomTo=CAM.zoom.start,zoomZ=CAM.zoom.start,zoomRaw=CAM.zoom.start,zoomSaveT=0;
const clampZoom=z=>Math.max(CAM.zoom.min,Math.min(CAM.zoom.max,z));
const camZoom=()=>zoomZ;
function syncZoom(){const z=parseFloat(settings().zoom);
  zoomTo=zoomRaw=clampZoom(isFinite(z)?z:CAM.zoom.start);zoomHud()}
// A wheel and a pinch move the level continuously, and the fitted view has a
// small magnet on it so it can be found again by feel. The raw value keeps
// moving under the magnet, which is what lets a slow trackpad leave it.
function zoomSet(raw){zoomRaw=clampZoom(raw);zoomTo=Math.abs(zoomRaw)<.045?0:zoomRaw;
  if(!S.settings)S.settings={};S.settings.zoom=Math.round(zoomTo*1000)/1000;
  // A wheel fires sixty times a second and save() writes the whole record.
  clearTimeout(zoomSaveT);zoomSaveT=setTimeout(save,250);zoomHud()}
// A key or a button moves to the next line of a grid that has the fitted view
// on it, so from anywhere a few presses land on it exactly. dir is 1 for in.
window.zoomStep=function(dir){const st=CAM.zoom.step,at=zoomTo/st;
  zoomSet((dir>0?Math.ceil(at-1e-6)-1:Math.floor(at+1e-6)+1)*st)};
window.zoomFit=function(){zoomSet(0)};
function zoomHud(){const a=$("zoom-in"),b=$("zoom-out"),f=$("zoom-fit");if(!a||!b||!f)return;
  a.disabled=zoomTo<=CAM.zoom.min;b.disabled=zoomTo>=CAM.zoom.max;
  f.setAttribute("aria-pressed",zoomTo===0?"true":"false")}

// What a level means: how far, how steep, and how much of the frame belongs
// to the walker (close) or to the archipelago (far). Distance is geometric in
// the level, so one step always looks like the same amount of zoom.
const smooth=x=>x*x*(3-2*x);
const RIG={d:0,p:0,walker:0,arch:0};
function camRig(z,fit,out){const Z=CAM.zoom;
  if(z<=0){const k=Z.min?z/Z.min:0;
    out.d=fit*Math.pow(Math.min(1,Z.near/fit),k);out.p=CAM.pitch+(Z.nearPitch-CAM.pitch)*k;
    out.walker=smooth(k);out.arch=0}
  else{const k=z/Z.max;
    out.d=fit*Math.pow(Z.far,k);out.p=CAM.pitch+(Z.farPitch-CAM.pitch)*k;
    out.walker=0;out.arch=smooth(k)}
  return out}
// The inverse, for a pinch: the fingers ask for a distance, not for a level.
function zoomForDist(d,fit){const Z=CAM.zoom,r=Math.log(d/fit);
  if(r<=0){const n=Math.log(Math.min(1,Z.near/fit));return n<0?Z.min*Math.min(1,r/n):0}
  return Z.max*Math.min(1,r/Math.log(Z.far))}

// Where the fitted frame is centred on one axis. The follow is partial and
// capped at CAM.drift, which is the allowance camFitDist() frames on top of
// the island's radius, so nothing clips wherever the walker stands. Past the
// shore, on an annex or a bridge, the frame is about the walker and not the
// island any more, so it follows them one for one.
function camCentre(v){const c=Math.max(-CAM.drift,Math.min(CAM.drift,v*CAM.follow));
  const over=Math.abs(v)-W.land[0][2];
  return over<=0?c:c+Math.sign(v)*over}

// The middle of the four islands, seen from the one that is active.
const camArchC=new T.Vector3();let camWorld=null;
function camArch(from){camArchC.set(0,0,0);
  WORLD_IDS.forEach(id=>camArchC.add(worldOffset(id,from)));camArchC.multiplyScalar(1/WORLD_IDS.length)}

const camC=new T.Vector3(),camLook=new T.Vector3(),_ca=new T.Vector3(),_cb=new T.Vector3(),camTarget={d:0,p:0,walker:0,arch:0};
let camSnap=true,camFit=0,camTitle=true,glide=null;
// From wherever the camera is now down to the rig, in CAM.glide seconds: the
// title's orbit and a fast travel both end this way instead of in a cut.
function camGlide(){if(reducedMotion()){camSnap=true;return}
  glide={t:0,from:camera.position.clone(),look:camLook.clone()}}
// A crossing rebases the world on the new island; the camera moves with it so
// the frame does not notice.
function camShift(d,id){camera.position.sub(d);camC.sub(d);camLook.sub(d);camWorld=id;camArch(id);
  if(glide){glide.from.sub(d);glide.look.sub(d)}}

function tickCamera(dt,t,pos,vel){
  // A window dragged to another screen changes its pixel ratio and sends no
  // resize, and the media query for it is not dependable, so the frame asks.
  if(devicePixelRatio!==VIEW.dpr)fitRenderer();
  const fit=camFitDist(),calm=reducedMotion(),Z=CAM.zoom,WS=WORLD_SCALE;
  // Behind the title the island turns slowly under a camera that shows all of
  // it; the walk starts with a glide down from there.
  if(!started){const oa=calm?0:t*.07;camTitle=true;
    camera.position.lerp(_ca.set(Math.sin(oa)*fit*.86,fit*.52,Math.cos(oa)*fit*.86),calm?1:.04);
    camLook.set(0,-1,0);camera.lookAt(camLook);return}
  if(camWorld!==S.world){camWorld=S.world;camArch(camWorld);camSnap=true}
  if(camTitle){camTitle=false;camSnap=true;camGlide()}
  // A new fit is a new window, not movement in the world: a resize reframes at
  // once. A crossing changes the fit too, and that one is eased, because it
  // happens under a walker who is looking at the screen.
  const kz=calm||camSnap?1:1-Math.exp(-Z.ease*dt);
  zoomZ+=(zoomTo-zoomZ)*kz;if(Math.abs(zoomTo-zoomZ)<1e-4)zoomZ=zoomTo;
  camFit=camFit?camFit+(fit-camFit)*kz:fit;
  const r=camRig(zoomZ,camFit,RIG);
  // The look-ahead runs a little in front of the walk; it shrinks with the
  // view so a close camera does not swing a quarter of the screen on a turn.
  const ahead=CAM.ahead*Math.sqrt(Math.min(1,r.d/camFit));
  const ix=camCentre(pos.x),iz=camCentre(pos.z);
  _ca.set(ix+(pos.x-ix)*r.walker+(camArchC.x-ix)*r.arch+vel.x*ahead*(1-r.arch),0,
          iz+(pos.z-iz)*r.walker+(camArchC.z-iz)*r.arch+vel.z*ahead*(1-r.arch));
  camC.lerp(_ca,calm||camSnap?1:Math.min(1,1-Math.exp(-CAM.ease*dt)));
  _ca.set(camC.x,Math.sin(r.p)*r.d,camC.z+Math.cos(r.p)*r.d);_cb.set(camC.x,.8,camC.z-WS);
  if(glide){glide.t+=dt;const e=smooth(Math.min(1,glide.t/CAM.glide));
    camera.position.copy(glide.from).lerp(_ca,e);camLook.copy(glide.look).lerp(_cb,e);if(e>=1)glide=null}
  else{camera.position.copy(_ca);camLook.copy(_cb)}
  camera.lookAt(camLook);camSnap=false;
  const near=Math.max(.3,r.d*CAM.nearK);
  if(Math.abs(near-camera.near)>camera.near*.02){camera.near=near;camera.updateProjectionMatrix()}
  // The haze starts behind the island whatever the distance, so zooming out
  // to the archipelago does not wash out the island the walker is on.
  const push=Math.max(0,r.d-fit);scene.fog.near=80*WS+push;scene.fog.far=Math.min(280*WS+push*1.6,camera.far*.92)}
// How far the camera still is from where the zoom asks it to be: zero once it
// has landed, which is what a test waits for instead of counting frames.
function camOff(){const r=camRig(zoomTo,camFitDist(),camTarget);
  return Math.abs(camera.position.y-Math.sin(r.p)*r.d)+(glide?1:0)}

/* ---------------- zoom input ---------------- */
// Wheel and trackpad pinch (a wheel with ctrlKey) on the canvas, two fingers
// on a touch screen, plus and minus on the keyboard, 0 for the fitted view.
// Only the canvas listens, so a gesture that starts on a HUD control, the
// stick or the jump button never zooms, and the page's own zoom is left alone
// everywhere but over the 3D view.
const pinch={pts:new Map(),on:false,span:0,dist:0};
const pinching=()=>pinch.on;
function pinchSpan(){const p=[...pinch.pts.values()];return Math.hypot(p[0][0]-p[1][0],p[0][1]-p[1][1])}
function setupZoom(){const c=$("c");
  c.addEventListener("wheel",e=>{if(experienceId()!=="islands"||!started||flight)return;e.preventDefault();
    const px=e.deltaMode===1?e.deltaY*16:e.deltaMode===2?e.deltaY*VIEW.h:e.deltaY;
    zoomSet(zoomRaw+px*CAM.zoom.wheel*(e.ctrlKey?CAM.zoom.pinch:1))},{passive:false});
  // A pinch is over when the last finger lifts, but the tap handler runs after
  // this one on that same pointerup, so the flag is cleared by the next touch.
  c.addEventListener("pointerdown",e=>{if(e.pointerType==="mouse")return;
    if(!pinch.pts.size)pinch.on=false;
    pinch.pts.set(e.pointerId,[e.clientX,e.clientY]);
    if(pinch.pts.size===2){pinch.on=true;pinch.span=Math.max(1,pinchSpan());
      pinch.dist=camRig(zoomTo,camFitDist(),camTarget).d}});
  c.addEventListener("pointermove",e=>{const p=pinch.pts.get(e.pointerId);if(!p)return;
    p[0]=e.clientX;p[1]=e.clientY;
    if(pinch.pts.size===2&&started&&!flight)
      zoomSet(zoomForDist(pinch.dist*pinch.span/Math.max(1,pinchSpan()),camFitDist()))});
  const lift=e=>{pinch.pts.delete(e.pointerId)};
  c.addEventListener("pointerup",lift);c.addEventListener("pointercancel",lift);
  // iOS Safari announces a pinch with events of its own and zooms the page on
  // them; the stage keeps its size and the camera takes the gesture.
  ["gesturestart","gesturechange","gestureend"].forEach(n=>
    $("stage").addEventListener(n,e=>e.preventDefault(),{passive:false}));
  addEventListener("keydown",e=>{if(experienceId()!=="islands"||!started||e.ctrlKey||e.metaKey||e.altKey||inField(e.target))return;
    if(document.querySelector("#sheet.on,#vault.on,#pal.on"))return;
    if(e.key==="+"||e.key==="=")zoomStep(1);else if(e.key==="-"||e.key==="_")zoomStep(-1);
    else if(e.key==="0")zoomFit();else return;
    e.preventDefault()});
  syncZoom()}
