// Artifact props: one small procedural building per artifact that carries a
// "model" key in campaign.json. Each builder returns a group at the origin,
// facing +z like the inn, with userData.r (the radius the walker is pushed
// out of), userData.h (where the name label floats) and, optionally, spin (a
// part the animation loop turns). buildArtifactProps() in the world builder
// places them; the yellow ring under each one stays the marker you walk to.
const ART_PROPS={
  // raw, bronze, silver, gold: a hall with two chimneys and three crates in front
  factory(){const g=new T.Group();g.add(box(3,1.4,1.8,PALETTE.stone,0,.7,0));g.add(box(3.2,.3,2,"#6B7280",0,1.55,0));g.add(cyl(.22,.26,1.8,PALETTE.timber,1,2.4,-.4,6));g.add(cyl(.18,.22,1.3,PALETTE.timber,.3,2.1,-.4,6));
    [["#A9743F",-.9],["#CBD5E1",0],[PALETTE.yellow,.9]].forEach(([c,x])=>g.add(box(.5,.5,.5,c,x,.25,1.5)));g.userData={r:1.7,h:3.7};return g},
  // a cottage with a red pillar box and a letter on the step
  postOffice(){const g=new T.Group();g.add(box(1.8,1.4,1.6,"#E7C9A0",0,.7,0));const r=cone(1.5,.9,PALETTE.red,0,1.85,0,4);r.rotation.y=Math.PI/4;g.add(r);g.add(box(.6,.9,.08,"#5A3C22",0,.45,.82));
    g.add(cyl(.28,.28,1.1,PALETTE.red,1.5,.55,.7,8));g.add(sph(.3,PALETTE.red,1.5,1.1,.7,8));g.add(box(.3,.05,.06,PALETTE.ink,1.5,.85,.99));g.add(box(.5,.03,.35,PALETTE.snow,-1.1,.02,1.3));g.userData={r:1.5,h:3};return g},
  // a shopfront with an orange awning, a shelf of three tins and a sign
  shop(){const g=new T.Group();g.add(box(2.2,1.3,1.4,"#E7C9A0",0,.65,0));g.add(box(2.4,.2,1.6,PALETTE.timber,0,1.4,0));const aw=box(2.5,.06,1,PALETTE.orange,0,1.35,1.15);aw.rotation.x=.35;g.add(aw);
    g.add(box(2,.06,.4,PALETTE.timber,0,.55,.85));[[PALETTE.blue,-.6],[PALETTE.green,0],[PALETTE.yellow,.6]].forEach(([c,x])=>g.add(cyl(.16,.16,.34,c,x,.75,.85,8)));g.add(box(1,.4,.06,PALETTE.snow,0,1.8,0));g.userData={r:1.5,h:2.9};return g},
  // a squat stone building with two columns, a dark door and a gold dial
  bank(){const g=new T.Group();g.add(box(2.4,1.5,1.8,"#CBD5E1",0,.75,0));g.add(box(2.7,.25,2.1,PALETTE.stone,0,1.62,0));g.add(box(2.7,.15,2.1,PALETTE.stone,0,.08,0));[-.85,.85].forEach(x=>g.add(cyl(.14,.14,1.4,PALETTE.snow,x,.8,1.05,8)));
    g.add(box(.6,.9,.08,PALETTE.ink,0,.45,.92));const d=cyl(.22,.22,.1,PALETTE.yellow,0,1.15,.95,8);d.rotation.x=Math.PI/2;g.add(d);g.userData={r:1.6,h:3};return g},
  // a windowless hall: three racks with one green LED strip and two roof fans
  dataCentre(){const g=new T.Group();g.add(box(3,1.6,2,"#334155",0,.8,0));g.add(box(3.2,.15,2.2,"#6B7280",0,1.65,0));[-.9,0,.9].forEach(x=>g.add(box(.6,1.2,.08,PALETTE.ink,x,.7,1.02)));g.add(box(2.4,.06,.06,PALETTE.green,0,1.2,1.08));
    [-.8,.8].forEach(x=>g.add(cyl(.32,.32,.16,PALETTE.stone,x,1.8,-.3,10)));g.userData={r:1.7,h:3.2};return g},
  // a pylon, a turbine that turns, and a red fuse box at the foot
  energyGrid(){const g=new T.Group();[-.45,.45].forEach(x=>g.add(box(.12,3.2,.12,"#6B7280",x,1.6,0)));g.add(box(2.2,.12,.12,"#6B7280",0,2.9,0));
    g.add(cyl(.08,.14,2.8,PALETTE.snow,1.7,1.4,-.8,6));g.add(box(.45,.26,.26,PALETTE.snow,1.7,2.9,-.8));const bl=new T.Group();for(let i=0;i<3;i++){const b=box(.1,1.2,.08,PALETTE.snow,0,0,0);b.geometry.translate(0,.6,0);b.rotation.z=i*Math.PI*2/3;bl.add(b)}bl.position.set(1.7,2.9,-.6);g.add(bl);
    g.add(box(.5,.7,.3,PALETTE.red,-1.4,.35,.5));g.userData={r:1.7,h:4,spin:bl};return g},
  // steps, two columns and three book spines on the front wall
  library(){const g=new T.Group();g.add(box(2.6,1.8,1.8,"#E7C9A0",0,.9,0));g.add(box(2.9,.2,2.1,PALETTE.timber,0,1.9,0));g.add(box(2.2,.15,.7,"#CBD5E1",0,.08,1.2));[-.9,.9].forEach(x=>g.add(cyl(.12,.12,1.6,PALETTE.snow,x,.95,1,8)));
    [[PALETTE.blue,-.35],[PALETTE.green,0],[PALETTE.orange,.35]].forEach(([c,x])=>g.add(box(.28,.9,.08,c,x,.65,.92)));g.userData={r:1.7,h:3.3};return g},
  // a small tower with three window bands and a flag
  office(){const g=new T.Group();g.add(box(2,2.8,1.6,"#CBD5E1",0,1.4,0));[.9,1.7,2.5].forEach(y=>g.add(box(2.06,.32,1.66,PALETTE.blue,0,y,0)));g.add(box(.6,.8,.08,PALETTE.ink,0,.4,.82));
    g.add(cyl(.04,.04,1.4,"#6B7280",1.3,.7,.9,5));g.add(box(.45,.28,.03,PALETTE.orange,1.55,1.25,.9));g.userData={r:1.5,h:3.6};return g},
  // three houses in a row behind one fence
  households(){const g=new T.Group();[["#E7C9A0",PALETTE.red,-1.2],["#CBD5E1",PALETTE.blue,0],["#E7C9A0",PALETTE.green,1.2]].forEach(([w,rc,x])=>{g.add(box(.9,.75,.8,w,x,.375,0));const r=cone(.75,.55,rc,x,1.02,0,4);r.rotation.y=Math.PI/4;g.add(r)});
    g.add(box(3.6,.06,.06,PALETTE.timber,0,.38,.75));[-1.75,1.75].forEach(x=>g.add(box(.08,.5,.08,PALETTE.timber,x,.25,.75)));g.userData={r:1.8,h:2.4};return g},
  // a hall with a bell tower, a blackboard on the front and a ball in the yard
  school(){const g=new T.Group();g.add(box(2.6,1.4,1.6,"#E7C9A0",0,.7,0));const r=cone(2,.9,PALETTE.blue,0,1.85,0,4);r.rotation.y=Math.PI/4;g.add(r);g.add(box(.5,1,.5,PALETTE.snow,0,2.5,0));const tr=cone(.5,.45,PALETTE.blue,0,3.2,0,4);tr.rotation.y=Math.PI/4;g.add(tr);
    g.add(sph(.13,PALETTE.yellow,0,2.3,.27,6));g.add(box(1.2,.6,.06,PALETTE.ink,0,.85,.82));g.add(sph(.2,PALETTE.orange,1.7,.2,.9,7));g.userData={r:1.7,h:3.8};return g}
};
