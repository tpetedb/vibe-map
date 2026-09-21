// The minimap: the four islands, the bridges, you, and the next stop. It is a
// 2D canvas rather than a second camera, so it costs no draw call in the
// scene. Like everything else on screen it is derived: it reads S, WORLDS and
// the bridges of this frame and holds no state of its own beyond whether it
// is open on a phone and whether it has been made big.
//
// It is also where the island says where to go next: the map knows the next
// stop and the state of every bridge, so the arrow at the edge of the screen
// reads the same two facts rather than working them out a second time.
//
// The element is built here instead of in body.html because it belongs to the
// archipelago, not to the HUD, and a fork that drops this file should lose the
// map and nothing else.

const MM_SIZE=136,MM_PHONE=560;
// A finger target, the same 44 px every other control on a phone keeps.
const MM_TAP=44;
// How close to a plot a tap has to land, in canvas pixels of the drawn map.
const MM_HIT=14;
// mmPaints counts the times the map has actually been painted, so a test can
// wait for a drawn map rather than for a number of frames: the paint is
// throttled and a fast frame loop can pass three times before one lands.
let mmCv=null,mmCtx=null,mmBtn=null,mmBig=false,mmBigBtn=null,mmList=null,mmBack=null,mmOpen=false,mmT=0,mmPaints=0,mmW=0;
// Where the HUD ends, measured when the map lays itself out and read by the
// arrow every frame: asking the layout engine sixty times a second for a
// number that changes when the window does is work a phone feels.
let mmTopY=60;
const mmPhone=()=>innerWidth<=MM_PHONE;
// How tall the list of stops is when the map is big: two and a half rows, so
// that it reads as a list that scrolls rather than as a list that is cut off.
const MM_LIST=120;
// How wide the map is drawn, in CSS pixels. Big it takes the window, because
// a dark sheet behind it has taken the island and the controls at the foot of
// the screen with it: while the map is what you are looking at, it is the
// only thing to press.
function mmDim(){return mmBig
  ?Math.max(MM_SIZE,Math.min(MM_PHONE,innerWidth-24,
    innerHeight-mmTopY-MM_TAP-MM_LIST-56))
  :MM_SIZE}
function mmBuild(){
  if(mmCv)return;
  mmCv=document.createElement("canvas");mmCv.id="minimap";mmCv.width=mmCv.height=MM_SIZE*2;
  mmCv.setAttribute("role","img");
  mmCv.setAttribute("aria-label","Map of the archipelago. The stops are listed as buttons under the big map.");
  mmCv.style.cssText="position:fixed;right:10px;z-index:6;width:"+MM_SIZE+"px;height:"+MM_SIZE+
    "px;border-radius:12px;background:rgba(0,0,0,.55);border:1px solid rgba(241,241,248,.18);display:none;touch-action:none";
  document.body.appendChild(mmCv);mmCtx=mmCv.getContext("2d");
  mmTaps();
  // On a phone the map would cover a quarter of the screen, so it stays shut
  // behind a button of its own until it is asked for.
  mmBtn=mmChrome("minimap-btn","Map");
  // Opening the map paints it on the next frame instead of waiting out the
  // throttle, so it is never shown blank.
  mmBtn.addEventListener("click",()=>{mmOpen=!mmOpen;if(!mmOpen)mmBig=false;mmT=1;mmLayout()});
  mmBigBtn=mmChrome("minimap-big","Bigger");
  mmBigBtn.addEventListener("click",()=>mmSetBig(!mmBig));
  mmList=document.createElement("div");mmList.id="minimap-stops";
  mmList.setAttribute("role","group");mmList.setAttribute("aria-label","Walk to a stop");
  mmList.style.cssText="position:fixed;z-index:6;display:none;flex-direction:column;gap:6px;overflow-y:auto;"+
    "padding:8px;border-radius:12px;background:rgba(0,0,0,.55);border:1px solid rgba(241,241,248,.18)";
  document.body.appendChild(mmList);
  // The sheet behind the big map. It is what makes the big map a place you
  // are in: the island, the stick and the jump button are behind it, and a
  // press on it is the way out, like every other overlay in the game.
  mmBack=document.createElement("div");mmBack.id="minimap-back";
  mmBack.style.cssText="position:fixed;inset:0;z-index:19;display:none;background:rgba(0,0,0,.72)";
  mmBack.addEventListener("pointerdown",()=>mmSetBig(false));
  document.body.appendChild(mmBack);
  // Escape closes it, the way it closes the palette and the panels.
  addEventListener("keydown",e=>{if(e.key==="Escape"&&mmBig)mmSetBig(false)});
  mmBtnState();guideBuild();
  addEventListener("resize",mmLayout);mmLayout()}
// The map's own chrome: one look for the two buttons beside it, built here
// because the map builds itself and the stylesheet never hears of it.
function mmChrome(id,text){const b=document.createElement("button");b.id=id;b.type="button";
  b.textContent=text;
  b.style.cssText="position:fixed;right:10px;z-index:6;display:none;padding:6px 12px;font-size:12px;"+
    "min-height:"+MM_TAP+"px;border-radius:10px;background:rgba(0,0,0,.55);color:#F1F1F8;"+
    "border:1px solid rgba(241,241,248,.18)";
  document.body.appendChild(b);return b}
function mmSetBig(on){mmBig=on;mmT=1;mmLayout();drawMinimap()}
// A toggle says whether it is on: the button carries its own state rather
// than leaving a screen reader to guess from the canvas it controls.
function mmBtnState(){if(!mmBtn)return;
  mmBtn.setAttribute("aria-pressed",mmOpen?"true":"false");
  mmBtn.setAttribute("aria-expanded",mmOpen?"true":"false");
  mmBtn.setAttribute("aria-controls","minimap");
  mmBtn.setAttribute("aria-label",(mmOpen?"Hide":"Show")+" the map of the archipelago");
  if(!mmBigBtn)return;
  mmBigBtn.textContent=mmBig?"Smaller":"Bigger";
  mmBigBtn.setAttribute("aria-pressed",mmBig?"true":"false");
  mmBigBtn.setAttribute("aria-controls","minimap");
  mmBigBtn.setAttribute("aria-label",(mmBig?"Shrink":"Enlarge")+" the map of the archipelago")}
function mmLayout(){
  if(!mmCv)return;
  // Under everything the HUD has already put at the top, whatever it holds.
  const below=["hud","kpis"].map(id=>$(id)).filter(Boolean)
    .reduce((y,el)=>Math.max(y,el.getBoundingClientRect().bottom),60),top=below+8;
  mmTopY=below;
  // A full-screen panel owns the screen while it is open; the map waits.
  const busy=!!document.querySelector("#sheet.on, #vault.on"),
    phone=mmPhone(),show=!busy&&(!phone||mmOpen);
  const y=top+(phone&&!mmBig?MM_TAP+8:0),D=mmDim(),
    left=Math.max(12,(innerWidth-D)/2),under=y+D+8;
  // Resizing a canvas clears it, so it is only ever resized when the size it
  // is drawn at has actually changed.
  if(mmW!==D){mmW=D;mmCv.width=mmCv.height=D*2;mmCv.style.width=mmCv.style.height=D+"px"}
  mmCv.style.top=y+"px";mmBtn.style.top=top+"px";
  mmCv.style.display=show?"block":"none";
  // Big, the map and its two controls are one column down the middle; small,
  // the map keeps its corner and its button sits under it there.
  mmCv.style.right=mmBig?"":"10px";mmCv.style.left=mmBig?left+"px":"";
  mmBtn.style.display=phone&&!busy?"block":"none";
  mmBigBtn.style.display=show?"block":"none";
  mmBigBtn.style.top=under+"px";
  mmBigBtn.style.right=mmBig?"":"10px";mmBigBtn.style.left=mmBig?left+"px":"";
  mmList.style.display=show&&mmBig?"flex":"none";
  mmList.style.top=(under+MM_TAP+8)+"px";
  mmList.style.left=left+"px";
  mmList.style.width=D+"px";
  mmList.style.maxHeight=MM_LIST+"px";
  // Big, the map and what belongs to it stand in front of the sheet.
  mmBack.style.display=show&&mmBig?"block":"none";
  [mmCv,mmBigBtn,mmList].forEach(el=>{el.style.zIndex=mmBig?"20":"6"});
  mmBtnState();if(mmBig)mmStops();guideLayout()}
// The stops of this island as buttons: the map is a canvas, so a tap on a
// plot needs a twin that a keyboard and a screen reader can reach. The list is
// laid out six times a second and rebuilt only when what it says has changed:
// a list rebuilt under a keyboard is a list that loses the focus in it.
let mmSaid="";
function mmStops(){
  if(!mmList)return;
  const done=S.done||[];
  const said=(S.world||"campus")+":"+CH.length+":"+done.join(",");
  if(said===mmSaid&&mmList.firstChild)return;
  mmSaid=said;mmList.textContent="";
  CH.forEach((c,i)=>{const k=i+1,was=done.includes(k),locked=k>1&&!done.includes(k-1);
    const b=document.createElement("button");b.type="button";b.className="mm-stop";b.dataset.stop=String(k);
    b.textContent=c.h+", "+c.n+(was?" (delivered)":locked?" (not open yet)":"");
    b.setAttribute("aria-label","Walk to "+c.h+", "+c.n);
    b.style.cssText="display:block;width:100%;text-align:left;min-height:"+MM_TAP+"px;padding:8px 12px;"+
      "font-size:13px;border-radius:10px;background:rgba(241,241,248,.08);color:#F1F1F8;"+
      "border:1px solid rgba(241,241,248,.18)";
    // A stop a camp added has a lesson but no plot on the island, so there is
    // nowhere to walk to and the row says so by being unavailable.
    if(!PLOT_POS[i])b.disabled=true;
    b.addEventListener("click",()=>{if(walkTo(k))mmShut()});
    mmList.appendChild(b)})}
// What the map does once the walker is on its way: it has said what it had to
// say, and on a phone it was covering the island the walk happens on.
function mmShut(){mmSetBig(false);if(mmPhone()){mmOpen=false;mmLayout()}}
// Archipelago coordinates to canvas pixels. The square of four origins plus
// the widest island is what has to fit, whichever island is active.
function mmScale(){const half=ISLAND_GAP/2+WORLDS.campus.land[0][2]+6;return mmDim()/(half*2)}
// The next stop of this island, the one the map circles and the arrow points
// at. One answer, because two would drift apart.
function mmNext(){const done=(S.done||[]).length;
  return done<stopCount()?PLOT_POS[done]||null:null}
// A tap on a plot is a walk to it, which is the whole point of a map you can
// reach. A long press on a touch screen makes the map big; every pointer has
// the Bigger button, so nothing here has to be held down.
function mmTaps(){
  let at=null,press=null;
  const end=()=>{clearTimeout(press);press=null};
  mmCv.addEventListener("pointerdown",e=>{at=[e.clientX,e.clientY];
    if(e.pointerType==="touch")press=setTimeout(()=>{press=null;at=null;mmSetBig(true)},500)});
  mmCv.addEventListener("pointermove",e=>{if(at&&Math.hypot(e.clientX-at[0],e.clientY-at[1])>10){at=null;end()}});
  mmCv.addEventListener("pointercancel",()=>{at=null;end()});
  mmCv.addEventListener("pointerup",e=>{const from=at;at=null;end();
    if(!from||Math.hypot(e.clientX-from[0],e.clientY-from[1])>10)return;
    const k=mmPlotAt(e.clientX,e.clientY);if(k&&walkTo(k))mmShut()})}
// Which plot a point on the canvas is over, or 0. The map's own projection
// read backwards, so the plot a finger lands on is the plot that was drawn
// under it at whatever size the map has.
function mmPlotAt(clientX,clientY){
  if(!mmCv||!started)return 0;
  const r=mmCv.getBoundingClientRect(),D=mmDim();
  if(!r.width)return 0;
  const x=(clientX-r.left)/r.width*D,y=(clientY-r.top)/r.height*D;
  const s=mmScale(),o=islandOrigin(S.world||"campus"),c=D/2;
  let best=0,bd=MM_HIT;
  PLOT_POS.forEach((p,i)=>{const d=Math.hypot(c+(p.x+o.x)*s-x,c+(p.z+o.z)*s-y);
    if(d<bd){bd=d;best=i+1}});
  return best}
// Where a plot is on the screen, for the tests: the same projection the map
// draws with, so a test taps where the plot actually is at whatever size the
// map has rather than working the place out a second time.
function mmClientAt(p){const r=mmCv.getBoundingClientRect(),D=mmDim(),s=mmScale(),o=islandOrigin(S.world||"campus");
  return [r.left+D/2+(p.x+o.x)*s,r.top+D/2+(p.z+o.z)*s]}
function drawMinimap(){
  if(!mmCtx||mmCv.style.display==="none")return;
  mmPaints++;
  const D=mmDim(),g=mmCtx,s=mmScale()*2,c=D,here=S.world||"campus";
  g.setTransform(1,0,0,1,0,0);g.clearRect(0,0,D*2,D*2);
  // Canvas x is world x, canvas y is world z, both centred on the square.
  const px=(x,z)=>[c+x*s,c+z*s];
  bridges.forEach(b=>{const o=islandOrigin(here);
    const a=px(b.pa.x+o.x,b.pa.z+o.z),d=px(b.pb.x+o.x,b.pb.z+o.z);
    g.strokeStyle=b.open?PALETTE.text:PALETTE.muted;g.lineWidth=b.open?3:2;
    g.setLineDash(b.open?[]:[5,5]);g.beginPath();g.moveTo(a[0],a[1]);g.lineTo(d[0],d[1]);g.stroke()});
  g.setLineDash([]);
  WORLD_IDS.forEach(id=>{const o=islandOrigin(id),w=WORLDS[id],p=px(o.x,o.z);
    g.fillStyle=w.swatch;g.globalAlpha=id===here?1:.45;
    g.beginPath();g.arc(p[0],p[1],w.land[0][2]*s,0,Math.PI*2);g.fill();g.globalAlpha=1;
    if(id===here){g.strokeStyle=PALETTE.text;g.lineWidth=2;g.stroke()}});
  // Every plot of this island, so a tap has something to aim at, and the next
  // one ringed. Big, each carries its number: a map you walk from says which
  // stop is which.
  const o=islandOrigin(here),next=mmNext();
  g.font="bold "+(mmBig?22:14)+"px Inter,sans-serif";g.textAlign="center";g.textBaseline="middle";
  PLOT_POS.forEach((p,i)=>{const q=px(p.x+o.x,p.z+o.z),was=(S.done||[]).includes(i+1);
    g.fillStyle=was?PALETTE.greenBright:PALETTE.text;g.globalAlpha=was?.9:.55;
    g.beginPath();g.arc(q[0],q[1],mmBig?9:4,0,Math.PI*2);g.fill();g.globalAlpha=1;
    if(!mmBig)return;
    g.fillStyle=PALETTE.black;g.fillText(String(i+1),q[0],q[1]+1)});
  if(next){const p=px(next.x+o.x,next.z+o.z);
    g.strokeStyle=PALETTE.orange;g.lineWidth=3;g.beginPath();g.arc(p[0],p[1],mmBig?14:7,0,Math.PI*2);g.stroke()}
  const L=chars.lotte;if(L){const p=px(L.g.position.x+o.x,L.g.position.z+o.z);
    g.fillStyle=PALETTE.greenBright;g.beginPath();g.arc(p[0],p[1],mmBig?8:5,0,Math.PI*2);g.fill();
    g.strokeStyle=PALETTE.black;g.lineWidth=2;g.stroke()}}

/* ---------------- the arrow at the edge of the screen ---------------- */
// Where the next stop is, always, so nobody circles the island looking for
// the signpost; once the island is finished it points at the bridge that has
// opened instead. Pressing it walks you there, so the cue and the way to
// follow it are one control. The mode is S.settings.guide: on, next (the stop
// and never the bridge) or off, and the two hardest difficulties, where
// finding your own way is the game, start it off.
let gEl=null,gArrow=null,gText=null,gSaid="",gGoal=null;
const _gv=new T.Vector3();
function guideMode(){const g=(S.settings||{}).guide;
  if(g==="on"||g==="next"||g==="off")return g;
  return ["expert","god"].includes(typeof difficulty==="function"?difficulty():"normal")?"off":"on"}
function guideBuild(){
  if(gEl)return;
  gEl=document.createElement("button");gEl.id="guide";gEl.type="button";
  // Placed by its middle, so the point it is put on is the point it marks and
  // no width has to be measured every frame.
  gEl.style.cssText="position:fixed;z-index:6;display:none;align-items:center;gap:8px;"+
    "transform:translate(-50%,-50%);min-height:"+MM_TAP+"px;padding:6px 12px;font-size:12px;"+
    "font-weight:700;border-radius:22px;background:rgba(0,0,0,.55);color:#F1F1F8;"+
    "border:1px solid rgba(241,241,248,.18)";
  // The chevron is two borders and no glyph: a triangle renders the same in
  // every font, and it is the one thing on screen that has to rotate.
  gArrow=document.createElement("span");
  gArrow.style.cssText="width:0;height:0;border-left:8px solid transparent;border-right:8px solid transparent;"+
    "border-bottom:13px solid "+PALETTE.orange+";display:block";
  gText=document.createElement("span");
  gEl.appendChild(gArrow);gEl.appendChild(gText);
  gEl.addEventListener("click",guideGo);
  document.body.appendChild(gEl)}
// What the arrow is pointing at: the next stop of this island, or, once they
// are all delivered, the nearest open bridge off it.
function guideGoal(){
  const mode=guideMode();if(mode==="off"||!started)return null;
  const next=mmNext();
  if(next)return {x:next.x,z:next.z,stop:(S.done||[]).length+1,name:stopName((S.done||[]).length+1),colour:PALETTE.orange};
  if(mode!=="on")return null;
  const p=chars.lotte?chars.lotte.g.position:null;
  let b=null,bd=1e9;
  bridges.forEach(x=>{if(!x.open||!x.near)return;const d=p?Math.hypot(p.x-x.mid.x,p.z-x.mid.z):0;
    if(d<bd){bd=d;b=x}});
  if(!b)return null;
  const other=b.a===(S.world||"campus")?b.b:b.a;
  return {x:b.mid.x,z:b.mid.z,stop:0,name:"the bridge to "+((WORLDS[other]||{}).name||other),colour:PALETTE.text}}
function stopName(n){const c=CH[n-1];return c?c.h+", "+c.n:"the next stop"}
function guideGo(){if(!gGoal)return;
  if(gGoal.stop){walkTo(gGoal.stop);return}
  aim(gGoal.x,gGoal.z);toast(icon("compass")+"Walking there",esc(gGoal.name))}
// Placed every frame, because it tracks the camera; the words under it are
// written only when they change, which is once a walk.
function guideLayout(){
  if(!gEl)return;
  const busy=!!document.querySelector("#sheet.on, #vault.on, #pal.on");
  gGoal=busy?null:guideGoal();
  if(!gGoal||!chars.lotte){gEl.style.display="none";return}
  const p=chars.lotte.g.position,away=Math.round(Math.hypot(p.x-gGoal.x,p.z-gGoal.z));
  const v=_gv.set(gGoal.x,1.2,gGoal.z).project(camera);
  const w=innerWidth,h=innerHeight,cx=w/2,cy=h/2;
  // Behind the camera the projection comes out mirrored, so it is turned back.
  const back=v.z>1;let dx=(back?-v.x:v.x)*cx,dy=(back?v.y:-v.y)*cy;
  if(Math.abs(dx)<1e-3&&Math.abs(dy)<1e-3)dy=-1;
  // The rectangle the arrow is allowed to sit in: clear of the HUD at the top
  // and of the stick, the jump button and the Enter button at the bottom.
  const l=60-cx,r=w-60-cx,t=Math.min(cy-30,mmTopY+60)-cy,b=h-170-cy;
  const s=Math.min(dx>0?r/dx:dx<0?l/dx:1e9,dy>0?b/dy:dy<0?t/dy:1e9);
  if(s<1){dx*=s;dy*=s}
  gEl.style.display="flex";
  gEl.style.left=Math.round(cx+dx)+"px";gEl.style.top=Math.round(cy+dy)+"px";
  // The triangle is drawn pointing up, so zero degrees is up and the angle is
  // measured from there.
  gArrow.style.transform="rotate("+Math.round(Math.atan2(dx,-dy)*180/Math.PI)+"deg)";
  gArrow.style.borderBottomColor=gGoal.colour;
  const said=away+" m";
  if(said!==gSaid){gSaid=said;gText.textContent=said;
    gEl.setAttribute("aria-label","Walk to "+gGoal.name+", "+away+" metres away")}}
// Six times a second is plenty for a map of four islands, and it keeps the
// canvas work off the frame budget. The arrow is placed every frame: it
// follows the camera, and a chevron that lagged a sixth of a second behind
// the turn would point at where the island used to be.
function tickMinimap(dt){
  if(!started)return;
  mmBuild();guideLayout();mmT+=dt;if(mmT<.16)return;mmT=0;mmLayout();drawMinimap()}
window.__minimap=()=>({open:mmCv?mmCv.style.display!=="none":false,phone:mmPhone(),
  islands:WORLD_IDS.length,bridges:bridges.length,size:mmDim(),big:mmBig,
  stops:mmList?mmList.querySelectorAll("button").length:0,painted:mmPaints,
  plots:mmCv&&mmCv.style.display!=="none"?PLOT_POS.map(p=>mmClientAt(p)):[],
  at:PLOT_POS.map(p=>[p.x,p.z]),
  guide:gGoal?{name:gGoal.name,stop:gGoal.stop,shown:gEl.style.display!=="none",
    at:[parseFloat(gEl.style.left),parseFloat(gEl.style.top)],said:gSaid}:null});
