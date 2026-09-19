let renderer,scene,camera,clock,island,water,stars,sunM,moonM,dirL,hemiL,ambL;
const plots=[],builds={},clouds=[],parts=[],chars={},props={};
let PLOT_POS=[];
const mat=(c,o={})=>{const m=new T.MeshStandardMaterial(Object.assign({color:c,roughness:.9,metalness:0,flatShading:true},o));m.color.convertSRGBToLinear();if(o.emissive)m.emissive.convertSRGBToLinear();m.userData.viaMat=1;m.userData.cs=1;return m};
function fixColors(root){root.traverse(o=>{const m=o.material;if(m&&m.color&&!m.userData.cs){m.userData.cs=1;if(!(m instanceof T.MeshStandardMaterial&&m.flatShading&&m.userData.viaMat)){m.color.convertSRGBToLinear();if(m.emissive)m.emissive.convertSRGBToLinear()}}})}
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
const shape=(key,make)=>BGEO[key]||(BGEO[key]=make());
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
  g.fillStyle=gr;g.fillRect(0,0,64,64);blobTex=new T.CanvasTexture(cv);return blobTex}
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

// A name can be long; the canvas cannot grow, so the font shrinks until the
// text fits the plate instead of running off it. The canvas is drawn at twice
// the plate's coordinates so the text is sharp at the camera's distance, and
// the dark stroke keeps it legible over bright grass.
const plates=[];
function label(text,scale=1){const cv=document.createElement("canvas");const DPR=2;cv.width=256*DPR;cv.height=64*DPR;
  const g=cv.getContext("2d");g.scale(DPR,DPR);const MAXW=222;let fs=30;g.font="bold "+fs+"px Inter,sans-serif";
  while(fs>11&&g.measureText(text).width>MAXW){fs-=1;g.font="bold "+fs+"px Inter,sans-serif"}
  g.textAlign="center";g.fillStyle="rgba(0,0,0,.62)";g.beginPath();const w=g.measureText(text).width+28;g.roundRect?g.roundRect(128-w/2,10,w,44,22):g.rect(128-w/2,10,w,44);g.fill();
  g.textBaseline="middle";g.lineJoin="round";g.lineWidth=Math.max(3,fs*.22);g.strokeStyle="rgba(0,0,0,.85)";g.strokeText(text,128,33);
  g.fillStyle="#fff";g.fillText(text,128,33);
  const sp=new T.Sprite(new T.SpriteMaterial({map:new T.CanvasTexture(cv),transparent:true,depthTest:false}));
  sp.scale.set(4.6*scale,1.15*scale,1);sp.userData.text=text;sp.userData.fs=fs;plates.push(sp);return sp}
// Plates cost a draw call each, so only the ones near the walker are drawn;
// the rest fade out and stop being rendered at all.
const PLATE_FAR=11*WORLD_SCALE,PLATE_FADE=3.5*WORLD_SCALE,_pw=new T.Vector3();
function tickPlates(at){for(let i=plates.length-1;i>=0;i--){const sp=plates[i];
  if(!sp.parent){plates.splice(i,1);continue}
  sp.getWorldPosition(_pw);const d=Math.hypot(_pw.x-at.x,_pw.z-at.z);
  const o=Math.max(0,Math.min(1,(PLATE_FAR-d)/PLATE_FADE));
  sp.material.opacity=o;sp.visible=o>.02}}
