// The switchboard's prop, in its own module so the artifact family can grow
// without touching the shared builders in 17-artifact-props.js. Same contract
// as every entry there: a group at the origin facing +z, with userData.r (the
// radius the walker is pushed out of) and userData.h (where the label floats).
ART_PROPS.switchboard=function(){const g=new T.Group();
  // A desk, an upright panel, two rows of labelled sockets and one patch cord
  // already plugged in: the line you connect by name.
  g.add(box(2.2,.18,1,"#5A3C22",0,.72,.25));
  [-.95,.95].forEach(x=>g.add(box(.14,.72,.14,"#5A3C22",x,.36,.25)));
  g.add(box(2.2,1.5,.16,"#334155",0,1.45,-.2));
  [[-.6,1.75],[0,1.75],[.6,1.75],[-.6,1.15],[0,1.15],[.6,1.15]].forEach(([x,y])=>{
    const s=cyl(.11,.11,.1,"#FFBF00",x,y,-.1,8);s.rotation.x=Math.PI/2;g.add(s)});
  const cord=box(.06,.9,.06,"#00A86B",.3,1.45,.05);cord.rotation.z=-.55;g.add(cord);
  g.add(box(1.6,.22,.04,"#F8FAFC",0,.78,-.1));
  g.userData={r:1.4,h:3};return g};
