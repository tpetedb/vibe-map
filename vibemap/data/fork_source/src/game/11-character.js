function character(spec){
  const g=new T.Group();const c={g};
  const skin="#F5D7BC";
  c.lLeg=box(.34,.7,.34,spec.legs,-.2,.7,0,true);c.rLeg=box(.34,.7,.34,spec.legs,.2,.7,0,true);
  c.body=box(.9,.9,.5,spec.body,0,1.15,0);
  c.lArm=box(.24,.8,.24,spec.arms||spec.body,-.58,1.55,0,true);c.rArm=box(.24,.8,.24,spec.arms||spec.body,.58,1.55,0,true);
  c.head=box(.8,.8,.8,skin,0,2.05,0);
  g.add(c.lLeg,c.rLeg,c.body,c.lArm,c.rArm,c.head);
  // eyes
  const eye=(x)=>box(.1,.12,.05,"#222",x,2.1,.42);g.add(eye(-.18),eye(.18));
  if(spec.kind==="lotte"){
    g.add(box(.9,1.1,.3,"#F2CF6F",0,1.85,-.35));g.add(box(.88,.22,.88,"#F2CF6F",0,2.5,0));g.add(box(.3,.4,.2,"#F2CF6F",-.4,2.2,.2));g.add(box(.3,.4,.2,"#F2CF6F",.4,2.2,.2));
    g.add(box(.78,.2,.12,"#111",0,2.1,.44)); // sunglasses
    g.add(box(.36,.1,.36,"#C9C1B8",-.2,.02,0));g.add(box(.36,.1,.36,"#C9C1B8",.2,.02,0));
  }
  if(spec.kind==="rolinda"){
    [[-.35,2.55,-.1],[0,2.62,-.05],[.35,2.55,-.1],[-.45,2.3,-.35],[.45,2.3,-.35],[0,2.5,-.4],[-.2,2.62,.25],[.2,2.62,.25]].forEach(p=>g.add(sph(.22,"#F2CF6F",...p)));
    g.add(box(.36,.12,.42,"#fff",-.2,.03,.02));g.add(box(.36,.12,.42,"#fff",.2,.03,.02));
    g.add(box(.1,.1,.1,"#E36F3D",-.2,.1,.22));g.add(box(.1,.1,.1,"#3E7CC9",.2,.1,.22));
    const bottle=cyl(.07,.09,.5,"#5A2A3A",.62,1.15,.25);g.add(bottle); // wine
    g.add(box(.3,.15,.05,"#B0534B",0,1.85,.42)); // smile
  }
  if(spec.kind==="mentor"){const lk=spec.look;g.add(box(.86,.3,.86,lk.hair,0,2.5,0));g.add(box(.86,.5,.2,lk.hair,0,2.2,-.34));if(lk.glasses){g.add(box(.3,.16,.06,"#111",-.18,2.12,.42));g.add(box(.3,.16,.06,"#111",.18,2.12,.42));g.add(box(.1,.04,.06,"#111",0,2.12,.42))}if(lk.beard)g.add(box(.6,.28,.2,lk.hair,0,1.78,.34));g.add(box(.3,.08,.05,"#B0534B",0,1.86,.42))}
  if(spec.kind==="tom"){
    g.add(box(.9,.28,.9,"#1F2A44",0,2.55,0));g.add(box(.6,.06,.5,"#E8E8E8",0,2.44,.6));
    g.add(box(.2,.5,.7,"#6B4A2B",-.5,2.0,-.05));g.add(box(.2,.5,.7,"#6B4A2B",.5,2.0,-.05));
    g.add(box(.4,.08,.06,"#6B4A2B",0,1.88,.42)); // moustache
    g.add(box(.35,.95,.52,"#fff",0,1.15,0)); // tee strip
    c.rArm.rotation.x=-2.7; c.raised=true;
    const beer=cyl(.12,.12,.3,"#F2B441",0,-.85,0);c.rArm.add(beer);
  }
  const lab=label(spec.label,.55);lab.position.y=3.1;g.add(lab);
  c.walkT=0;return c;
}

