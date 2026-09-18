// The minimap: the four islands, the bridges, you, and the next stop. It is a
// 2D canvas rather than a second camera, so it costs no draw call in the
// scene. Like everything else on screen it is derived: it reads S, WORLDS and
// the bridges of this frame and holds no state of its own beyond whether it
// is open on a phone.
//
// The element is built here instead of in body.html because it belongs to the
// archipelago, not to the HUD, and a fork that drops this file should lose the
// map and nothing else.

const MM_SIZE=136,MM_PHONE=560;
let mmCv=null,mmCtx=null,mmBtn=null,mmOpen=false,mmT=0;
const mmPhone=()=>innerWidth<=MM_PHONE;
function mmBuild(){
  if(mmCv)return;
  mmCv=document.createElement("canvas");mmCv.id="minimap";mmCv.width=mmCv.height=MM_SIZE*2;
  mmCv.setAttribute("aria-label","Map of the archipelago");
  mmCv.style.cssText="position:fixed;right:10px;z-index:6;width:"+MM_SIZE+"px;height:"+MM_SIZE+
    "px;border-radius:12px;background:rgba(0,0,0,.55);border:1px solid rgba(241,241,248,.18);display:none";
  document.body.appendChild(mmCv);mmCtx=mmCv.getContext("2d");
  // On a phone the map would cover a quarter of the screen, so it stays shut
  // behind a button of its own until it is asked for.
  mmBtn=document.createElement("button");mmBtn.id="minimap-btn";mmBtn.type="button";
  mmBtn.textContent="Map";mmBtn.setAttribute("aria-label","Show the map of the archipelago");
  mmBtn.style.cssText="position:fixed;right:10px;z-index:6;display:none;padding:6px 10px;font-size:12px;"+
    "border-radius:10px;background:rgba(0,0,0,.55);color:#F1F1F8;border:1px solid rgba(241,241,248,.18)";
  mmBtn.addEventListener("click",()=>{mmOpen=!mmOpen;mmLayout()});
  document.body.appendChild(mmBtn);
  addEventListener("resize",mmLayout);mmLayout()}
function mmLayout(){
  if(!mmCv)return;
  // Under everything the HUD has already put at the top, whatever it holds.
  const below=["hud","kpis"].map(id=>$(id)).filter(Boolean)
    .reduce((y,el)=>Math.max(y,el.getBoundingClientRect().bottom),60),top=below+8;
  mmCv.style.top=top+"px";mmBtn.style.top=top+"px";
  // A full-screen panel owns the screen while it is open; the map waits.
  const busy=!!document.querySelector("#sheet.on, #vault.on"),
    phone=mmPhone(),show=!busy&&(!phone||mmOpen);
  mmCv.style.display=show?"block":"none";
  mmBtn.style.display=phone&&!busy?"block":"none";
  if(phone&&show)mmCv.style.top=(top+34)+"px"}
// Archipelago coordinates to canvas pixels. The square of four origins plus
// the widest island is what has to fit, whichever island is active.
function mmScale(){const half=ISLAND_GAP/2+WORLDS.campus.land[0][2]+6;return MM_SIZE/(half*2)}
function drawMinimap(){
  if(!mmCtx||mmCv.style.display==="none")return;
  const g=mmCtx,s=mmScale()*2,c=MM_SIZE,here=S.world||"campus";
  g.setTransform(1,0,0,1,0,0);g.clearRect(0,0,MM_SIZE*2,MM_SIZE*2);
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
  // The next stop on this island, and the walker.
  const o=islandOrigin(here),next=PLOT_POS[(S.done||[]).length];
  if(next){const p=px(next.x+o.x,next.z+o.z);
    g.strokeStyle=PALETTE.orange;g.lineWidth=3;g.beginPath();g.arc(p[0],p[1],7,0,Math.PI*2);g.stroke()}
  const L=chars.lotte;if(L){const p=px(L.g.position.x+o.x,L.g.position.z+o.z);
    g.fillStyle=PALETTE.greenBright;g.beginPath();g.arc(p[0],p[1],5,0,Math.PI*2);g.fill();
    g.strokeStyle=PALETTE.black;g.lineWidth=2;g.stroke()}}
// Six times a second is plenty for a map of four islands, and it keeps the
// canvas work off the frame budget.
function tickMinimap(dt){
  if(!started)return;
  mmBuild();mmT+=dt;if(mmT<.16)return;mmT=0;mmLayout();drawMinimap()}
window.__minimap=()=>({open:mmCv?mmCv.style.display!=="none":false,phone:mmPhone(),
  islands:WORLD_IDS.length,bridges:bridges.length,size:MM_SIZE});
