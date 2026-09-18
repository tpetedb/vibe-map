let renderer,scene,camera,clock,island,water,wGeo,wBase,stars,sunM,moonM,dirL,hemiL,ambL;
const plots=[],builds={},clouds=[],parts=[],chars={},props={};
let PLOT_POS=[];
const mat=(c,o={})=>{const m=new T.MeshStandardMaterial(Object.assign({color:c,roughness:.9,metalness:0,flatShading:true},o));m.color.convertSRGBToLinear();if(o.emissive)m.emissive.convertSRGBToLinear();m.userData.viaMat=1;m.userData.cs=1;return m};
function fixColors(root){root.traverse(o=>{const m=o.material;if(m&&m.color&&!m.userData.cs){m.userData.cs=1;if(!(m instanceof T.MeshStandardMaterial&&m.flatShading&&m.userData.viaMat)){m.color.convertSRGBToLinear();if(m.emissive)m.emissive.convertSRGBToLinear()}}})}
function box(w,h,d,c,x=0,y=0,z=0,py=false){const g=new T.BoxGeometry(w,h,d);if(py)g.translate(0,-h/2,0);const m=new T.Mesh(g,mat(c));m.position.set(x,y,z);m.castShadow=true;m.receiveShadow=true;return m}
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
// A name can be long; the canvas cannot grow, so the font shrinks until the
// text fits the plate instead of running off it.
function label(text,scale=1){const cv=document.createElement("canvas");cv.width=256;cv.height=64;const g=cv.getContext("2d");const MAXW=222;let fs=30;g.font="bold "+fs+"px Inter,sans-serif";
  while(fs>11&&g.measureText(text).width>MAXW){fs-=1;g.font="bold "+fs+"px Inter,sans-serif"}
  g.textAlign="center";g.fillStyle="rgba(0,0,0,.45)";g.beginPath();const w=g.measureText(text).width+28;g.roundRect?g.roundRect(128-w/2,10,w,44,22):g.rect(128-w/2,10,w,44);g.fill();g.fillStyle="#fff";g.textBaseline="middle";g.fillText(text,128,33);
  const sp=new T.Sprite(new T.SpriteMaterial({map:new T.CanvasTexture(cv),transparent:true,depthTest:false}));sp.scale.set(4*scale,1*scale,1);sp.userData.text=text;sp.userData.fs=fs;return sp}

