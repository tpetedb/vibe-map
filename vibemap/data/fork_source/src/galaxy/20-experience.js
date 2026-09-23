/* ---------------- Galaxy experience ---------------- */
let galaxyState=null;
const GALAXY_POS={earth:[-3.35,0,0],datacentre:[0,.75,-.7],cloud:[3.35,0,0]};
function galaxyDone(){return Array.isArray(S.topics)?S.topics:[]}
function galaxyGroups(model){const groups={};model.places.forEach(place=>{(groups[place.globe]||(groups[place.globe]=[])).push(place)});return groups}
function galaxyCamera(view){const at=["journey","chart"].includes(view)?[0,5.5,14]:view==="globe"?[0,2.8,7]:[0,2.2,4.3];
  if(innerWidth<=620)at[2]=["journey","chart"].includes(view)?28:view==="globe"?11:8;
  camera.position.set(...at);camera.lookAt(0,0,0);camera.near=.05;camera.far=100;camera.updateProjectionMatrix()}
function galaxySelected(){if(!galaxyState)return null;return galaxyState.model.places.find(place=>place.id===galaxyState.selected)||galaxyState.model.places[0]}
function clearGalaxyFocus(){if(galaxyState&&galaxyState.focusRing){discard(galaxyState.focusRing);galaxyState.focusRing=null}}
window.galaxyFocus=function(id,on){if(!galaxyState)return;clearGalaxyFocus();if(!on)return;galaxyState.selected=id;
  const selected=galaxySelected(),ring=new T.Mesh(new T.TorusGeometry(galaxyState.view==="dome"?1.58:.48,.045,8,48),mat(PALETTE.yellow,{emissive:PALETTE.yellow,emissiveIntensity:1.1}));
  if(galaxyState.view==="dome")ring.rotation.x=Math.PI/2;
  else if(galaxyState.view==="journey"){const stop=galaxyState.journey.children.find(item=>item.userData.placeId===id);if(stop)ring.position.copy(stop.position);ring.lookAt(camera.position)}
  else{const planet=galaxyState.planets[selected.globe],site=planet&&planet.sites.find(item=>item.id===id);if(site)site.dome.getWorldPosition(ring.position);ring.lookAt(camera.position)}
  scene.add(ring);galaxyState.focusRing=ring};
function galaxyShow(view){if(!galaxyState)return;const state=galaxyState,selected=galaxySelected();state.view=view;
  clearGalaxyFocus();
  state.journey.visible=view==="journey";
  Object.entries(state.planets).forEach(([kind,planet])=>{const overview=view==="chart",chosen=kind===selected.globe;
    planet.root.visible=overview||(view==="globe"&&chosen);planet.root.position.set(...(overview?(GALAXY_POS[kind]||[0,0,0]):[0,0,0]));planet.root.scale.setScalar(overview?1.7:2.45);
    if(view==="globe"&&chosen){const site=planet.sites.find(item=>item.id===selected.id);if(site)planet.root.quaternion.setFromUnitVectors(site.normal,new T.Vector3(0,.37,1).normalize())}});
  if(state.detail){discard(state.detail);state.detail=null}
  if(view==="dome"&&selected){state.detail=state.visuals.makeDome(selected,selected.state);state.detail.scale.setScalar(1.45);state.detail.rotation.x=-.12;scene.add(state.detail)}
  galaxyCamera(view);
  // Keep the miniature clear of the list on desktop, above it on phones.
  if(innerWidth>620)camera.setViewOffset(innerWidth,innerHeight,-190,0,innerWidth,innerHeight);
  else camera.setViewOffset(innerWidth,innerHeight,0,innerHeight*.13,innerWidth,innerHeight);
  renderGalaxyList()}
window.galaxyView=function(view){if(["journey","chart","globe","dome"].includes(view))galaxyShow(view)};
window.galaxyKey=function(event){if(!galaxyState)return;const buttons=[...document.querySelectorAll("[data-galaxy-place]")],at=buttons.indexOf(event.currentTarget);
  if(["ArrowDown","ArrowRight","ArrowUp","ArrowLeft"].includes(event.key)){event.preventDefault();const step=["ArrowDown","ArrowRight"].includes(event.key)?1:-1;buttons[(at+step+buttons.length)%buttons.length].focus()}
  else if(event.key==="Escape"){event.preventDefault();galaxyShow("chart");document.querySelector('[data-galaxy-view="chart"]').focus()}}
window.galaxyTopic=function(id){if(!galaxyState)return;const topic=galaxyState.model.topics.find(item=>item.id===id);if(!topic)return;
  galaxyState.topic=id;if(!galaxySelected().topics.some(t=>t.id===id))galaxyState.selected=topic.place;galaxyShow("dome");openTopic(id)};
window.galaxyPlace=function(id){if(!galaxyState||!galaxyState.model.places.some(place=>place.id===id))return;
  galaxyState.selected=id;const topic=galaxySelected().topics[0];galaxyState.topic=topic?topic.id:null;galaxyShow("dome")};
function renderGalaxyList(){const ui=$("galaxy-ui");if(!ui)return;ui.hidden=false;
  const state=galaxyState,model=state?state.model:galaxyModel(PLACES,TREE,galaxyDone()),selected=state?galaxySelected():model.places[0];
  $("galaxy-title").textContent=selected?selected.name:"Galaxy";
  $("galaxy-summary").textContent=model.topics.filter(topic=>topic.state==="done").length+" of "+model.topics.length+" topics complete";
  $("galaxy-next").textContent=model.next?"Next: "+model.next.name+" · "+model.places.find(p=>p.id===model.next.place).name:"Journey complete";
  $("galaxy-context").textContent=state&&state.view==="dome"?selected.name+" · "+selected.topics[0].year+". "+selected.topics[0].what:"Course order · Square: done · Diamond: next · Ring: ahead";
  const places=Object.fromEntries(model.places.map(place=>[place.id,place]));
  if(state&&state.view==="chart")$("galaxy-list").innerHTML=model.eras.map(era=>`<section class="galaxy-era" role="listitem"><h3>${esc(era.name)}</h3>${model.places.filter(place=>place.era===era.id).map(place=>`<div class="galaxy-place" data-state="${place.state}"><b>${esc(place.name)}</b><span class="galaxy-state">${place.state} · ${place.done} of ${place.count}</span><button data-galaxy-place="${place.id}"${place.id===selected.id?' aria-current="location"':""} onkeydown="galaxyKey(event)" onfocus="galaxyFocus('${place.id}',true)" onblur="galaxyFocus('${place.id}',false)" onclick="galaxyPlace('${place.id}')">Land</button></div>`).join("")}</section>`).join("");
  else $("galaxy-list").innerHTML=(state&&["dome","globe"].includes(state.view)?selected.topics:model.topics).map(topic=>{const place=places[topic.place];return `<div class="galaxy-place" role="listitem" data-state="${topic.state}"><b>${model.topics.findIndex(item=>item.id===topic.id)+1}. ${esc(topic.name)}</b><span class="galaxy-state">${topic.state} · ${topic.year} · ${esc(place.name)}</span><button data-galaxy-topic="${topic.id}" data-galaxy-place="${place.id}"${topic.state==="next"?' aria-current="step"':""} onkeydown="galaxyKey(event)" onfocus="galaxyFocus('${place.id}',true)" onblur="galaxyFocus('${place.id}',false)" onclick="galaxyTopic('${topic.id}')">Learn</button></div>`}).join("");
  document.querySelectorAll("[data-galaxy-view]").forEach(button=>button.classList.toggle("on",state&&button.dataset.galaxyView===state.view))}
function announceExperience(){const name=activeExperience().name;document.body.dataset.experience=experienceId();copySay(name+" experience shown")}
let galaxyDown=null;
$("c").addEventListener("pointerdown",event=>{if(experienceId()==="galaxy")galaxyDown=[event.clientX,event.clientY]});
$("c").addEventListener("pointerup",event=>{if(experienceId()!=="galaxy"||!galaxyState||!galaxyDown)return;
  const moved=Math.hypot(event.clientX-galaxyDown[0],event.clientY-galaxyDown[1]);galaxyDown=null;if(moved>10)return;
  const box=$("c").getBoundingClientRect(),pointer=new T.Vector2((event.clientX-box.left)/box.width*2-1,-(event.clientY-box.top)/box.height*2+1),pick=new T.Raycaster();pick.setFromCamera(pointer,camera);
  // Decorative route lines and hidden globes must never steal a destination tap.
  let node=null;
  for(const hit of pick.intersectObjects(scene.children.filter(item=>item.visible),true)){
    let candidate=hit.object;while(candidate&&candidate!==scene&&!candidate.userData.topicId&&!candidate.userData.placeId&&!candidate.userData.globe)candidate=candidate.parent;
    if(candidate&&candidate!==scene){node=candidate;break}
  }
  if(node&&node.userData.topicId)galaxyTopic(node.userData.topicId);
  else if(node&&node.userData.placeId)galaxyPlace(node.userData.placeId);
  else if(node&&node.userData.globe){const place=(galaxyState.groups[node.userData.globe]||[])[0];if(place)galaxyPlace(place.id)}});
EXPERIENCES.galaxy={
  name:"Galaxy",
  build(){const model=galaxyModel(PLACES,TREE,galaxyDone()),groups=galaxyGroups(model),visuals=createGalaxyVisuals({three:T,palette:PALETTE,material:mat,finish:fixColors});
    scene=new T.Scene();scene.background=new T.Color(PALETTE.black);scene.add(new T.AmbientLight(PALETTE.snow,.5));
    scene.add(new T.HemisphereLight(PALETTE.blueBright,PALETTE.orange,.35));
    const light=new T.DirectionalLight(PALETTE.snow,1.4);light.position.set(3,8,8);scene.add(light);
    const rim=new T.PointLight(PALETTE.yellow,.7,18);rim.position.set(-5,3,-3);scene.add(rim);
    const planets={};Object.entries(groups).forEach(([kind,places])=>{const planet=visuals.makePlanet(places,{states:Object.fromEntries(places.map(p=>[p.id,p.state])),domeScale:.22});planet.root.position.set(...(GALAXY_POS[kind]||[0,0,0]));planet.root.scale.setScalar(1.7);scene.add(planet.root);planets[kind]=planet});
    const journey=galaxyRoute(visuals,model);scene.add(journey);galaxyState={model,groups,visuals,planets,journey,progress:JSON.stringify(galaxyDone()),detail:null,focusRing:null,topic:(model.next||{}).id||null,selected:(model.next||model.places[0]||{}).place||(model.places[0]||{}).id,view:"journey"};
    document.body.dataset.experience="galaxy";galaxyShow("journey");renderGalaxyList()},
  dispose(){camera.clearViewOffset();const ui=$("galaxy-ui");if(ui)ui.hidden=true;if(scene){release(scene);scene=null}galaxyState=null;document.body.dataset.experience="islands"},
  tick(dt,t){if(!galaxyState)return;galaxyRefresh();if(reducedMotion()||galaxyState.view==="globe")return;Object.values(galaxyState.planets).forEach((planet,i)=>{planet.root.rotation.y=t*(.035+i*.008)})},
  goTo(to){if(!to||!to.place)return false;galaxyPlace(to.place);return true},
  where(){const place=galaxySelected();return place?{kind:"place",id:place.id}:null},
  listing(){const model=galaxyModel(PLACES,TREE,galaxyDone()),places=Object.fromEntries(model.places.map(place=>[place.id,place]));return model.topics.map(topic=>({id:topic.id,title:topic.name,place:topic.place,placeTitle:places[topic.place].name,year:topic.year,state:topic.state}))},
};

// Progress can arrive through any shared entry point, including import while
// motion is off. Rebuild only when the record changes, preserving navigation.
function galaxyRefresh(){const state=galaxyState,key=JSON.stringify(galaxyDone());if(key===state.progress)return;
  state.progress=key;state.model=galaxyModel(PLACES,TREE,galaxyDone());state.groups=galaxyGroups(state.model);
  discard(state.journey);state.journey=galaxyRoute(state.visuals,state.model);scene.add(state.journey);
  Object.entries(state.groups).forEach(([kind,places])=>{discard(state.planets[kind].root);
    const planet=state.visuals.makePlanet(places,{states:Object.fromEntries(places.map(p=>[p.id,p.state])),domeScale:.22});
    state.planets[kind]=planet;scene.add(planet.root)});
  const focused=document.activeElement,topic=focused&&focused.dataset.galaxyTopic;
  galaxyShow(state.view);if(topic){const button=[...document.querySelectorAll("[data-galaxy-topic]")].find(b=>b.dataset.galaxyTopic===topic);if(button)button.focus()}
}
function galaxyRoute(visuals,model){
  const cols=10,rows=Math.ceil(model.topics.length/cols);
  const nodes=model.topics.map((topic,i)=>{const row=Math.floor(i/cols),col=row%2?cols-1-i%cols:i%cols;
    return {...topic,position:[(col-(cols-1)/2)*.78,(rows-1-row)*.68-1.7,0]}});
  const root=visuals.makeJourney(nodes);root.userData.courseRoute=true;
  nodes.forEach((node,i)=>{
    const color=node.state==="done"?PALETTE.greenBright:node.state==="next"?PALETTE.yellow:PALETTE.muted;
    const group=new T.Group();group.position.set(...node.position);group.userData={topicId:node.id,placeId:node.place,state:node.state,order:i+1};
    const shape=node.state==="next"?new T.OctahedronGeometry(.16):node.state==="done"?new T.BoxGeometry(.20,.20,.10):new T.TorusGeometry(.11,.023,6,16);
    group.add(new T.Mesh(shape,mat(color,{emissive:color,emissiveIntensity:.6})));
    const canvas=document.createElement("canvas");canvas.width=128;canvas.height=64;const ctx=canvas.getContext("2d");
    ctx.fillStyle="#"+new T.Color(PALETTE.snow).getHexString();ctx.font="bold 36px sans-serif";ctx.textAlign="center";ctx.fillText(String(i+1),64,44);
    const texture=new T.CanvasTexture(canvas),label=new T.Sprite(new T.SpriteMaterial({map:texture,depthTest:false}));label.scale.set(.42,.21,1);label.position.y=.28;group.add(label);root.add(group);
  });return root;
}

addEventListener("resize",()=>{if(galaxyState)galaxyShow(galaxyState.view)});

// Read-only projected route for entry-point browser tests and framing checks.
window.__galaxyRoute=()=>galaxyState?galaxyState.journey.children.filter(item=>item.userData.topicId).map(item=>{
  const point=item.getWorldPosition(new T.Vector3()).project(camera),box=$("c").getBoundingClientRect();
  return {x:box.left+(point.x+1)*box.width/2,y:box.top+(1-point.y)*box.height/2,state:item.userData.state};
}):[];
