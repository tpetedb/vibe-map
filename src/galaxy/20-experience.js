/* ---------------- Galaxy experience ---------------- */
let galaxyState=null,galaxyCameraState=null;
const GALAXY_POS={earth:[-3.35,0,0],datacentre:[0,.75,-.7],cloud:[3.35,0,0]};
function galaxyDone(){return Array.isArray(S.topics)?S.topics:[]}
function galaxyGroups(model){const groups={};model.places.forEach(place=>{(groups[place.globe]||(groups[place.globe]=[])).push(place)});return groups}
function galaxyFallback(){if(!galaxyState){const model=galaxyModel(PLACES,TREE,galaxyDone());
  galaxyState={model,groups:galaxyGroups(model),visuals:null,planets:{},journey:null,progress:JSON.stringify(galaxyDone()),selected:(model.next||{}).place||model.places[0].id,view:"journey"}}
  document.body.dataset.experience="galaxy";renderGalaxyList();return true}
function galaxySelected(){if(!galaxyState)return null;return galaxyState.model.places.find(place=>place.id===galaxyState.selected)||galaxyState.model.places[0]}
function clearGalaxyFocus(){if(galaxyState&&galaxyState.focusRing){discard(galaxyState.focusRing);galaxyState.focusRing=null}}
window.galaxyFocus=function(id,on,topicId){
  const state=galaxyState;if(!state)return;
  if(!on){state.focusTopic=null;if(state.view==="journey")clearGalaxyFocus();galaxyLabel();return}
  state.selected=id;if(topicId){state.topic=topicId;state.focusTopic=topicId;galaxyRouteWindow(topicId)}
  if(!state.visuals)return;clearGalaxyFocus();
  const selected=galaxySelected(),ring=new T.Mesh(new T.TorusGeometry(state.view==="journey"?.23:state.view==="dome"?1.58:.34,.025,8,48),mat(PALETTE.yellow,{emissive:PALETTE.yellow,emissiveIntensity:1}));
  ring.userData.focusTopic=topicId||null;
  if(state.view==="dome")ring.rotation.x=Math.PI/2;
  else if(state.view==="journey"){const stop=state.journey.children.find(item=>item.userData.topicId===topicId);if(stop)ring.position.copy(stop.position);ring.lookAt(camera.position)}
  else{const planet=state.planets[selected.globe],site=planet&&planet.sites.find(item=>item.id===id);if(site){site.dome.getWorldPosition(ring.position);ring.userData.anchor=site.dome}ring.lookAt(camera.position)}
  scene.add(ring);state.focusRing=ring;galaxyLabel();galaxyRenderCheck();
};
function galaxyShow(view){if(!galaxyState)return;const state=galaxyState,selected=galaxySelected();const carry=galaxyWalk&&galaxyWalk.place===selected.id?[galaxyWalk.anchor.position.x,galaxyWalk.anchor.position.z]:null;state.view=view;state.tappedTopic=null;galaxyWalkStop();
  if(!state.visuals){state.model=galaxyModel(PLACES,TREE,galaxyDone());renderGalaxyList();return}
  clearGalaxyFocus();
  state.journey.visible=view==="journey";
  Object.entries(state.planets).forEach(([kind,planet])=>{const overview=view==="chart",chosen=kind===selected.globe;
    planet.root.visible=overview||(view==="globe"&&chosen);planet.root.position.set(...(overview?(GALAXY_POS[kind]||[0,0,0]):[0,0,0]));planet.root.scale.setScalar(overview?1.7:2.45);
    planet.root.rotation.set(0,0,0);if(view==="globe"&&chosen)galaxyOrient(planet,selected)});
  if(state.detail){discard(state.detail);state.detail=null}
  if(view==="dome"&&selected){
    state.detail=new T.Group();state.detail.add(state.visuals.makeDome(selected,selected.state,buildMiniature));
    const world=state.visuals.makePlanet([selected],{states:{[selected.id]:selected.state},domeScale:.01});
    world.root.userData.placeId=selected.id;world.sites.forEach(site=>site.dome.visible=false);world.root.scale.setScalar(.94);world.root.position.y=-.98;
    world.root.quaternion.setFromUnitVectors(world.sites[0].normal,new T.Vector3(0,1,0));state.detail.add(world.root);
    state.detail.scale.setScalar(1.45);state.detail.rotation.x=-.12;scene.add(state.detail);galaxyWalkStart(state.detail,carry)}
  renderGalaxyList();galaxyFrame();if(["chart","globe"].includes(view))galaxyFocus(selected.id,true);requestAnimationFrame(()=>{galaxyFrame();galaxyLabel()})}
window.galaxyView=function(view){if(!["journey","chart","globe","dome"].includes(view))return;
  const state=galaxyState;if(state&&view==="journey"&&state.model.next){state.topic=state.model.next.id;state.selected=state.model.next.place;state.focusTopic=null;
    if(state.visuals){discard(state.journey);state.journey=galaxyRoute(state.visuals,state.model);scene.add(state.journey)}}galaxyShow(view)};
window.galaxyKey=function(event){if(!galaxyState||$("vault").classList.contains("on"))return;const buttons=[...document.querySelectorAll("[data-galaxy-place]")],at=buttons.indexOf(event.currentTarget);
  if(["ArrowDown","ArrowRight","ArrowUp","ArrowLeft"].includes(event.key)){event.preventDefault();const step=["ArrowDown","ArrowRight"].includes(event.key)?1:-1;buttons[(at+step+buttons.length)%buttons.length].focus()}
  else if(event.key==="Escape"){event.preventDefault();galaxyShow("chart");document.querySelector('[data-galaxy-view="chart"]').focus()}}
window.galaxyTopic=function(id){const state=galaxyState;if(!state)return;
  const topic=state.model.topics.find(item=>item.id===id);if(!topic)return;
  state.topic=id;if(!galaxySelected().topics.some(t=>t.id===id))state.selected=topic.place;
  galaxyRenderCheck();openTopic(id);$("vnote").append(galaxyCheck(topic));
};
function galaxyCheck(topic){const section=document.createElement("section");section.className="galaxy-check";
  const heading=document.createElement("h3");heading.textContent="Try it, check it, bring it back";
  const text=document.createElement("p");text.textContent="Complete the lesson in your camp terminal, check it, then export your progress.";
  const command=document.createElement("pre");command.className="cmd";command.textContent="uv run vibe check --topic "+topic.id+"\nuv run vibe export";
  const button=document.createElement("button");button.textContent="Import progress";button.onclick=()=>{closeVault();openSheet("s-map");$("impcode").focus()};
  section.append(heading,text,command,button);wrapCommands(section);return section;
}
function galaxyRenderCheck(){const state=galaxyState;if(!state)return;const topic=state.model.topics.find(t=>t.id===state.topic)||state.model.next;
  const box=$("galaxy-check");box.replaceChildren();if(!topic)return;
  const details=document.createElement("details"),summary=document.createElement("summary");summary.textContent="Finish "+topic.name+": check and import";details.append(summary,galaxyCheck(topic));box.append(details);
}
window.galaxyPlace=function(id){if(!galaxyState||!galaxyState.model.places.some(place=>place.id===id))return;
  galaxyState.selected=id;const topic=galaxySelected().topics[0];galaxyState.topic=topic?topic.id:null;galaxyShow("dome")};
function renderGalaxyList(){const ui=$("galaxy-ui");if(!ui)return;ui.hidden=false;
  ui.dataset.rendering=galaxyState&&galaxyState.visuals&&$("stage").clientHeight>=520?"scene":"list";
  const state=galaxyState,model=state?state.model:galaxyModel(PLACES,TREE,galaxyDone()),selected=state?galaxySelected():model.places[0];
  $("galaxy-title").textContent=state.view==="journey"?"Your journey":state.view==="chart"?"Places in the course":selected?selected.name:"Galaxy";
  $("galaxy-summary").textContent=model.topics.filter(topic=>topic.state==="done").length+" of "+model.topics.length+" topics complete";
  $("galaxy-next").textContent=model.next?"Next: "+model.next.name+" · "+model.places.find(p=>p.id===model.next.place).name:"Journey complete";
  $("galaxy-context").textContent=state&&state.view==="dome"?selected.name+" · "+selected.topics[0].year+". "+selected.topics[0].what:"Course order · Square: done · Diamond: next · Ring: ahead";
  if(state&&state.view==="dome"&&selected.count>6)$("galaxy-context").textContent+=" · Six lesson pavilions shown. All "+selected.count+" topics are in the list.";
  if(!state||!state.visuals)$("galaxy-context").textContent+=" · 3D is unavailable. All destinations and lessons are available in this list.";
  const places=Object.fromEntries(model.places.map(place=>[place.id,place]));
  if(state&&state.view==="chart")$("galaxy-list").innerHTML=model.eras.map(era=>`<section class="galaxy-era" role="listitem"><h3>${esc(era.name)}</h3>${model.places.filter(place=>place.era===era.id).map(place=>`<div class="galaxy-place" data-state="${place.state}"><b>${esc(place.name)}</b><span class="galaxy-state">${place.state} · ${place.done} of ${place.count}</span><button data-galaxy-place="${place.id}"${place.id===selected.id?' aria-current="location"':""} onkeydown="galaxyKey(event)" onfocus="galaxyFocus('${place.id}',true)" onblur="galaxyFocus('${place.id}',false)" aria-label="Land at ${esc(place.name)}" onclick="galaxyPlace('${place.id}')">Land</button></div>`).join("")}</section>`).join("");
  else $("galaxy-list").innerHTML=(state&&["dome","globe"].includes(state.view)?selected.topics:model.topics).map(topic=>{const place=places[topic.place];return `<div class="galaxy-place" role="listitem" data-state="${topic.state}"><b>${model.topics.findIndex(item=>item.id===topic.id)+1}. ${esc(topic.name)}</b><span class="galaxy-state">${topic.state} · ${topic.year} · ${esc(place.name)}</span><button data-galaxy-topic="${topic.id}" data-galaxy-place="${place.id}"${topic.state==="next"?' aria-current="step"':""} onkeydown="galaxyKey(event)" onfocus="galaxyFocus('${place.id}',true,'${topic.id}')" onblur="galaxyFocus('${place.id}',false,'${topic.id}')" aria-label="Learn ${esc(topic.name)}" onclick="galaxyTopic('${topic.id}')">Learn</button></div>`}).join("");
  document.querySelectorAll("[data-galaxy-view]").forEach(button=>{const on=!!state&&button.dataset.galaxyView===state.view;button.classList.toggle("on",on);button.setAttribute("aria-pressed",String(on))});
  const buttons=[...$("galaxy-list").querySelectorAll("button")],current=buttons.find(b=>b.dataset.galaxyTopic===state.topic)||buttons.find(b=>b.hasAttribute("aria-current"))||buttons[0];buttons.forEach(b=>b.tabIndex=b===current?0:-1);
  galaxyRenderCheck();galaxyOverview(model);
}
let galaxyDown=null;
$("c").addEventListener("pointerdown",event=>{if(experienceId()==="galaxy")galaxyDown=[event.clientX,event.clientY]});
$("c").addEventListener("pointerup",event=>{if(experienceId()!=="galaxy"||!galaxyState||!galaxyState.visuals||!galaxyDown)return;
  const moved=Math.hypot(event.clientX-galaxyDown[0],event.clientY-galaxyDown[1]);galaxyDown=null;if(moved>10)return;
  if(galaxyState.view==="journey"){const point=galaxyPickTopic(event.clientX,event.clientY);if(point){if(galaxyState.tappedTopic===point.topicId)galaxyTopic(point.topicId);else{galaxyState.tappedTopic=point.topicId;galaxyFocus(point.placeId,true,point.topicId)}}return}
  const box=$("c").getBoundingClientRect(),pointer=new T.Vector2((event.clientX-box.left)/box.width*2-1,-(event.clientY-box.top)/box.height*2+1),pick=new T.Raycaster();pick.setFromCamera(pointer,camera);
  if(galaxyState.view==="dome"){document.activeElement.blur();galaxyWalkPick(pick,event.clientX,event.clientY);return}
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
  fallback:galaxyFallback,
  refresh:galaxyRefresh,
  layout:galaxyFrame,
  world(){galaxyShow("chart")},
  backLabel:"Back to Galaxy",
  presentation:{tagline:"Programming history, one place and one topic at a time.",intro:"Welcome to Galaxy. Follow the course journey through the places behind programming. Land on a tiny planet, open its lessons, and build your shared learning record.","btn-go":"Begin the journey","btn-continue":"Resume Galaxy"},
  guidance(){bubble("rolinda","Follow the course journey. Choose Learn to open a topic, or Chart to land at a place.")},
  build(){galaxyCameraState={fov:camera.fov,near:camera.near,far:camera.far,aspect:camera.aspect,view:camera.view?{...camera.view}:null};const model=galaxyModel(PLACES,TREE,galaxyDone()),groups=galaxyGroups(model),visuals=createGalaxyVisuals({three:T,palette:PALETTE,material:mat,finish:fixColors});
    scene=new T.Scene();scene.background=new T.Color(PALETTE.black);scene.add(galaxyStars());scene.add(new T.AmbientLight(PALETTE.snow,.5));
    scene.add(new T.HemisphereLight(PALETTE.blueBright,PALETTE.orange,.35));
    const light=new T.DirectionalLight(PALETTE.snow,1.4);light.position.set(3,8,8);scene.add(light);
    const rim=new T.PointLight(PALETTE.yellow,.7,18);rim.position.set(-5,3,-3);scene.add(rim);
    const planets={};Object.entries(groups).forEach(([kind,places])=>{const planet=visuals.makePlanet(places,{states:Object.fromEntries(places.map(p=>[p.id,p.state])),domeScale:.22});planet.root.position.set(...(GALAXY_POS[kind]||[0,0,0]));planet.root.scale.setScalar(1.7);scene.add(planet.root);planets[kind]=planet});
    const journey=galaxyRoute(visuals,model);scene.add(journey);galaxyState={model,groups,visuals,planets,journey,progress:JSON.stringify(galaxyDone()),detail:null,focusRing:null,topic:(model.next||{}).id||null,selected:(model.next||model.places[0]||{}).place||(model.places[0]||{}).id,view:"journey"};
    document.body.dataset.experience="galaxy";galaxyShow("journey");renderGalaxyList()},
  dispose(){galaxyWalkStop();if(camera&&galaxyCameraState){Object.assign(camera,galaxyCameraState);camera.updateProjectionMatrix();galaxyCameraState=null}const ui=$("galaxy-ui");if(ui)ui.hidden=true;$("galaxy-label").hidden=true;if(scene){release(scene);scene=null}galaxyState=null;document.body.dataset.experience="islands"},
  tick(dt,t){if(!galaxyState)return;galaxyRefresh();galaxyWalkTick(dt,t);if(!reducedMotion()&&galaxyState.view==="chart")Object.values(galaxyState.planets).forEach((planet,i)=>{planet.root.rotation.y=t*(.035+i*.008)});
    const ring=galaxyState.focusRing;if(ring&&ring.userData.anchor){ring.userData.anchor.getWorldPosition(ring.position);ring.lookAt(camera.position)}if(!reducedMotion()&&galaxyState.view==="chart")galaxyLabel()},
  goTo(to){if(!to)return false;if(to.topic&&galaxyState.model.topics.some(t=>t.id===to.topic)){galaxyTopic(to.topic);return true}if(to.place&&galaxyState.model.places.some(p=>p.id===to.place)){galaxyPlace(to.place);return true}return false},
  where(){if(!galaxyWalk)return null;
    return galaxyWalk.near?{kind:"topic",id:galaxyWalk.near,place:galaxyWalk.place}:{kind:"place",id:galaxyWalk.place}},
  listing(){const model=galaxyModel(PLACES,TREE,galaxyDone()),places=Object.fromEntries(model.places.map(place=>[place.id,place]));return model.topics.map(topic=>({id:topic.id,title:topic.name,place:topic.place,placeTitle:places[topic.place].name,year:topic.year,state:topic.state}))},
};

// Progress can arrive through any shared entry point, including import while
// motion is off. Rebuild only when the record changes, preserving navigation.
function galaxyRefresh(){if(!galaxyState)return;const state=galaxyState,key=JSON.stringify(galaxyDone());if(key===state.progress)return;
  state.progress=key;state.model=galaxyModel(PLACES,TREE,galaxyDone());state.groups=galaxyGroups(state.model);
  if(!state.visuals){renderGalaxyList();return}
  discard(state.journey);state.journey=galaxyRoute(state.visuals,state.model);scene.add(state.journey);
  Object.entries(state.groups).forEach(([kind,places])=>{discard(state.planets[kind].root);
    const planet=state.visuals.makePlanet(places,{states:Object.fromEntries(places.map(p=>[p.id,p.state])),domeScale:.22});
    state.planets[kind]=planet;scene.add(planet.root)});
  const focused=document.activeElement,topic=focused&&focused.dataset.galaxyTopic;
  galaxyShow(state.view);if(topic){const button=[...document.querySelectorAll("[data-galaxy-topic]")].find(b=>b.dataset.galaxyTopic===topic);if(button)button.focus()}
}
addEventListener("resize",()=>{if(galaxyState){if(galaxyState.visuals){discard(galaxyState.journey);galaxyState.journey=galaxyRoute(galaxyState.visuals,galaxyState.model,galaxyState.topic);scene.add(galaxyState.journey)}galaxyShow(galaxyState.view)}});

$("galaxy-list").addEventListener("focusin",event=>{const button=event.target.closest("button");if(button)$("galaxy-list").querySelectorAll("button").forEach(b=>b.tabIndex=b===button?0:-1)});
