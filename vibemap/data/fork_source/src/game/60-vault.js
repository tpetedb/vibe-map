// One colour per shelf of the tree; the same map drives the Obsidian graph groups.
const CAT_COL={shell:"#0067A5",git:"#FF8C1A",formats:"#FFBF00",code:"#00A86B",data:"#00D084",net:"#0088CC",ship:"#F04923",agents:"#D32F2F",docs:"#C29200",knowledge:"#FFA94D",future:"#CCCCCC"};
// Grow mode (vibe.toml [vault] mode, or ?vault=grow for a look): the vault
// starts with the hubs and unlocks a note when the campaign earns it, the
// same rules as vibemap/grow.py. Locked notes keep their place in NOTES;
// they just do not enter the graph yet.
function vaultMode(){const q=new URLSearchParams(location.search).get("vault");if(q)return q;const s=(S.settings&&S.settings.vault)||"config";return s!=="config"?s:((CONFIG.vault&&CONFIG.vault.mode)||"full")}
const ALWAYS_NOTES=["Tonight","Workstreams","Your path","Artifacts","Tech tree","Resources","Template repo","Terminal companion","Tom","Rolinda","Rolinda's questions","Lotte","Beverage stack"];
let UNLOCKED=null;
function linksOf(md){const out=[];const re=/\[\[([^\]|#]+)(?:[#|][^\]]*)?\]\]/g;let m;while((m=re.exec(md.replace(/```[\s\S]*?```/g,"").replace(/`[^`\n]*`/g,""))))out.push(m[1].trim());return out}
function computeUnlocked(){const keys=Object.keys(NOTES);if(vaultMode()!=="grow")return new Set(keys);const set=new Set(ALWAYS_NOTES.filter(k=>NOTES[k]));
  const byLower={};keys.forEach(k=>byLower[k.toLowerCase()]=k);
  Object.keys(S.doneW||{}).forEach(w=>{(S.doneW[w]||[]).forEach(n=>{const ws=(CAMPAIGN[w]&&CAMPAIGN[w].ws[n-1])||null;const title=ws&&byLower[ws.n.toLowerCase()];if(title){set.add(title);linksOf(NOTES[title].md).forEach(t=>{if(NOTES[t])set.add(t)})}})});
  MENTORS.forEach(m=>{if(S.path[m.id]==="deep"&&NOTES[m.name])set.add(m.name)});
  (typeof ARTIFACTS==="undefined"?[]:ARTIFACTS).forEach(a=>{if(S.artifacts.includes(a.id))a.links.forEach(t=>{if(NOTES[t])set.add(t)})});
  return set}
let VN=[],VL=[],vsel=null,vdrag=null,VSIM=null,vctx,vW,vH,vctxScale=1,vz=1,vtx=0,vty=0;
// A node's label hangs under it and is centred on it, so the simulation keeps
// half a label's width from the sides and a label's height from the bottom.
const VMX=54,VMY=30;
const vToWorld=(sx,sy)=>[(sx-vtx)/vz,(sy-vty)/vz];
// The layout is a d3-force simulation: charge, links, a weak pull to the
// centre and collision. It cools and stops on its own; a drag or a fresh
// build reheats it. Nothing moves once alpha has decayed, so the graph settles.
function buildGraph(){
  UNLOCKED=computeUnlocked();VN=Object.keys(NOTES).filter(id=>UNLOCKED.has(id)).map((id,i)=>({id,t:NOTES[id].t,x:0,y:0,vx:0,vy:0,deg:0}));const idx={};VN.forEach((n,i)=>idx[n.id]=i);VL=[];
  VN.forEach(n=>{const re=/\[\[([^\]]+)\]\]/g;let m;const seen={};while((m=re.exec(NOTES[n.id].md))){const to=m[1];if(idx[to]!==undefined&&to!==n.id&&!seen[to]){seen[to]=1;VL.push([idx[n.id],idx[to]]);n.deg++;VN[idx[to]].deg++}}});
  const cv=$("vg");vW=cv.clientWidth;vH=cv.clientHeight;vctxScale=Math.min(2,devicePixelRatio||1);cv.width=vW*vctxScale;cv.height=vH*vctxScale;vctx=cv.getContext("2d");
  VN.forEach((n,i)=>{const a=i/VN.length*Math.PI*2;n.x=vW/2+Math.cos(a)*Math.min(vW,vH)*.35;n.y=vH/2+Math.sin(a)*Math.min(vW,vH)*.35});
  if(VSIM)VSIM.stop();
  const r=n=>4+Math.min(10,n.deg*1.1);
  VSIM=d3.forceSimulation(VN)
    .force("link",d3.forceLink(VL.map(([source,target])=>({source,target}))).distance(l=>56+Math.min(40,(l.source.deg+l.target.deg)*2)).strength(.5))
    .force("charge",d3.forceManyBody().strength(n=>-90-n.deg*12).distanceMax(360))
    .force("x",d3.forceX(vW/2).strength(.045)).force("y",d3.forceY(vH/2).strength(.06))
    .force("collide",d3.forceCollide(n=>r(n)+9).iterations(2))
    .velocityDecay(.45).alphaDecay(.028)
    .on("tick",()=>{VN.forEach(n=>{n.x=Math.max(VMX,Math.min(vW-VMX,n.x));n.y=Math.max(16,Math.min(vH-VMY,n.y))});vdraw()})
    .stop();
  VSIM.tick(160);
}
function vdraw(){
  const c=vctx;c.setTransform(vctxScale,0,0,vctxScale,0,0);c.clearRect(0,0,vW,vH);c.setTransform(vctxScale*vz,0,0,vctxScale*vz,vctxScale*vtx,vctxScale*vty);
  const nb=new Set();if(vsel!==null)VL.forEach(([i,j])=>{if(i===vsel)nb.add(j);if(j===vsel)nb.add(i)});
  VL.forEach(([i,j])=>{const a=VN[i],b=VN[j];const hot=vsel!==null&&(i===vsel||j===vsel);c.strokeStyle=hot?"rgba(0,136,204,.9)":"rgba(255,255,255,"+(vsel===null?.16:.06)+")";c.lineWidth=(hot?1.6:1)/vz;c.beginPath();c.moveTo(a.x,a.y);c.lineTo(b.x,b.y);c.stroke()});
  // Same legend as the Obsidian graph (docs/VAULT.md): workstreams green, people blue, concepts orange, ages by tier.
  const col=Object.assign({ws:"#00A86B",c:"#FF8C1A",p:"#0088CC"},CAT_COL);
  // Labels: the selection and its neighbours always; the rest only when the
  // node is big enough on screen, so a phone shows hubs and a zoom shows all.
  const small=Math.min(vW,vH)<520;
  // Zoomed out, only the hubs are labelled; everything else would overlap.
  const minDeg=vz<.9?3:vz<1.4?2:1;
  VN.forEach((n,i)=>{const r=4+Math.min(10,n.deg*1.1);const dim=vsel!==null&&i!==vsel&&!nb.has(i);c.globalAlpha=dim?.3:1;
    if(i===vsel){c.fillStyle="rgba(0,136,204,.25)";c.beginPath();c.arc(n.x,n.y,r+8,0,7);c.fill()}
    c.fillStyle=col[n.t];c.beginPath();c.arc(n.x,n.y,r,0,7);c.fill();
    const label=i===vsel||nb.has(i)||(!dim&&r*vz>=(small?9:5.5)&&n.deg>=minDeg);
    if(label){c.fillStyle="#dcddde";c.font=(i===vsel?"600 ":"")+"11px Inter,sans-serif";c.textAlign="center";
      // Keep the whole label on the canvas, whatever the pan and the zoom.
      const half=c.measureText(n.id).width/2,lo=(-vtx)/vz+half+4,hi=(vW-vtx)/vz-half-4;
      c.fillText(n.id,Math.max(lo,Math.min(hi,n.x)),n.y+r+13)}
    c.globalAlpha=1});
}
function vpick(x,y){let best=null,bd=22/vz;VN.forEach((n,i)=>{const d=Math.hypot(n.x-x,n.y-y);if(d<bd){bd=d;best=i}});return best}
function vrender(id){
  vsel=VN.findIndex(n=>n.id===id);const md=NOTES[id].md;
  let html=md.split("\n").map(l=>{
    if(l.startsWith("# "))return "<h1>"+l.slice(2)+"</h1>";
    if(l.startsWith("- "))return "<li>"+l.slice(2)+"</li>";
    if(l.startsWith("#")&&!l.includes(" "))return '<span class="tag">'+l+"</span>";
    return l?"<p>"+l+"</p>":""}).join("").replace(/<\/li><li>/g,"</li><li>").replace(/(<li>.*?<\/li>)+/g,m=>"<ul>"+m+"</ul>");
  html=html.replace(/\*\*(.+?)\*\*/g,"<b>$1</b>").replace(/`(.+?)`/g,"<code>$1</code>").replace(/\[([^\]]+)\]\((https?:[^)]+)\)/g,'<a href="$2" target="_blank" rel="noopener">$1</a>').replace(/\[\[([^\]]+)\]\]/g,(m,t)=>NOTES[t]?(UNLOCKED&&!UNLOCKED.has(t)?'<span class="wl locked" title="Not unlocked yet: finish the stop, meet the mentor or inspect the artifact that leads here">'+t+'</span>':'<span class="wl" data-n="'+t+'">'+t+'</span>'):t);
  const back=VN.filter(n=>n.id!==id&&NOTES[n.id].md.includes("[["+id+"]]")).map(n=>'<span class="wl" data-n="'+n.id+'">'+n.id+'</span>').join("");
  html+='<div class="bl"><h2>Linked from</h2>'+(back||'<span class="muted">nothing yet</span>')+'</div>';
  $("vnote").innerHTML=html;$("vnote").scrollTop=0;$("vnote").querySelectorAll(".wl:not(.locked)").forEach(e=>e.onclick=()=>vrender(e.dataset.n));
  if(vctx)vdraw();
}
window.openVault=function(){NOTES["Your path"].md=pathMd();NOTES["Artifacts"].md=artifactsMd();MENTORS.forEach(m=>{NOTES[m.name].md=mentorMd(m)});$("sheet").classList.remove("on");$("vault").classList.add("on");fx($("vault"));buildGraph();setTimeout(()=>$("vault").scrollIntoView({behavior:"smooth",block:"start"}),30);$("vcount").textContent=(vaultMode()==="grow"?VN.length+" of "+Object.keys(NOTES).length+" notes unlocked · ":VN.length+" notes · ")+VL.length+" links · tap a node, drag to arrange";
  const cv=$("vg");const pos=e=>{const r=cv.getBoundingClientRect();return [e.clientX-r.left,e.clientY-r.top]};let moved=false;
  let pan=null;vz=1;vtx=0;vty=0;
  cv.onpointerdown=e=>{const [sx,sy]=pos(e);const [x,y]=vToWorld(sx,sy);const i=vpick(x,y);moved=false;cv.setPointerCapture(e.pointerId);if(i!==null){vdrag=VN[i];vdrag.fx=vdrag.x;vdrag.fy=vdrag.y}else pan={sx,sy,tx:vtx,ty:vty}};
  cv.onpointermove=e=>{const [sx,sy]=pos(e);if(vdrag){if(!moved){moved=true;VSIM.alphaTarget(.25).restart()}const [x,y]=vToWorld(sx,sy);vdrag.fx=x;vdrag.fy=y}else if(pan){moved=true;vtx=pan.tx+(sx-pan.sx);vty=pan.ty+(sy-pan.sy);vdraw()}};
  cv.onpointerup=e=>{if(vdrag){if(!moved)vrender(vdrag.id);else VSIM.alphaTarget(0);vdrag.fx=vdrag.fy=null;vdrag=null}pan=null};
  cv.onwheel=e=>{e.preventDefault();const [sx,sy]=pos(e);const f=Math.exp(-e.deltaY*.0015);const nz=Math.max(.4,Math.min(3,vz*f));const k=nz/vz;vtx=sx-(sx-vtx)*k;vty=sy-(sy-vty)*k;vz=nz;vdraw()};
  vrender("Tonight");VSIM.alpha(.6).restart()};
let treeOn=false;
window.openTree=function(){openVault();if(!treeOn)toggleTree();vrender("Tech tree");renderTree()};
window.toggleTree=function(){treeOn=!treeOn;$("vtree").classList.toggle("on",treeOn);$("vg").style.display=treeOn?"none":"block";$("vmode").innerHTML=icon(treeOn?"book-open":"git-branch")+(treeOn?"Graph":"Tech tree");if(treeOn)renderTree()};
window.treeScroll=function(d){const el=$("vtree");el.scrollBy({left:d*el.clientWidth*.8,behavior:motionOff()?"auto":"smooth"})};
function renderTree(){const cur=vsel!==null&&VN[vsel]?VN[vsel].id:"";
  $("vtree").innerHTML='<div class="treenav"><button onclick="treeScroll(-1)" aria-label="Earlier ages">Earlier</button><button onclick="treeScroll(1)" aria-label="Later ages">Later</button><span class="small muted">Eleven ages, side by side. Scroll or use the buttons.</span></div><div class="ages">'+CATS.map(([c,cn,d])=>`<div class="age"><div class="lvl">${TREE[c].length} topics</div><h4>${cn}</h4><p>${d}</p>${TREE[c].map(t=>`<button class="tech${t.n===cur?' sel':''}" data-n="${t.n}"><i style="background:${CAT_COL[c]}"></i>${t.n}<em class="d d${t.d}">${DEPTHS[t.d]}</em></button>`).join("")}</div>`).join("")+'</div>';
  $("vtree").querySelectorAll(".tech").forEach(b=>b.onclick=()=>{vrender(b.dataset.n);renderTree();$("vnote").scrollIntoView({behavior:"smooth",block:"start"})})}
// Only a file:// game knows where the vault folder is; over http the button
// sends you to the same notes on GitHub, and says so.
window.openObsidian=function(){
  if(location.protocol==="file:"){const dir=decodeURIComponent(location.pathname).replace(/\/game\/[^/]*$/,"");location.href="obsidian://open?path="+encodeURIComponent(dir+"/vault/Camp/Tonight.md");
    $("vcount").textContent="Opening Obsidian. First time: Open folder as vault, pick vault/.";return}
  window.open((CONFIG.repo||"https://github.com/tpetedb/vibe-map")+"/tree/main/vault/Camp","_blank","noopener")};
// Open the vault on a note; inline handlers and tests reach it by name.
window.openNote=function(title){openVault();vrender(title)};
window.closeVault=function(){const was=$("vault").classList.contains("on");$("vault").classList.remove("on");if(VSIM)VSIM.stop();if(was)window.scrollTo({top:0,behavior:"smooth"})};

/* ---------------- workstream logic ---------------- */
