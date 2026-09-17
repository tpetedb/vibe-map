function init3d(){
  const st=$("stage");renderer=new T.WebGLRenderer({canvas:$("c"),antialias:true});renderer.setPixelRatio(Math.min(devicePixelRatio,2));renderer.setSize(st.clientWidth,st.clientHeight);renderer.shadowMap.enabled=true;renderer.shadowMap.type=T.PCFSoftShadowMap;renderer.outputEncoding=T.sRGBEncoding;
  camera=new T.PerspectiveCamera(46,st.clientWidth/st.clientHeight,.1,300*WORLD_SCALE);camera.position.set(0,22*WORLD_SCALE,26*WORLD_SCALE);
  clock=new T.Clock();
  addEventListener("resize",()=>{const w=st.clientWidth,h=st.clientHeight;renderer.setSize(w,h);camera.aspect=w/h;camera.updateProjectionMatrix()});
  buildWorld(S.world||"campus");setupInput();inited=true;animate();
}
// A land blob: a grass disc with a dirt skirt below the waterline, the same
// shape for the island, its satellites and the annexes. Returns the grass.
function landBlob(group,x,z,r,seg){const g=cyl(r,r+1.2,2.4,W.grass,x,-1.2,z,seg||9);const d=cyl(r+1.1,r+2.2,2.2,W.dirt,x,-2.6,z,seg||9);group.add(g,d);return g}
function slabMat(id){return mat(id==="prod"?"#8A8A98":id==="winter"?"#C9D6E2":id==="desert"?"#C9A24E":"#E9D9B5")}
function buildWorld(id){
  W=WORLDS[id]||WORLDS.campus;S.world=id;if(!S.doneW[id])S.doneW[id]=[];S.done=S.doneW[id];CH=CAMPAIGN[id].ws;save();
  plots.length=0;clouds.length=0;parts.length=0;for(const k in builds)delete builds[k];for(const k in props)delete props[k];obstacles=[];annexes=[];
  PLOT_POS=W.plots.map(p=>new T.Vector3(p[0],0,p[1]));
  const WS=WORLD_SCALE;
  scene=new T.Scene();scene.fog=new T.Fog(W.fog,60*WS,150*WS);
  hemiL=new T.HemisphereLight("#cfe9ff","#4a7a3a",.7);scene.add(hemiL);ambL=new T.AmbientLight("#fff",.15);scene.add(ambL);
  dirL=new T.DirectionalLight("#fff5d6",1.1);dirL.position.set(14*WS,24*WS,10*WS);dirL.castShadow=true;dirL.shadow.mapSize.set(CONFIG.shadowMap,CONFIG.shadowMap);Object.assign(dirL.shadow.camera,{left:-28*WS,right:28*WS,top:28*WS,bottom:-28*WS,near:1,far:80*WS});scene.add(dirL);
  const ex=k=>W.extras.includes(k);const dummy=new T.Object3D();
  // landmass
  const land=new T.Group();
  island=landBlob(land,...W.land[0],12);W.land.slice(1).forEach(b=>landBlob(land,...b));scene.add(land);island.userData.parts=land.children.filter((m,i)=>i%2===0);
  // sea
  wGeo=new T.PlaneGeometry(220*WS,220*WS,72,72);wGeo.rotateX(-Math.PI/2);wBase=wGeo.attributes.position.array.slice();
  water=new T.Mesh(wGeo,new T.MeshStandardMaterial({color:W.water,transparent:true,opacity:.86,roughness:.3,metalness:.1,flatShading:true}));water.position.y=-1.6;water.receiveShadow=true;scene.add(water);
  const lava=id==="prod";
  const wmat=new T.MeshStandardMaterial({color:W.river,transparent:!lava,opacity:.9,roughness:.25,flatShading:true,emissive:lava?"#FF4500":"#000",emissiveIntensity:lava?1.2:0});
  if(W.river){for(let i=0;i<W.river.length-1;i++){const a=W.river[i],b=W.river[i+1],dx=b[0]-a[0],dz=b[1]-a[1],len=Math.hypot(dx,dz);const m=new T.Mesh(new T.BoxGeometry(len+.6,.12,2.2),wmat);m.position.set((a[0]+b[0])/2,.04,(a[1]+b[1])/2);m.rotation.y=-Math.atan2(dz,dx);scene.add(m);const bank=new T.Mesh(new T.BoxGeometry(len+.8,.06,3),mat(W.bank));bank.position.set(m.position.x,.01,m.position.z);bank.rotation.y=m.rotation.y;scene.add(bank)}}
  const lakeM=new T.Mesh(new T.CylinderGeometry(2.8,2.8,.12,10),id==="winter"?new T.MeshStandardMaterial({color:"#D8EEFB",roughness:.15,metalness:.2,flatShading:true}):wmat);lakeM.position.set(W.lake[0],.05,W.lake[1]);scene.add(lakeM);scene.add(cyl(3.3,3.3,.06,W.bank,W.lake[0],.01,W.lake[1],10));obstacles.push([W.lake[0],W.lake[1],3.1]);
  if(id!=="winter"&&!lava){const fnt=new T.Group();fnt.add(cyl(.9,1.1,.5,"#CBD5E1",0,.25,0,8));fnt.add(cyl(.15,.2,1.4,"#CBD5E1",0,1,0,6));fnt.add(cyl(.55,.4,.15,"#CBD5E1",0,1.7,0,8));const drops=[];for(let i=0;i<10;i++){const d=new T.Mesh(new T.SphereGeometry(.09,5,5),new T.MeshBasicMaterial({color:"#BAE6FD"}));d.userData.p=i/10;fnt.add(d);drops.push(d)}fnt.position.set(W.lake[0],0,W.lake[1]);fnt.userData.drops=drops;scene.add(fnt);props.fountain=fnt}
  if(id==="winter"){const sl=new T.Group();sl.add(box(1.2,.15,.6,"#B44A46",0,.15,0));[-.25,.25].forEach(z=>sl.add(box(1.4,.06,.08,"#7B5128",0,.05,z)));sl.position.set(W.lake[0]+1,0,W.lake[1]-.5);scene.add(sl);props.sled=sl}
  // path
  const way=W.way.map(p=>new T.Vector3(p[0],0,p[1]));const curve=new T.CatmullRomCurve3(way,false,"catmullrom",.5);const N=Math.floor(curve.getLength()/.42);
  const inst=new T.InstancedMesh(new T.BoxGeometry(1.15,.07,.42),slabMat(id),N);
  for(let i=0;i<N;i++){const t=i/N,pt=curve.getPointAt(t),tg=curve.getTangentAt(t);dummy.position.set(pt.x,.035,pt.z);dummy.rotation.y=-Math.atan2(tg.z,tg.x)+Math.PI/2;dummy.updateMatrix();inst.setMatrixAt(i,dummy.matrix)}inst.receiveShadow=true;scene.add(inst);props.curve=curve;
  if(W.bridge){const br=new T.Group();for(let i=0;i<7;i++)br.add(box(1.6,.14,.45,"#D9A76A",0,.35,-1.5+i*.5));br.add(box(.1,.9,3.6,"#7B5128",-.75,.7,0));br.add(box(.1,.9,3.6,"#7B5128",.75,.7,0));[-1.5,0,1.5].forEach(z=>{br.add(box(.12,.9,.12,"#7B5128",-.75,.55,z));br.add(box(.12,.9,.12,"#7B5128",.75,.55,z))});const tg=curve.getTangentAt(W.bridge[2]);br.position.set(W.bridge[0],0,W.bridge[1]);br.rotation.y=-Math.atan2(tg.z,tg.x)+Math.PI;scene.add(br)}
  props.lamps=[];for(let i=0;i<14;i++){const t=(i+.5)/14,pt=curve.getPointAt(t),tg=curve.getTangentAt(t),nx=-tg.z,nz=tg.x;const g=new T.Group();g.add(cyl(.05,.07,1.6,"#334155",0,.8,0,5));const lamp=new T.Mesh(new T.SphereGeometry(.18,6,6),new T.MeshStandardMaterial({color:"#FDE68A",emissive:"#FFBF00",emissiveIntensity:0}));lamp.position.y=1.7;g.add(lamp);g.position.set(pt.x+nx*1.1,0,pt.z+nz*1.1);scene.add(g);props.lamps.push(lamp)}
  // inn: stays at the origin, unscaled, with the walkers' start around its terrace
  const inn=new T.Group();const roofC=id==="winter"?"#F8FAFC":id==="prod"?"#3B1F2B":id==="desert"?"#C2410C":"#B44A46";inn.add(box(3.6,2.2,3,id==="prod"?"#6B6B7A":"#EFD9B8",0,1.1,0));const roof=cone(3.1,1.7,roofC,0,3.05,0,4);roof.rotation.y=Math.PI/4;inn.add(roof);inn.add(box(.5,1.1,.5,"#9C948A",1,3.6,.5));
  inn.add(box(.7,1.2,.1,"#5A3C22",0,.6,1.52));inn.add(box(.6,.6,.1,"#FFD36B",-1.2,1.3,1.52));inn.add(box(.6,.6,.1,"#FFD36B",1.2,1.3,1.52));inn.add(box(1.5,.8,.1,"#FFF3C2",-2.4,1.5,1.3));inn.add(box(.1,1.5,.1,"#7B5128",-2.4,.75,1.3));
  inn.add(box(5,.12,3,"#D9C49A",0,.06,3.2));[-1.4,1.4].forEach(x=>{inn.add(cyl(.5,.5,.1,"#7B5128",x,.55,3.4,8));inn.add(cyl(.06,.06,.5,"#7B5128",x,.3,3.4,5));inn.add(cone(1.1,.5,"#F87171",x,2.1,3.4,8));inn.add(cyl(.04,.04,1.7,"#94A3B8",x,1.15,3.4,4))});
  const lab=label("Hospitality Hub",.7);lab.position.set(0,4.8,0);inn.add(lab);const innLight=new T.PointLight("#FFD36B",0,10);innLight.position.set(0,1.5,2.5);inn.add(innLight);inn.userData.light=innLight;scene.add(inn);builds.inn=inn;obstacles.push([0,0,2.3],[0,3.2,2.6]);
  if(ex("stall")){const stall=new T.Group();stall.add(box(2,.9,1,"#A9743F",0,.45,0));stall.add(box(2.4,.1,1.4,"#E11D48",0,2,0));[-1,1].forEach(x=>stall.add(cyl(.05,.05,2,"#7B5128",x,1,.5,4)));[["#FFBF00",-.6],["#22C55E",0],["#F87171",.6]].forEach(([c,x])=>stall.add(sph(.22,c,x,1.05,.2,6)));const sp=P(4.5,2);stall.position.set(sp[0],0,sp[1]);stall.rotation.y=-.6;scene.add(stall);obstacles.push([sp[0],sp[1],1.3])}
  if(ex("well")){const well=new T.Group();well.add(cyl(.7,.75,.8,"#9CA3AF",0,.4,0,8));well.add(cone(.9,.6,"#7B5128",0,1.9,0,6));[-.5,.5].forEach(x=>well.add(box(.1,1.4,.1,"#7B5128",x,1,0)));const wp=P(-3,-4);well.position.set(wp[0],0,wp[1]);scene.add(well);obstacles.push([wp[0],wp[1],.9])}
  if(ex("mountain")){const mt=new T.Group();mt.add(cone(6,7,id==="winter"?"#B8C4CF":"#8B7355",0,3.5,0,7));mt.add(cone(2.3,2.6,"#F8FAFC",0,5.7,0,7));const mp=P(-9,-14);mt.position.set(mp[0],0,mp[1]);mt.traverse(o=>{if(o.isMesh)o.castShadow=true});scene.add(mt);obstacles.push([mp[0],mp[1],4.5])}
  if(ex("volcano")){const v=new T.Group();v.add(cyl(2,6.5,7,"#2E2E38",0,3.5,0,8));v.add(cyl(1.4,2.1,.5,"#FF4500",0,7.1,0,8).material.emissive.set("#FF4500")?cyl(1.4,2.1,.5,"#FF6A1A",0,7.1,0,8):null);const glow=new T.PointLight("#FF4500",2.5,18);glow.position.y=8;v.add(glow);const sm=[];for(let i=0;i<8;i++){const m=new T.Mesh(new T.SphereGeometry(.7,6,6),new T.MeshStandardMaterial({color:"#4B4B55",transparent:true,opacity:.6}));m.userData.o=i;v.add(m);sm.push(m)}v.userData.smoke=sm;const vp=P(-9,-14);v.position.set(vp[0],0,vp[1]);scene.add(v);props.volcano=v;obstacles.push([vp[0],vp[1],5.5]);
    for(let i=0;i<4;i++){const l=new T.Mesh(new T.BoxGeometry(1.5,.15,4+i),wmat);l.position.set(vp[0]+i*1.5,.06,vp[1]+4.5+i*.5);l.rotation.y=.4-i*.25;scene.add(l)}}
  if(ex("harbour")){const dock=new T.Group();for(let i=0;i<9;i++)dock.add(box(.5,.12,2,"#D9A76A",i*.55,.1,0));[0,2.2,4.4].forEach(x=>{dock.add(cyl(.1,.12,1.4,"#7B5128",x,-.4,-1));dock.add(cyl(.1,.12,1.4,"#7B5128",x,-.4,1))});const hp=id==="winter"?P(15,-5):P(15,-8);dock.position.set(hp[0],0,hp[1]);scene.add(dock);
    const boat=(c)=>{const g=new T.Group();g.add(box(2.6,.6,1.1,c,0,-.1,0));g.add(box(2.0,.3,.9,"#F8FAFC",0,.25,0));g.add(cyl(.05,.05,2.6,"#7B5128",.2,1.5,0,4));const sail=new T.Mesh(new T.ConeGeometry(.9,2.2,3),new T.MeshStandardMaterial({color:"#F8FAFC",side:T.DoubleSide,flatShading:true}));sail.position.set(.4,1.6,0);sail.rotation.z=-.15;g.add(sail);g.traverse(o=>{if(o.isMesh)o.castShadow=true});return g};
    const b1=boat(id==="prod"?"#7F1D1D":"#E11D48");b1.position.set(hp[0]+6,-1.35,hp[1]+.5);scene.add(b1);props.boat=b1;const b2=boat("#2563EB");scene.add(b2);props.boat2=b2}
  if(ex("lighthouse")){const lh=new T.Group();lh.add(cyl(.9,1.2,4.5,"#F8FAFC",0,2.25,0,8));[1,2.6].forEach(y=>lh.add(cyl(1.02,1.02,.5,"#DC2626",0,y,0,8)));lh.add(cyl(1,1,.6,"#1F2937",0,4.8,0,8));const lamp=new T.Mesh(new T.CylinderGeometry(.7,.7,.7,8),new T.MeshStandardMaterial({color:"#FEF3C7",emissive:"#FFBF00",emissiveIntensity:0}));lamp.position.y=5.4;lh.add(lamp);lh.userData.lamp=lamp;lh.add(cone(.9,.7,"#DC2626",0,6.1,0,8));
    const beam=new T.Mesh(new T.ConeGeometry(2.2,14,10,1,true),new T.MeshBasicMaterial({color:"#FDE68A",transparent:true,opacity:0,side:T.DoubleSide,depthWrite:false}));beam.rotation.z=Math.PI/2;beam.position.set(7,5.4,0);const bg=new T.Group();bg.add(beam);lh.add(bg);lh.userData.beam=bg;lh.userData.beamM=beam;const lp=P(19,5);lh.position.set(lp[0],0,lp[1]);scene.add(lh);props.lighthouse=lh;obstacles.push([lp[0],lp[1],1.4])}
  if(ex("windmill")){const wm=new T.Group();wm.add(cyl(1,1.4,3.6,"#E7C9A0",0,1.8,0,8));wm.add(cone(1.3,1,"#B44A46",0,4.1,0,8));wm.add(box(.6,.9,.1,"#5A3C22",0,.45,1.3));const blades=new T.Group();for(let i=0;i<4;i++){const b=box(.22,3.2,.06,"#F8FAFC",0,0,0);b.geometry.translate(0,1.6,0);b.rotation.z=i*Math.PI/2;blades.add(b)}blades.position.set(0,3.4,1.5);wm.add(blades);wm.userData.blades=blades;const wp=P(11,14.5);wm.position.set(wp[0],0,wp[1]);wm.rotation.y=Math.PI;scene.add(wm);props.windmill=wm;obstacles.push([wp[0],wp[1],1.6])}
  // the runway is one strip; its markings and the parked plane sit relative to it
  const ap=P(4,-16.5);
  if(ex("airstrip")){scene.add(box(9,.1,2.2,"#6B7280",ap[0],.05,ap[1]));for(let i=0;i<5;i++)scene.add(box(.9,.02,.15,"#F8FAFC",ap[0]-3+i*1.6,.11,ap[1]))}
  const plane=(c)=>{const g=new T.Group();g.add(box(2.8,.6,.7,c,0,.5,0));g.add(box(.7,.12,3.6,"#F8FAFC",.2,.6,0));g.add(box(.8,.12,1.4,"#F8FAFC",-1.2,.9,0));g.add(box(.6,.7,.12,"#F8FAFC",-1.2,1.05,0));g.add(box(.6,.4,.6,"#BAE6FD",.6,.9,0));const prop=box(.08,1.2,.15,"#1F2937",1.5,.5,0);g.add(prop);g.userData.prop=prop;[-.5,.5].forEach(z=>g.add(cyl(.18,.18,.12,"#1F2937",.3,.15,z,8)));g.traverse(o=>{if(o.isMesh)o.castShadow=true});return g};
  if(ex("airstrip")){const p1=plane("#FF8C1A");p1.position.set(ap[0]-2.5,0,ap[1]);scene.add(p1);props.plane=p1}
  const p2=plane(id==="prod"?"#7F1D1D":"#EF4444");scene.add(p2);props.plane2=p2;
  if(ex("balloon")){const bal=new T.Group();bal.add(sph(1.8,"#FF8C1A",0,3.4,0,10));const st2=sph(1.82,"#FFBF00",0,3.4,0,10);st2.scale.set(.5,1,1);bal.add(st2);bal.add(box(.9,.7,.9,"#A9743F",0,0,0));[-.4,.4].forEach(x=>bal.add(cyl(.03,.03,2.3,"#1F2937",x,1.2,0,3)));const bp=P(-15,11);bal.position.set(bp[0],7,bp[1]);scene.add(bal);props.balloon=bal}
  if(ex("birds")){props.birds=[];for(let i=0;i<6;i++){const b=new T.Group();const w1=box(.6,.05,.15,"#1F2937",-.3,0,0),w2=box(.6,.05,.15,"#1F2937",.3,0,0);b.add(w1,w2);b.userData={w1,w2,o:i};scene.add(b);props.birds.push(b)}}
  // vegetation by world
  const treeAt=(x,z,k)=>{const t=new T.Group();
    if(W.tree==="pine"){t.add(cyl(.18,.25,1.2,"#5B3A1E",0,.6,0,6));t.add(cone(.9,1.6,"#2F6B4F",0,1.9,0,6));t.add(cone(.75,1.3,"#3E8464",0,2.8,0,6));t.add(cone(.8,.4,"#F8FAFC",0,2.55,0,6));t.add(cone(.55,.35,"#F8FAFC",0,3.3,0,6))}
    else if(W.tree==="palm"){t.add(cyl(.14,.22,2.6,"#8B5A2B",0,1.3,0,6));for(let i=0;i<5;i++){const f=cone(.35,1.9,"#3F9B57",0,0,0,3);f.geometry.translate(0,.9,0);f.rotation.z=1.15;f.rotation.y=i/5*Math.PI*2;f.position.y=2.6;t.add(f)}}
    else if(W.tree==="dead"){t.add(cyl(.12,.25,2,"#2B2B33",0,1,0,5));[[.5,1.6,.3],[-.5,1.3,-.2]].forEach(a=>{const b=box(.12,1,.12,"#2B2B33",a[0],a[1],a[2]);b.rotation.z=a[0]>0?-.7:.7;t.add(b)})}
    else if(k===0){t.add(cyl(.18,.25,1.2,"#7B5128",0,.6,0,6));t.add(cone(.9,1.6,"#3F9B57",0,1.9,0,6));t.add(cone(.7,1.3,"#4FB864",0,2.7,0,6))}
    else{t.add(cyl(.2,.28,1.5,"#7B5128",0,.75,0,6));t.add(sph(1,"#4FB864",0,2.1,0,7));t.add(sph(.7,"#5FCB7B",.5,2.6,.3,6))}
    t.position.set(x,0,z);t.rotation.y=x*.7;t.traverse(o=>{if(o.isMesh)o.castShadow=true});scene.add(t);obstacles.push([x,z,.7])};
  const treeSpots=[[5,-7,0],[-4,-8,1],[9,-13,0],[-13,-8,0],[-15,11,1],[-11,12,0],[3,15,1],[12,9,0],[17,-1,1],[8,3,1],[-6,-2,0],[6,-3,1],[-1,-13,0],[15,-13,0],[-12,-14,0]].map(a=>[...P(a[0],a[1]),a[2]]);
  treeSpots.forEach(a=>{if(onLandW(a[0],a[1])&&!PLOT_POS.some(p=>p.distanceTo(new T.Vector3(a[0],0,a[1]))<2.8))treeAt(...a)});
  [[7,7],[-8,-6],[2,-6],[-14,4],[10,-2]].map(a=>P(a[0],a[1])).forEach(([x,z])=>{if(onLandW(x,z))scene.add(sph(.45,id==="prod"?"#1F1F27":"#9CA3AF",x,.2,z,5))});
  if(ex("flowers")){const fl=new T.InstancedMesh(new T.BoxGeometry(.18,.18,.18),new T.MeshStandardMaterial({color:"#fff",flatShading:true}),160);const colr=new T.Color();for(let i=0;i<160;i++){const a=Math.random()*Math.PI*2,r=(3+Math.random()*11)*WS;dummy.position.set(Math.cos(a)*r,.12,Math.sin(a)*r);dummy.rotation.set(0,Math.random(),0);dummy.updateMatrix();fl.setMatrixAt(i,dummy.matrix);colr.set(["#FF8C1A","#FFBF00","#F8FAFC","#FFA94D"][i%4]);fl.setColorAt(i,colr)}scene.add(fl)}
  if(ex("cacti")){[[6,-6],[-5,-7],[10,5],[-9,1],[3,-15],[14,-4]].map(a=>P(a[0],a[1])).forEach(([x,z])=>{if(!onLandW(x,z))return;const c=new T.Group();c.add(cyl(.3,.35,2,"#2F855A",0,1,0,7));c.add(cyl(.18,.2,.9,"#2F855A",.5,1.5,0,6));c.add(cyl(.18,.2,.7,"#2F855A",-.5,1.2,0,6));c.position.set(x,0,z);scene.add(c);obstacles.push([x,z,.6])})}
  if(ex("mesas")){[[-8,-14,4,3.5],[12,-13,3,2.5],[-16,8,2.5,2]].forEach(([x,z,r,h])=>{[x,z]=P(x,z);const m=new T.Group();m.add(cyl(r*.8,r,h,"#B45309",0,h/2,0,8));m.add(cyl(r*.75,r*.8,.4,"#D97706",0,h+.2,0,8));m.position.set(x,0,z);m.traverse(o=>{if(o.isMesh)o.castShadow=true});scene.add(m);obstacles.push([x,z,r])})}
  if(ex("dunes")){[[6,8],[-6,9],[8,-9],[-11,-4]].map(a=>P(a[0],a[1])).forEach(([x,z])=>{const d=sph(3,"#F1DDA2",x,-2.2,z,10);d.scale.set(1,.5,1);scene.add(d)})}
  if(ex("tumbleweed")){const tw=new T.Mesh(new T.IcosahedronGeometry(.6,1),new T.MeshStandardMaterial({color:"#A16207",wireframe:true}));scene.add(tw);props.tumble=tw}
  if(ex("snowmen")){[[6,-4],[-7,9]].map(a=>P(a[0],a[1])).forEach(([x,z])=>{const g=new T.Group();g.add(sph(.7,"#F8FAFC",0,.6,0,9));g.add(sph(.5,"#F8FAFC",0,1.55,0,9));g.add(sph(.36,"#F8FAFC",0,2.25,0,9));g.add(cone(.1,.4,"#F97316",0,2.25,.5,5).rotateX(Math.PI/2)?cone(.1,.4,"#F97316",0,2.25,.5,5):null);g.add(box(.6,.1,.6,"#1F2937",0,2.55,0));g.add(box(.4,.35,.4,"#1F2937",0,2.75,0));g.position.set(x,0,z);scene.add(g);obstacles.push([x,z,.9])})}
  if(ex("icefloes")){for(let i=0;i<10;i++){const a=i/10*Math.PI*2,r=(24+(i%3)*3)*WS;const f=cyl(1+(i%3)*.5,1.2+(i%3)*.5,.3,"#E8F3FA",Math.cos(a)*r,-1.5,Math.sin(a)*r,6);scene.add(f)}}
  if(ex("snow")){const g=new T.BufferGeometry();const v=[];for(let i=0;i<500;i++)v.push((Math.random()-.5)*60*WS,Math.random()*20,(Math.random()-.5)*60*WS);g.setAttribute("position",new T.Float32BufferAttribute(v,3));const pts=new T.Points(g,new T.PointsMaterial({color:"#fff",size:.25,transparent:true,opacity:.9}));scene.add(pts);props.snow=pts}
  if(ex("embers")){const g=new T.BufferGeometry();const v=[];const ep=P(-9,-14);for(let i=0;i<250;i++)v.push(ep[0]+(Math.random()-.5)*10,Math.random()*16,ep[1]+(Math.random()-.5)*10);g.setAttribute("position",new T.Float32BufferAttribute(v,3));const pts=new T.Points(g,new T.PointsMaterial({color:"#FF7A1A",size:.22,transparent:true,opacity:.9}));scene.add(pts);props.embers=pts}
  if(ex("aurora")){const ag=new T.PlaneGeometry(90*WS,14,40,4);const am=new T.MeshBasicMaterial({color:"#00D084",transparent:true,opacity:0,side:T.DoubleSide,depthWrite:false,blending:T.AdditiveBlending});const au=new T.Mesh(ag,am);au.position.set(0,26*WS,-45*WS);scene.add(au);props.aurora=au;props.auroraBase=ag.attributes.position.array.slice()}
  // plots
  buildArtifactProps();placeArtifacts();
  PLOT_POS.forEach((p,i)=>{const g=new T.Group();g.position.copy(p);const ring=new T.Mesh(new T.TorusGeometry(2,.07,6,32),new T.MeshBasicMaterial({color:"#ffffff",transparent:true,opacity:.7}));ring.rotation.x=Math.PI/2;ring.position.y=.06;g.add(ring);
    const post=box(.1,1.6,.1,"#7B5128",0,.8,0);const sign=box(1.3,.6,.1,"#FFF3C2",0,1.6,0);g.add(post,sign);const lb=label(CH[i].h,.55);lb.position.y=2.3;g.add(lb);
    [[-1.6,-1.6],[1.6,-1.6]].forEach(([x,z])=>g.add(box(.08,.6,.08,"#7B5128",x,.3,z)));g.add(box(3.3,.06,.06,"#7B5128",0,.55,-1.6));g.userData={ring,post,sign,lb};scene.add(g);plots.push(g)});
  for(let i=0;i<8;i++){const c=new T.Group();[[0,0,0,1.6],[1.5,.3,.2,1.1],[-1.4,.2,.3,1],[.4,.7,-.3,.9]].forEach(([x,y,z,r])=>{const m=new T.Mesh(new T.SphereGeometry(r,7,7),new T.MeshStandardMaterial({color:id==="prod"?"#6B6B78":"#fff",flatShading:true,transparent:true,opacity:.92}));m.position.set(x,y,z);c.add(m)});c.position.set((-40+i*11)*WS,(13+Math.sin(i)*2.5)*WS,(-22+((i*7)%14))*WS);c.userData.v=(.4+i*.08)*WS;scene.add(c);clouds.push(c)}
  sunM=new T.Mesh(new T.SphereGeometry(2.4,10,10),new T.MeshBasicMaterial({color:"#FFD36B"}));scene.add(sunM);moonM=new T.Mesh(new T.SphereGeometry(1.7,10,10),new T.MeshBasicMaterial({color:"#FFF3C2"}));scene.add(moonM);
  const sg=new T.BufferGeometry();const sv=[];for(let i=0;i<400;i++){const a=Math.random()*Math.PI*2,b=Math.random()*Math.PI*.5;sv.push(Math.cos(a)*Math.cos(b)*120*WS,Math.sin(b)*120*WS+5,Math.sin(a)*Math.cos(b)*120*WS)}sg.setAttribute("position",new T.Float32BufferAttribute(sv,3));stars=new T.Points(sg,new T.PointsMaterial({color:"#fff",size:.6,transparent:true,opacity:0}));scene.add(stars);
  // characters (keep positions if switching)
  const lp=chars.lotte?chars.lotte.g.position.clone():new T.Vector3(2.8,0,5.2);
  chars.lotte=character({kind:"lotte",body:"#FFFFFF",legs:"#C9C1B8",arms:"#F5D7BC",label:S.name+", CoS"});chars.lotte.g.position.copy(onLandW(lp.x,lp.z)?lp:new T.Vector3(2.8,0,5.2));scene.add(chars.lotte.g);
  chars.tom=character({kind:"tom",body:"#D8C49B",legs:"#6E6A66",arms:"#F5D7BC",label:"Tom, SRE"});chars.tom.g.position.set(-1.6,0,6.4);scene.add(chars.tom.g);
  chars.rolinda=character({kind:"rolinda",body:"#8FD18A",legs:"#9CC4E8",arms:"#8FD18A",label:"Rolinda, Ops"});chars.rolinda.g.position.set(0.4,0,4.6);chars.rolinda.g.rotation.y=Math.PI*.95;scene.add(chars.rolinda.g);
  // mentors (NPC scientists) for this world
  props.mentors=[];MENTORS.filter(m=>m.world===id).forEach(m=>{const c=character({kind:"mentor",body:m.look.shirt,legs:"#374151",arms:"#F5D7BC",label:m.name,look:m.look});c.g.position.set(m.pos[0],0,m.pos[1]);c.g.rotation.y=Math.PI;scene.add(c.g);c.id=m.id;props.mentors.push(c);obstacles.push([m.pos[0],m.pos[1],.6]);
    const ring=new T.Mesh(new T.TorusGeometry(1.1,.05,6,24),new T.MeshBasicMaterial({color:S.path[m.id]==="deep"?"#0088CC":S.path[m.id]==="skip"?"#F04923":"#FFA94D",transparent:true,opacity:.6}));ring.rotation.x=Math.PI/2;ring.position.set(m.pos[0],.05,m.pos[1]);scene.add(ring);c.ring=ring});
  // shadow blob + marker
  props.shadow=new T.Mesh(new T.CircleGeometry(.55,12),new T.MeshBasicMaterial({color:"#000",transparent:true,opacity:.25}));props.shadow.rotation.x=-Math.PI/2;props.shadow.position.y=.02;scene.add(props.shadow);
  marker=new T.Mesh(new T.RingGeometry(.3,.45,20),new T.MeshBasicMaterial({color:"#0088CC",transparent:true,opacity:0,side:T.DoubleSide}));marker.rotation.x=-Math.PI/2;marker.position.y=.06;scene.add(marker);
  S.done.forEach(k=>placeBuilding(k,false));applySky(S.done.length,true);fixColors(scene);hud();
}
// One building per artifact of this world that names a model in ART_PROPS;
// the group is an obstacle so the walker goes round it, and the ring stays.
function buildArtifactProps(){props.artProps=[];props.artR={};(typeof ARTIFACTS==="undefined"?[]:ARTIFACTS).filter(a=>a.world===S.world&&a.model&&ART_PROPS[a.model]).forEach(a=>{const g=ART_PROPS[a.model]();const r=g.userData.r||1.4;
  const lb=label(a.name,.55);lb.position.y=g.userData.h||3;g.add(lb);g.position.set(a.pos[0],0,a.pos[1]);g.traverse(o=>{if(o.isMesh)o.castShadow=true});scene.add(g);props.artProps.push(g);props.artR[a.id]=r;obstacles.push([a.pos[0],a.pos[1],r])})}
// Walkable ground: the island's blobs, plus every annex that has appeared and
// the causeway of its spur (a capsule from the plot to the annex).
function onLandW(x,z){if(W.land.some(b=>Math.hypot(x-b[0],z-b[1])<b[2]-.6))return true;
  return annexes.some(a=>Math.hypot(x-a.x,z-a.z)<a.r-.6||segDist(x,z,a.x,a.z,a.px,a.pz)<1)}
function segDist(x,z,ax,az,bx,bz){const dx=bx-ax,dz=bz-az,l2=dx*dx+dz*dz;const t=l2?Math.max(0,Math.min(1,((x-ax)*dx+(z-az)*dz)/l2)):0;return Math.hypot(x-(ax+dx*t),z-(az+dz*t))}
window.nextWorld=function(){const ids=Object.keys(WORLDS);const i=(ids.indexOf(S.world||"campus")+1)%ids.length;setWorld(ids[i])};
window.setWorld=function(id){S.world=id;save();renderWorldPicker();if(started)buildWorld(id)};
function renderWorldPicker(){const el=$("worlds");if(!el)return;el.innerHTML=Object.keys(WORLDS).map(k=>`<button class="world${(S.world||"campus")===k?' pick':''}" onclick="setWorld('${k}')"><b><i style="background:${WORLDS[k].swatch}"></i>${CAMPAIGN[k].title.split(":")[0]}</b>${WORLDS[k].name}. ${CAMPAIGN[k].title.split(": ")[1]}</button>`).join("")}
function placeBuilding(k,pop){
  const g=building(k);g.position.copy(PLOT_POS[k-1]);const p=plots[k-1];p.userData.ring.visible=false;p.userData.post.visible=false;p.userData.sign.visible=false;p.userData.lb.visible=false;
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
  const grass=landBlob(g,0,0,ANNEX_R,9);
  const dx=pp.x-ax,dz=pp.z-az,len=Math.hypot(dx,dz),ux=dx/len,uz=dz/len,ang=-Math.atan2(uz,ux);
  const from=len-2.3,to=1.3,mid=(from+to)/2;
  const cw=box(from-to+1.5,2.4,2.6,W.grass,ux*mid,-1.2,uz*mid);cw.rotation.y=ang;g.add(cw);
  const cd=box(from-to+2.5,2.2,4.4,W.dirt,ux*mid,-2.6,uz*mid);cd.rotation.y=ang;g.add(cd);
  const n=Math.max(1,Math.floor((from-to)/.42));const inst=new T.InstancedMesh(new T.BoxGeometry(1.15,.07,.42),slabMat(S.world),n);const dummy=new T.Object3D();
  for(let i=0;i<n;i++){const d=to+(i+.5)*(from-to)/n;dummy.position.set(ux*d,.035,uz*d);dummy.rotation.y=ang+Math.PI/2;dummy.updateMatrix();inst.setMatrixAt(i,dummy.matrix)}inst.receiveShadow=true;g.add(inst);
  g.add(cyl(1,1.15,.2,W.bank,0,.1,0,9));g.add(cyl(.05,.07,3.2,"#5A3C22",0,1.7,0,5));
  const flag=new T.Mesh(new T.PlaneGeometry(1.2,.7,6,1),new T.MeshStandardMaterial({color:"#FF8C1A",side:T.DoubleSide,flatShading:true}));flag.position.set(.62,3,0);g.add(flag);g.userData.flag=flag;
  const lb=label(CH[k-1].h,.5);lb.position.y=3.9;g.add(lb);
  fixColors(g);scene.add(g);island.userData.parts.push(grass,cw);
  annexes.push({k,x:ax,z:az,r:ANNEX_R,px:pp.x,pz:pp.z,g});obstacles.push([ax,az,.5]);
  if(pop)popIn(g);
}
// The pop every new thing on the island gets: it grows from nothing (the
// animation loop eases popT) under a burst of forty confetti cubes.
function popIn(g){g.scale.set(.01,.01,.01);g.userData.popT=0;for(let i=0;i<40;i++){const m=new T.Mesh(new T.BoxGeometry(.18,.18,.18),new T.MeshBasicMaterial({color:["#0088CC","#0067A5","#FFBF00","#00D084"][i%4]}));m.position.copy(g.position).add(new T.Vector3((Math.random()-.5)*2,1,(Math.random()-.5)*2));m.userData.v=new T.Vector3((Math.random()-.5)*6,4+Math.random()*5,(Math.random()-.5)*6);m.userData.life=1.4+Math.random();scene.add(m);parts.push(m)}}
function tickPop(g,dt){if(g.userData.popT===undefined)return;g.userData.popT+=dt;const x=Math.min(1,g.userData.popT/.9);const s=1+Math.sin(x*Math.PI*1.5)*(1-x)*.35;g.scale.setScalar(x<1?Math.max(.01,x*x*(3-2*x))*s:1);if(x>=1)delete g.userData.popT}

let skyFrom=new T.Color("#9BD3F5"),skyTo=new T.Color("#9BD3F5"),skyT=1,skyN=0;
function applySky(n,instant){skyN=Math.min(8,n);skyFrom.copy(scene.background||new T.Color(W.sky[0]));skyTo.set(W.sky[skyN]);skyT=instant?1:0;if(instant){scene.background=skyTo.clone();scene.fog.color.copy(skyTo)}}

/* ---------------- input & movement ---------------- */
