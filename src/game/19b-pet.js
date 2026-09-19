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

// The three states the island asks for, mapped onto what a pack actually
// carries. Sitting is the sleep row, which is the sitting pose in both of the
// OpenGameArt packs; a set without one idles instead of failing.
const PET_STATE={idle:"idle",walk:"walk",sit:"sleep"};
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
// One canvas per set: every frame of the three states in a row, nearest
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
  const tex=new T.CanvasTexture(cv);
  tex.magFilter=T.NearestFilter;tex.minFilter=T.NearestFilter;tex.generateMipmaps=false;
  tex.encoding=T.sRGBEncoding;
  return petSheets[id]={canvas:cv,tex,index,cells:cells.length,cw,ch,
    fps:d.fps||PET.FPS,source:d.source}}

// The companion itself: its sprite, where it is and what it is doing. The
// island is rebuilt on every crossing, so it notices a new scene and walks
// back in beside the walker rather than being left in the old one.
let pet=null;
function petBuild(id){
  const sh=petSheet(id);
  const m=new T.SpriteMaterial({map:sh.tex,transparent:true,alphaTest:.5});
  const spr=new T.Sprite(m);
  spr.scale.set(PET.HEIGHT*sh.cw/sh.ch,PET.HEIGHT,1);
  // Tapping the ground walks there; the companion is never a click target.
  spr.raycast=function(){};
  const L=chars.lotte,p=L?L.g.position:new T.Vector3();
  pet={id,sh,spr,x:p.x,z:p.z,face:1,state:"idle",frame:0,fT:0};
  scene.add(spr);return pet}

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
  if(id==="none"||!PETS[id]){if(pet){if(pet.spr.parent)pet.spr.parent.remove(pet.spr);pet=null}return}
  const L=chars.lotte;if(!L)return;
  if(!pet||pet.id!==id||pet.spr.parent!==scene){if(pet&&pet.spr.parent)pet.spr.parent.remove(pet.spr);petBuild(id)}
  const p=L.g.position,ry=L.g.rotation.y;
  // It settles behind the walker, in the walker's own facing, so turning on
  // the spot swings it round instead of dragging it through his legs.
  const tx=p.x-Math.sin(ry)*PET.FOLLOW,tz=p.z-Math.cos(ry)*PET.FOLLOW;
  const k=1-Math.exp(-PET.LAG*dt),nx=pet.x+(tx-pet.x)*k,nz=pet.z+(tz-pet.z)*k;
  // Land and bridges only: it slides along an edge the way the walker does
  // rather than paddling out over the water.
  if(onLandW(nx,nz)){pet.x=nx;pet.z=nz}
  else if(onLandW(nx,pet.z))pet.x=nx;
  else if(onLandW(pet.x,nz))pet.z=nz;
  const moved=Math.hypot(pet.x-tx,pet.z-tz),speed=Math.hypot(nx-pet.x,nz-pet.z)/Math.max(dt,1e-4);
  const sitting=typeof isSitting==="function"&&isSitting(L);
  pet.state=sitting?"sit":(speed>PET.WALK_AT||moved>PET.FOLLOW*.6?"walk":"idle");
  if(Math.abs(nx-pet.x)>1e-3)pet.face=nx>pet.x?1:-1;
  else if(Math.abs(tx-pet.x)>.2)pet.face=tx>pet.x?1:-1;
  pet.fT+=dt;const step=1/(pet.sh.fps||PET.FPS);
  while(pet.fT>=step){pet.fT-=step;pet.frame++}
  petPaint();
  // Reduced motion keeps the companion, and takes the bobbing away.
  const bob=(pet.state==="sit"||reducedMotion())?0:Math.sin(t*4)*PET.BOB;
  pet.spr.position.set(pet.x,PET.HEIGHT/2+bob,pet.z);
}

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

// Test seam: what the companion is and where, read-only.
window.__pet=()=>({id:petId(),on:!!(pet&&pet.spr.parent===scene),
  state:pet?pet.state:null,x:pet?pet.x:null,z:pet?pet.z:null,
  frames:pet?pet.sh.cells:0,onLand:pet?!!onLandW(pet.x,pet.z):true});
