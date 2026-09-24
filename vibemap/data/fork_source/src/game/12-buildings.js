function building(k){
  const g=new T.Group();
  if(k===1){for(let i=0;i<6;i++){const a=i/6*Math.PI*2;g.add(box(.5,1+((i*7)%3)*.3,.5,"#B3A08B",Math.cos(a)*1.6,.5,Math.sin(a)*1.6))}
    const cr=new T.Mesh(new T.OctahedronGeometry(.7),mat("#FFA94D",{emissive:"#6D28D9",emissiveIntensity:1.1}));cr.position.y=1.6;g.add(cr);g.userData.spin=cr;
    const l=new T.PointLight("#FFA94D",1.2,6);l.position.y=1.6;g.add(l)}
  if(k===2){g.add(box(2.2,1.6,2,"#E7C9A0",0,.8,0));g.add(cone(1.8,1.2,"#B44A46",0,2.2,0,4));g.children[1].rotation.y=Math.PI/4;
    g.add(box(.5,.8,.1,"#5A3C22",.5,.4,1.02));g.add(win(.5,.5,.1,"#7DB8E6",-.5,.9,1.02));g.add(win(.9,.7,.1,"#FFF3C2",-1.5,.9,.6));g.add(box(.08,.9,.08,PALETTE.timber,-1.5,.45,.6))}
  if(k===3){g.add(box(2.8,1.8,2.2,"#F1D8A5",0,.9,0));g.add(cone(2.2,1.3,"#7B9C4B",0,2.45,0,4));g.children[1].rotation.y=Math.PI/4;
    [.5,.9,.7,1.2].forEach((h,i)=>g.add(box(.25,h,.1,"#3B2F2A",-.6+i*.4,h/2+.1,1.12)));g.add(win(.5,.5,.1,"#7DB8E6",1,1.1,1.12))}
  if(k===4){g.add(cyl(.9,1.1,4,"#DCD3C4",0,2,0,8));g.add(cone(1.3,1.4,"#4A5D8A",0,4.6,0,8));g.add(cyl(.05,.05,2,"#5A3C22",0,6.2,0,4));
    const flag=new T.Mesh(new T.PlaneGeometry(1.2,.7,6,1),new T.MeshStandardMaterial({color:PALETTE.orangeBright,side:T.DoubleSide,flatShading:true}));flag.position.set(.62,6.8,0);g.add(flag);g.userData.flag=flag;
    [1.2,2.2,3.2].forEach(y=>g.add(win(.3,.4,.1,"#4A5568",0,y,1.0)))}
  if(k===5){for(let i=0;i<7;i++)g.add(box(1.2,.15,.5,PALETTE.deck,0,.1,.6+i*.55));g.add(box(.08,.6,4,PALETTE.timber,-.55,.4,2.2));g.add(box(.08,.6,4,PALETTE.timber,.55,.4,2.2));
    const islet=cyl(1.6,1.9,1.2,"#79CC72",0,-.4,5.2,7);g.add(islet);g.add(sph(.35,PALETTE.blueBright,-.5,.55,5,8));g.add(sph(.35,PALETTE.yellow,.5,.55,5.4,8));
    g.userData.orbs=[g.children[g.children.length-2],g.children[g.children.length-1]]}
  if(k===6){g.add(cyl(.35,.5,2.6,PALETTE.timber,0,1.3,0,7));g.add(sph(1.6,"#3F9B57",0,3.2,0,7));g.add(sph(1.1,"#4FB864",-1.1,2.7,.3,7));g.add(sph(1.1,"#2E7D4A",1.1,2.8,-.3,7));g.add(sph(.9,"#5FCB7B",0,4.5,0,7));
    const orbs=[];for(let i=0;i<7;i++){const o=new T.Mesh(new T.SphereGeometry(.14,6,6),new T.MeshStandardMaterial({color:"#FFF3C2",emissive:PALETTE.yellow,emissiveIntensity:1.2}));const a=i/7*Math.PI*2;o.position.set(Math.cos(a)*1.6,3+Math.sin(i)*.8,Math.sin(a)*1.6);o.userData.a=a;g.add(o);orbs.push(o)}
    g.userData.orbs=orbs;const l=new T.PointLight(PALETTE.yellow,1,7);l.position.y=3.2;g.add(l)}
  if(k===7){g.add(box(2.2,.5,2.2,PALETTE.stone,0,.25,0));for(let i=0;i<4;i++){const a=i*Math.PI/2;g.add(cyl(.08,.1,6,"#CBD5E1",Math.cos(a)*.7,3,Math.sin(a)*.7,4))}
    for(let y=1.5;y<6;y+=1.5)g.add(box(1.5,.08,1.5,"#94A3B8",0,y,0));g.add(cyl(.05,.05,2.5,"#CBD5E1",0,7.2,0,4));
    const bl=new T.Mesh(new T.SphereGeometry(.22,8,8),new T.MeshStandardMaterial({color:PALETTE.orangeBright,emissive:PALETTE.orangeBright,emissiveIntensity:2}));bl.position.y=8.5;g.add(bl);g.userData.blink=bl;
    const bb=win(2.6,1.2,.12,"#0EA5E9",0,4.2,1.1);g.add(bb);const lab=label("LIVE",.7);lab.position.set(0,4.2,1.3);g.add(lab)}
  if(k===8){g.add(box(3,1.8,2.4,"#64748B",0,.9,0));g.add(box(3.2,.3,2.6,"#475569",0,1.95,0));g.add(cyl(.3,.35,1.6,"#94A3B8",1,2.8,-.6,6));
    const gear=new T.Mesh(new T.TorusGeometry(.8,.22,6,10),mat(PALETTE.yellow));gear.position.set(-.6,2.9,0);g.add(gear);g.userData.gear=gear;
    for(let i=0;i<8;i++){const a=i/8*Math.PI*2;const t=box(.3,.3,.3,PALETTE.yellow,-.6+Math.cos(a)*1.05,2.9+Math.sin(a)*1.05,0);t.rotation.z=a;g.add(t)}
    g.add(win(.6,.9,.1,PALETTE.ink,0,.45,1.22));const sm=[];for(let i=0;i<5;i++){const m=new T.Mesh(new T.SphereGeometry(.25,6,6),new T.MeshStandardMaterial({color:"#E5E7EB",transparent:true,opacity:.6}));m.position.set(1,3.6+i*.6,-.6);m.userData.o=i;g.add(m);sm.push(m)}g.userData.smoke=sm}
  g.traverse(o=>{if(o.isMesh){o.castShadow=true;o.receiveShadow=true}});
  // A finished building never moves again, so everything but the parts the
  // animation loop holds is baked into one mesh, and the windows into a
  // second one the evening lights. Eight of these is the difference between
  // a finished island inside the phone's draw-call budget and over it.
  mergeStatic(g);
  return g;
}


// Scene assembly is separate from buildWorld's campaign and progress writes.
// Coordinates here are local to a miniature; its caller owns scale and travel.
function buildMiniature({look,terrain,structures,lessonSites,obstacles=[]}){
  const root=new T.Group(),ground=new T.Group(),radius=terrain.radius;
  buildLandSurface(ground,{r:15,segments:24,grass:terrain.grass,dirt:terrain.dirt});
  ground.scale.setScalar(radius/15);root.add(ground,structures);
  const sites=lessonSites.map(site=>({...site,position:[...site.position]}));
  sites.forEach(site=>{const pavilion=building(2);pavilion.scale.setScalar(.045);
    pavilion.position.set(site.position[0],0,site.position[1]);pavilion.userData.lessonId=site.id;
    pavilion.userData.topicId=site.id;root.add(pavilion)});
  const walkSurface={radius,y:0};root.userData={miniature:true,look,walkSurface,lessonSites:sites,obstacles};
  return {root,walkSurface,obstacles,lessonSites:sites};
}
