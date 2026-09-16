let VN=[],VL=[],vsel=null,vdrag=null,vraf=null,vctx,vW,vH,vctxScale=1;
function buildGraph(){
  VN=Object.keys(NOTES).map((id,i)=>({id,t:NOTES[id].t,x:0,y:0,vx:0,vy:0,deg:0}));const idx={};VN.forEach((n,i)=>idx[n.id]=i);VL=[];
  VN.forEach(n=>{const re=/\[\[([^\]]+)\]\]/g;let m;const seen={};while((m=re.exec(NOTES[n.id].md))){const to=m[1];if(idx[to]!==undefined&&to!==n.id&&!seen[to]){seen[to]=1;VL.push([idx[n.id],idx[to]]);n.deg++;VN[idx[to]].deg++}}});
  const cv=$("vg");vW=cv.clientWidth;vH=cv.clientHeight;vctxScale=Math.min(2,devicePixelRatio||1);cv.width=vW*vctxScale;cv.height=vH*vctxScale;vctx=cv.getContext("2d");
  VN.forEach((n,i)=>{const a=i/VN.length*Math.PI*2;n.x=vW/2+Math.cos(a)*Math.min(vW,vH)*.35;n.y=vH/2+Math.sin(a)*Math.min(vW,vH)*.35});
  for(let i=0;i<120;i++)vstep(1);
}
function vstep(k){
  const cx=vW/2,cy=vH/2;
  for(let i=0;i<VN.length;i++){const a=VN[i];a.vx+=(cx-a.x)*.004*k;a.vy+=(cy-a.y)*.004*k;
    for(let j=i+1;j<VN.length;j++){const b=VN[j];let dx=b.x-a.x,dy=b.y-a.y,d2=dx*dx+dy*dy+.01,d=Math.sqrt(d2);const f=1400/d2*k;dx/=d;dy/=d;a.vx-=dx*f;a.vy-=dy*f;b.vx+=dx*f;b.vy+=dy*f}}
  VL.forEach(([i,j])=>{const a=VN[i],b=VN[j];let dx=b.x-a.x,dy=b.y-a.y,d=Math.sqrt(dx*dx+dy*dy)+.01;const f=(d-78)*.02*k;dx/=d;dy/=d;a.vx+=dx*f;a.vy+=dy*f;b.vx-=dx*f;b.vy-=dy*f});
  VN.forEach(n=>{if(n===vdrag)return;n.vx*=.82;n.vy*=.82;n.x+=n.vx;n.y+=n.vy;n.x=Math.max(14,Math.min(vW-14,n.x));n.y=Math.max(14,Math.min(vH-14,n.y))});
}
function vdraw(){
  const c=vctx;c.setTransform(vctxScale,0,0,vctxScale,0,0);c.clearRect(0,0,vW,vH);
  const nb=new Set();if(vsel!==null)VL.forEach(([i,j])=>{if(i===vsel)nb.add(j);if(j===vsel)nb.add(i)});
  VL.forEach(([i,j])=>{const a=VN[i],b=VN[j];const hot=vsel!==null&&(i===vsel||j===vsel);c.strokeStyle=hot?"rgba(167,139,250,.9)":"rgba(255,255,255,"+(vsel===null?.16:.06)+")";c.lineWidth=hot?1.6:1;c.beginPath();c.moveTo(a.x,a.y);c.lineTo(b.x,b.y);c.stroke()});
  const col={ws:"#22D3EE",c:"#A78BFA",p:"#FBBF24",dark:"#94A3B8",feudal:"#34D399",castle:"#F59E0B",imperial:"#C084FC",future:"#67E8F9"};
  VN.forEach((n,i)=>{const r=4+Math.min(10,n.deg*1.1);const dim=vsel!==null&&i!==vsel&&!nb.has(i);c.globalAlpha=dim?.3:1;
    if(i===vsel){c.fillStyle="rgba(167,139,250,.25)";c.beginPath();c.arc(n.x,n.y,r+8,0,7);c.fill()}
    c.fillStyle=col[n.t];c.beginPath();c.arc(n.x,n.y,r,0,7);c.fill();
    if(!dim||i===vsel){c.fillStyle="#dcddde";c.font=(i===vsel?"600 ":"")+"11px Inter,sans-serif";c.textAlign="center";c.fillText(n.id,n.x,n.y+r+13)}
    c.globalAlpha=1});
}
function vloop(){vstep(1);vdraw();vraf=requestAnimationFrame(vloop)}
function vpick(x,y){let best=null,bd=22;VN.forEach((n,i)=>{const d=Math.hypot(n.x-x,n.y-y);if(d<bd){bd=d;best=i}});return best}
function vrender(id){
  vsel=VN.findIndex(n=>n.id===id);const md=NOTES[id].md;
  let html=md.split("\n").map(l=>{
    if(l.startsWith("# "))return "<h1>"+l.slice(2)+"</h1>";
    if(l.startsWith("- "))return "<li>"+l.slice(2)+"</li>";
    if(l.startsWith("#")&&!l.includes(" "))return '<span class="tag">'+l+"</span>";
    return l?"<p>"+l+"</p>":""}).join("").replace(/<\/li><li>/g,"</li><li>").replace(/(<li>.*?<\/li>)+/g,m=>"<ul>"+m+"</ul>");
  html=html.replace(/\*\*(.+?)\*\*/g,"<b>$1</b>").replace(/`(.+?)`/g,"<code>$1</code>").replace(/\[([^\]]+)\]\((https?:[^)]+)\)/g,'<a href="$2" target="_blank" rel="noopener">$1</a>').replace(/\[\[([^\]]+)\]\]/g,(m,t)=>NOTES[t]?'<span class="wl" data-n="'+t+'">'+t+'</span>':t);
  const back=VN.filter(n=>n.id!==id&&NOTES[n.id].md.includes("[["+id+"]]")).map(n=>'<span class="wl" data-n="'+n.id+'">'+n.id+'</span>').join("");
  html+='<div class="bl"><h2>Linked from</h2>'+(back||'<span class="muted">nothing yet</span>')+'</div>';
  $("vnote").innerHTML=html;$("vnote").scrollTop=0;$("vnote").querySelectorAll(".wl").forEach(e=>e.onclick=()=>vrender(e.dataset.n));
  const n=VN[vsel];if(n){n.vx+=(vW/2-n.x)*.15;n.vy+=(vH/2-n.y)*.15}
}
window.openVault=function(){NOTES["Your path"].md=pathMd();MENTORS.forEach(m=>{NOTES[m.name].md=mentorMd(m)});$("sheet").classList.remove("on");$("vault").classList.add("on");buildGraph();setTimeout(()=>$("vault").scrollIntoView({behavior:"smooth",block:"start"}),30);$("vcount").textContent=VN.length+" notes · "+VL.length+" links · tap a node, drag to arrange";
  const cv=$("vg");const pos=e=>{const r=cv.getBoundingClientRect();return [e.clientX-r.left,e.clientY-r.top]};let moved=false;
  cv.onpointerdown=e=>{const [x,y]=pos(e);const i=vpick(x,y);moved=false;if(i!==null){vdrag=VN[i];cv.setPointerCapture(e.pointerId)}};
  cv.onpointermove=e=>{if(!vdrag)return;const [x,y]=pos(e);vdrag.x=x;vdrag.y=y;vdrag.vx=vdrag.vy=0;moved=true};
  cv.onpointerup=e=>{if(vdrag&&!moved)vrender(vdrag.id);vdrag=null};
  vrender("Tonight");if(vraf)cancelAnimationFrame(vraf);vloop()};
let treeOn=false;
window.openTree=function(){openVault();if(!treeOn)toggleTree();vrender("Tech tree");renderTree()};
window.toggleTree=function(){treeOn=!treeOn;$("vtree").classList.toggle("on",treeOn);$("vg").style.display=treeOn?"none":"block";$("vmode").textContent=treeOn?"Graph":"Tech tree";if(treeOn)renderTree()};
function renderTree(){const col={dark:"#94A3B8",feudal:"#34D399",castle:"#F59E0B",imperial:"#C084FC",future:"#67E8F9"};const cur=vsel!==null&&VN[vsel]?VN[vsel].id:"";
  $("vtree").innerHTML='<div class="ages">'+AGES.map(([a,an,lv,d])=>`<div class="age"><div class="lvl">${lv}</div><h4>${an}</h4><p>${d}</p>${TREE[a].map(t=>`<button class="tech${t.n===cur?' sel':''}" data-n="${t.n}"><i style="background:${col[a]}"></i>${t.n}</button>`).join("")}</div>`).join("")+'</div>';
  $("vtree").querySelectorAll(".tech").forEach(b=>b.onclick=()=>{vrender(b.dataset.n);renderTree();$("vnote").scrollIntoView({behavior:"smooth",block:"start"})})}
window.closeVault=function(){const was=$("vault").classList.contains("on");$("vault").classList.remove("on");if(vraf)cancelAnimationFrame(vraf);vraf=null;if(was)window.scrollTo({top:0,behavior:"smooth"})};

/* ---------------- workstream logic ---------------- */
