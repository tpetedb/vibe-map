/* ---------------- the pixel companion ---------------- */
// The pets were a terminal feature. The same packed frames are injected here
// as PETS by tools/build.py from vibemap/data/pets, so there is one source of
// pixels for the panel and for the island, and a hosted game with no CLI
// anywhere still has all six. CREDITS.md next to that data names the artists
// and the licences; petCredits() repeats them exactly.
//
// One billboard sprite, one draw call: every frame of every state is painted
// once into a canvas atlas and the sprite picks a cell out of it, so a change
// of frame costs two numbers rather than a texture upload.

// The four states the island asks for, mapped onto what a pack actually
// carries. Sitting is the sleep row, which is the sitting pose in both of the
// OpenGameArt packs, and the cheer is the happy row every pack draws; a set
// without one of them idles instead of failing.
const PET_STATE={idle:"idle",walk:"walk",sit:"sleep",cheer:"happy"};
const PET_LABEL={cat:"Cat",crab:"Crab",dog:"Dog",duck:"Duck",snail:"Snail",turtle:"Turtle"};
// A transparent gutter around every cell, so a sprite scaled to a size that
// is not a whole number of pixels bleeds into nothing instead of its neighbour.
const PET_GUTTER=1;

const petIds=()=>Object.keys(typeof PETS==="undefined"?{}:PETS);
function petKnown(id){return id==="none"||petIds().indexOf(id)>=0}
// Which companion this game shows. S.pet is the player's choice; with none
// made the camp decides, through [pet] in config/camp.toml, which is what a
// published build carries. An unknown id never reaches here: the picker and
// the progress code both refuse one.
function petId(){if(S.pet&&petKnown(S.pet))return S.pet;
  const c=CONFIG.pet||{};if(c.enabled===false)return "none";
  return petKnown(c.species)?c.species:"none"}

const petSheets={};
// One canvas per set: every frame of the four states in a row, nearest
// filtered, built once and kept.
function petSheet(id){
  if(petSheets[id])return petSheets[id];
  const d=PETS[id],g=PET_GUTTER,cw=d.width+g*2,ch=d.height+g*2,cells=[],index={};
  Object.keys(PET_STATE).forEach(st=>{
    const frames=d.states[PET_STATE[st]]||d.states.idle;
    index[st]=frames.map(f=>{cells.push(f);return cells.length-1})});
  const cv=document.createElement("canvas");cv.width=cw*cells.length;cv.height=ch;
  const ctx=cv.getContext("2d");
  cells.forEach((frame,i)=>frame.forEach((row,y)=>{let x=0;
    row.forEach(run=>{const n=run[0],c=d.palette[run[1]];
      if(c){ctx.fillStyle=c;ctx.fillRect(i*cw+g+x,g+y,n,1)}x+=n})}));
  const tex=keep(new T.CanvasTexture(cv));
  tex.magFilter=T.NearestFilter;tex.minFilter=T.NearestFilter;tex.generateMipmaps=false;
  tex.encoding=T.sRGBEncoding;
  return petSheets[id]={canvas:cv,tex,index,cells:cells.length,cw,ch,
    fps:d.fps||PET.FPS,source:d.source}}

// The companion itself: its sprite, where it is and what it is doing. The
// island is rebuilt on every crossing, so it notices a new scene and walks
// back in beside the walker rather than being left in the old one.
let pet=null;
function petBuild(id,was){
  const sh=petSheet(id);
  // The pixels are the artist's colours, so the filmic curve that shapes the
  // lit scene is not applied to them; the night tints them instead (petTint).
  const m=new T.SpriteMaterial({map:sh.tex,transparent:true,alphaTest:.5,toneMapped:false});
  const spr=new T.Sprite(m);
  spr.scale.set(PET.PX*sh.cw,PET.PX*sh.ch,1);
  // Tapping the ground walks there; the companion is never a click target.
  spr.raycast=function(){};
  // The same soft decal the walker stands on (blobTexture in 10-scene.js), so
  // the companion is grounded rather than floating over the grass.
  const sd=new T.Mesh(new T.PlaneGeometry(PET.PX*sh.cw,PET.PX*sh.cw),
    new T.MeshBasicMaterial({map:blobTexture(),transparent:true,depthWrite:false,opacity:.45}));
  sd.rotation.x=-Math.PI/2;sd.renderOrder=1;sd.material.userData.cs=1;sd.raycast=function(){};
  // A crossing rebuilds the island under the walker, in new coordinates. The
  // companion is put back where it was beside him, not on top of him.
  const L=chars.lotte,p=L?L.g.position:new T.Vector3();was=was||{dx:0,dz:0,face:1,done:-1,world:null};
  pet={id,sh,spr,shadow:sd,x:p.x+was.dx,z:p.z+was.dz,dx:was.dx,dz:was.dz,face:was.face,
    state:"idle",frame:0,fT:0,cheer:0,done:was.done,world:was.world};
  scene.add(spr);scene.add(sd);return pet}

function petRemove(){if(!pet)return;discard(pet.spr);discard(pet.shadow);pet=null}
function petCell(){const cells=pet.sh.index[pet.state]||pet.sh.index.idle;
  return cells[pet.frame%cells.length]}
function petPaint(){const sh=pet.sh,du=sh.cw/sh.canvas.width,u=petCell()*du;
  // A companion walking left is the same pixels mirrored: a negative repeat
  // reads the cell backwards, which costs nothing and needs no second sheet.
  if(pet.face>0){sh.tex.offset.x=u;sh.tex.repeat.x=du}
  else{sh.tex.offset.x=u+du;sh.tex.repeat.x=-du}}

// Called once a frame from the animation loop. It owns the companion end to
// end: building it when the choice or the island changed, easing it after the
// walker, and picking the frame.
function tickPet(dt,t){
  petPreview(dt);
  const id=petId();
  if(id==="none"||!PETS[id]){if(pet)petRemove();return}
  const L=chars.lotte;if(!L)return;
  if(!pet||pet.id!==id||pet.spr.parent!==scene){const was=pet;petRemove();petBuild(id,was)}
  // A stop claimed on this island is worth a cheer. The count is state, so
  // the companion notices it by looking, whoever made the claim and however.
  const world=S.world||"campus",done=(S.done||[]).length;
  if(pet.world===world&&done>pet.done)pet.cheer=PET.CHEER;
  pet.world=world;pet.done=done;pet.cheer=Math.max(0,pet.cheer-dt);
  const p=L.g.position,ry=L.g.rotation.y;
  // It settles behind the walker, in the walker's own facing, so turning on
  // the spot swings it round instead of dragging it through his legs.
  let tx=p.x-Math.sin(ry)*PET.FOLLOW+Math.cos(ry)*PET.SIDE,
      tz=p.z-Math.cos(ry)*PET.FOLLOW-Math.sin(ry)*PET.SIDE;
  // Its spot beside the walker can be over the water: on a bridge, on a
  // causeway, at the shore. Then it falls in behind him, and where even that
  // is water, or it has been left a leash behind, it comes to where he stands.
  if(!onLandW(tx,tz)){tx=p.x-Math.sin(ry)*PET.FOLLOW;tz=p.z-Math.cos(ry)*PET.FOLLOW}
  if(!onLandW(tx,tz)||Math.hypot(pet.x-p.x,pet.z-p.z)>PET.LEASH){tx=p.x;tz=p.z}
  const px=pet.x,pz=pet.z;
  const k=1-Math.exp(-PET.LAG*dt),nx=px+(tx-px)*k,nz=pz+(tz-pz)*k;
  // Land and bridges only: it slides along an edge the way the walker does
  // rather than paddling out over the water.
  if(onLandW(nx,nz)){pet.x=nx;pet.z=nz}
  else if(onLandW(nx,pz))pet.x=nx;
  else if(onLandW(px,nz))pet.z=nz;
  // Two leashes behind there is water between them that it cannot walk round.
  if(Math.hypot(pet.x-p.x,pet.z-p.z)>PET.LEASH*2){pet.x=tx;pet.z=tz}
  pet.dx=pet.x-p.x;pet.dz=pet.z-p.z;
  // Walking is what it does this frame or what it still has to catch up: the
  // ease is slow enough that the last strides of a long catch-up are quiet.
  const travel=Math.hypot(pet.x-px,pet.z-pz)/Math.max(dt,1e-4),gap=Math.hypot(pet.x-tx,pet.z-tz);
  const sitting=typeof isSitting==="function"&&isSitting(L);
  const moving=travel>PET.WALK_AT||gap>PET.FOLLOW*.6;
  pet.state=sitting?"sit":moving?"walk":pet.cheer>0?"cheer":"idle";
  if(Math.abs(pet.x-px)>1e-3)pet.face=pet.x>px?1:-1;
  else if(Math.abs(tx-pet.x)>.2)pet.face=tx>pet.x?1:-1;
  pet.fT+=dt;const step=1/(pet.sh.fps||PET.FPS);
  while(pet.fT>=step){pet.fT-=step;pet.frame++}
  petPaint();
  // Reduced motion keeps the companion, and takes the bobbing and the hop of
  // the cheer away.
  const calm=reducedMotion(),hop=pet.state==="cheer"&&!calm?Math.abs(Math.sin(t*9))*.35:0;
  const bob=(pet.state==="sit"||calm)?0:Math.sin(t*4)*PET.BOB;
  const s=petScale();pet.spr.scale.set(PET.PX*pet.sh.cw*s,PET.PX*pet.sh.ch*s,1);
  // The gutter row is transparent, so the feet sit on the grass rather than
  // a pixel above it.
  pet.spr.position.set(pet.x,PET.PX*s*(pet.sh.ch/2-PET_GUTTER)+bob+hop,pet.z);
  pet.shadow.position.set(pet.x,.05,pet.z);pet.shadow.scale.setScalar(s);
  petTint();
}
// Pixel art is only crisp when every sprite pixel covers the same whole number
// of device pixels; at any other size nearest filtering makes some columns a
// pixel wider than their neighbours and they crawl as the camera moves. So the
// sprite is resized a little every frame to the nearest whole number for its
// depth, and never below PET.MIN_TEXEL.
const _pv=new T.Vector3();
function petScale(){
  const depth=Math.max(.1,-_pv.set(pet.x,0,pet.z).applyMatrix4(camera.matrixWorldInverse).z);
  const texel=PET.PX*VIEW.h/(2*Math.tan(camera.fov*Math.PI/360))/depth*renderer.getPixelRatio();
  pet.texel=Math.max(PET.MIN_TEXEL,Math.round(texel));return pet.texel/texel}
// A sprite takes no light, so the sky stage colours it by hand: the artist's
// pixels at noon, and towards the moonlight of the rig as the night comes on,
// dimmed but never so far that it is lost against dark grass.
const _pc=new T.Color(),WHITE=new T.Color("#ffffff");
function petTint(){const r=SKY_RIG[skyN]||SKY_RIG[0],k=PET.NIGHT*Math.max(0,Math.min(1,(skyN-2)/4));
  pet.spr.material.color.copy(WHITE).lerp(_pc.set(r.sun).convertSRGBToLinear(),k).multiplyScalar(1-k*.35)}

/* ---------------- choosing one ---------------- */
// The picker, the same markup in the onboarding and in Settings: a select and
// a preview that walks on the spot, so the choice is made by looking at it.
function petOptions(){return ["none"].concat(petIds())}
// The onboarding and Settings both carry one, so the caller names the select:
// two elements with one id would make the hidden one answer for the visible.
function petPicker(el){el=el||"set-pet";const id=petId();
  return `<div class="setting wide pet"><label for="${el}">Companion</label>`+
    `<select id="${el}" onchange="setPet(this.value)">`+
    petOptions().map(k=>`<option value="${k}"${id===k?" selected":""}>${k==="none"?"No companion":PET_LABEL[k]||k}</option>`).join("")+
    `</select><canvas id="${el}-prev" width="96" height="72" aria-hidden="true"></canvas>`+
    `<p class="small muted">A pixel friend that follows you across the islands, the same one <code>vibe pet</code> shows in the terminal. ${petCredits()}</p></div>`}
// The credits, exactly as vibemap/data/pets/CREDITS.md names them.
function petCredits(){return "Pixels: "+petIds().map(k=>{const s=PETS[k].source;
  return `${PET_LABEL[k]||k} by <a href="${s.author_url||s.url}" target="_blank" rel="noopener">${s.author}</a>, <a href="${s.url}" target="_blank" rel="noopener">${s.project}</a> (${s.licence})`}).join("; ")+"."}
// The choice is state, so an unknown id is refused here rather than stored.
window.setPet=function(id){if(!petKnown(id))return;S.pet=id;save();
  if(typeof renderSettings==="function"&&$("s-settings")&&$("s-settings").classList.contains("on"))renderSettings();
  if(typeof renderOnboarding==="function"&&$("onboard"))renderOnboarding()};

// The preview draws straight from the atlas canvas, so it shares the frames
// with the island and never touches the sprite's own texture offsets.
let petPrevT=0,petPrevF=0;
function petPreview(dt){const cv=$("set-pet-prev")||$("ob-pet-prev");if(!cv)return;
  const ctx=cv.getContext("2d");ctx.clearRect(0,0,cv.width,cv.height);
  const id=petId();if(id==="none"||!PETS[id])return;
  const sh=petSheet(id),cells=sh.index.walk||sh.index.idle;
  petPrevT+=dt;const step=1/(sh.fps||PET.FPS);
  while(petPrevT>=step){petPrevT-=step;petPrevF++}
  const cell=cells[petPrevF%cells.length],z=Math.floor(Math.min(cv.width/sh.cw,cv.height/sh.ch));
  ctx.imageSmoothingEnabled=false;
  ctx.drawImage(sh.canvas,cell*sh.cw,0,sh.cw,sh.ch,
    Math.round((cv.width-sh.cw*z)/2),Math.round((cv.height-sh.ch*z)/2),sh.cw*z,sh.ch*z)}

// Test seam: what the companion is and where, read-only. screen is where it
// is on the canvas, so a screenshot can be framed on it instead of on guesswork.
function petScreen(){if(!pet||!camera)return null;
  const v=pet.spr.position.clone().project(camera),rc=$("c").getBoundingClientRect();
  return {x:rc.left+(v.x+1)/2*rc.width,y:rc.top+(1-v.y)/2*rc.height}}
window.__pet=()=>({id:petId(),on:!!(pet&&pet.spr.parent===scene),
  state:pet?pet.state:null,x:pet?pet.x:null,z:pet?pet.z:null,
  // texel is how many device pixels one sprite pixel covers, always whole.
  texel:pet?pet.texel:0,
  frames:pet?pet.sh.cells:0,
  // What the companion costs the renderer: the billboard and its contact
  // shadow, one draw call each, whatever the pack or the state.
  objects:pet?[pet.spr,pet.shadow].filter(o=>o.parent===scene).length:0,onLand:pet?!!onLandW(pet.x,pet.z):true,screen:petScreen()});
