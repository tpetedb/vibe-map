function animate(){
  requestAnimationFrame(animate);if(!scene)return;const dt=Math.min(.05,clock.getDelta()),t=clock.elapsedTime;
  // movement: acceleration, turning, collisions, jump
  const L=chars.lotte,pos=L.g.position;let mv=new T.Vector3();
  if(keys.arrowup||keys.w)mv.z-=1;if(keys.arrowdown||keys.s)mv.z+=1;if(keys.arrowleft||keys.a)mv.x-=1;if(keys.arrowright||keys.d)mv.x+=1;
  if(joy.on&&(Math.abs(joy.x)>.12||Math.abs(joy.y)>.12)){mv.set(joy.x,0,joy.y)}
  let steer=false;if(mv.lengthSq()>0){hasTarget=false;marker.material.opacity=0;const l=mv.length();mv.normalize().multiplyScalar(Math.min(1,l));steer=true}
  else if(hasTarget){mv.subVectors(target,pos);mv.y=0;const d=mv.length();if(d<.25){hasTarget=false;marker.material.opacity=0;mv.set(0,0,0)}else{mv.normalize().multiplyScalar(Math.min(1,d/1.5));steer=true}}
  if(!L.vel)L.vel=new T.Vector3();if(L.jy===undefined){L.jy=0;L.jv=0}
  const MAXV=4.6,ACC=22,FRIC=14;
  if(steer&&started){L.vel.x+=(mv.x*MAXV-L.vel.x)*Math.min(1,ACC*dt/MAXV*1.5);L.vel.z+=(mv.z*MAXV-L.vel.z)*Math.min(1,ACC*dt/MAXV*1.5)}
  else{L.vel.x-=L.vel.x*Math.min(1,FRIC*dt);L.vel.z-=L.vel.z*Math.min(1,FRIC*dt)}
  const sp=Math.hypot(L.vel.x,L.vel.z);const walking=sp>.35&&started;
  if(started&&sp>.01){const prev=pos.clone();pos.x+=L.vel.x*dt;pos.z+=L.vel.z*dt;
    // land edge: try axis slide
    if(!onLandW(pos.x,pos.z)){const px=onLandW(pos.x,prev.z),pz=onLandW(prev.x,pos.z);if(px)pos.z=prev.z;else if(pz)pos.x=prev.x;else{pos.copy(prev);L.vel.multiplyScalar(-.2);hasTarget=false;marker.material.opacity=0}}
    // obstacles: push out
    obstacles.forEach(o=>{const dx=pos.x-o[0],dz=pos.z-o[1],d=Math.hypot(dx,dz),m=o[2]+.45;if(d<m&&d>1e-4){pos.x=o[0]+dx/d*m;pos.z=o[1]+dz/d*m;const dot=L.vel.x*dx/d+L.vel.z*dz/d;if(dot<0){L.vel.x-=dx/d*dot;L.vel.z-=dz/d*dot}}});
    if(hasTarget&&target.distanceTo(pos)<.6){hasTarget=false;marker.material.opacity=0}
    const ang=Math.atan2(L.vel.x,L.vel.z);let da=ang-L.g.rotation.y;while(da>Math.PI)da-=Math.PI*2;while(da<-Math.PI)da+=Math.PI*2;L.g.rotation.y+=da*Math.min(1,12*dt);
  }
  // jump
  if(wantJump&&started){wantJump=false;if(L.jy<=0.001){L.jv=7}}
  if(L.jv!==0||L.jy>0){L.jv-=22*dt;L.jy=Math.max(0,L.jy+L.jv*dt);if(L.jy===0)L.jv=0}
  // dust when walking
  if(walking&&L.jy===0&&Math.random()<dt*14){const m=new T.Mesh(new T.SphereGeometry(.09,5,5),new T.MeshBasicMaterial({color:W.bank,transparent:true,opacity:.7}));m.position.set(pos.x+(Math.random()-.5)*.4,.1,pos.z+(Math.random()-.5)*.4);m.userData.v=new T.Vector3((Math.random()-.5)*1.2,1.2,(Math.random()-.5)*1.2);m.userData.life=.5;m.userData.dust=1;scene.add(m);parts.push(m)}
  if(props.shadow){props.shadow.position.set(pos.x,.02,pos.z);const sc=Math.max(.4,1-L.jy*.25);props.shadow.scale.setScalar(sc)}
  animChar(L,walking,dt,t);if(L.jy>0){L.g.position.y+=L.jy;L.lLeg.rotation.x=-.5;L.rLeg.rotation.x=.4;L.lArm.rotation.x=-2.4;L.rArm.rotation.x=-2.4}
  // tom follows
  const Tm=chars.tom,tp=Tm.g.position,dv=new T.Vector3().subVectors(pos,tp);dv.y=0;const dd=dv.length();let tw=false;
  if(dd>3.2&&started){dv.normalize();tp.addScaledVector(dv,3.6*dt);Tm.g.rotation.y=Math.atan2(dv.x,dv.z);tw=true}else if(started){Tm.g.rotation.y+= (Math.atan2(dv.x,dv.z)-Tm.g.rotation.y)*.05}
  animChar(Tm,tw,dt,t+1);animChar(chars.rolinda,false,dt,t+2);
  marker.material.opacity*=.985;marker.rotation.z+=dt*2;
  // camera
  const asp=$("stage").clientWidth/$("stage").clientHeight;const port=Math.min(1.5,Math.max(1,1.15/asp));const lv=chars.lotte.vel||new T.Vector3();const cp=new T.Vector3(pos.x*.55+lv.x*.4,16*port,pos.z*.55+18*port+lv.z*.4);camera.position.lerp(cp,.06);const lk=new T.Vector3(pos.x*.65,.8,pos.z*.65-1);camera.lookAt(lk);
  // water
  const a=wGeo.attributes.position.array;for(let i=0;i<a.length;i+=3){a[i+1]=Math.sin(wBase[i]*.35+t*1.3)*.16+Math.cos(wBase[i+2]*.3+t*1.1)*.16}wGeo.attributes.position.needsUpdate=true;wGeo.computeVertexNormals();
  clouds.forEach(c=>{c.position.x+=c.userData.v*dt;if(c.position.x>50)c.position.x=-50});
  // props
  const P=props;if(P.boat){P.boat.rotation.z=Math.sin(t*1.3)*.06;P.boat.rotation.x=Math.sin(t*.9)*.04;P.boat.position.y=-1.35+Math.sin(t*1.5)*.08}
  if(P.boat2){const a=t*.12;P.boat2.position.set(Math.cos(a)*34,-1.35+Math.sin(t*1.4)*.08,Math.sin(a)*34);P.boat2.rotation.y=-a-Math.PI/2;P.boat2.rotation.z=Math.sin(t*1.2)*.05}
  if(P.plane2){const a=t*.25;P.plane2.position.set(Math.cos(a)*30,15+Math.sin(t*.7)*1.2,Math.sin(a)*30);P.plane2.rotation.y=-a-Math.PI/2;P.plane2.rotation.z=.25;P.plane2.userData.prop.rotation.x+=dt*40}
  if(P.plane)P.plane.userData.prop.rotation.x+=dt*6;
  if(P.windmill)P.windmill.userData.blades.rotation.z+=dt*1.2;
  if(P.balloon){P.balloon.position.y=7+Math.sin(t*.6)*.5;P.balloon.position.x=-15+Math.sin(t*.15)*3;P.balloon.rotation.y=t*.1}
  if(P.birds)P.birds.forEach(b=>{const o=b.userData.o,a=t*.5+o;b.position.set(Math.cos(a)*(12+o*1.5),9+o*.5+Math.sin(t*2+o)*.4,Math.sin(a)*(12+o*1.5)-4);b.rotation.y=-a;const f=Math.sin(t*10+o)*.6;b.userData.w1.rotation.z=f;b.userData.w2.rotation.z=-f});
  if(P.fountain)P.fountain.userData.drops.forEach(d=>{const u=(t*.9+d.userData.p)%1;d.position.set(Math.cos(d.userData.p*6.28)*u*1.1,1.8+Math.sin(u*Math.PI)*1.4-u*.6,Math.sin(d.userData.p*6.28)*u*1.1)});
  if(P.lighthouse){const nt=skyN>=4;P.lighthouse.userData.beam.rotation.y=t*.8;P.lighthouse.userData.beamM.material.opacity=nt?.18:0;P.lighthouse.userData.lamp.material.emissiveIntensity=nt?2:0}
  if(P.tumble){const a=t*.35;P.tumble.position.set(Math.cos(a)*11,.6,Math.sin(a)*11);P.tumble.rotation.x+=dt*3;P.tumble.rotation.z+=dt*2}
  if(P.snow){const a=P.snow.geometry.attributes.position.array;for(let i=1;i<a.length;i+=3){a[i]-=dt*2.2;a[i-1]+=Math.sin(t+i)*dt*.6;if(a[i]<0)a[i]=20}P.snow.geometry.attributes.position.needsUpdate=true}
  if(P.embers){const a=P.embers.geometry.attributes.position.array;for(let i=1;i<a.length;i+=3){a[i]+=dt*(1.5+(i%5)*.3);a[i-1]+=Math.sin(t*2+i)*dt*.8;if(a[i]>16)a[i]=6}P.embers.geometry.attributes.position.needsUpdate=true}
  if(P.aurora){const a=P.aurora.geometry.attributes.position.array,b=P.auroraBase;for(let i=0;i<a.length;i+=3){a[i+1]=b[i+1]+Math.sin(b[i]*.15+t*.8)*2.5;a[i+2]=b[i+2]+Math.cos(b[i]*.1+t*.5)*1.5}P.aurora.geometry.attributes.position.needsUpdate=true;P.aurora.material.opacity=skyN>=4?.35+Math.sin(t*.7)*.1:0;P.aurora.material.color.setHSL(.4+Math.sin(t*.2)*.1,.8,.55)}
  if(P.volcano)P.volcano.userData.smoke.forEach(m=>{const u=(t*.25+m.userData.o*.125)%1;m.position.set(Math.sin(u*6+m.userData.o)*u*2,7.5+u*7,Math.cos(u*5)*u*2);m.scale.setScalar(.5+u*2);m.material.opacity=.55*(1-u)});
  if(P.lamps)P.lamps.forEach((l,i)=>{l.material.emissiveIntensity=skyN>=3?1.2+Math.sin(t*3+i)*.3:0});
  // plots pulse & buildings
  plots.forEach((p,i)=>{const k=i+1,locked=k>1&&!S.done.includes(k-1);p.userData.ring.material.opacity=locked?.15:.55+Math.sin(t*3+i)*.3;p.userData.ring.scale.setScalar(1+Math.sin(t*3+i)*.04)});
  for(const k in builds){const g=builds[k];if(g.userData.popT!==undefined){g.userData.popT+=dt;const x=Math.min(1,g.userData.popT/.9);const s=1+Math.sin(x*Math.PI*1.5)*(1-x)*.35;g.scale.setScalar(x<1?Math.max(.01,x*x*(3-2*x))*s:1);if(x>=1)delete g.userData.popT}
    if(g.userData.spin){g.userData.spin.rotation.y+=dt;g.userData.spin.position.y=1.6+Math.sin(t*2)*.2}
    if(g.userData.flag)g.userData.flag.rotation.y=Math.sin(t*4)*.35;
    if(g.userData.orbs)g.userData.orbs.forEach((o,j)=>{o.position.y+=Math.sin(t*2+j)*.004});
    if(g.userData.blink)g.userData.blink.material.emissiveIntensity=1+Math.sin(t*4)*1;
    if(g.userData.gear)g.userData.gear.rotation.z+=dt*1.5;
    if(g.userData.smoke)g.userData.smoke.forEach(m=>{const u=(t*.4+m.userData.o*.2)%1;m.position.y=3.6+u*3;m.scale.setScalar(.6+u*1.2);m.material.opacity=.6*(1-u)})}
  parts.forEach((m,i)=>{m.userData.life-=dt;m.position.addScaledVector(m.userData.v,dt);m.userData.v.y-=(m.userData.dust?4:9)*dt;if(m.userData.dust)m.material.opacity=Math.max(0,m.userData.life*1.4);m.rotation.x+=dt*4;m.rotation.y+=dt*3;if(m.userData.life<=0){scene.remove(m);parts.splice(i,1)}});
  // sky
  if(skyT<1){skyT=Math.min(1,skyT+dt*.5);const c=skyFrom.clone().lerp(skyTo,skyT);scene.background=c;scene.fog.color.copy(c)}
  const n=skyN;const day=Math.max(0,1-n/4);dirL.intensity=.2+day*.95;hemiL.intensity=.12+day*.6;ambL.intensity=.04+day*.12;stars.material.opacity=Math.max(0,(n-3)/3);
  sunM.position.set(-30+n*14,26-n*6,-50);sunM.visible=n<4;moonM.position.set(30,26,-50);moonM.visible=n>=4;
  builds.inn.userData.light.intensity=n>=3?1.6:0;
  // proximity
  if(started){const np=nearestPlot();const k=np.i+1,locked=k>1&&!S.done.includes(k-1),done=S.done.includes(k);
    const allDone=S.done.length===8,nearInn=Math.hypot(pos.x,pos.z)<4.2;
    let nm=null,nd=99;(props.mentors||[]).forEach(c=>{const d=c.g.position.distanceTo(pos);if(d<nd){nd=d;nm=c}});
    (props.mentors||[]).forEach(c=>{c.g.position.y=Math.sin(t*2+c.g.position.x)*.03;c.head.rotation.y=Math.sin(t*.7+c.g.position.z)*.2;c.ring.scale.setScalar(1+Math.sin(t*3)*.05)});
    if(nm&&nd<2.4){nearK="m:"+nm.id;$("enterbtn").textContent="Talk to "+MENTORS.find(m=>m.id===nm.id).name.split(" ").slice(-1)[0];$("enter").classList.add("on")}
    else if(allDone&&nearInn){nearK=9;$("enterbtn").textContent=S.world==="campus"?"Calendar alignment":"Evening complete";$("enter").classList.add("on")}
    else if(np.d<2.6&&!locked){nearK=k;$("enterbtn").textContent=(done?"Revisit ":"Enter ")+CH[np.i].n;$("enter").classList.add("on");if(!done&&lastSay!=="near"){say("near");lastSay="near"}}
    else{nearK=0;$("enter").classList.remove("on")}}
  renderer.render(scene,camera);
}
function animChar(c,walking,dt,t){
  if(walking){c.walkT+=dt*11;const s=Math.sin(c.walkT);c.lLeg.rotation.x=s*.7;c.rLeg.rotation.x=-s*.7;c.lArm.rotation.x=-s*.6;if(!c.raised)c.rArm.rotation.x=s*.6;c.g.position.y=Math.abs(Math.sin(c.walkT))*.08}
  else{c.lLeg.rotation.x*=.85;c.rLeg.rotation.x*=.85;c.lArm.rotation.x=Math.sin(t*2)*.08;if(!c.raised)c.rArm.rotation.x=-Math.sin(t*2)*.08;c.g.position.y=Math.sin(t*2)*.03}
  c.head.rotation.y=Math.sin(t*.7)*.15;
}

/* ---------------- UI ---------------- */
function hud(){$("hud-name").textContent=S.name+" · "+CAMPAIGN[S.world||"campus"].title.split(":")[0];$("hud-runes").innerHTML=[1,2,3,4,5,6,7,8].map(k=>`<i class="${S.done.includes(k)?'on':''}"></i>`).join("");
  $("k1").textContent=S.done.length*13+S.versions.length*2;$("k2").textContent=Math.round(S.done.length/8*100)+"%";$("k3").textContent=Object.values(S.bridges).filter(Boolean).length}
