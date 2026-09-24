// Fit the visible subject into the space the actual HUD and list leave free.
// View offsets retain the full canvas, so pointer picking uses canvas coordinates.
function galaxySubject(){const state=galaxyState;
  if(state.view==="dome")return [state.detail];
  if(state.view==="journey")return [state.journey];
  return Object.values(state.planets).map(p=>p.root).filter(root=>root.visible)}
function galaxyBounds(){const bounds=new T.Box3(),instance=new T.Matrix4(),matrix=new T.Matrix4();
  // r128 Box3.setFromObject ignores instance transforms. Read those matrices,
  // or a tiny beacon is measured as its unscaled unit cylinder.
  galaxySubject().forEach(root=>{root.updateMatrixWorld(true);root.traverseVisible(node=>{
    if(!node.geometry)return;const geometry=node.geometry;if(!geometry.boundingBox)geometry.computeBoundingBox();
    if(node.isInstancedMesh){for(let i=0;i<node.count;i++){node.getMatrixAt(i,instance);matrix.multiplyMatrices(node.matrixWorld,instance);bounds.union(geometry.boundingBox.clone().applyMatrix4(matrix))}}
    else bounds.union(geometry.boundingBox.clone().applyMatrix4(node.matrixWorld));
  })});return bounds}
function galaxyCorners(bounds){const points=[];for(const x of [bounds.min.x,bounds.max.x])for(const y of [bounds.min.y,bounds.max.y])for(const z of [bounds.min.z,bounds.max.z])points.push(new T.Vector3(x,y,z));return points}
function galaxyFrame(){if(!galaxyState||!galaxyState.visuals)return;
  const canvas=$("c").getBoundingClientRect(),panel=$("galaxy-ui").getBoundingClientRect(),hud=$("hud").getBoundingClientRect();
  const top=Math.max(16,hud.bottom-canvas.top+16),bottom=innerWidth<=1100?panel.top-canvas.top-18:canvas.height-18;
  const left=innerWidth<=1100?20:panel.right-canvas.left+24,right=canvas.width-20;
  const width=Math.max(80,right-left),height=Math.max(80,bottom-top),centerX=left+width/2,centerY=top+height/2;
  camera.clearViewOffset();camera.aspect=canvas.width/canvas.height;camera.near=.05;camera.far=200;
  const bounds=galaxyBounds(),center=bounds.getCenter(new T.Vector3());
  const direction=new T.Vector3(0,galaxyState.view==="journey"?0:.48,1).normalize();
  camera.position.copy(center).add(direction);camera.lookAt(center);camera.updateMatrixWorld(true);
  const local=galaxyCorners(bounds).map(p=>p.sub(center).applyQuaternion(camera.quaternion.clone().invert()));
  const halfX=Math.max(...local.map(p=>Math.abs(p.x))),halfY=Math.max(...local.map(p=>Math.abs(p.y))),depth=Math.max(...local.map(p=>Math.abs(p.z)));
  const tan=Math.tan(camera.fov*Math.PI/360),distance=1.13*Math.max(halfY/(tan*height/canvas.height),halfX/(tan*camera.aspect*width/canvas.width))+depth;
  camera.position.copy(center).addScaledVector(direction,distance);camera.lookAt(center);
  camera.setViewOffset(canvas.width,canvas.height,canvas.width/2-centerX,canvas.height/2-centerY,canvas.width,canvas.height);camera.updateMatrixWorld(true);
}
// Read-only projection evidence: geometry bounds, not the intended layout box.
window.__galaxyFrame=()=>{if(!galaxyState||!galaxyState.visuals)return null;
  const canvas=$("c").getBoundingClientRect(),panel=$("galaxy-ui").getBoundingClientRect(),hud=$("hud").getBoundingClientRect();
  const points=galaxyCorners(galaxyBounds()).map(p=>{p.project(camera);return {x:canvas.left+(p.x+1)*canvas.width/2,y:canvas.top+(1-p.y)*canvas.height/2}});
  const left=Math.min(...points.map(p=>p.x)),right=Math.max(...points.map(p=>p.x)),top=Math.min(...points.map(p=>p.y)),bottom=Math.max(...points.map(p=>p.y));
  return {left,right,top,bottom,inside:left>=canvas.left&&right<=canvas.right&&top>=canvas.top&&bottom<=canvas.bottom,clearOfUi:top>hud.bottom&&(right<panel.left||left>panel.right||bottom<panel.top||top>panel.bottom)};
};

// A fixed star field gives depth without motion or external image assets.
function galaxyStars(){const points=[];for(let i=0;i<360;i++){
  const y=1-2*(i+.5)/360,a=i*2.3999632297,r=Math.sqrt(1-y*y);
  points.push(r*Math.cos(a)*65,y*65,r*Math.sin(a)*65)}
  const geometry=new T.BufferGeometry();geometry.setAttribute("position",new T.Float32BufferAttribute(points,3));
  const field=new T.Points(geometry,new T.PointsMaterial({color:PALETTE.muted,size:.11,sizeAttenuation:true,transparent:true,opacity:.65,depthWrite:false}));
  field.raycast=()=>{};return field;
}
