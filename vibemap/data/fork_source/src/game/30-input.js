const ray=new T.Raycaster(),ndc=new T.Vector2(),target=new T.Vector3(),keys={};let hasTarget=false,downPos=null,marker=null;
let joy={x:0,y:0,on:false},wantJump=false;
function setupInput(){
  const c=$("c");
  c.addEventListener("pointerdown",e=>{downPos=[e.clientX,e.clientY]});
  c.addEventListener("pointerup",e=>{if(!downPos)return;const d=Math.hypot(e.clientX-downPos[0],e.clientY-downPos[1]);downPos=null;if(d>10)return;
    const rc=$("c").getBoundingClientRect();ndc.set((e.clientX-rc.left)/rc.width*2-1,-((e.clientY-rc.top)/rc.height)*2+1);ray.setFromCamera(ndc,camera);const hit=ray.intersectObjects(island.userData.parts)[0];if(!hit)return;
    target.copy(hit.point);target.y=0;hasTarget=true;marker.position.set(target.x,.06,target.z);marker.material.opacity=1});
  addEventListener("keydown",e=>{const k=e.key.toLowerCase();keys[k]=true;if(k===" "){wantJump=true;if(document.activeElement===document.body)e.preventDefault()}if(["arrowup","arrowdown","arrowleft","arrowright"].includes(k))e.preventDefault()});
  addEventListener("keyup",e=>{keys[e.key.toLowerCase()]=false});
  const j=$("joy"),kn=$("knob");let jid=null;
  j.addEventListener("pointerdown",e=>{jid=e.pointerId;j.setPointerCapture(jid);joy.on=true;jm(e)});
  j.addEventListener("pointermove",e=>{if(e.pointerId===jid)jm(e)});
  const je=e=>{if(e.pointerId!==jid)return;jid=null;joy={x:0,y:0,on:false};kn.style.transform=""};
  j.addEventListener("pointerup",je);j.addEventListener("pointercancel",je);
  function jm(e){const r=j.getBoundingClientRect();let dx=(e.clientX-r.left-r.width/2)/(r.width/2),dy=(e.clientY-r.top-r.height/2)/(r.height/2);const l=Math.hypot(dx,dy);if(l>1){dx/=l;dy/=l}joy.x=dx;joy.y=dy;kn.style.transform=`translate(${dx*30}px,${dy*30}px)`}
  $("jump").addEventListener("pointerdown",e=>{e.preventDefault();wantJump=true});
  $("c").addEventListener("dblclick",()=>{wantJump=true});
}
function nearestPlot(){let best=-1,bd=99;PLOT_POS.forEach((p,i)=>{const d=p.distanceTo(chars.lotte.g.position);if(d<bd){bd=d;best=i}});return {i:best,d:bd}}
let nearK=0,started=false,inited=false,lastSay="";
