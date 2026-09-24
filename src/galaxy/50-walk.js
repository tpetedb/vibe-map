// A miniature owns local coordinates. Nothing here writes campaign positions.
const GALAXY_WALK_R=.035,GALAXY_STEP=.07;
let galaxyWalk=null;
function galaxyWalkFree(x,z,data){
  if(Math.hypot(x,z)>data.walkSurface.radius-GALAXY_WALK_R)return false;
  for(const w of data.walkSurface.water||[]){
    if(w.kind==='disc'&&Math.hypot(x-w.x,z-w.z)<w.radius+GALAXY_WALK_R)return false;
    if(w.kind==='box'&&Math.abs(x-w.x)<w.width/2+GALAXY_WALK_R&&Math.abs(z-w.z)<w.depth/2+GALAXY_WALK_R)return false;
  }
  return !data.obstacles.some(([ox,oz,r])=>Math.hypot(x-ox,z-oz)<r+GALAXY_WALK_R)&&
    !data.lessonSites.some(s=>Math.hypot(x-s.position[0],z-s.position[1])<.095);
}
function galaxyWalkStop(){galaxyWalk=null;document.body.dataset.galaxyWalk='off';$("galaxy-walk").hidden=true;surfaceInputReset()}
function galaxyWalkStart(detail,carry){
  galaxyWalkStop();let root=null;detail.traverse(node=>{if(node.userData.miniature)root=node});if(!root)return;
  const data=root.userData,actor=character(playerSpec()),anchor=new T.Group();actor.g.scale.setScalar(.075);actor.plate.visible=false;anchor.add(actor.g);root.add(anchor);
  const ring=new T.Mesh(new T.TorusGeometry(.055,.009,6,24),mat(PALETTE.yellow,{emissive:PALETTE.yellow,emissiveIntensity:.6}));ring.rotation.x=-Math.PI/2;ring.position.y=.013;anchor.add(ring);
  const cells=[],byKey=new Map();
  for(let ix=-13;ix<=13;ix++)for(let iz=-13;iz<=13;iz++){
    const x=ix*GALAXY_STEP,z=iz*GALAXY_STEP;if(!galaxyWalkFree(x,z,data))continue;
    const cell={x,z,ix,iz};cells.push(cell);byKey.set(ix+','+iz,cell);
  }
  const start=cells.reduce((best,p)=>Math.hypot(p.x-.35,p.z-.72)<Math.hypot(best.x-.35,best.z-.72)?p:best,cells[0]);
  anchor.position.set(start.x,.012,start.z);if(carry&&galaxyWalkFree(...carry,data))anchor.position.set(carry[0],.012,carry[1]);fixColors(anchor);
  galaxyWalk={root,data,actor,anchor,place:galaxySelected().id,cells,byKey,path:[],near:null,frame:0,moving:false};
  document.body.dataset.galaxyWalk='on';$("galaxy-walk").hidden=false;galaxyWalkNear();
}
// Search only this small surface. A blocked tap never walks through a building.
function galaxyWalkAim(x,z,lesson=false){const w=galaxyWalk;if(!w)return false;
  if(!lesson&&!galaxyWalkFree(x,z,w.data)){copySay('Choose open ground inside the dome.');return false}
  const p=w.anchor.position,start=w.cells.reduce((a,b)=>Math.hypot(b.x-p.x,b.z-p.z)<Math.hypot(a.x-p.x,a.z-p.z)?b:a,w.cells[0]);
  const queue=[start],from=new Map([[start,null]]);let best=start;
  for(let i=0;i<queue.length;i++){const cell=queue[i];if(Math.hypot(cell.x-x,cell.z-z)<Math.hypot(best.x-x,best.z-z))best=cell;
    for(const [dx,dz] of [[1,0],[-1,0],[0,1],[0,-1]]){const next=w.byKey.get((cell.ix+dx)+','+(cell.iz+dz));if(!next||from.has(next))continue;
      if(!galaxyWalkFree((next.x+cell.x)/2,(next.z+cell.z)/2,w.data))continue;from.set(next,cell);queue.push(next)}
  }
  if(Math.hypot(best.x-x,best.z-z)>(lesson?.23:.11)){copySay('That spot is blocked. Choose nearby open ground.');return false}
  const path=[];for(let cell=best;cell;cell=from.get(cell))path.unshift(cell);w.path=path;surfaceInputReset();return true;
}
function galaxyWalkPick(pick,clientX,clientY){const w=galaxyWalk;if(!w)return;
  const rc=$("c").getBoundingClientRect();let lesson=null,best=22;
  for(const site of w.data.lessonSites){const v=w.root.localToWorld(new T.Vector3(site.position[0],.025,site.position[1])).project(camera);
    const distance=Math.hypot(rc.left+(v.x+1)*rc.width/2-clientX,rc.top+(1-v.y)*rc.height/2-clientY);if(distance<best){best=distance;lesson=site}}
  if(lesson){galaxyWalkAim(...lesson.position,true);return}
  for(const hit of pick.intersectObjects(w.root.children,true)){let node=hit.object;while(node&&node!==w.root&&!node.userData.lessonId)node=node.parent;if(node&&node.userData.lessonId){lesson=w.data.lessonSites.find(s=>s.id===node.userData.lessonId);break}}
  if(lesson){galaxyWalkAim(...lesson.position,true);return}
  // Transform the camera ray into miniature space before intersecting its ground.
  const local=pick.ray.clone().applyMatrix4(w.root.matrixWorld.clone().invert()),point=new T.Vector3();
  if(local.intersectPlane(new T.Plane(new T.Vector3(0,1,0),0),point))galaxyWalkAim(point.x,point.z);
}
function galaxyWalkNear(){const w=galaxyWalk;if(!w)return;const p=w.anchor.position;
  const site=w.data.lessonSites.find(s=>Math.hypot(p.x-s.position[0],p.z-s.position[1])<.24),id=site?site.id:null;
  if(w.near===id&&w.labelled)return;w.near=id;w.labelled=true;
  const topic=galaxyState.model.topics.find(t=>t.id===id),button=$("galaxy-near");button.disabled=!topic;
  $("galaxy-walk-status").textContent=topic?'Nearby: '+topic.name:'Walk with arrows, WASD or the stick. Tap open ground or a lesson pavilion.';
  if(topic)copySay('Nearby lesson: '+topic.name);
}
window.galaxyOpenNearby=function(){if(galaxyWalk&&galaxyWalk.near)galaxyTopic(galaxyWalk.near)};
function galaxyWalkTick(dt,t){const w=galaxyWalk;if(!w)return;w.frame++;
  const input=surfaceInput(),p=w.anchor.position;let x=input.x,z=input.z;
  if(input.blocked){w.moving=false;return}
  if(x||z)w.path=[];
  else if(w.path.length){const next=w.path[0],dx=next.x-p.x,dz=next.z-p.z,d=Math.hypot(dx,dz);if(d<.015)w.path.shift();else{x=dx/d;z=dz/d}}
  const length=Math.hypot(x,z),step=Math.min(.025,.62*dt*speedMult()*runMult());w.moving=false;
  if(length){x=x/Math.max(1,length)*step;z=z/Math.max(1,length)*step;
    if(w.path.length){const next=w.path[0],d=Math.hypot(next.x-p.x,next.z-p.z);if(d<step){x=next.x-p.x;z=next.z-p.z}}
    const oldX=p.x,oldZ=p.z;if(galaxyWalkFree(p.x+x,p.z,w.data))p.x+=x;if(galaxyWalkFree(p.x,p.z+z,w.data))p.z+=z;
    w.moving=Math.hypot(p.x-oldX,p.z-oldZ)>.0001;if(w.moving)w.actor.g.rotation.y=Math.atan2(x,z);else w.path=[];
  }
  animChar(w.actor,w.moving,dt,t);galaxyWalkNear();
}
addEventListener('keydown',event=>{if(experienceId()!=='galaxy'||!galaxyWalk||document.activeElement!==document.body||surfaceInput().blocked)return;
  if(event.key==='Enter'){galaxyOpenNearby();event.preventDefault()}
  if(event.key==='Escape'){galaxyView('chart');document.querySelector('[data-galaxy-view="chart"]').focus();event.preventDefault()}
});
window.__galaxyWalk=()=>{const w=galaxyWalk;if(!w)return null;const p=w.anchor.position,rc=$("c").getBoundingClientRect();
  const project=(x,z)=>{const v=w.root.localToWorld(new T.Vector3(x,.025,z)).project(camera);return [rc.left+(v.x+1)*rc.width/2,rc.top+(1-v.y)*rc.height/2]};
  return {active:true,position:[p.x,p.z],valid:galaxyWalkFree(p.x,p.z,w.data),near:w.near,frame:w.frame,moving:w.moving,route:w.path.length,
    sites:w.data.lessonSites.map(s=>({id:s.id,position:s.position,screen:project(...s.position)})),
    water:w.data.walkSurface.water,obstacles:w.data.obstacles};
};
window.__galaxyGroundAt=(x,z)=>{if(!galaxyWalk)return null;const rc=$("c").getBoundingClientRect(),v=galaxyWalk.root.localToWorld(new T.Vector3(x,0,z)).project(camera);return [rc.left+(v.x+1)*rc.width/2,rc.top+(1-v.y)*rc.height/2]};
