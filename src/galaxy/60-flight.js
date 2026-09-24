// Flight is transient presentation. Progress and the last visited topic stay in S.
let galaxyFlight=null,galaxyCanvasFocus=null;
function galaxyShip(){
  const ship=new T.Group(),hull=new T.Mesh(new T.ConeGeometry(.18,.8,6),mat(PALETTE.snow));
  hull.rotation.z=-Math.PI/2;ship.add(hull);
  const canopy=new T.Mesh(new T.SphereGeometry(.12,12,8),mat(PALETTE.blueBright,{emissive:PALETTE.blue,emissiveIntensity:.5}));
  canopy.position.set(.06,.12,0);canopy.scale.set(1.5,.6,1);ship.add(canopy);
  for(const z of [-1,1]){const wing=new T.Mesh(new T.BoxGeometry(.36,.04,.32),mat(PALETTE.orange));wing.position.set(-.2,-.02,z*.22);wing.rotation.y=z*.3;ship.add(wing)}
  const engine=new T.Mesh(new T.ConeGeometry(.09,.3,8),mat(PALETTE.blueBright,{emissive:PALETTE.blueBright,emissiveIntensity:1}));
  engine.rotation.z=Math.PI/2;engine.position.x=-.5;ship.add(engine);fixColors(ship);return ship;
}
function galaxyFlightClear(){
  const flight=galaxyFlight;galaxyFlight=null;
  if(flight)discard(flight.ship);
  const dialog=$("galaxy-flight");if(dialog.open)dialog.close();
}
function galaxyFlightDispose(){
  galaxyFlightClear();
  if(galaxyCanvasFocus){const value=galaxyCanvasFocus.value;if(value===null)$("c").removeAttribute("tabindex");else $("c").setAttribute("tabindex",value);if(galaxyCanvasFocus.label===null)$("c").removeAttribute("aria-label");else $("c").setAttribute("aria-label",galaxyCanvasFocus.label);galaxyCanvasFocus=null}
}
function galaxyArrive(id){
  galaxyFlightClear();if(!galaxyState)return;
  galaxyState.landedPlace=id;galaxyState.selected=id;const topic=galaxySelected().topics[0];galaxyState.topic=topic?topic.id:null;
  galaxyShow("dome");if(!galaxyCanvasFocus)galaxyCanvasFocus={value:$("c").getAttribute("tabindex"),label:$("c").getAttribute("aria-label")};$("c").setAttribute("tabindex","-1");$("c").setAttribute("aria-label","Planet surface. Use arrow keys to walk, or Tab to browse lessons.");
  ($("galaxy-ui").dataset.rendering==="scene"?$("c"):$("galaxy-title")).focus();
  copySay("Landed at "+galaxySelected().name+". Choose a lesson or walk inside the dome.");
}
window.galaxySkipFlight=function(){if(galaxyFlight)galaxyArrive(galaxyFlight.destination)};
function galaxyFly(id){
  const state=galaxyState,destination=state.model.places.find(place=>place.id===id);if(!destination)return;
  if(reducedMotion()||!state.visuals){galaxyArrive(id);return}
  const origin=state.model.places.find(place=>place.id===state.landedPlace)||(state.model.places.find(place=>place.id===(state.model.next||{}).place))||galaxySelected();galaxyFlightClear();galaxyShow("chart");
  const end=new T.Vector3(...(GALAXY_POS[destination.globe]||[0,0,0]));end.y+=2.15;
  const start=new T.Vector3(...(GALAXY_POS[origin.globe]||[0,0,0]));start.y+=2.15;
  // Places on the same globe still have a legible approach, without camera travel.
  if(start.distanceTo(end)<1)start.x-=2;
  const control=start.clone().lerp(end,.5);control.y+=1;
  const ship=galaxyShip();ship.position.copy(start);scene.add(ship);
  galaxyFlight={destination:id,ship,start,control,end,started:performance.now()};
  $("galaxy-flight-status").textContent="Autopilot to "+destination.name+". Arrival in a few seconds.";
  $("galaxy-flight").showModal();$("galaxy-skip-flight").focus();
}
function galaxyFlightTick(){
  const flight=galaxyFlight;if(!flight)return;
  if(reducedMotion()){galaxySkipFlight();return}
  const t=Math.min(1,(performance.now()-flight.started)/3000),u=t*t*(3-2*t);
  const {start,control,end,ship}=flight;
  ship.position.copy(start).multiplyScalar((1-u)**2).addScaledVector(control,2*(1-u)*u).addScaledVector(end,u*u);
  const tangent=control.clone().sub(start).multiplyScalar(1-u).addScaledVector(end.clone().sub(control),u);
  ship.rotation.z=Math.atan2(tangent.y,tangent.x);
  if(t===1)galaxySkipFlight();
}
$("galaxy-flight").addEventListener("cancel",event=>{event.preventDefault();galaxySkipFlight()});
// Keep focus on Skip for the whole Enter key cycle, including key repeat.
$("galaxy-flight").addEventListener("keydown",event=>{
  if(["Enter","Escape"].includes(event.key)){event.preventDefault();event.stopImmediatePropagation();if(event.key==="Escape")galaxySkipFlight()}
});

$("galaxy-flight").addEventListener("keyup",event=>{if(event.key==="Enter"){event.preventDefault();event.stopImmediatePropagation();galaxySkipFlight()}});
