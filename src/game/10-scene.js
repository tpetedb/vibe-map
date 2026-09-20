let renderer,scene,camera,clock,island,water,stars,sunM,moonM,dirL,hemiL,ambL;
const plots=[],builds={},clouds=[],parts=[],chars={},props={};
let PLOT_POS=[];
const mat=(c,o={})=>{const m=new T.MeshStandardMaterial(Object.assign({color:c,roughness:.9,metalness:0,flatShading:true},o));m.color.convertSRGBToLinear();if(o.emissive)m.emissive.convertSRGBToLinear();m.userData.viaMat=1;m.userData.cs=1;return m};
function fixColors(root){root.traverse(o=>{const m=o.material;if(m&&m.color&&!m.userData.cs){m.userData.cs=1;if(!(m instanceof T.MeshStandardMaterial&&m.flatShading&&m.userData.viaMat)){m.color.convertSRGBToLinear();if(m.emissive)m.emissive.convertSRGBToLinear()}}})}
// What the GPU holds for an object, given back. The island is rebuilt on every
// crossing and the walker on every change of look, and three.js frees nothing
// on its own: without this each rebuild left its buffers, its plate textures
// and its shadow map behind. A geometry, a material or a texture that outlives
// a scene (the shapes the instanced props share, the contact shadow, a pet's
// sheet, the one laptop every lap shows) is marked with keep() and left alone.
const KEPT=new WeakSet();
const keep=o=>{KEPT.add(o);return o};
function release(root){root.traverse(o=>{
  if(o.geometry&&!KEPT.has(o.geometry))o.geometry.dispose();
  (Array.isArray(o.material)?o.material:o.material?[o.material]:[]).forEach(m=>{
    if(KEPT.has(m))return;if(m.map&&!KEPT.has(m.map))m.map.dispose();m.dispose()});
  if(o.isInstancedMesh)o.dispose();
  if(o.isLight&&o.shadow)o.shadow.dispose()})}
// Whether an object is still part of the island being drawn: a plate of a
// walker that was rebuilt still has a parent, just not one in the scene.
function inScene(o){for(;o;o=o.parent)if(o===scene)return true;return false}
function discard(o){if(!o)return;if(o.parent)o.parent.remove(o);release(o)}
function box(w,h,d,c,x=0,y=0,z=0,py=false){const g=new T.BoxGeometry(w,h,d);if(py)g.translate(0,-h/2,0);const m=new T.Mesh(g,mat(c));m.position.set(x,y,z);m.castShadow=true;m.receiveShadow=true;return m}
// A window: the same box, marked so the merge keeps it in the lit half and
// the evening can put a light behind it.
function win(w,h,d,c,x,y,z){const m=box(w,h,d,c,x,y,z);m.userData.win=1;return m}
function sph(r,c,x=0,y=0,z=0,seg=8){const m=new T.Mesh(new T.SphereGeometry(r,seg,seg),mat(c));m.position.set(x,y,z);m.castShadow=true;return m}
function cyl(rt,rb,h,c,x=0,y=0,z=0,seg=8){const m=new T.Mesh(new T.CylinderGeometry(rt,rb,h,seg),mat(c));m.position.set(x,y,z);m.castShadow=true;m.receiveShadow=true;return m}
function cone(r,h,c,x=0,y=0,z=0,seg=4){const m=new T.Mesh(new T.ConeGeometry(r,h,seg),mat(c));m.position.set(x,y,z);m.castShadow=true;return m}
// Static props that never move share one draw call per shape and colour. The
// phone's draw-call budget is the reason: fifteen trees are four meshes, not
// forty-five, which is the headroom the archipelago is built inside. The
// builder collects matrices while it works and flushes them once.
const _q=new T.Quaternion(),_e=new T.Euler(),_p=new T.Vector3(),ONE=new T.Vector3(1,1,1);
function xform(x,y,z,rx=0,ry=0,rz=0,s){return new T.Matrix4().compose(_p.set(x,y,z),_q.setFromEuler(_e.set(rx,ry,rz)),s||ONE)}
// One instanced mesh from a list of matrices, or nothing when the list is
// empty. Shadows are opt-in: what stands far from the walker does not cast.
function instOf(geo,material,mats,shadow){if(!mats.length)return null;
  const im=new T.InstancedMesh(geo,material,mats.length);
  mats.forEach((m,i)=>im.setMatrixAt(i,m));
  im.castShadow=im.receiveShadow=!!shadow;scene.add(im);return im}
let BATCH=new Map();const BGEO={};
const shape=(key,make)=>BGEO[key]||(BGEO[key]=keep(make()));
function batchAdd(key,make,colour,m){const k=key+"|"+colour;let e=BATCH.get(k);
  if(!e){e={geo:shape(key,make),colour,m:[]};BATCH.set(k,e)}e.m.push(m)}
function batchFlush(){BATCH.forEach(e=>instOf(e.geo,mat(e.colour),e.m,true));BATCH=new Map()}

// Contact shadows: one soft decal under everything that stands on the ground,
// all of them in a single instanced draw. The shadow map is too broad to
// ground a trunk or a pair of feet, and the decal is the only shadow left
// when the shadows setting is off, which is when grounding matters most.
let BLOBS=[],blobTex=null;
function blobTexture(){if(blobTex)return blobTex;
  const cv=document.createElement("canvas");cv.width=cv.height=64;const g=cv.getContext("2d");
  const gr=g.createRadialGradient(32,32,0,32,32,32);
  gr.addColorStop(0,"rgba(0,0,0,.9)");gr.addColorStop(.5,"rgba(0,0,0,.45)");gr.addColorStop(1,"rgba(0,0,0,0)");
  g.fillStyle=gr;g.fillRect(0,0,64,64);blobTex=keep(new T.CanvasTexture(cv));return blobTex}
function blobAdd(x,z,r){BLOBS.push(xform(x,.04,z,-Math.PI/2,0,0,new T.Vector3(r,r,1)))}
function blobFlush(){if(!BLOBS.length)return;
  const m=new T.MeshBasicMaterial({map:blobTexture(),transparent:true,depthWrite:false,opacity:.5});
  m.userData.cs=1;
  const im=instOf(shape("blob-decal",()=>new T.PlaneGeometry(2,2)),m,BLOBS,false);
  BLOBS=[];if(im)im.renderOrder=1;props.blobs=im}

// Vertex colours on a land blob: the grass is lightest on the top face and
// darkens down the cliff to the waterline, with a little variation across the
// face, so one flat slab reads as ground instead of paper.
function tintGeo(geo,lo,hi){const p=geo.attributes.position,n=p.count,c=new Float32Array(n*3);
  let lowest=Infinity,highest=-Infinity;
  for(let i=0;i<n;i++){const y=p.getY(i);if(y<lowest)lowest=y;if(y>highest)highest=y}
  const span=Math.max(.001,highest-lowest);
  for(let i=0;i<n;i++){const t=(p.getY(i)-lowest)/span;
    const v=Math.sin(p.getX(i)*1.7+p.getZ(i)*2.3)*.5+.5;
    const f=lo+(hi-lo)*t*t+v*.07*t;
    c[i*3]=c[i*3+1]=c[i*3+2]=f}
  geo.setAttribute("color",new T.BufferAttribute(c,3));return geo}

// One mesh where a group had twenty. A finished building never moves, so its
// parts are baked into a single geometry that carries their colours as vertex
// colours; the windows go into a second one so the evening can light them.
// Anything the animation loop holds, a sprite, a light or an instanced mesh
// keeps its own node, because those still change.
function mergeGeos(list){let n=0;list.forEach(e=>n+=e.geo.attributes.position.count);
  const pos=new Float32Array(n*3),nor=new Float32Array(n*3),col=new Float32Array(n*3);
  let at=0;
  list.forEach(({geo,c})=>{const count=geo.attributes.position.count,old=geo.attributes.color;
    pos.set(geo.attributes.position.array,at*3);nor.set(geo.attributes.normal.array,at*3);
    for(let i=0;i<count;i++){const f=old?old.getX(i):1,g=old?old.getY(i):1,b=old?old.getZ(i):1;
      col[(at+i)*3]=c.r*f;col[(at+i)*3+1]=c.g*g;col[(at+i)*3+2]=c.b*b}
    at+=count;geo.dispose()});
  const out=new T.BufferGeometry();
  out.setAttribute("position",new T.BufferAttribute(pos,3));
  out.setAttribute("normal",new T.BufferAttribute(nor,3));
  out.setAttribute("color",new T.BufferAttribute(col,3));
  return out}
function mergeStatic(g){
  const keep=new Set();
  Object.values(g.userData).forEach(v=>(Array.isArray(v)?v:[v]).forEach(o=>{if(o&&o.isObject3D)keep.add(o)}));
  const matte=[],lit=[],dead=[],inv=new T.Matrix4();
  g.updateMatrixWorld(true);inv.copy(g.matrixWorld).invert();
  const take=o=>{const m=o.material;
    if(!m||!m.color||m.transparent||m.wireframe||m.vertexColors&&!o.geometry.attributes.color)return;
    const geo=(o.geometry.index?o.geometry.toNonIndexed():o.geometry.clone());
    geo.applyMatrix4(new T.Matrix4().multiplyMatrices(inv,o.matrixWorld));
    (o.userData.win?lit:matte).push({geo,c:m.color});dead.push(o)};
  const walk=o=>{if(keep.has(o)||o.isSprite||o.isLight||o.isInstancedMesh)return;
    if(o.isMesh){take(o);return}
    o.children.slice().forEach(walk)};
  g.children.slice().forEach(walk);
  dead.forEach(o=>{o.parent.remove(o);o.geometry.dispose();o.material.dispose()});
  const add=(list,material)=>{if(!list.length)return null;
    const m=new T.Mesh(mergeGeos(list),material);m.castShadow=m.receiveShadow=true;g.add(m);return m};
  const base=new T.MeshStandardMaterial({color:"#ffffff",vertexColors:true,roughness:.9,metalness:0,flatShading:true});
  base.userData.cs=1;
  const glow=new T.MeshStandardMaterial({color:"#ffffff",vertexColors:true,roughness:.7,metalness:0,flatShading:true,emissive:new T.Color(PALETTE.yellow).convertSRGBToLinear(),emissiveIntensity:0});
  glow.userData.cs=1;
  const merged=add(matte,base);g.userData.lit=add(lit,glow);
  return merged}

// A name can be long, so the plate is as wide as it has to be: the canvas is
// one or two plate widths, a power of two either way, and only a name too long
// for two shrinks its font. The canvas is drawn at twice the plate's
// coordinates so the text is sharp at the camera's distance, and the dark
// stroke keeps it legible over bright grass.
const plates=[];let plateProbe=null;
// The night lift of the people on the island: a share of each figure's own
// colour added to what the lights give it, so a face stays a face and a dark
// coat stays dark. One uniform object is shared by every figure material, so
// the rig moves them all by writing one number (tickRig), and one cache key
// keeps them on one program per material kind.
const FIG_LIFT={value:0};
function figMat(m){m.onBeforeCompile=s=>{s.uniforms.uLift=FIG_LIFT;
  s.fragmentShader="uniform float uLift;\n"+s.fragmentShader.replace("#include <emissivemap_fragment>",
    "#include <emissivemap_fragment>\ntotalEmissiveRadiance+=diffuseColor.rgb*uLift;")};
  m.customProgramCacheKey=()=>"fig";m.needsUpdate=true;return m}
function label(text,scale=1){const DPR=2,FONT=f=>"bold "+f+"px Inter,sans-serif";
  const probe=plateProbe||(plateProbe=document.createElement("canvas").getContext("2d"));
  let fs=30;probe.font=FONT(fs);
  const wide=probe.measureText(text).width>222,CW=wide?512:256,MAXW=CW-34;
  while(fs>11&&probe.measureText(text).width>MAXW){fs-=1;probe.font=FONT(fs)}
  const cv=document.createElement("canvas");cv.width=CW*DPR;cv.height=64*DPR;
  const g=cv.getContext("2d");g.scale(DPR,DPR);g.font=FONT(fs);
  g.textAlign="center";g.fillStyle="rgba(0,0,0,.62)";g.beginPath();const w=g.measureText(text).width+28;g.roundRect?g.roundRect(CW/2-w/2,10,w,44,22):g.rect(CW/2-w/2,10,w,44);g.fill();
  g.textBaseline="middle";g.lineJoin="round";g.lineWidth=Math.max(3,fs*.22);g.strokeStyle="rgba(0,0,0,.85)";g.strokeText(text,CW/2,33);
  g.fillStyle="#fff";g.fillText(text,CW/2,33);
  const sp=new T.Sprite(new T.SpriteMaterial({map:new T.CanvasTexture(cv),transparent:true,depthTest:false}));
  // sx and sy are the plate's own size; pw and ph are the part of it the pill
  // covers, which is what may not overlap another pill.
  const sx=4.6*scale*CW/256,sy=1.15*scale;sp.scale.set(sx,sy,1);
  Object.assign(sp.userData,{text,fs,sx,sy,pw:w/CW,ph:44/64,o:0});
  sp.material.opacity=0;sp.visible=false;plates.push(sp);return sp}
// Which plates are drawn, and how large. A plate costs a draw call, so only
// the ones near the walker are candidates. Each is held at a legible size on
// screen however far the camera is (PLATE.minPx), and where two pills would
// overlap the nearer one wins: the walker's own first, then by distance. The
// loser fades rather than pops. Nothing here allocates: it runs every frame.
// A plate that must stay hidden (a signpost whose stop is built) says so with
// userData.off, because visible is this function's to set.
const PLATE_FAR=11*WORLD_SCALE,PLATE_FADE=3.5*WORLD_SCALE,_pw=new T.Vector3(),_shown=[];
const plateOrder=(a,b)=>a.userData.d-b.userData.d;
function plateHidden(u){for(let i=0;i<_shown.length;i++){const o=_shown[i];
  if(Math.abs(o.cx-u.cx)<o.hw+u.hw&&Math.abs(o.cy-u.cy)<o.hh+u.hh)return true}
  return false}
function tickPlates(at,dt){
  const you=chars.lotte&&chars.lotte.plate,h=VIEW.h||1,w=VIEW.w||1;
  const unit=h/(2*Math.tan(camera.fov*Math.PI/360));
  const out=1-Math.max(0,Math.min(1,(camZoom()-PLATE.fadeZoom)/.3));
  for(let i=plates.length-1;i>=0;i--){const sp=plates[i],u=sp.userData;
    if(!inScene(sp)){plates.splice(i,1);continue}
    // y0 is where the caller put the plate; it grows upwards from there.
    if(u.y0===undefined)u.y0=sp.position.y;
    sp.position.y=u.y0;sp.getWorldPosition(_pw);u.d=sp===you?-1:Math.hypot(_pw.x-at.x,_pw.z-at.z);
    u.want=u.off?0:Math.max(0,Math.min(1,(PLATE_FAR-u.d)/PLATE_FADE))*out;
    const depth=Math.max(.1,-_pw.applyMatrix4(camera.matrixWorldInverse).z);
    const px=u.sy*unit/depth,k=Math.min(PLATE.grow,Math.max(PLATE.minPx,Math.min(PLATE.maxPx,px))/px);
    sp.scale.set(u.sx*k,u.sy*k,1);sp.position.y=u.y0+(k-1)*u.sy/2;
    // The pill's box on the canvas, in CSS pixels.
    _pw.applyMatrix4(camera.projectionMatrix);
    u.cx=(_pw.x+1)/2*w;u.cy=(1-_pw.y)/2*h-(k-1)*u.sy/2*unit/depth;
    u.hw=u.sx*k*u.pw*unit/depth/2+PLATE.gap;u.hh=u.sy*k*u.ph*unit/depth/2+PLATE.gap}
  plates.sort(plateOrder);_shown.length=0;
  const ease=reducedMotion()?1:Math.min(1,dt*9);
  for(const sp of plates){const u=sp.userData;
    if(u.want>0&&plateHidden(u))u.want=0;
    if(u.want>0)_shown.push(u);
    u.o+=(u.want-u.o)*ease;sp.material.opacity=u.o;sp.visible=u.o>.02}}
