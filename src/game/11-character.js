// A walker is six meshes: four limbs that animate, one torso and one head.
// Everything that hangs off the torso or the head is built in place and then
// baked into that one mesh, because a scene with six characters in it cannot
// afford twenty draw calls each on a phone. The head is a group so what is on
// it turns with it, which is also why the glasses now follow the look.
function character(spec){
  const g=new T.Group();const c={g};
  const skin="#F5D7BC";
  c.lLeg=box(.34,.7,.34,spec.legs,-.2,.7,0,true);c.rLeg=box(.34,.7,.34,spec.legs,.2,.7,0,true);
  c.lArm=box(.24,.8,.24,spec.arms||spec.body,-.58,1.55,0,true);c.rArm=box(.24,.8,.24,spec.arms||spec.body,.58,1.55,0,true);
  const torso=new T.Group(),head=new T.Group();
  torso.add(box(.9,.9,.5,spec.body,0,1.15,0));
  head.add(box(.8,.8,.8,skin,0,2.05,0));
  // eyes
  const eye=(x)=>box(.1,.12,.05,"#222",x,2.1,.42);head.add(eye(-.18),eye(.18));
  if(spec.kind==="lotte"){
    head.add(box(.9,1.1,.3,"#F2CF6F",0,1.85,-.35));head.add(box(.88,.22,.88,"#F2CF6F",0,2.5,0));head.add(box(.3,.4,.2,"#F2CF6F",-.4,2.2,.2));head.add(box(.3,.4,.2,"#F2CF6F",.4,2.2,.2));
    head.add(box(.78,.2,.12,"#111",0,2.1,.44)); // sunglasses
    torso.add(box(.36,.1,.36,"#C9C1B8",-.2,.02,0));torso.add(box(.36,.1,.36,"#C9C1B8",.2,.02,0));
  }
  if(spec.kind==="rolinda"){
    [[-.35,2.55,-.1],[0,2.62,-.05],[.35,2.55,-.1],[-.45,2.3,-.35],[.45,2.3,-.35],[0,2.5,-.4],[-.2,2.62,.25],[.2,2.62,.25]].forEach(p=>head.add(sph(.22,"#F2CF6F",...p)));
    torso.add(box(.36,.12,.42,"#fff",-.2,.03,.02));torso.add(box(.36,.12,.42,"#fff",.2,.03,.02));
    torso.add(box(.1,.1,.1,"#E36F3D",-.2,.1,.22));torso.add(box(.1,.1,.1,"#3E7CC9",.2,.1,.22));
    torso.add(cyl(.07,.09,.5,"#5A2A3A",.62,1.15,.25)); // wine
    head.add(box(.3,.15,.05,"#B0534B",0,1.85,.42)); // smile
  }
  if(spec.kind==="mentor"){const lk=spec.look;head.add(box(.86,.3,.86,lk.hair,0,2.5,0));head.add(box(.86,.5,.2,lk.hair,0,2.2,-.34));if(lk.glasses){head.add(box(.3,.16,.06,"#111",-.18,2.12,.42));head.add(box(.3,.16,.06,"#111",.18,2.12,.42));head.add(box(.1,.04,.06,"#111",0,2.12,.42))}if(lk.beard)head.add(box(.6,.28,.2,lk.hair,0,1.78,.34));head.add(box(.3,.08,.05,"#B0534B",0,1.86,.42))}
  if(spec.kind==="tom"){
    head.add(box(.9,.28,.9,"#1F2A44",0,2.55,0));head.add(box(.6,.06,.5,"#E8E8E8",0,2.44,.6));
    head.add(box(.2,.5,.7,"#6B4A2B",-.5,2.0,-.05));head.add(box(.2,.5,.7,"#6B4A2B",.5,2.0,-.05));
    head.add(box(.4,.08,.06,"#6B4A2B",0,1.88,.42)); // moustache
    torso.add(box(.35,.95,.52,"#fff",0,1.15,0)); // tee strip
    c.rArm.rotation.x=-2.7; c.raised=true;
    const beer=cyl(.12,.12,.3,"#F2B441",0,-.85,0);c.rArm.add(beer);
  }
  // The head turns on its own axis, so the group sits where the head does and
  // what it carries is offset into its frame before the parts are baked.
  head.position.set(0,2.05,0);head.children.forEach(m=>{m.position.y-=2.05});
  g.add(c.lLeg,c.rLeg,c.lArm,c.rArm,torso,head);
  mergeStatic(torso);mergeStatic(head);
  c.body=torso;c.head=head;
  const lab=label(spec.label,.55);lab.position.y=3.1;g.add(lab);c.plate=lab;
  // A character carries a pose and a wardrobe; what they mean is the avatar
  // module's (src/game/18-avatar.js), so every walker, mentor and host has
  // the same actions available.
  // The night lifts the body (figMat), before the wardrobe goes on so a lit
  // screen or a hat keeps its own material.
  g.traverse(o=>{if(o.isMesh&&o.material.isMeshStandardMaterial)figMat(o.material)});
  c.pose="stand";c.poseY=0;applyWear(c,spec.wear);
  c.walkT=0;return c;
}
