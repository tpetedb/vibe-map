// Course order stays complete in the overview and list. The local view gives
// the next few lessons enough room to be distinct, touchable destinations.
function galaxyRoute(visuals,model,at){
  const narrow=innerWidth<=620,count=narrow?5:12;
  const next=Math.max(0,model.topics.findIndex(t=>t.id===(at||(model.next||{}).id)));
  const start=Math.max(0,Math.min(model.topics.length-count,next-(narrow?1:3))),end=Math.min(model.topics.length,start+count);
  const nodes=model.topics.map((topic,i)=>{
    const u=i-start;
    const position=narrow?[Math.sin(u*.9)*1.15,(count-1-u)*1.22,0]:[u*1.15,Math.sin(u*.53)*1.15+u*.10,0];
    return {...topic,position,visible:i>=start&&i<end};
  });
  const visible=nodes.filter(n=>n.visible),root=visuals.makeJourney(visible);
  root.userData={courseRoute:true,start,end,narrow};
  nodes.forEach((node,i)=>{const point=new T.Group();point.position.set(...node.position);point.visible=node.visible;
    point.userData={topicId:node.id,placeId:node.place,state:node.state,order:i+1};root.add(point)});
  for(const state of ['done','next','ahead']){
    const batch=visible.filter(node=>node.state===state);if(!batch.length)continue;
    const geometry=state==='next'?new T.OctahedronGeometry(.19):state==='done'?new T.BoxGeometry(.23,.23,.12):new T.TorusGeometry(.13,.035,8,20);
    const color=visuals.stateColor(state),mesh=new T.InstancedMesh(geometry,mat(color,{emissive:color,emissiveIntensity:.75}),batch.length);
    batch.forEach((node,i)=>mesh.setMatrixAt(i,new T.Matrix4().makeTranslation(...node.position)));root.add(mesh);
  }
  // Each nearby world is the actual primary place of a bead in this window.
  const groups=new Map();visible.forEach(node=>{if(!groups.has(node.place))groups.set(node.place,[]);groups.get(node.place).push(node)});
  const places=[...new Set([model.topics[next].place,visible[visible.length-1].place,visible[0].place,...groups.keys()])].slice(0,narrow?2:3);
  places.forEach((id,i)=>{
    const place=model.places.find(p=>p.id===id),samples=groups.get(id),anchor=samples[Math.floor(samples.length/2)];
    const planet=visuals.makePlanet([place],{states:{[id]:place.state},domeScale:.5});
    galaxyOrient(planet,place);planet.root.scale.setScalar(i===0?(narrow?.9:1.16):(narrow?.66:.85));
    planet.root.position.set(anchor.position[0]+(narrow?(i%2?1.2:-1.2):0),anchor.position[1]+(narrow?-.35:(i===0?1.75:-1.5)),-.75);
    planet.root.userData.routePlace=id;root.add(planet.root);
    const from=new T.Vector3(...anchor.position),to=planet.root.position.clone(),mid=from.clone().lerp(to,.5);mid.z-=.25;
    const tether=new T.Line(new T.BufferGeometry().setFromPoints(new T.QuadraticBezierCurve3(from,mid,to).getPoints(24)),new T.LineBasicMaterial({color:PALETTE.blueBright,transparent:true,opacity:.5}));root.add(tether);
  });
  return root;
}
function galaxyOrient(planet,place){
  planet.root.rotation.set(0,0,0);
  if(place.globe==='earth'){
    // Yaw around the geographic pole, then pitch the chosen latitude into view.
    const yaw=new T.Quaternion().setFromAxisAngle(new T.Vector3(0,1,0),-(place.lon+90)*Math.PI/180);
    const pitch=new T.Quaternion().setFromAxisAngle(new T.Vector3(1,0,0),place.lat*Math.PI/180-.28);
    planet.root.quaternion.copy(pitch).multiply(yaw);
  }else{
    const site=planet.sites.find(s=>s.id===place.id);if(site)planet.root.quaternion.setFromUnitVectors(site.normal,new T.Vector3(0,.35,1).normalize());
  }
}
function galaxyRouteWindow(topicId){const state=galaxyState;if(!state||!state.visuals||state.view!=='journey')return;
  const node=state.journey.children.find(n=>n.userData.topicId===topicId);
  if(node&&node.visible)return;
  discard(state.journey);state.journey=galaxyRoute(state.visuals,state.model,topicId);scene.add(state.journey);galaxyOverview(state.model);galaxyFrame();
}
function galaxyOverview(model){
  const box=$('galaxy-overview');if(!box)return;
  const svg=document.createElementNS('http://www.w3.org/2000/svg','svg');svg.setAttribute('viewBox','0 0 320 44');svg.setAttribute('aria-hidden','true');
  const points=model.topics.map((topic,i)=>({topic,x:8+i*304/Math.max(1,model.topics.length-1),y:22+Math.sin(i/Math.max(1,model.topics.length-1)*Math.PI*2)*11}));
  const line=document.createElementNS(svg.namespaceURI,'polyline');line.setAttribute('points',points.map(p=>p.x+','+p.y).join(' '));line.setAttribute('class','galaxy-overview-line');svg.append(line);
  points.forEach(({topic,x,y})=>{const dot=document.createElementNS(svg.namespaceURI,'circle');dot.setAttribute('cx',x);dot.setAttribute('cy',y);dot.setAttribute('r',topic.state==='next'?4:1.7);dot.setAttribute('data-state',topic.state);svg.append(dot)});
  const range=document.createElement('span');range.className='small muted';const route=galaxyState.journey;
  range.textContent=route?'Nearby '+(route.userData.start+1)+' to '+route.userData.end+' · Full course above':'';
  box.replaceChildren(svg,range);box.hidden=galaxyState.view!=='journey';
}
function galaxyProject(position){const box=$('c').getBoundingClientRect(),p=position.clone().project(camera);return {x:box.left+(p.x+1)*box.width/2,y:box.top+(1-p.y)*box.height/2}}
window.__galaxyRoute=()=>galaxyState&&galaxyState.journey?galaxyState.journey.children.filter(n=>n.visible&&n.userData.topicId).map(n=>({...galaxyProject(n.getWorldPosition(new T.Vector3())),...n.userData,hitRadius:22})):[];
function galaxyPickTopic(x,y){return window.__galaxyRoute().map(p=>({...p,d:Math.hypot(p.x-x,p.y-y)})).filter(p=>p.d<=22).sort((a,b)=>a.d-b.d)[0]}
function galaxyLabel(){const label=$('galaxy-label'),state=galaxyState;if(!label||!state)return;if(!state.visuals||$('galaxy-ui').dataset.rendering==='list'){label.hidden=true;return}
  let point=null,text='',detail='';
  if(state.view==='journey'){
    const id=state.focusTopic||(state.model.next||{}).id,node=state.journey.children.find(n=>n.visible&&n.userData.topicId===id),topic=state.model.topics.find(t=>t.id===id);
    if(node&&topic){point=node.getWorldPosition(new T.Vector3());text=(topic.state==='next'?'Next · ':'')+topic.name;detail=state.model.places.find(p=>p.id===topic.place).name}
  }else if(['chart','globe'].includes(state.view)){
    const place=galaxySelected(),planet=state.planets[place.globe],site=planet.sites.find(s=>s.id===place.id);
    if(site){point=site.dome.getWorldPosition(new T.Vector3());text=place.name;detail=place.done+' of '+place.count+' topics complete'}
  }
  label.hidden=!point;if(!point)return;const p=galaxyProject(point),stage=$('stage').getBoundingClientRect();
  label.querySelector('b').textContent=text;label.querySelector('span').textContent=detail;
  label.style.left=Math.max(12,Math.min(stage.width-label.offsetWidth-12,p.x-stage.left-label.offsetWidth/2))+'px';label.style.top=Math.max(12,p.y-stage.top-64)+'px';
}
