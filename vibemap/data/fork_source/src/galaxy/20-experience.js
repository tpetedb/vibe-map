/* ---------------- Galaxy experience ---------------- */
let galaxyState=null;
const GALAXY_POS={earth:[-3.35,0,0],datacentre:[0,.75,-.7],cloud:[3.35,0,0]};
function galaxyDone(){return Array.isArray(S.topics)?S.topics:[]}
function galaxyGroups(model){const groups={};model.places.forEach(place=>{(groups[place.globe]||(groups[place.globe]=[])).push(place)});return groups}
function galaxyCamera(view){const at=view==="journey"?[0,5.5,14]:view==="globe"?[0,2.8,7]:[0,2.2,4.3];
  camera.position.set(...at);camera.lookAt(0,0,0);camera.near=.05;camera.far=100;camera.updateProjectionMatrix()}
function galaxySelected(){if(!galaxyState)return null;return galaxyState.model.places.find(place=>place.id===galaxyState.selected)||galaxyState.model.places[0]}
function clearGalaxyFocus(){if(galaxyState&&galaxyState.focusRing){discard(galaxyState.focusRing);galaxyState.focusRing=null}}
window.galaxyFocus=function(id,on){if(!galaxyState)return;clearGalaxyFocus();if(!on)return;galaxyState.selected=id;
  const selected=galaxySelected(),ring=new T.Mesh(new T.TorusGeometry(galaxyState.view==="dome"?1.58:.48,.045,8,48),mat(PALETTE.yellow,{emissive:PALETTE.yellow,emissiveIntensity:1.1}));
  if(galaxyState.view==="dome")ring.rotation.x=Math.PI/2;
  else{const planet=galaxyState.planets[selected.globe],site=planet&&planet.sites.find(item=>item.id===id);if(site)site.dome.getWorldPosition(ring.position);ring.lookAt(camera.position)}
  scene.add(ring);galaxyState.focusRing=ring};
function galaxyShow(view){if(!galaxyState)return;const state=galaxyState,selected=galaxySelected();state.view=view;
  clearGalaxyFocus();
  state.journey.visible=view==="journey";
  Object.entries(state.planets).forEach(([kind,planet])=>{const journey=view==="journey",chosen=kind===selected.globe;
    planet.root.visible=journey||(view==="globe"&&chosen);planet.root.position.set(...(journey?(GALAXY_POS[kind]||[0,0,0]):[0,0,0]));planet.root.scale.setScalar(journey?1.7:2.45)});
  if(state.detail){discard(state.detail);state.detail=null}
  if(view==="dome"&&selected){state.detail=state.visuals.makeDome(selected,selected.state);state.detail.scale.setScalar(1.45);state.detail.rotation.x=-.12;scene.add(state.detail)}
  galaxyCamera(view);renderGalaxyList()}
window.galaxyView=function(view){if(["journey","globe","dome"].includes(view))galaxyShow(view)};
window.galaxyPlace=function(id){if(!galaxyState||!galaxyState.model.places.some(place=>place.id===id))return;
  galaxyState.selected=id;galaxyShow("dome");const row=document.querySelector(`[data-galaxy-place="${id}"]`);if(row)row.focus()};
function renderGalaxyList(){const ui=$("galaxy-ui");if(!ui)return;ui.hidden=false;
  const state=galaxyState,model=state?state.model:galaxyModel(PLACES,TREE,galaxyDone()),selected=state?galaxySelected():model.places[0];
  $("galaxy-title").textContent=selected?selected.name:"Galaxy";
  $("galaxy-summary").textContent=model.topics.filter(topic=>topic.state==="done").length+" of "+model.topics.length+" topics complete";
  const places=Object.fromEntries(model.places.map(place=>[place.id,place]));
  $("galaxy-list").innerHTML=model.topics.map(topic=>{const place=places[topic.place];return `<div class="galaxy-place" role="listitem" data-state="${topic.state}"><b>${esc(topic.name)}</b><span class="galaxy-state">${topic.state} · ${topic.year} · ${esc(place.name)}</span><button data-galaxy-place="${place.id}"${topic.state==="next"?' aria-current="step"':""} onfocus="galaxyFocus('${place.id}',true)" onblur="galaxyFocus('${place.id}',false)" onclick="galaxyPlace('${place.id}')">Show</button></div>`}).join("");
  document.querySelectorAll("[data-galaxy-view]").forEach(button=>button.classList.toggle("on",state&&button.dataset.galaxyView===state.view))}
function announceExperience(){const name=activeExperience().name;document.body.dataset.experience=experienceId();copySay(name+" experience shown")}
let galaxyDown=null;
$("c").addEventListener("pointerdown",event=>{if(experienceId()==="galaxy")galaxyDown=[event.clientX,event.clientY]});
$("c").addEventListener("pointerup",event=>{if(experienceId()!=="galaxy"||!galaxyState||!galaxyDown)return;
  const moved=Math.hypot(event.clientX-galaxyDown[0],event.clientY-galaxyDown[1]);galaxyDown=null;if(moved>10)return;
  const box=$("c").getBoundingClientRect(),pointer=new T.Vector2((event.clientX-box.left)/box.width*2-1,-(event.clientY-box.top)/box.height*2+1),pick=new T.Raycaster();pick.setFromCamera(pointer,camera);
  const hit=pick.intersectObjects(scene.children,true)[0];if(!hit)return;let node=hit.object;
  while(node&&node!==scene&&!node.userData.placeId&&!node.userData.globe)node=node.parent;
  if(node&&node.userData.placeId)galaxyPlace(node.userData.placeId);
  else if(node&&node.userData.globe){const place=(galaxyState.groups[node.userData.globe]||[])[0];if(place)galaxyPlace(place.id)}});
EXPERIENCES.galaxy={
  name:"Galaxy",
  build(){const model=galaxyModel(PLACES,TREE,galaxyDone()),groups=galaxyGroups(model),visuals=createGalaxyVisuals({three:T,palette:PALETTE,material:mat,finish:fixColors});
    scene=new T.Scene();scene.background=new T.Color(PALETTE.black);scene.add(new T.AmbientLight(PALETTE.snow,1.15));
    scene.add(new T.HemisphereLight(PALETTE.blueBright,PALETTE.orange,.95));
    const light=new T.DirectionalLight(PALETTE.snow,2.5);light.position.set(3,8,8);scene.add(light);
    const rim=new T.PointLight(PALETTE.yellow,1.4,18);rim.position.set(-5,3,-3);scene.add(rim);
    const planets={};Object.entries(groups).forEach(([kind,places])=>{const planet=visuals.makePlanet(places,{states:Object.fromEntries(places.map(p=>[p.id,p.state])),domeScale:.22});planet.root.position.set(...(GALAXY_POS[kind]||[0,0,0]));planet.root.scale.setScalar(1.7);scene.add(planet.root);planets[kind]=planet});
    const kinds=Object.keys(planets),nodes=kinds.map(kind=>({position:GALAXY_POS[kind]||[0,0,0],state:groups[kind].some(p=>p.state==="next")?"next":groups[kind].every(p=>p.state==="done")?"done":"ahead"}));
    const journey=visuals.makeJourney(nodes);scene.add(journey);galaxyState={model,groups,visuals,planets,journey,detail:null,focusRing:null,selected:(model.next||model.places[0]||{}).place||(model.places[0]||{}).id,view:"journey"};
    document.body.dataset.experience="galaxy";galaxyShow("journey");renderGalaxyList()},
  dispose(){const ui=$("galaxy-ui");if(ui)ui.hidden=true;if(scene){release(scene);scene=null}galaxyState=null;document.body.dataset.experience="islands"},
  tick(dt,t){if(!galaxyState||reducedMotion())return;Object.values(galaxyState.planets).forEach((planet,i)=>{planet.root.rotation.y=t*(.035+i*.008)})},
  goTo(to){if(!to||!to.place)return false;galaxyPlace(to.place);return true},
  where(){const place=galaxySelected();return place?{kind:"place",id:place.id}:null},
  listing(){const model=galaxyModel(PLACES,TREE,galaxyDone()),places=Object.fromEntries(model.places.map(place=>[place.id,place]));return model.topics.map(topic=>({id:topic.id,title:topic.name,place:topic.place,placeTitle:places[topic.place].name,year:topic.year,state:topic.state}))},
};
