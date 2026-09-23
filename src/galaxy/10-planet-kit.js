// Pure scene kit. The caller owns state, camera, selection, lighting and disposal.
// All returned resources belong to that root and may be released with discard().
function createGalaxyVisuals({three:T,palette:P,material:mat,finish:fixColors}){
  const TAU=Math.PI*2,UP=new T.Vector3(0,1,0);
  const mix=(a,b,k)=>new T.Color(a).lerp(new T.Color(b),k).getHex();
  const C={ocean:mix(P.blue,P.black,.35),land:mix(P.green,P.ink,.08),
    ground:mix(P.green,P.ink,.3),glass:mix(P.blueBright,P.snow,.65),
    steel:mix(P.stone,P.blue,.32),cream:mix(P.snow,P.deck,.16)};
  const stateColor=s=>s==='done'?P.greenBright:s==='next'?P.yellow:P.muted;
  function surface(lat,lon,r=1){
    const a=lat*Math.PI/180,b=lon*Math.PI/180;
    return new T.Vector3(r*Math.cos(a)*Math.cos(b),r*Math.sin(a),-r*Math.cos(a)*Math.sin(b));
  }
  function line(parent,points,color,opacity=1,dashed=false){
    const opts={color,transparent:opacity<1,opacity,depthWrite:false};
    const material=dashed?new T.LineDashedMaterial({...opts,dashSize:.10,gapSize:.08}):new T.LineBasicMaterial(opts);
    const m=new T.Line(new T.BufferGeometry().setFromPoints(points),material);
    if(dashed)m.computeLineDistances();parent.add(m);return m;
  }
  function ring(parent,r,y,color,opacity=1,start=0,end=TAU){
    const pts=[];for(let i=0;i<=80;i++){const a=start+(end-start)*i/80;pts.push(new T.Vector3(Math.cos(a)*r,y,Math.sin(a)*r))}
    return line(parent,pts,color,opacity);
  }
  // A kit is instanced by shape and finish: a hundred tiny details cost a few draws.
  function kit(parent){
    const batches=new Map(),matrix=new T.Matrix4(),q=new T.Quaternion(),e=new T.Euler();
    function put(shape,color,x,y,z,sx,sy,sz,ry=0,glow=false){
      // Matte instances share one draw per shape and carry their own colour.
      // Glowing parts keep a colour batch because emissive is not instanced.
      const key=shape+'|'+(glow?color:'matte')+'|'+glow;
      if(!batches.has(key))batches.set(key,{shape,color,glow,transforms:[],colors:[]});
      q.setFromEuler(e.set(0,ry,0));
      matrix.compose(new T.Vector3(x,y,z),q,new T.Vector3(sx,sy,sz));
      const batch=batches.get(key);batch.transforms.push(matrix.clone());batch.colors.push(color);
    }
    return {
      box:(x,y,z,w,h,d,color,ry=0,glow=false)=>put('box',color,x,y+h/2,z,w,h,d,ry,glow),
      tree:(x,z,h=.28)=>{put('cylinder',P.timber,x,h*.23,z,.035,h*.46,.035);put('cone',P.green,x,h*.64,z,h*.40,h*.8,h*.40)},
      ball:(x,y,z,r,color)=>put('sphere',color,x,y,z,r,r,r),
      cylinder:(x,y,z,r,h,color)=>put('cylinder',color,x,y+h/2,z,r,h,r),
      flush:()=>batches.forEach(({shape,color,glow,transforms,colors})=>{
        const geo=shape==='box'?new T.BoxGeometry(1,1,1):shape==='cone'?new T.ConeGeometry(1,1,7):shape==='cylinder'?new T.CylinderGeometry(1,1,1,12):new T.IcosahedronGeometry(1,1);
        const m=mat(glow?color:P.snow,glow?{emissive:color,emissiveIntensity:.75}:{});
        const mesh=new T.InstancedMesh(geo,m,transforms.length);
        transforms.forEach((v,i)=>{mesh.setMatrixAt(i,v);
          if(!glow)mesh.setColorAt(i,new T.Color(colors[i]).convertSRGBToLinear())});
        parent.add(mesh);
      })
    };
  }
  function building(k,x,z,w,d,h,accent=P.blueBright){
    k.box(x,0,z,w,h,d,C.cream);
    k.box(x,h,z,w+.035,.025,d+.035,P.snow);
    k.box(x,.055,z+d/2+.003,w*.84,h*.42,.008,C.steel);
    k.box(x,.065,z+d/2+.009,w*.74,.015,.01,accent,0,true);
    for(let i=1;i<4;i++)k.box(x-w/2+w*i/4,.055,z+d/2+.009,.012,h*.43,.013,C.cream);
  }
  function campus(k,look){
    // Original courtyard geometry, with no borrowed campus footprint.
    k.box(0,.001,.05,.88,.012,.58,P.deck);
    k.box(0,.014,.05,.45,.012,.30,C.ground);
    building(k,-.34,-.15,.27,.62,.18);
    building(k,.32,-.24,.27,.44,.24);
    building(k,.04,-.43,.47,.20,.17);
    for(let i=0;i<5;i++){
      k.box(-.34,.211,-.38+i*.10,.20,.008,.065,C.steel);
      k.tree(-.61+i*.29,.53,.24+(i%2)*.07);
    }
    k.box(0,.018,.50,.12,.013,.65,C.cream);
    k.box(.16,.015,.28,.12,.04,.04,P.timber);
    k.box(-.14,.015,.28,.12,.04,.04,P.timber);
    if(look==='lab'){
      k.cylinder(.31,.28,-.28,.07,.045,P.stone);
      k.box(.31,.325,-.28,.10,.018,.10,P.snow);
    }
    k.ball(0,.035,.025,.085,P.green);
  }
  function city(k){
    // Water, a low park edge, and unequal stepped towers make a readable skyline.
    k.cylinder(-.33,.002,.10,.37,.012,P.blue);
    k.box(-.33,.015,.10,.44,.013,.08,P.deck,-.22);
    k.box(-.48,.03,.14,.026,.045,.026,P.orange);
    k.box(-.15,.03,.07,.026,.045,.026,P.orange);
    const towers=[[.08,-.43,.20,.18,.43],[.33,-.31,.21,.23,.61],[.50,.02,.18,.21,.37],[.20,.03,.16,.20,.49],[.08,.39,.23,.18,.24]];
    towers.forEach(([x,z,w,d,h],i)=>{
      k.box(x,0,z,w,h,d,i%2?P.stone:C.cream);
      k.box(x,h,z,w*.71,.055,d*.71,C.steel);
      k.box(x-w*.15,h+.055,z,.018,.065,.018,P.orange);
      for(let y=.06;y<h-.025;y+=.072){
        k.box(x,y,z+d/2+.006,w*.82,.018,.009,P.blueBright,0,true);
        k.box(x-w/2-.006,y,z,.009,.018,d*.80,P.blueBright,0,true);
      }
      k.box(x,.018,z+d/2+.04,w*.65,.025,.065,P.orange);
    });
    for(let i=0;i<5;i++)k.tree(-.66+i*.21,.46,.18);
    k.box(.43,.002,.40,.23,.008,.06,P.deck);
  }
  function datacentre(k){
    k.box(0,.003,0,1.25,.014,1.05,C.steel);
    for(let row=0;row<3;row++)for(let col=0;col<4;col++){
      const x=-.44+col*.285,z=-.36+row*.31;
      k.box(x,.018,z,.21,.32,.19,P.ink);
      k.box(x,.338,z,.23,.025,.21,P.stone);
      for(let y=.066;y<.3;y+=.055){
        k.box(x,y,z+.10,.16,.022,.009,C.steel);
        k.box(x-.058,y+.003,z+.107,.021,.008,.006,P.greenBright,0,true);
      }
      k.cylinder(x,.364,z,.060,.014,C.steel);
      k.box(x,.38,z,.09,.009,.013,P.muted,.7);
      k.box(x,.38,z,.09,.009,.013,P.muted,-.7);
    }
    for(let x of [-.62,.62]){
      k.box(x,.02,0,.025,.023,1.10,P.yellow);
      k.cylinder(x,.015,.60,.065,.15,P.stone);
      k.cylinder(x,.165,.60,.043,.011,C.steel);
    }
    k.box(0,.025,-.57,1.25,.022,.024,P.yellow);
  }
  function lanes(k){
    k.cylinder(0,.002,0,.72,.018,C.steel);k.ball(0,.08,0,.08,P.yellow);
    for(let i=0;i<8;i++){
      const a=i/8*TAU,r=i%2?.56:.42,x=Math.sin(a)*r,z=Math.cos(a)*r;
      k.box(x/2,.025,z/2,.025,.018,r,P.blueBright,a, true);
      k.ball(x,.065,z,.055,i%3?P.blueBright:P.greenBright)
    }
  }
  function station(k,look){
    if(look==='house'){
      building(k,0,0,.58,.40,.29,P.orange);
      k.box(0,.315,0,.66,.05,.46,P.deck);
      [-.48,.48].forEach(x=>k.tree(x,.12,.35));
    }else if(look==='harbour'){
      k.box(0,.005,.25,1.30,.018,.55,P.blue);
      building(k,-.28,-.23,.38,.26,.25);
      for(let i=0;i<3;i++)k.box(.1+i*.16,.02,.24,.08,.09,.31,[P.orange,P.stone,P.blueBright][i]);
      k.box(.48,0,-.25,.035,.52,.035,P.yellow);
      k.box(.24,.5,-.25,.5,.035,.035,P.yellow);
    }else{
      building(k,0,-.13,.70,.38,.28);
      k.cylinder(.0,.315,-.13,.20,.045,P.stone);
      k.ball(0,.37,-.13,.14,P.blueBright);
      for(let i=0;i<4;i++)k.tree(-.45+i*.30,.38,.24);
    }
  }
  function makeDome(place,state='ahead'){
    const g=new T.Group(),k=kit(g),look=place.look;
    g.userData={placeId:place.id,look,state};
    k.cylinder(0,-.095,0,1.01,.075,C.steel);
    k.cylinder(0,-.025,0,.965,.025,look==='racks'?P.surface:C.ground);
    if(look==='campus'||look==='lab')campus(k,look);
    else if(look==='tower')city(k);
    else if(look==='racks')datacentre(k);
    else if(look==='lanes')lanes(k);
    else if(['station','house','harbour','hall'].includes(look))station(k,look);
    else throw new Error('Unsupported Galaxy look: '+look);
    k.flush();
    const color=stateColor(state);
    ring(g,1.016,-.022,color,1);
    ring(g,.965,.003,C.glass,.45);
    // Thin ribs and two broken highlights read as glass without fogging the model.
    const ribPoints=[];
    for(let a=0;a<TAU;a+=Math.PI/3){
      for(let i=0;i<24;i++){
        for(let t of [i/24,(i+1)/24]){
          const b=t*Math.PI/2;
          ribPoints.push(new T.Vector3(Math.cos(b)*Math.cos(a),Math.sin(b)*.86,Math.cos(b)*Math.sin(a)));
        }
      }
    }
    const ribs=new T.LineSegments(new T.BufferGeometry().setFromPoints(ribPoints),new T.LineBasicMaterial({color:C.glass,transparent:true,opacity:.22,depthWrite:false}));g.add(ribs);
    const glass=new T.Mesh(new T.SphereGeometry(1,40,20,0,TAU,0,Math.PI/2),mat(C.glass,{transparent:true,opacity:.055,roughness:.18,metalness:.05,depthWrite:false,side:T.FrontSide,flatShading:false}));
    glass.scale.y=.86;glass.renderOrder=3;g.add(glass);
    for(let a of [-2.4,-2.1]){
      const points=[];for(let i=0;i<=16;i++){const t=.32+i*.018;points.push(new T.Vector3(Math.cos(t)*Math.cos(a)*1.004,Math.sin(t)*.863,Math.cos(t)*Math.sin(a)*1.004))}
      line(g,points,P.snow,.63);
    }
    if(state==='next'){
      ring(g,1.08,-.02,P.yellow,.80,.06,Math.PI*.72);
      ring(g,1.08,-.02,P.yellow,.80,Math.PI+.06,Math.PI*1.72);
    }
    fixColors(g);return g;
  }
  // Deliberately simplified, hand-drawn continent outlines; never administrative borders.
  const continents=[
    [[-168,71],[-143,70],[-125,60],[-125,49],[-123,40],[-115,29],[-106,23],[-97,16],[-88,16],[-83,9],[-77,8],[-87,22],[-81,25],[-80,33],[-66,45],[-58,52],[-67,58],[-83,62],[-99,73],[-125,73],[-149,72]],
    [[-81,12],[-68,10],[-60,6],[-49,-1],[-35,-7],[-40,-21],[-51,-30],[-65,-55],[-74,-49],[-72,-30],[-79,-10]],
    [[-73,60],[-48,59],[-20,72],[-26,82],[-49,83],[-64,76]],
    [[-17,36],[0,37],[12,33],[31,31],[35,23],[44,12],[51,12],[43,-12],[34,-26],[19,-35],[11,-18],[9,4],[-1,5],[-16,15]],
    [[-10,36],[-10,44],[-2,49],[8,55],[5,60],[20,71],[32,70],[41,67],[58,70],[76,72],[100,77],[140,72],[177,63],[177,53],[156,58],[146,45],[133,42],[129,33],[121,23],[109,20],[103,8],[99,7],[93,23],[86,21],[79,8],[73,19],[64,25],[50,27],[43,12],[36,16],[34,29],[26,36],[20,40],[15,38],[10,44],[2,43]],
    [[112,-11],[130,-12],[142,-10],[153,-26],[145,-39],[129,-33],[115,-35],[112,-24]],
    [[47,-13],[50,-17],[48,-26],[44,-24]],[[130,32],[142,46],[145,42],[139,34]],
    [[-8,50],[0,51],[-3,59],[-7,58]],[[-10,51],[-6,51],[-6,56],[-10,55]],
    [[95,5],[105,-6],[119,-8],[116,1],[108,5]],[[166,-35],[174,-40],[168,-47],[165,-44]]
  ];
  function inLand(lat,lon){
    if(lat< -72)return true;
    return continents.some(poly=>{let inside=false;for(let i=0,j=poly.length-1;i<poly.length;j=i++){
      const a=poly[i],b=poly[j];if((a[1]>lat)!==(b[1]>lat)&&lon<(b[0]-a[0])*(lat-a[1])/(b[1]-a[1])+a[0])inside=!inside;
    }return inside});
  }
  function earthGeometry(){
    const geo=new T.SphereGeometry(1,96,48).toNonIndexed(),p=geo.attributes.position;
    const colors=new Float32Array(p.count*3),v=new T.Vector3();
    const land=new T.Color(C.land).convertSRGBToLinear(),ocean=new T.Color(C.ocean).convertSRGBToLinear();
    for(let i=0;i<p.count;i+=3){
      v.set(0,0,0);for(let j=0;j<3;j++)v.add(new T.Vector3().fromBufferAttribute(p,i+j));v.normalize();
      const lat=Math.asin(v.y)*180/Math.PI,lon=Math.atan2(-v.z,v.x)*180/Math.PI;
      const c=inLand(lat,lon)?land:ocean;
      for(let j=0;j<3;j++)c.toArray(colors,(i+j)*3);
    }
    geo.setAttribute('color',new T.BufferAttribute(colors,3));return geo;
  }
  function graticule(parent){
    const points=[];
    for(let lat=-60;lat<=60;lat+=30)for(let lon=-180;lon<180;lon+=5)points.push(surface(lat,lon,1.004),surface(lat,lon+5,1.004));
    for(let lon=-180;lon<180;lon+=30)for(let lat=-90;lat<90;lat+=5)points.push(surface(lat,lon,1.004),surface(lat+5,lon,1.004));
    parent.add(new T.LineSegments(new T.BufferGeometry().setFromPoints(points),new T.LineBasicMaterial({color:P.blue,transparent:true,opacity:.19,depthWrite:false})));
  }
  function makePlanet(places,{states={},domeScale=.34}={}){
    if(!places.length)throw new Error('A Galaxy planet needs at least one place');
    const globe=places[0].globe;
    if(places.some(p=>p.globe!==globe))throw new Error('A Galaxy planet cannot mix globe kinds');
    const g=new T.Group(),sites=[];
    const body=new T.Mesh(globe==='earth'?earthGeometry():new T.IcosahedronGeometry(1,1),mat(globe==='earth'?P.snow:C.steel,{vertexColors:globe==='earth',roughness:.88,flatShading:globe!=='earth'}));
    body.userData.galaxyPlanet=true;g.add(body);
    if(globe==='earth')graticule(g);
    else if(globe==='datacentre'){
      // A fabricated geodesic enclosure, without geographic meridians or land.
      const shell=new T.IcosahedronGeometry(1.006,1),edges=new T.EdgesGeometry(shell);
      shell.dispose();g.add(new T.LineSegments(edges,new T.LineBasicMaterial({color:P.blueBright,transparent:true,opacity:.36,depthWrite:false})));
    }
    if(globe==='cloud'){
      const k=kit(g);for(let i=0;i<9;i++){const a=i*2.4;k.ball(Math.cos(a)*.64,Math.sin(i*1.7)*.35,Math.sin(a)*.64,.47,mix(P.blue,P.snow,.6))}k.flush();body.visible=false;
    }
    const siteScale=Math.min(domeScale,.62/Math.sqrt(places.length));
    const vectors=places.map((p,i)=>{
      if(globe!=='earth')return new T.Vector3(Math.sin(i*.6)*.45,.9,.35).normalize();
      if(!Number.isFinite(p.lat)||!Number.isFinite(p.lon))throw new Error('Earth place needs coordinates: '+p.id);
      return surface(p.lat,p.lon);
    });
    // Nearby true pins keep their exact beacons. Their domes fan onto a local
    // tangent grid, small enough to fit dense regions without overlapping.
    const displays=vectors.map(v=>v.clone()),seen=new Set();
    vectors.forEach((vector,start)=>{if(seen.has(start))return;
      const cluster=[],todo=[start];seen.add(start);
      while(todo.length){const at=todo.pop();cluster.push(at);
        vectors.forEach((other,i)=>{if(!seen.has(i)&&vectors[at].angleTo(other)<siteScale*2.25){seen.add(i);todo.push(i)}})}
      if(cluster.length<2)return;
      const centre=cluster.reduce((v,i)=>v.add(vectors[i]),new T.Vector3()).normalize();
      const east=new T.Vector3().crossVectors(Math.abs(centre.y)>.98?new T.Vector3(1,0,0):UP,centre).normalize();
      const north=new T.Vector3().crossVectors(centre,east).normalize();
      const cols=Math.ceil(Math.sqrt(cluster.length)),rows=Math.ceil(cluster.length/cols),gap=siteScale*3.6;
      cluster.forEach((at,i)=>{const col=i%cols,row=Math.floor(i/cols);
        displays[at]=centre.clone().addScaledVector(east,(col-(cols-1)/2)*gap)
          .addScaledVector(north,(row-(rows-1)/2)*gap).normalize()})
    });
    places.forEach((place,i)=>{
      const normal=vectors[i],state=states[place.id]||'ahead',point=normal.clone().multiplyScalar(1.012);
      const display=displays[i];
      const dome=makeDome(place,state);dome.scale.setScalar(siteScale);dome.position.copy(display).multiplyScalar(1.025);dome.quaternion.setFromUnitVectors(UP,display);g.add(dome);
      const beacon=new T.Group();beacon.position.copy(point);beacon.quaternion.setFromUnitVectors(UP,normal);
      const k=kit(beacon);k.cylinder(0,0,0,.012,.15,stateColor(state));k.ball(0,.17,0,.026,stateColor(state));k.flush();g.add(beacon);
      if(display.angleTo(normal)>.01){
        const pts=[];for(let j=0;j<=24;j++)pts.push(normal.clone().lerp(display,j/24).normalize().multiplyScalar(1.018));line(g,pts,stateColor(state),.80);
      }
      sites.push({id:place.id,dome,pin:point,normal:normal.clone(),displayNormal:display,state});
    });
    g.userData.globe=globe;fixColors(g);return {root:g,body,sites};
  }
  function makeJourney(nodes){
    const g=new T.Group();
    for(let i=1;i<nodes.length;i++){
      const a=new T.Vector3(...nodes[i-1].position),b=new T.Vector3(...nodes[i].position),mid=a.clone().lerp(b,.5);
      mid.z-=.08;
      const curve=new T.QuadraticBezierCurve3(a,mid,b),state=nodes[i].state||'ahead';
      line(g,curve.getPoints(64),stateColor(state),state==='ahead'?.48:1,state==='ahead');
      if(state==='next'){
        const m=new T.Mesh(new T.TubeGeometry(curve,64,.012,5,false),mat(P.yellow,{emissive:P.yellow,emissiveIntensity:.8}));g.add(m);
      }
    }
    fixColors(g);return g;
  }
  return {surface,makeDome,makePlanet,makeJourney};
}
