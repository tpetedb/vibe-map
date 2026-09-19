function init3d(){
  const st=$("stage");renderer=new T.WebGLRenderer({canvas:$("c"),antialias:true});renderer.shadowMap.enabled=true;renderer.shadowMap.type=T.PCFSoftShadowMap;renderer.outputEncoding=T.sRGBEncoding;
  // Filmic roll-off instead of a linear clip: without it a lit window at
  // night and grass at noon land on the same flat value.
  renderer.toneMapping=T.ACESFilmicToneMapping;renderer.toneMappingExposure=EXPOSURE;
  camera=new T.PerspectiveCamera(CAM.fov,st.clientWidth/st.clientHeight,.5,CAM.far*WORLD_SCALE);camera.position.set(0,22*WORLD_SCALE,26*WORLD_SCALE);
  clock=new T.Clock();fitRenderer();
  addEventListener("resize",fitRenderer);watchContext($("c"));
  // The zoom listens before the walk does, so a pinch is known to be a pinch
  // by the time the tap handler sees the same finger lift.
  buildWorld(S.world||"campus");setupZoom();setupInput();inited=true;animate();
}
// The browser may take the WebGL context back: a phone short of memory, a tab
// that slept, a driver reset. three.js stops drawing and says nothing, which
// left a flat blue stage with a HUD that carried on. The loop stops with it,
// the stage says what happened, and the Roadmap, which needs no 3D, opens the
// way it does when 3D fails at the start. three.js rebuilds its own state when
// the context returns, so the island comes back without a reload.
let gfxLost=false;
function watchContext(c){
  c.addEventListener("webglcontextlost",e=>{e.preventDefault();gfxLost=true;gfxNotice()});
  c.addEventListener("webglcontextrestored",()=>{gfxLost=false;clock.getDelta();fitRenderer();gfxNotice()})}
function gfxNotice(){const n=$("gfxlost");if(n)n.hidden=!gfxLost;
  $("stage").classList.toggle("lost",gfxLost);
  if(gfxLost&&started){$("enter").classList.remove("on");openSheet("s-map")}}
// The frame the island needs: the distance that makes a disc of the island's
// radius fit inside both the vertical and the horizontal field of view. A
// narrow window pushes the camera back rather than cropping the diorama, and
// the drift allowance covers how far the follow pulls the island off centre.
function camFitDist(){const asp=Math.max(.35,VIEW.w/VIEW.h);
  const r=(W.land[0][2]+2.6+CAM.drift*.5)*CAM.margin;
  const vf=camera.fov*Math.PI/360,hf=Math.atan(Math.tan(vf)*asp),p=CAM.pitch;
  // The island is a disc on the ground, not a sphere: the near edge is what
  // runs out of the top of the frame first, and it sits closer than the
  // centre, which is the cos term. Sideways the edge is at the centre's
  // depth, so that one is the plain half-angle.
  return Math.max(r*Math.cos(p)+r*Math.sin(p)/Math.tan(vf),r/Math.tan(hf))}
// A land blob: a grass disc with a dirt skirt below the waterline, the same
// shape for the island, its satellites and the annexes. Returns the grass.
function landBlob(group,x,z,r,seg){
  const g=new T.Mesh(tintGeo(new T.CylinderGeometry(r,r+1.2,2.4,seg||9,3),.58,1),mat(W.grass,{vertexColors:true}));
  g.position.set(x,-1.2,z);g.castShadow=g.receiveShadow=true;
  const d=new T.Mesh(tintGeo(new T.CylinderGeometry(r+1.1,r+2.2,2.2,seg||9,2),.72,1),mat(W.dirt,{vertexColors:true}));
  d.position.set(x,-2.6,z);d.castShadow=d.receiveShadow=true;
  group.add(g,d);return g}
function slabMat(id){return mat(id==="prod"?"#8A8A98":id==="winter"?"#C9D6E2":id==="desert"?"#C9A24E":"#E9D9B5")}
// A scene that has been replaced, waiting for the frame that follows it.
const trash=[];
function emptyTrash(){while(trash.length)release(trash.pop())}
// `carry` hands the walker across a bridge: a position already converted into
// the new island's coordinates, so the crossing does not interrupt the walk.
function buildWorld(id,carry){
  const prevBg=scene&&scene.background?scene.background.clone():null;
  W=WORLDS[id]||WORLDS.campus;S.world=id;if(!S.doneW[id])S.doneW[id]=[];S.done=S.doneW[id];CH=CAMPAIGN[id].ws;save();
  plots.length=0;clouds.length=0;parts.length=0;plates.length=0;for(const k in builds)delete builds[k];for(const k in props)delete props[k];obstacles=[];annexes=[];
  PLOT_POS=W.plots.map(p=>new T.Vector3(p[0],0,p[1]));
  // The bridges are ground, so they exist before anything asks onLandW.
  bridges=bridgesFor(id);
  const WS=WORLD_SCALE;
  // The fog has to reach across the archipelago: a neighbour island is a
  // silhouette in the haze, not a wall of sky colour.
  if(scene)trash.push(scene);
  scene=new T.Scene();scene.fog=new T.Fog(W.fog,80*WS,280*WS);
  hemiL=new T.HemisphereLight("#cfe9ff","#4a7a3a",.7);scene.add(hemiL);ambL=new T.AmbientLight("#fff",.15);scene.add(ambL);
  dirL=new T.DirectionalLight("#fff5d6",1.1);dirL.position.set(14*WS,24*WS,10*WS);dirL.castShadow=true;dirL.shadow.mapSize.set(CONFIG.shadowMap,CONFIG.shadowMap);dirL.shadow.bias=-.0008;dirL.shadow.normalBias=.02;Object.assign(dirL.shadow.camera,{left:-28*WS,right:28*WS,top:28*WS,bottom:-28*WS,near:1,far:80*WS});scene.add(dirL);
  buildSky();
  const ex=k=>W.extras.includes(k);const dummy=new T.Object3D();
  // landmass. Every blob is baked into one mesh: the island is the ground the
  // tap-to-walk ray hits, and it never moves, so it costs one draw call.
  const land=new T.Group();
  landBlob(land,...W.land[0],12);W.land.slice(1).forEach(b=>landBlob(land,...b));scene.add(land);
  island=mergeStatic(land);island.userData.parts=[island];
  buildSilhouettes(id);buildBridges();
  // sea
  // Wide enough that its edge is behind the haze from the farthest zoom.
  water=new T.Mesh(new T.PlaneGeometry(SEA_SIZE*WS,SEA_SIZE*WS,64,64).rotateX(-Math.PI/2),seaMaterial());
  water.position.y=-1.6;water.receiveShadow=true;scene.add(water);
  const lava=id==="prod";
  const wmat=new T.MeshStandardMaterial({color:W.river,transparent:!lava,opacity:.9,roughness:.25,flatShading:true,emissive:lava?PALETTE.lava:"#000",emissiveIntensity:lava?1.1:0});
  if(lava)props.lava=wmat;
  if(W.river){for(let i=0;i<W.river.length-1;i++){const a=W.river[i],b=W.river[i+1],dx=b[0]-a[0],dz=b[1]-a[1],len=Math.hypot(dx,dz);const m=new T.Mesh(new T.BoxGeometry(len+.6,.12,2.2),wmat);m.position.set((a[0]+b[0])/2,.04,(a[1]+b[1])/2);m.rotation.y=-Math.atan2(dz,dx);scene.add(m);const bank=new T.Mesh(new T.BoxGeometry(len+.8,.06,3),mat(W.bank));bank.position.set(m.position.x,.01,m.position.z);bank.rotation.y=m.rotation.y;scene.add(bank)}}
  const lakeM=new T.Mesh(new T.CylinderGeometry(2.8,2.8,.12,10),id==="winter"?new T.MeshStandardMaterial({color:"#D8EEFB",roughness:.15,metalness:.2,flatShading:true}):wmat);lakeM.position.set(W.lake[0],.05,W.lake[1]);scene.add(lakeM);scene.add(cyl(3.3,3.3,.06,W.bank,W.lake[0],.01,W.lake[1],10));obstacles.push([W.lake[0],W.lake[1],3.1]);
  if(id!=="winter"&&!lava){const fnt=new T.Group();fnt.add(cyl(.9,1.1,.5,"#CBD5E1",0,.25,0,8));fnt.add(cyl(.15,.2,1.4,"#CBD5E1",0,1,0,6));fnt.add(cyl(.55,.4,.15,"#CBD5E1",0,1.7,0,8));const drops=[];for(let i=0;i<10;i++){const d=new T.Mesh(new T.SphereGeometry(.09,5,5),new T.MeshBasicMaterial({color:"#BAE6FD"}));d.userData.p=i/10;fnt.add(d);drops.push(d)}fnt.position.set(W.lake[0],0,W.lake[1]);fnt.userData.drops=drops;mergeStatic(fnt);scene.add(fnt);props.fountain=fnt}
  if(id==="winter"){const sl=new T.Group();sl.add(box(1.2,.15,.6,"#B44A46",0,.15,0));[-.25,.25].forEach(z=>sl.add(box(1.4,.06,.08,PALETTE.timber,0,.05,z)));sl.position.set(W.lake[0]+1,0,W.lake[1]-.5);mergeStatic(sl);scene.add(sl);props.sled=sl}
  // path
  const way=W.way.map(p=>new T.Vector3(p[0],0,p[1]));const curve=new T.CatmullRomCurve3(way,false,"catmullrom",.5);const N=Math.floor(curve.getLength()/.42);
  const inst=new T.InstancedMesh(new T.BoxGeometry(1.15,.07,.42),slabMat(id),N);
  for(let i=0;i<N;i++){const t=i/N,pt=curve.getPointAt(t),tg=curve.getTangentAt(t);dummy.position.set(pt.x,.035,pt.z);dummy.rotation.y=-Math.atan2(tg.z,tg.x)+Math.PI/2;dummy.updateMatrix();inst.setMatrixAt(i,dummy.matrix)}inst.receiveShadow=true;scene.add(inst);props.curve=curve;
  if(W.bridge){const br=new T.Group();for(let i=0;i<7;i++)br.add(box(1.6,.14,.45,PALETTE.deck,0,.35,-1.5+i*.5));br.add(box(.1,.9,3.6,PALETTE.timber,-.75,.7,0));br.add(box(.1,.9,3.6,PALETTE.timber,.75,.7,0));[-1.5,0,1.5].forEach(z=>{br.add(box(.12,.9,.12,PALETTE.timber,-.75,.55,z));br.add(box(.12,.9,.12,PALETTE.timber,.75,.55,z))});const tg=curve.getTangentAt(W.bridge[2]);br.position.set(W.bridge[0],0,W.bridge[1]);br.rotation.y=-Math.atan2(tg.z,tg.x)+Math.PI;mergeStatic(br);scene.add(br)}
  // Every path lamp is the same post and the same bulb: two instanced meshes
  // for fourteen lamps, and one shared material the evening lights at once.
  props.lamps=null;{const posts=[],bulbs=[];
    for(let i=0;i<14;i++){const t=(i+.5)/14,pt=curve.getPointAt(t),tg=curve.getTangentAt(t),nx=-tg.z,nz=tg.x;
      posts.push(xform(pt.x+nx*1.1,.8,pt.z+nz*1.1));bulbs.push(xform(pt.x+nx*1.1,1.7,pt.z+nz*1.1))}
    instOf(shape("lamppole",()=>new T.CylinderGeometry(.05,.07,1.6,5)),mat("#334155"),posts,false);
    const bulb=instOf(shape("lampbulb",()=>new T.SphereGeometry(.18,6,6)),
      mat(PALETTE.lamp,{emissive:PALETTE.yellow,emissiveIntensity:0}),bulbs,false);
    if(bulb)props.lamps=bulb.material}
  // inn: stays at the origin, unscaled, with the walkers' start around its terrace
  const inn=new T.Group();const roofC=id==="winter"?PALETTE.snow:id==="prod"?"#3B1F2B":id==="desert"?"#C2410C":"#B44A46";inn.add(box(3.6,2.2,3,id==="prod"?"#6B6B7A":"#EFD9B8",0,1.1,0));const roof=cone(3.1,1.7,roofC,0,3.05,0,4);roof.rotation.y=Math.PI/4;inn.add(roof);inn.add(box(.5,1.1,.5,"#9C948A",1,3.6,.5));
  inn.add(box(.7,1.2,.1,"#5A3C22",0,.6,1.52));inn.add(win(.6,.6,.1,PALETTE.window,-1.2,1.3,1.52));inn.add(win(.6,.6,.1,PALETTE.window,1.2,1.3,1.52));inn.add(box(1.5,.8,.1,"#FFF3C2",-2.4,1.5,1.3));inn.add(box(.1,1.5,.1,PALETTE.timber,-2.4,.75,1.3));
  inn.add(box(5,.12,3,"#D9C49A",0,.06,3.2));[-1.4,1.4].forEach(x=>{inn.add(cyl(.5,.5,.1,PALETTE.timber,x,.55,3.4,8));inn.add(cyl(.06,.06,.5,PALETTE.timber,x,.3,3.4,5));inn.add(cone(1.1,.5,"#F87171",x,2.1,3.4,8));inn.add(cyl(.04,.04,1.7,"#94A3B8",x,1.15,3.4,4))});
  const lab=label("Hospitality Hub",.7);lab.position.set(0,4.8,0);inn.add(lab);const innLight=new T.PointLight(PALETTE.window,0,10);innLight.position.set(0,1.5,2.5);inn.add(innLight);inn.userData.light=innLight;mergeStatic(inn);scene.add(inn);builds.inn=inn;obstacles.push([0,0,2.3],[0,3.2,2.6]);blobAdd(0,0,3.1);blobAdd(0,3.2,3);
  if(ex("stall")){const stall=new T.Group();stall.add(box(2,.9,1,"#A9743F",0,.45,0));stall.add(box(2.4,.1,1.4,"#E11D48",0,2,0));[-1,1].forEach(x=>stall.add(cyl(.05,.05,2,PALETTE.timber,x,1,.5,4)));[[PALETTE.yellow,-.6],["#22C55E",0],["#F87171",.6]].forEach(([c,x])=>stall.add(sph(.22,c,x,1.05,.2,6)));const sp=P(4.5,2);stall.position.set(sp[0],0,sp[1]);stall.rotation.y=-.6;mergeStatic(stall);scene.add(stall);obstacles.push([sp[0],sp[1],1.3]);blobAdd(sp[0],sp[1],1.5)}
  if(ex("well")){const well=new T.Group();well.add(cyl(.7,.75,.8,PALETTE.stone,0,.4,0,8));well.add(cone(.9,.6,PALETTE.timber,0,1.9,0,6));[-.5,.5].forEach(x=>well.add(box(.1,1.4,.1,PALETTE.timber,x,1,0)));const wp=P(-3,-4);well.position.set(wp[0],0,wp[1]);mergeStatic(well);scene.add(well);obstacles.push([wp[0],wp[1],.9]);blobAdd(wp[0],wp[1],1.1)}
  if(ex("mountain")){const mt=new T.Group();mt.add(cone(6,7,id==="winter"?"#B8C4CF":"#8B7355",0,3.5,0,7));mt.add(cone(2.3,2.6,PALETTE.snow,0,5.7,0,7));const mp=P(-9,-14);mt.position.set(mp[0],0,mp[1]);mt.traverse(o=>{if(o.isMesh)o.castShadow=true});mergeStatic(mt);scene.add(mt);obstacles.push([mp[0],mp[1],4.5])}
  if(ex("volcano")){const v=new T.Group();v.add(cyl(2,6.5,7,"#2E2E38",0,3.5,0,8));v.add(cyl(1.4,2.1,.5,PALETTE.lava,0,7.1,0,8).material.emissive.set(PALETTE.lava)?cyl(1.4,2.1,.5,"#FF6A1A",0,7.1,0,8):null);const glow=new T.PointLight(PALETTE.lava,2.5,18);glow.position.y=8;v.add(glow);const sm=[];for(let i=0;i<8;i++){const m=new T.Mesh(new T.SphereGeometry(.7,6,6),new T.MeshStandardMaterial({color:"#4B4B55",transparent:true,opacity:.6}));m.userData.o=i;v.add(m);sm.push(m)}v.userData.smoke=sm;const vp=P(-9,-14);v.position.set(vp[0],0,vp[1]);mergeStatic(v);scene.add(v);props.volcano=v;obstacles.push([vp[0],vp[1],5.5]);
    for(let i=0;i<4;i++){const l=new T.Mesh(new T.BoxGeometry(1.5,.15,4+i),wmat);l.position.set(vp[0]+i*1.5,.06,vp[1]+4.5+i*.5);l.rotation.y=.4-i*.25;scene.add(l)}}
  if(ex("harbour")){const dock=new T.Group();for(let i=0;i<9;i++)dock.add(box(.5,.12,2,PALETTE.deck,i*.55,.1,0));[0,2.2,4.4].forEach(x=>{dock.add(cyl(.1,.12,1.4,PALETTE.timber,x,-.4,-1));dock.add(cyl(.1,.12,1.4,PALETTE.timber,x,-.4,1))});const hp=id==="winter"?P(15,-5):P(15,-8);dock.position.set(hp[0],0,hp[1]);mergeStatic(dock);scene.add(dock);
    const boat=(c)=>{const g=new T.Group();g.add(box(2.6,.6,1.1,c,0,-.1,0));g.add(box(2.0,.3,.9,PALETTE.snow,0,.25,0));g.add(cyl(.05,.05,2.6,PALETTE.timber,.2,1.5,0,4));const sail=new T.Mesh(new T.ConeGeometry(.9,2.2,3),new T.MeshStandardMaterial({color:PALETTE.snow,side:T.DoubleSide,flatShading:true}));sail.position.set(.4,1.6,0);sail.rotation.z=-.15;g.add(sail);g.traverse(o=>{if(o.isMesh)o.castShadow=true});mergeStatic(g);return g};
    const b1=boat(id==="prod"?"#7F1D1D":"#E11D48");b1.position.set(hp[0]+6,-1.35,hp[1]+.5);scene.add(b1);props.boat=b1;const b2=boat("#2563EB");scene.add(b2);props.boat2=b2}
  if(ex("lighthouse")){const lh=new T.Group();lh.add(cyl(.9,1.2,4.5,PALETTE.snow,0,2.25,0,8));[1,2.6].forEach(y=>lh.add(cyl(1.02,1.02,.5,"#DC2626",0,y,0,8)));lh.add(cyl(1,1,.6,PALETTE.ink,0,4.8,0,8));const lamp=new T.Mesh(new T.CylinderGeometry(.7,.7,.7,8),new T.MeshStandardMaterial({color:"#FEF3C7",emissive:PALETTE.yellow,emissiveIntensity:0}));lamp.position.y=5.4;lh.add(lamp);lh.userData.lamp=lamp;lh.add(cone(.9,.7,"#DC2626",0,6.1,0,8));
    const beam=new T.Mesh(new T.ConeGeometry(2.2,14,10,1,true),new T.MeshBasicMaterial({color:PALETTE.lamp,transparent:true,opacity:0,side:T.DoubleSide,depthWrite:false}));beam.rotation.z=Math.PI/2;beam.position.set(7,5.4,0);const bg=new T.Group();bg.add(beam);lh.add(bg);lh.userData.beam=bg;lh.userData.beamM=beam;const lp=P(19,5);lh.position.set(lp[0],0,lp[1]);mergeStatic(lh);scene.add(lh);props.lighthouse=lh;obstacles.push([lp[0],lp[1],1.4]);blobAdd(lp[0],lp[1],1.6)}
  if(ex("windmill")){const wm=new T.Group();wm.add(cyl(1,1.4,3.6,"#E7C9A0",0,1.8,0,8));wm.add(cone(1.3,1,"#B44A46",0,4.1,0,8));wm.add(box(.6,.9,.1,"#5A3C22",0,.45,1.3));const blades=new T.Group();for(let i=0;i<4;i++){const b=box(.22,3.2,.06,PALETTE.snow,0,0,0);b.geometry.translate(0,1.6,0);b.rotation.z=i*Math.PI/2;blades.add(b)}mergeStatic(blades);blades.position.set(0,3.4,1.5);wm.add(blades);wm.userData.blades=blades;const wp=P(11,14.5);wm.position.set(wp[0],0,wp[1]);wm.rotation.y=Math.PI;mergeStatic(wm);scene.add(wm);props.windmill=wm;obstacles.push([wp[0],wp[1],1.6]);blobAdd(wp[0],wp[1],1.8)}
  // the runway is one strip; its markings and the parked plane sit relative to it
  const ap=P(4,-16.5);
  if(ex("airstrip")){scene.add(box(9,.1,2.2,"#6B7280",ap[0],.05,ap[1]));for(let i=0;i<5;i++)scene.add(box(.9,.02,.15,PALETTE.snow,ap[0]-3+i*1.6,.11,ap[1]))}
  const plane=(c)=>{const g=new T.Group();g.add(box(2.8,.6,.7,c,0,.5,0));g.add(box(.7,.12,3.6,PALETTE.snow,.2,.6,0));g.add(box(.8,.12,1.4,PALETTE.snow,-1.2,.9,0));g.add(box(.6,.7,.12,PALETTE.snow,-1.2,1.05,0));g.add(box(.6,.4,.6,"#BAE6FD",.6,.9,0));const prop=box(.08,1.2,.15,PALETTE.ink,1.5,.5,0);g.add(prop);g.userData.prop=prop;[-.5,.5].forEach(z=>g.add(cyl(.18,.18,.12,PALETTE.ink,.3,.15,z,8)));g.traverse(o=>{if(o.isMesh)o.castShadow=true});mergeStatic(g);return g};
  if(ex("airstrip")){const p1=plane(PALETTE.orange);p1.position.set(ap[0]-2.5,0,ap[1]);scene.add(p1);props.plane=p1}
  const p2=plane(id==="prod"?"#7F1D1D":"#EF4444");scene.add(p2);props.plane2=p2;
  if(ex("balloon")){const bal=new T.Group();bal.add(sph(1.8,PALETTE.orange,0,3.4,0,10));const st2=sph(1.82,PALETTE.yellow,0,3.4,0,10);st2.scale.set(.5,1,1);bal.add(st2);bal.add(box(.9,.7,.9,"#A9743F",0,0,0));[-.4,.4].forEach(x=>bal.add(cyl(.03,.03,2.3,PALETTE.ink,x,1.2,0,3)));const bp=P(-15,11);mergeStatic(bal);bal.position.set(bp[0],7,bp[1]);scene.add(bal);props.balloon=bal}
  if(ex("birds")){props.birds=[];for(let i=0;i<6;i++){const b=new T.Group();const w1=box(.6,.05,.15,PALETTE.ink,-.3,0,0),w2=box(.6,.05,.15,PALETTE.ink,.3,0,0);b.add(w1,w2);b.userData={w1,w2,o:i};scene.add(b);props.birds.push(b)}}
  // vegetation by world
  // A tree is static, so its parts go into the batch: every trunk of a kind is
  // one instanced mesh however many trees there are, which is what pays for
  // the archipelago's bridges and silhouettes.
  const treeAt=(x,z,k)=>{const base=xform(x,0,z,0,x*.7,0);
    const add=(key,make,colour,m)=>batchAdd(key,make,colour,new T.Matrix4().multiplyMatrices(base,m));
    if(W.tree==="pine"){add("pine-trunk",()=>new T.CylinderGeometry(.18,.25,1.2,6),"#5B3A1E",xform(0,.6,0));
      add("pine-1",()=>new T.ConeGeometry(.9,1.6,6),"#2F6B4F",xform(0,1.9,0));
      add("pine-2",()=>new T.ConeGeometry(.75,1.3,6),"#3E8464",xform(0,2.8,0));
      add("pine-3",()=>new T.ConeGeometry(.8,.4,6),PALETTE.snow,xform(0,2.55,0));
      add("pine-4",()=>new T.ConeGeometry(.55,.35,6),PALETTE.snow,xform(0,3.3,0))}
    else if(W.tree==="palm"){add("palm-trunk",()=>new T.CylinderGeometry(.14,.22,2.6,6),"#8B5A2B",xform(0,1.3,0));
      for(let i=0;i<5;i++)add("palm-frond",()=>{const g=new T.ConeGeometry(.35,1.9,3);g.translate(0,.9,0);return g},
        "#3F9B57",xform(0,2.6,0,0,i/5*Math.PI*2,1.15))}
    else if(W.tree==="dead"){add("dead-trunk",()=>new T.CylinderGeometry(.12,.25,2,5),"#2B2B33",xform(0,1,0));
      [[.5,1.6,.3],[-.5,1.3,-.2]].forEach(a=>add("dead-branch",()=>new T.BoxGeometry(.12,1,.12),"#2B2B33",
        xform(a[0],a[1],a[2],0,0,a[0]>0?-.7:.7)))}
    else if(k===0){add("tree-trunk",()=>new T.CylinderGeometry(.18,.25,1.2,6),PALETTE.timber,xform(0,.6,0));
      add("tree-1",()=>new T.ConeGeometry(.9,1.6,6),"#3F9B57",xform(0,1.9,0));
      add("tree-2",()=>new T.ConeGeometry(.7,1.3,6),"#4FB864",xform(0,2.7,0))}
    else{add("bush-trunk",()=>new T.CylinderGeometry(.2,.28,1.5,6),PALETTE.timber,xform(0,.75,0));
      add("bush-1",()=>new T.SphereGeometry(1,7,7),"#4FB864",xform(0,2.1,0));
      add("bush-2",()=>new T.SphereGeometry(.7,6,6),"#5FCB7B",xform(.5,2.6,.3))}
    obstacles.push([x,z,.7]);blobAdd(x,z,W.tree==="palm"?1:1.3)};
  const treeSpots=[[5,-7,0],[-4,-8,1],[9,-13,0],[-13,-8,0],[-15,11,1],[-11,12,0],[3,15,1],[12,9,0],[17,-1,1],[8,3,1],[-6,-2,0],[6,-3,1],[-1,-13,0],[15,-13,0],[-12,-14,0]].map(a=>[...P(a[0],a[1]),a[2]]);
  treeSpots.forEach(a=>{if(onLandW(a[0],a[1])&&!PLOT_POS.some(p=>p.distanceTo(new T.Vector3(a[0],0,a[1]))<2.8))treeAt(...a)});
  [[7,7],[-8,-6],[2,-6],[-14,4],[10,-2]].map(a=>P(a[0],a[1])).forEach(([x,z])=>{if(!onLandW(x,z))return;
    batchAdd("rock",()=>new T.SphereGeometry(.45,5,5),id==="prod"?"#1F1F27":PALETTE.stone,xform(x,.2,z));blobAdd(x,z,.7)});
  if(ex("flowers")){const fl=new T.InstancedMesh(new T.BoxGeometry(.18,.18,.18),new T.MeshStandardMaterial({color:"#fff",flatShading:true}),160);const colr=new T.Color();for(let i=0;i<160;i++){const a=Math.random()*Math.PI*2,r=(3+Math.random()*11)*WS;dummy.position.set(Math.cos(a)*r,.12,Math.sin(a)*r);dummy.rotation.set(0,Math.random(),0);dummy.updateMatrix();fl.setMatrixAt(i,dummy.matrix);colr.set([PALETTE.orange,PALETTE.yellow,PALETTE.snow,"#FFA94D"][i%4]);fl.setColorAt(i,colr)}scene.add(fl)}
  buildTufts();
  if(ex("cacti")){[[6,-6],[-5,-7],[10,5],[-9,1],[3,-15],[14,-4]].map(a=>P(a[0],a[1])).forEach(([x,z])=>{if(!onLandW(x,z))return;
    batchAdd("cactus",()=>new T.CylinderGeometry(.3,.35,2,7),"#2F855A",xform(x,1,z));
    batchAdd("cactus-arm",()=>new T.CylinderGeometry(.18,.2,.9,6),"#2F855A",xform(x+.5,1.5,z));
    batchAdd("cactus-arm2",()=>new T.CylinderGeometry(.18,.2,.7,6),"#2F855A",xform(x-.5,1.2,z));
    obstacles.push([x,z,.6]);blobAdd(x,z,.8)})}
  if(ex("mesas")){[[-8,-14,4,3.5],[12,-13,3,2.5],[-16,8,2.5,2]].forEach(([x,z,r,h])=>{[x,z]=P(x,z);const m=new T.Group();m.add(cyl(r*.8,r,h,"#B45309",0,h/2,0,8));m.add(cyl(r*.75,r*.8,.4,"#D97706",0,h+.2,0,8));m.position.set(x,0,z);m.traverse(o=>{if(o.isMesh)o.castShadow=true});mergeStatic(m);scene.add(m);obstacles.push([x,z,r])})}
  if(ex("dunes")){[[6,8],[-6,9],[8,-9],[-11,-4]].map(a=>P(a[0],a[1])).forEach(([x,z])=>{const d=sph(3,"#F1DDA2",x,-2.2,z,10);d.scale.set(1,.5,1);scene.add(d)})}
  if(ex("tumbleweed")){const tw=new T.Mesh(new T.IcosahedronGeometry(.6,1),new T.MeshStandardMaterial({color:"#A16207",wireframe:true}));scene.add(tw);props.tumble=tw}
  if(ex("snowmen")){[[6,-4],[-7,9]].map(a=>P(a[0],a[1])).forEach(([x,z])=>{const g=new T.Group();g.add(sph(.7,PALETTE.snow,0,.6,0,9));g.add(sph(.5,PALETTE.snow,0,1.55,0,9));g.add(sph(.36,PALETTE.snow,0,2.25,0,9));g.add(cone(.1,.4,"#F97316",0,2.25,.5,5).rotateX(Math.PI/2)?cone(.1,.4,"#F97316",0,2.25,.5,5):null);g.add(box(.6,.1,.6,PALETTE.ink,0,2.55,0));g.add(box(.4,.35,.4,PALETTE.ink,0,2.75,0));g.position.set(x,0,z);mergeStatic(g);scene.add(g);obstacles.push([x,z,.9]);blobAdd(x,z,1)})}
  if(ex("icefloes")){for(let i=0;i<10;i++){const a=i/10*Math.PI*2,r=(24+(i%3)*3)*WS,s=1+(i%3)*.5;
    batchAdd("floe",()=>new T.CylinderGeometry(1,1.2,.3,6),"#E8F3FA",
      xform(Math.cos(a)*r,-1.5,Math.sin(a)*r,0,0,0,new T.Vector3(s,1,s)))}}
  if(ex("snow")){const g=new T.BufferGeometry();const v=[];for(let i=0;i<500;i++)v.push((Math.random()-.5)*60*WS,Math.random()*20,(Math.random()-.5)*60*WS);g.setAttribute("position",new T.Float32BufferAttribute(v,3));const pts=new T.Points(g,new T.PointsMaterial({color:"#fff",size:.25,transparent:true,opacity:.9}));scene.add(pts);props.snow=pts}
  if(ex("embers")){const g=new T.BufferGeometry();const v=[];const ep=P(-9,-14);for(let i=0;i<250;i++)v.push(ep[0]+(Math.random()-.5)*10,Math.random()*16,ep[1]+(Math.random()-.5)*10);g.setAttribute("position",new T.Float32BufferAttribute(v,3));const pts=new T.Points(g,new T.PointsMaterial({color:"#FF7A1A",size:.22,transparent:true,opacity:.9}));scene.add(pts);props.embers=pts}
  if(ex("aurora")){const ag=new T.PlaneGeometry(90*WS,14,40,4);const am=new T.MeshBasicMaterial({color:PALETTE.greenBright,transparent:true,opacity:0,side:T.DoubleSide,depthWrite:false,blending:T.AdditiveBlending});const au=new T.Mesh(ag,am);au.position.set(0,26*WS,-45*WS);scene.add(au);props.aurora=au;props.auroraBase=ag.attributes.position.array.slice()}
  batchFlush();
  // plots
  buildArtifactProps();placeArtifacts();
  PLOT_POS.forEach((p,i)=>{const g=new T.Group();g.position.copy(p);const ring=new T.Mesh(new T.TorusGeometry(2,.07,6,32),new T.MeshBasicMaterial({color:"#ffffff",transparent:true,opacity:.7}));ring.rotation.x=Math.PI/2;ring.position.y=.06;g.add(ring);
    const post=box(.1,1.6,.1,PALETTE.timber,0,.8,0);const sign=box(1.3,.6,.1,"#FFF3C2",0,1.6,0);g.add(post,sign);const lb=label(CH[i].h,.55);lb.position.y=2.3;g.add(lb);
    [[-1.6,-1.6],[1.6,-1.6]].forEach(([x,z])=>g.add(box(.08,.6,.08,PALETTE.timber,x,.3,z)));g.add(box(3.3,.06,.06,PALETTE.timber,0,.55,-1.6));g.userData={ring,post,sign,lb};mergeStatic(g);scene.add(g);plots.push(g);blobAdd(p.x,p.z,1.1)});
  // A cloud is four lumps, baked into one mesh so eight of them cost eight
  // draw calls and not thirty-two.
  for(let i=0;i<8;i++){const c=new T.Group();[[0,0,0,1.6],[1.5,.3,.2,1.1],[-1.4,.2,.3,1],[.4,.7,-.3,.9]].forEach(([x,y,z,r])=>{const m=new T.Mesh(new T.SphereGeometry(r,7,7),mat(id==="prod"?"#6B6B78":"#fff"));m.position.set(x,y,z);c.add(m)});mergeStatic(c);c.position.set((-40+i*11)*WS,(13+Math.sin(i)*2.5)*WS,(-22+((i*7)%14))*WS);c.userData.v=(.4+i*.08)*WS;scene.add(c);clouds.push(c)}
  sunM=new T.Mesh(new T.SphereGeometry(2.4,10,10),new T.MeshBasicMaterial({color:PALETTE.window}));scene.add(sunM);moonM=new T.Mesh(new T.SphereGeometry(1.7,10,10),new T.MeshBasicMaterial({color:"#FFF3C2"}));scene.add(moonM);
  const sg=new T.BufferGeometry();const sv=[];for(let i=0;i<400;i++){const a=Math.random()*Math.PI*2,b=Math.random()*Math.PI*.5;sv.push(Math.cos(a)*Math.cos(b)*120*WS,Math.sin(b)*120*WS+5,Math.sin(a)*Math.cos(b)*120*WS)}sg.setAttribute("position",new T.Float32BufferAttribute(sv,3));stars=new T.Points(sg,new T.PointsMaterial({color:"#fff",size:.6,transparent:true,opacity:0}));scene.add(stars);
  // characters (keep positions if switching)
  const lp=carry?new T.Vector3(carry.x,0,carry.z):chars.lotte?chars.lotte.g.position.clone():new T.Vector3(2.8,0,5.2);
  chars.lotte=character(playerSpec());chars.lotte.g.position.copy(carry||onLandW(lp.x,lp.z)?lp:new T.Vector3(2.8,0,5.2));scene.add(chars.lotte.g);
  if(carry){chars.lotte.g.rotation.y=carry.rot;chars.lotte.vel=carry.vel||new T.Vector3()}
  chars.tom=character({kind:"tom",body:"#D8C49B",legs:"#6E6A66",arms:"#F5D7BC",label:roleName("tom")});chars.tom.g.position.set(-1.6,0,6.4);scene.add(chars.tom.g);
  chars.rolinda=character({kind:"rolinda",body:"#8FD18A",legs:"#9CC4E8",arms:"#8FD18A",label:roleName("rolinda")});chars.rolinda.g.position.set(0.4,0,4.6);chars.rolinda.g.rotation.y=Math.PI*.95;scene.add(chars.rolinda.g);
  // mentors (NPC scientists) for this world
  props.mentors=[];MENTORS.filter(m=>m.world===id).forEach(m=>{const c=character({kind:"mentor",body:m.look.shirt,legs:"#374151",arms:"#F5D7BC",label:m.name,look:m.look});c.g.position.set(m.pos[0],0,m.pos[1]);c.g.rotation.y=Math.PI;scene.add(c.g);c.id=m.id;props.mentors.push(c);obstacles.push([m.pos[0],m.pos[1],.6]);blobAdd(m.pos[0],m.pos[1],.7);
    const ring=new T.Mesh(new T.TorusGeometry(1.1,.05,6,24),new T.MeshBasicMaterial({color:S.mentors.includes(m.id)?PALETTE.greenBright:S.path[m.id]==="deep"?PALETTE.blueBright:S.path[m.id]==="skip"?PALETTE.orangeBright:"#FFA94D",transparent:true,opacity:.6}));ring.rotation.x=Math.PI/2;ring.position.set(m.pos[0],.05,m.pos[1]);scene.add(ring);c.ring=ring});
  props.plaques={};placePlaques(false);
  // Seats and collectibles come from data, positioned against the plots and
  // the annexes that already exist (src/game/19-items.js).
  props.items=[];placeSeats();placeItems();
  // Every contact shadow collected while the island was built, in one draw.
  blobFlush();
  // shadow blob + marker
  props.shadow=new T.Mesh(new T.PlaneGeometry(1.4,1.4),new T.MeshBasicMaterial({map:blobTexture(),transparent:true,depthWrite:false,opacity:.5}));props.shadow.rotation.x=-Math.PI/2;props.shadow.position.y=.05;props.shadow.renderOrder=1;props.shadow.material.userData.cs=1;scene.add(props.shadow);
  // The ring that says which of the three figures you are steering.
  props.you=new T.Mesh(new T.RingGeometry(.62,.8,24),new T.MeshBasicMaterial({color:PALETTE.blueBright,transparent:true,opacity:.75,side:T.DoubleSide}));props.you.rotation.x=-Math.PI/2;props.you.position.y=.07;props.you.renderOrder=2;props.you.material.userData.cs=1;scene.add(props.you);
  marker=new T.Mesh(new T.RingGeometry(.3,.45,20),new T.MeshBasicMaterial({color:PALETTE.blueBright,transparent:true,opacity:0,side:T.DoubleSide}));marker.rotation.x=-Math.PI/2;marker.position.y=.06;scene.add(marker);
  // A crossing keeps the sky it walked under and fades to the new island's
  // mood; a fresh build or a fast travel arrives with the mood already on.
  if(carry&&prevBg){scene.background=prevBg;scene.fog.color.copy(prevBg)}
  S.done.forEach(k=>placeBuilding(k,false));applySky(S.done.length,!carry);fixColors(scene);hud();
}
// Tufts: a few hundred low lumps a shade darker than the ground, in one
// instanced draw. From the fitted view they are texture; from the close view
// they are what stops the ground being one flat sheet of colour under the
// walker's feet. They keep off the path, the plots, the inn and the lake, and
// they are seeded, so the island is the same island on every visit.
function buildTufts(){const mats=[],R=W.land[0][2],path=props.curve.getSpacedPoints(90);
  let seed=7;const rnd=()=>(seed=(seed*16807)%2147483647)/2147483647;
  for(let i=0;i<GROUND.tufts*3&&mats.length<GROUND.tufts;i++){
    const a=rnd()*Math.PI*2,r=Math.sqrt(rnd())*R,x=Math.cos(a)*r,z=Math.sin(a)*r,s=.7+rnd()*.9,ry=rnd()*Math.PI;
    if(!W.land.some(b=>Math.hypot(x-b[0],z-b[1])<b[2]-1.4))continue;
    if(Math.hypot(x,z)<6.2||Math.hypot(x-W.lake[0],z-W.lake[1])<4.2)continue;
    if(PLOT_POS.some(p=>Math.hypot(x-p.x,z-p.z)<3)||path.some(p=>Math.hypot(x-p.x,z-p.z)<1.5))continue;
    mats.push(xform(x,.1*s,z,0,ry,0,new T.Vector3(s,s,s)))}
  const c=new T.Color(W.grass).multiplyScalar(GROUND.shade);
  const im=instOf(shape("tuft",()=>new T.ConeGeometry(.22,.3,5)),mat("#"+c.getHexString()),mats,false);
  if(im)im.receiveShadow=true;props.tufts=im}
// One building per artifact of this world that names a model in ART_PROPS;
// the group is an obstacle so the walker goes round it, and the ring stays.
function buildArtifactProps(){props.artProps=[];props.artR={};(typeof ARTIFACTS==="undefined"?[]:ARTIFACTS).filter(a=>a.world===S.world&&a.model&&ART_PROPS[a.model]).forEach(a=>{const g=ART_PROPS[a.model]();const r=g.userData.r||1.4;
  g.position.set(a.pos[0],0,a.pos[1]);g.traverse(o=>{if(o.isMesh)o.castShadow=true});mergeStatic(g);
  const lb=label(a.name,.55);lb.position.y=g.userData.h||3;g.add(lb);
  scene.add(g);props.artProps.push(g);props.artR[a.id]=r;obstacles.push([a.pos[0],a.pos[1],r]);blobAdd(a.pos[0],a.pos[1],r*.9)})}
// A mentor's plaque: the visible consequence of their exercise. It appears
// only for an encounter the CLI verified, which reaches the game as part of
// the progress code, so the island stays derived from state.
function addPlaque(m){const g=new T.Group();
  g.add(box(1.4,.8,.12,"#C9C9D2",0,.95,0));g.add(box(1.5,.1,.2,PALETTE.muted,0,1.4,0));
  [-.55,.55].forEach(x=>g.add(cyl(.07,.09,1,"#5A3C22",x,.5,0,5)));
  g.position.set(m.pos[0]+1.7,0,m.pos[1]+1.3);g.rotation.y=-.3;g.traverse(o=>{if(o.isMesh)o.castShadow=true});mergeStatic(g);
  const lb=label(m.encounter.plaque,.45);lb.position.y=1.75;g.add(lb);
  fixColors(g);scene.add(g);props.plaques[m.id]=g;obstacles.push([g.position.x,g.position.z,.7]);return g}
function placePlaques(pop){MENTORS.filter(m=>m.world===(S.world||"campus")).forEach(m=>{
  if(!S.mentors.includes(m.id)||props.plaques[m.id])return;const g=addPlaque(m);
  const c=(props.mentors||[]).find(x=>x.id===m.id);if(c)c.ring.material.color.set(PALETTE.greenBright);
  if(pop)popIn(g)})}
// Walkable ground: the island's blobs, plus every annex that has appeared and
// the causeway of its spur (a capsule from the plot to the annex).
function onLandW(x,z){if(W.land.some(b=>Math.hypot(x-b[0],z-b[1])<b[2]-.6))return true;
  if(annexes.some(a=>Math.hypot(x-a.x,z-a.z)<a.r-.6||segDist(x,z,a.x,a.z,a.px,a.pz)<1))return true;
  return !!onBridge(x,z)}
function segDist(x,z,ax,az,bx,bz){const dx=bx-ax,dz=bz-az,l2=dx*dx+dz*dz;const t=l2?Math.max(0,Math.min(1,((x-ax)*dx+(z-az)*dz)/l2)):0;return Math.hypot(x-(ax+dx*t),z-(az+dz*t))}
window.nextWorld=function(){const ids=Object.keys(WORLDS);const i=(ids.indexOf(S.world||"campus")+1)%ids.length;setWorld(ids[i])};
// Fast travel. Before the island runs it is only a choice; once it runs the
// camera flies there first, and the world changes when it arrives.
window.setWorld=function(id){
  if(!started){S.world=id;save();renderWorldPicker();return}
  if(flight||id===S.world)return;
  if(reducedMotion()){buildWorld(id);renderWorldPicker();return}
  startFlight(id)};
function renderWorldPicker(){const el=$("worlds");if(!el)return;el.innerHTML=Object.keys(WORLDS).map(k=>`<button class="world${(S.world||"campus")===k?' pick':''}" onclick="setWorld('${k}')"><b><i style="background:${WORLDS[k].swatch}"></i>${CAMPAIGN[k].title.split(":")[0]}</b>${WORLDS[k].name}. ${CAMPAIGN[k].title.split(": ")[1]}</button>`).join("")}
function placeBuilding(k,pop){
  const g=building(k);g.position.copy(PLOT_POS[k-1]);const p=plots[k-1];p.userData.ring.visible=false;p.userData.post.visible=false;p.userData.sign.visible=false;p.userData.lb.userData.off=1;
  fixColors(g);scene.add(g);builds[k]=g;
  if(pop)popIn(g);else g.scale.set(1,1,1);
  placeAnnex(k,pop);
}
// The annex of stop k: a land blob at W.annex[k-1], a causeway with a slab
// path back to the plot, and a flag with the stop's hour at its end. Built in
// the annex's own frame so the pop grows the causeway out of the annex.
function placeAnnex(k,pop){
  if(annexes.some(a=>a.k===k))return;
  const [ax,az]=W.annex[k-1],pp=PLOT_POS[k-1];const g=new T.Group();g.position.set(ax,0,az);
  landBlob(g,0,0,ANNEX_R,9);
  const dx=pp.x-ax,dz=pp.z-az,len=Math.hypot(dx,dz),ux=dx/len,uz=dz/len,ang=-Math.atan2(uz,ux);
  const from=len-2.3,to=1.3,mid=(from+to)/2;
  const cw=box(from-to+1.5,2.4,2.6,W.grass,ux*mid,-1.2,uz*mid);cw.rotation.y=ang;g.add(cw);
  const cd=box(from-to+2.5,2.2,4.4,W.dirt,ux*mid,-2.6,uz*mid);cd.rotation.y=ang;g.add(cd);
  const n=Math.max(1,Math.floor((from-to)/.42));const inst=new T.InstancedMesh(new T.BoxGeometry(1.15,.07,.42),slabMat(S.world),n);const dummy=new T.Object3D();
  for(let i=0;i<n;i++){const d=to+(i+.5)*(from-to)/n;dummy.position.set(ux*d,.035,uz*d);dummy.rotation.y=ang+Math.PI/2;dummy.updateMatrix();inst.setMatrixAt(i,dummy.matrix)}inst.receiveShadow=true;g.add(inst);
  g.add(cyl(1,1.15,.2,W.bank,0,.1,0,9));g.add(cyl(.05,.07,3.2,"#5A3C22",0,1.7,0,5));
  const flag=new T.Mesh(new T.PlaneGeometry(1.2,.7,6,1),new T.MeshStandardMaterial({color:PALETTE.orange,side:T.DoubleSide,flatShading:true}));flag.position.set(.62,3,0);g.add(flag);g.userData.flag=flag;
  // The annex and its causeway are ground that never moves, so they are baked
  // into one mesh; that mesh is what the tap-to-walk ray hits.
  const merged=mergeStatic(g);
  const lb=label(CH[k-1].h,.5);lb.position.y=3.9;g.add(lb);
  fixColors(g);scene.add(g);if(merged)island.userData.parts.push(merged);
  annexes.push({k,x:ax,z:az,r:ANNEX_R,px:pp.x,pz:pp.z,g});obstacles.push([ax,az,.5]);
  placeItems();
  if(pop)popIn(g);
}
// The pop every new thing on the island gets: it grows from nothing (the
// animation loop eases popT) under a burst of forty confetti cubes.
function popIn(g){g.scale.set(.01,.01,.01);g.userData.popT=0;for(let i=0;i<40;i++){const m=new T.Mesh(new T.BoxGeometry(.18,.18,.18),new T.MeshBasicMaterial({color:[PALETTE.blueBright,PALETTE.blue,PALETTE.yellow,PALETTE.greenBright][i%4]}));m.position.copy(g.position).add(new T.Vector3((Math.random()-.5)*2,1,(Math.random()-.5)*2));m.userData.v=new T.Vector3((Math.random()-.5)*6,4+Math.random()*5,(Math.random()-.5)*6);m.userData.life=1.4+Math.random();scene.add(m);parts.push(m)}}
function tickPop(g,dt){if(g.userData.popT===undefined)return;g.userData.popT+=dt;const x=Math.min(1,g.userData.popT/.9);const s=1+Math.sin(x*Math.PI*1.5)*(1-x)*.35;g.scale.setScalar(x<1?Math.max(.01,x*x*(3-2*x))*s:1);if(x>=1)delete g.userData.popT}

/* ---------------- sky, sea and the light rig ---------------- */
// The sky is one dome with a vertical ramp: the world's horizon colour at the
// bottom, the stage's zenith at the top. A ramp is right here because this is
// the 3D sky and not a surface in the UI. Vertex colours rather than a shader
// so tone mapping and the output encoding are the renderer's, like every
// other material in the scene.
function buildSky(){
  const geo=new T.SphereGeometry(140*WORLD_SCALE,24,18);
  const n=geo.attributes.position.count,c=new Float32Array(n*3);
  geo.setAttribute("color",new T.BufferAttribute(c,3));
  const m=new T.MeshBasicMaterial({color:"#ffffff",vertexColors:true,side:T.BackSide,fog:false,depthWrite:false});
  m.userData.cs=1;
  const d=new T.Mesh(geo,m);d.renderOrder=-1;d.frustumCulled=false;scene.add(d);props.sky=d}
// The ramp, repainted whenever the stage moves. Height runs from the horizon
// to the zenith over the top half of the dome; below the horizon it holds the
// horizon colour, which is also the fog, so the two meet with no seam.
const _skyTop=new T.Color(),_skyBot=new T.Color();let skyPainted="";
function paintSky(bottom,top){const d=props.sky;if(!d)return;
  const key=bottom.getHexString()+top.getHexString();if(key===skyPainted)return;skyPainted=key;
  _skyBot.copy(bottom).convertSRGBToLinear();_skyTop.copy(top).convertSRGBToLinear();
  const p=d.geometry.attributes.position,c=d.geometry.attributes.color,r=140*WORLD_SCALE;
  for(let i=0;i<p.count;i++){const t=Math.max(0,Math.min(1,p.getY(i)/r*1.35+.06));
    const f=Math.pow(t,.8);
    c.setXYZ(i,_skyBot.r+(_skyTop.r-_skyBot.r)*f,_skyBot.g+(_skyTop.g-_skyBot.g)*f,_skyBot.b+(_skyTop.b-_skyBot.b)*f)}
  c.needsUpdate=true}
// The sea: one mesh, animated on the GPU. Two crossing swells and a slow
// diagonal carry the surface, the water reads shallow inside the island's
// radius with a foam line at the shore, and the roughness scrolls so the sun
// leaves a moving highlight instead of a flat sheet of colour. The swell moves
// the vertices, but the normal is worked out per pixel from the same function:
// the mesh is coarse, and a normal interpolated across an eleven unit quad
// shows the grid as a checkerboard in the highlight.
const SEA_SIZE=520;
const SEA_GLSL=`
float seaH(vec2 p,float t){return sin(p.x*.35+t*1.3)*.16+cos(p.y*.30+t*1.1)*.16+sin((p.x+p.y)*.12-t*.7)*.10;}
vec3 seaN(vec2 p,float t){float e=.7;
  float hx=seaH(p+vec2(e,0.),t)-seaH(p-vec2(e,0.),t);
  float hz=seaH(p+vec2(0.,e),t)-seaH(p-vec2(0.,e),t);
  return normalize(vec3(-hx,2.*e,-hz));}
`;
function seaMaterial(){
  const m=new T.MeshStandardMaterial({color:W.water,transparent:true,opacity:.92,roughness:.22,metalness:.14});
  m.color.convertSRGBToLinear();m.userData.cs=1;
  const u={uTime:{value:0},uShallow:{value:new T.Color(W.bank).convertSRGBToLinear()},
    uCoast:{value:W.land[0][2]+1.2}};
  m.userData.u=u;
  m.onBeforeCompile=s=>{Object.assign(s.uniforms,u);
    s.vertexShader="uniform float uTime;varying vec2 vSea;"+SEA_GLSL+"\n"+s.vertexShader
      .replace("#include <begin_vertex>",
        "vec3 transformed=vec3(position);transformed.y+=seaH(position.xz,uTime);vSea=position.xz;");
    s.fragmentShader="uniform float uTime;uniform vec3 uShallow;uniform float uCoast;uniform mat3 normalMatrix;varying vec2 vSea;\n"+SEA_GLSL+"\n"+
      s.fragmentShader
      .replace("#include <normal_fragment_maps>","normal=normalize(normalMatrix*seaN(vSea,uTime));")
      .replace("#include <color_fragment>",
        "#include <color_fragment>\nfloat sd=length(vSea);"+
        "float shallow=1.0-smoothstep(uCoast*0.98,uCoast*1.3,sd);"+
        "diffuseColor.rgb=mix(diffuseColor.rgb,uShallow,shallow*0.42);"+
        "float band=1.0-smoothstep(0.0,1.7,abs(sd-uCoast));"+
        "float foam=clamp(band*(0.45+0.4*sin(sd*2.2-uTime*2.0)),0.0,1.0);"+
        "diffuseColor.rgb=mix(diffuseColor.rgb,vec3(1.0),foam*0.32);")
      .replace("#include <roughnessmap_fragment>",
        "#include <roughnessmap_fragment>\n"+
        "roughnessFactor=clamp(roughnessFactor+0.24*sin(vSea.x*.5+uTime*.8)*cos(vSea.y*.45-uTime*.6),0.04,1.0);")};
  return m}

let skyFrom=new T.Color("#9BD3F5"),skyTo=new T.Color("#9BD3F5"),skyT=1,skyN=0;
let rigFig=0;
const rigSun=new T.Color(),rigZen=new T.Color("#3E8FD8"),_rigZenTo=new T.Color(),_dir=new T.Vector3(),_far=new T.Vector3();
function applySky(n,instant){skyN=Math.min(8,n);skyFrom.copy(scene.background||new T.Color(W.sky[0]));skyTo.set(W.sky[skyN]);skyT=instant?1:0;
  if(instant){scene.background=skyTo.clone();scene.fog.color.copy(skyTo)}
  if(instant)tickRig(1)}
// The rig follows the stage: the sun swings round and down, warm to cold, the
// hemisphere and the ambient come down with it, and past dusk the moon takes
// over. A night lit like a night is what makes the lamps and the lit windows
// worth having.
function tickRig(k){const r=SKY_RIG[skyN],WS=WORLD_SCALE;
  const az=r.az*Math.PI/180,el=r.el*Math.PI/180;
  _dir.set(Math.cos(az)*Math.cos(el),Math.sin(el),Math.sin(az)*Math.cos(el)).multiplyScalar(30*WS);
  dirL.position.lerp(_dir,k);
  rigSun.set(r.sun);dirL.color.lerp(rigSun,k);
  hemiL.color.lerp(rigSun.set(r.hs),k);hemiL.groundColor.lerp(rigSun.set(r.hg),k);
  dirL.intensity+=(r.i-dirL.intensity)*k;
  hemiL.intensity+=(r.hemi-hemiL.intensity)*k;
  ambL.intensity+=(r.amb-ambL.intensity)*k;
  // The discs ride the same bearing, far out past the fog.
  _far.copy(_dir).normalize().multiplyScalar(90*WS);
  sunM.position.copy(_far);sunM.visible=skyN<4;
  moonM.position.copy(_far);moonM.visible=skyN>=4;
  rigZen.lerp(_rigZenTo.set(r.zen),k);paintSky(scene.fog.color,rigZen);
  // The figures' lift, in the light's own colour. Written only when it moves
  // or a figure is new, and figures that have left the scene drop off the list.
  const fig=rigFig+(r.fig-rigFig)*k;
  if(figDirty||Math.abs(fig-rigFig)>1e-4){figDirty=false;rigFig=Math.abs(r.fig-fig)<1e-3?r.fig:fig;
    for(let i=figures.length-1;i>=0;i--){const c=figures[i];
      if(!inScene(c.g)){figures.splice(i,1);continue}
      c.mats.forEach(m=>{m.emissive.copy(dirL.color);m.emissiveIntensity=rigFig})}}}

// What the graphics tests read: the renderer's colour pipeline, the rig of
// this stage, the camera's fit, and how much of the island is inside the
// frame right now (the rim in normalised device coordinates, so a value over
// one means the island is being cropped).
window.__scene=()=>scene;
window.__gfx=()=>{const rim=[];const r=W.land[0][2],v=new T.Vector3();
  for(let i=0;i<48;i++){const a=i/48*Math.PI*2;v.set(Math.cos(a)*r,0,Math.sin(a)*r).project(camera);
    rim.push(Math.max(Math.abs(v.x),Math.abs(v.y)))}
  return {tone:renderer.toneMapping,aces:renderer.toneMapping===T.ACESFilmicToneMapping,
    exposure:renderer.toneMappingExposure,srgb:renderer.outputEncoding===T.sRGBEncoding,
    stage:skyN,sun:{i:dirL.intensity,c:"#"+dirL.color.getHexString(),
      pos:dirL.position.toArray(),up:dirL.position.y>0},
    hemi:hemiL.intensity,amb:ambL.intensity,
    sky:!!props.sky,sun_disc:!!(sunM&&sunM.visible),moon_disc:!!(moonM&&moonM.visible),
    sea:!!(water&&water.material.userData.u),
    blobs:props.blobs?props.blobs.count:0,
    // Each drawn plate with its pill's box on the canvas in CSS pixels, so a
    // test can ask whether it is legible and whether two of them collide.
    plates:{total:plates.length,shown:plates.filter(p=>p.visible).length,
      list:plates.filter(p=>p.visible).map(p=>{const u=p.userData;
        return {text:u.text,x:u.cx,y:u.cy,w:(u.hw-PLATE.gap)*2,h:(u.hh-PLATE.gap)*2,o:u.o,want:u.want}})},
    // Something that only ambient motion moves: the first cloud.
    ambient:clouds.length?clouds[0].position.x:0,
    // off is how far the camera still is from the height the fit asks for, so
    // a test can ask whether the frame has landed instead of counting frames.
    cam:{fit:camFitDist(),dist:camera.position.length(),aspect:camera.aspect,fov:camera.fov,
      off:camOff()},
    // level is where the eased camera is, target is the state it is easing to.
    zoom:{level:camZoom(),target:zoomTo,min:CAM.zoom.min,max:CAM.zoom.max,start:CAM.zoom.start,
      dist:camera.position.distanceTo(camLook)},
    lost:gfxLost,
    // What the GPU holds. It has to come back down after an island is left.
    mem:{geometries:renderer.info.memory.geometries,textures:renderer.info.memory.textures,
      programs:renderer.info.programs?renderer.info.programs.length:0},
    rim:Math.max.apply(null,rim),
    lit:Object.keys(builds).filter(k=>builds[k].userData.lit).length}};

/* ---------------- input & movement ---------------- */
// The player's walker after a look or a name change: same spot, new body. The
// pose is state, the limbs are the view, so the new body takes over what the
// old one was doing; the name is rebuilt on a timer, which can land long after
// the walker has sat down.
function rebuildPlayer(){if(!chars.lotte)return;const old=chars.lotte,p=old.g.position.clone(),r=old.g.rotation.y;
  scene.remove(old.g);chars.lotte=character(playerSpec());chars.lotte.g.position.copy(p);chars.lotte.g.rotation.y=r;
  // The limbs are put where the pose says in the same tick, so a rebuild never
  // shows one frame of a standing body with the laptop gone.
  setPose(chars.lotte,old.pose,old.seatH);poseChar(chars.lotte,0,0);scene.add(chars.lotte.g);release(old.g)}
