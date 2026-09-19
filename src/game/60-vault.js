// One colour per shelf of the tree; the same map drives the Obsidian graph groups.
const CAT_COL={shell:"#0067A5",git:"#FF8C1A",formats:"#FFBF00",code:"#00A86B",data:"#00D084",net:"#0088CC",ship:"#F04923",agents:"#D32F2F",docs:"#C29200",knowledge:"#FFA94D",future:"#CCCCCC"};
// Grow mode (config/camp.toml [vault] mode, or ?vault=grow for a look): the vault
// starts with the hubs and unlocks a note when the campaign earns it, the
// same rules as vibemap/grow.py. Locked notes keep their place in NOTES;
// they just do not enter the graph yet.
function vaultMode(){const q=new URLSearchParams(location.search).get("vault");if(q)return q;const s=(S.settings&&S.settings.vault)||"config";return s!=="config"?s:((CONFIG.vault&&CONFIG.vault.mode)||"full")}
// The same head start as vibemap/grow.py ALWAYS, minus the two notes only the
// written vault has (Map, Your field) and plus the two only the game has
// (Lotte, Beverage stack). Every other title is shared.
const ALWAYS_NOTES=["Tonight","Workstreams","Your path","Artifacts","Tech tree","Resources","Template repo","Terminal companion","Tom","Rolinda","Rolinda's questions","Lotte","Beverage stack"];
let UNLOCKED=null;
function linksOf(md){const out=[];const re=/\[\[([^\]|#]+)(?:[#|][^\]]*)?\]\]/g;let m;while((m=re.exec(md.replace(/```[\s\S]*?```/g,"").replace(/`[^`\n]*`/g,""))))out.push(m[1].trim());return out}
// Which note a claimed stop unlocks. Every evening but the campus names its
// note after the workstream; the campus stops carry the theme's own names, so
// they map by position to the notes written by hand in 50-notes.js.
function stopNote(w,n,byLower){if(w==="campus")return NOTES[CAMPUS_STOP_NOTES[n-1]]?CAMPUS_STOP_NOTES[n-1]:null;
  const ws=(CAMPAIGN[w]&&CAMPAIGN[w].ws[n-1])||null;return(ws&&byLower[ws.n.toLowerCase()])||null}
function computeUnlocked(){const keys=Object.keys(NOTES);if(vaultMode()!=="grow")return new Set(keys);const set=new Set(ALWAYS_NOTES.filter(k=>NOTES[k]));
  const byLower={};keys.forEach(k=>byLower[k.toLowerCase()]=k);
  Object.keys(S.doneW||{}).forEach(w=>{(S.doneW[w]||[]).forEach(n=>{const title=stopNote(w,n,byLower);if(title){set.add(title);linksOf(NOTES[title].md).forEach(t=>{if(NOTES[t])set.add(t)})}})});
  MENTORS.forEach(m=>{if(S.path[m.id]==="deep"&&NOTES[m.name])set.add(m.name)});
  (typeof ARTIFACTS==="undefined"?[]:ARTIFACTS).forEach(a=>{if(S.artifacts.includes(a.id))a.links.forEach(t=>{const k=noteId(t);if(NOTES[k])set.add(k)})});
  // A head start on what you chose: the basics of your shelves are open from
  // the first evening. Everything else still has to be earned.
  if(typeof TREE!=="undefined"&&!interestsAll())Object.keys(TREE).forEach(c=>{
    if(wantsShelf(c))TREE[c].filter(t=>t.d===1).forEach(t=>{if(NOTES[t.n])set.add(t.n)})});
  return set}
let VN=[],VL=[],vsel=null,vdrag=null,VSIM=null,vctx,vW,vH,vSW=0,vSH=0,vctxScale=1,vz=1,vtx=0,vty=0;
// A node's label hangs under it and is centred on it, so the simulation keeps
// half a label's width from the sides and a label's height from the bottom.
const VMX=54,VMY=30;
// The simulation runs unbounded and the view is fitted to where the nodes
// landed, labels included. Clamping them into the canvas instead piled a
// large vault into a solid row along the top and the bottom edge.
let vX0=0,vY0=0,vAR=1;
function vbounds(){let x0=0,y0=0,x1=vW,y1=vH;
  VN.forEach((n,i)=>{if(!i){x0=x1=n.x;y0=y1=n.y}
    x0=Math.min(x0,n.x);y0=Math.min(y0,n.y);x1=Math.max(x1,n.x);y1=Math.max(y1,n.y)});
  vX0=x0-VMX;vY0=y0-16;vSW=Math.max(1,x1-x0+VMX*2);vSH=Math.max(1,y1-y0+16+VMY)}
function vfit(){vbounds();vz=Math.min(1,vW/vSW,vH/vSH);vtx=(vW-vSW*vz)/2-vX0*vz;vty=(vH-vSH*vz)/2-vY0*vz}
const vToWorld=(sx,sy)=>[(sx-vtx)/vz,(sy-vty)/vz];
// The layout is a d3-force simulation: charge, links, a weak pull to the
// centre and collision. It cools and stops on its own; a drag or a fresh
// build reheats it. Nothing moves once alpha has decayed, so the graph settles.
function buildGraph(){
  UNLOCKED=computeUnlocked();VN=Object.keys(NOTES).filter(id=>UNLOCKED.has(id)).map((id,i)=>({id,t:NOTES[id].t,x:0,y:0,vx:0,vy:0,deg:0}));const idx={};VN.forEach((n,i)=>idx[n.id]=i);VL=[];
  VN.forEach(n=>{const re=/\[\[([^\]]+)\]\]/g;let m;const seen={};while((m=re.exec(NOTES[n.id].md))){const to=m[1];if(idx[to]!==undefined&&to!==n.id&&!seen[to]){seen[to]=1;VL.push([idx[n.id],idx[to]]);n.deg++;VN[idx[to]].deg++}}});
  const cv=$("vg");vW=cv.clientWidth;vH=cv.clientHeight;vAR=Math.sqrt(Math.max(vW,1)/Math.max(vH,1));vctxScale=Math.min(2,devicePixelRatio||1);cv.width=vW*vctxScale;cv.height=vH*vctxScale;vctx=cv.getContext("2d");
  VN.forEach((n,i)=>{const a=i/VN.length*Math.PI*2;n.x=vW/2+Math.cos(a)*Math.min(vW,vH)*.35;n.y=vH/2+Math.sin(a)*Math.min(vW,vH)*.35});
  if(VSIM)VSIM.stop();
  const r=n=>4+Math.min(10,n.deg*1.1);
  VSIM=d3.forceSimulation(VN)
    .force("link",d3.forceLink(VL.map(([source,target])=>({source,target}))).distance(l=>56+Math.min(40,(l.source.deg+l.target.deg)*2)).strength(.5))
    .force("charge",d3.forceManyBody().strength(n=>-90-n.deg*12).distanceMax(360))
    // The pull to the centre follows the canvas shape, so a wide panel gets a
    // wide cloud rather than a disc with empty margins on both sides.
    .force("x",d3.forceX(vW/2).strength(.045/vAR)).force("y",d3.forceY(vH/2).strength(.06*vAR))
    .force("collide",d3.forceCollide(n=>r(n)+9).iterations(2))
    .velocityDecay(.45).alphaDecay(.028)
    .on("tick",vdraw)
    .stop();
  VSIM.tick(160);
}
function vdraw(){
  const c=vctx;c.setTransform(vctxScale,0,0,vctxScale,0,0);c.clearRect(0,0,vW,vH);c.setTransform(vctxScale*vz,0,0,vctxScale*vz,vctxScale*vtx,vctxScale*vty);
  const nb=new Set();if(vsel!==null)VL.forEach(([i,j])=>{if(i===vsel)nb.add(j);if(j===vsel)nb.add(i)});
  VL.forEach(([i,j])=>{const a=VN[i],b=VN[j];const hot=vsel!==null&&(i===vsel||j===vsel);c.strokeStyle=hot?"rgba(0,136,204,.9)":"rgba(255,255,255,"+(vsel===null?.16:.06)+")";c.lineWidth=(hot?1.6:1)/vz;c.beginPath();c.moveTo(a.x,a.y);c.lineTo(b.x,b.y);c.stroke()});
  // Same legend as the Obsidian graph (docs/VAULT.md): workstreams green, people blue, concepts orange, ages by tier.
  const col=Object.assign({ws:"#00A86B",c:"#FF8C1A",p:"#0088CC"},CAT_COL);
  // The nodes first, so no label is painted under a circle.
  VN.forEach((n,i)=>{const r=4+Math.min(10,n.deg*1.1);const dim=vsel!==null&&i!==vsel&&!nb.has(i);c.globalAlpha=dim?.3:1;
    if(i===vsel){c.fillStyle="rgba(0,136,204,.25)";c.beginPath();c.arc(n.x,n.y,r+8,0,7);c.fill()}
    c.fillStyle=col[n.t];c.beginPath();c.arc(n.x,n.y,r,0,7);c.fill();
    c.globalAlpha=1});
  // Labels: the selection and its neighbours always, then the rest by degree,
  // the hubs first. A label whose box lands on one already drawn is dropped,
  // so a dense patch stays readable instead of turning into a smear. The
  // degree floor only thins what is offered; collision does the rest.
  const small=Math.min(vW,vH)<520;
  const minDeg=vz<.9?2:1;
  const boxes=[];
  const free=(x,y,w,h)=>{const b=[x-w/2-3,y-h,x+w/2+3,y+3];
    for(const o of boxes)if(b[0]<o[2]&&b[2]>o[0]&&b[1]<o[3]&&b[3]>o[1])return false;
    boxes.push(b);return true};
  const order=VN.map((n,i)=>i).sort((a,b)=>{
    const pa=a===vsel?2:nb.has(a)?1:0,pb=b===vsel?2:nb.has(b)?1:0;
    return pb-pa||VN[b].deg-VN[a].deg});
  // Labels are drawn in screen space, so the type stays readable and two of
  // them collide when the reader sees them collide, not when the layout does.
  c.setTransform(vctxScale,0,0,vctxScale,0,0);
  order.forEach(i=>{const n=VN[i];const r=4+Math.min(10,n.deg*1.1);const dim=vsel!==null&&i!==vsel&&!nb.has(i);
    const near=i===vsel||nb.has(i);
    if(!near&&(dim||r*vz<(small?9:5.5)||n.deg<minDeg))return;
    c.font=(i===vsel?"600 ":"")+"11px Inter,sans-serif";c.textAlign="center";
    // Keep the whole label on the canvas, whatever the pan and the zoom.
    const w=c.measureText(n.id).width,lo=w/2+4,hi=vW-w/2-4;
    const x=Math.max(lo,Math.min(hi,n.x*vz+vtx)),y=n.y*vz+vty+r*vz+13;
    // Only the selection is worth a label on top of another one; a neighbour
    // that cannot be placed is dropped like any other.
    if(!free(x,y,w,13)&&i!==vsel)return;
    c.globalAlpha=dim?.3:1;c.fillStyle="#dcddde";c.fillText(n.id,x,y);c.globalAlpha=1});
}
function vpick(x,y){let best=null,bd=22/vz;VN.forEach((n,i)=>{const d=Math.hypot(n.x-x,n.y-y);if(d<bd){bd=d;best=i}});return best}
// A handful of topics are covered by a note written by hand under a shorter
// name (NOTE_ALIAS, from the tree generator). The campaign data and the tech
// tree name the topic; every way into the vault goes through this.
function noteId(t){return(typeof NOTE_ALIAS!=="undefined"&&NOTE_ALIAS[t])||t}
// A note that grow mode has not earned yet. The one rule for the whole vault:
// a wikilink, a graph node and a tech tree button all ask this.
const LOCK_WHY="Not unlocked yet: finish the stop, meet the mentor or inspect the artifact that leads here";
function noteLocked(id){return !!(UNLOCKED&&NOTES[id]&&!UNLOCKED.has(id))}
// A link into the vault: a real one, or a dead end that says so rather than
// throwing. Both are keyboard reachable, so the vault is not mouse-only.
function wlSpan(t){return noteLocked(t)?'<span class="wl locked" title="'+LOCK_WHY+'">'+t+"</span>"
  :'<span class="wl" role="link" tabindex="0" data-n="'+esc(t)+'">'+t+"</span>"}
// The panel the vault shows when there is no note to render.
function vcard(title,body){vsel=null;$("vnote").innerHTML="<h1>"+esc(title)+'</h1><p class="muted">'+body+"</p>";$("vnote").scrollTop=0;if(vctx)vdraw()}
function vrender(raw){
  const id=noteId(raw);
  // A title no note carries is a dead link in the data, not a crash.
  if(!NOTES[id])return vcard(id,"No note by that name in this vault yet.");
  if(noteLocked(id))return vcard(id,LOCK_WHY+".");
  const i=VN.findIndex(n=>n.id===id);vsel=i<0?null:i;const md=NOTES[id].md;
  let html=md.split("\n").map(l=>{
    if(l.startsWith("# "))return "<h1>"+l.slice(2)+"</h1>";
    if(l.startsWith("- "))return "<li>"+l.slice(2)+"</li>";
    // A tag line is one or more tags, so "#tech #shell" renders like "#tech".
    if(/^#[^\s#]+(\s+#[^\s#]+)*$/.test(l))return l.split(/\s+/).map(t=>'<span class="tag">'+t+"</span>").join("");
    return l?"<p>"+l+"</p>":""}).join("").replace(/<\/li><li>/g,"</li><li>").replace(/(<li>.*?<\/li>)+/g,m=>"<ul>"+m+"</ul>");
  html=html.replace(/\*\*(.+?)\*\*/g,"<b>$1</b>").replace(/\*([^*\n]+)\*/g,"<i>$1</i>").replace(/`(.+?)`/g,"<code>$1</code>").replace(/\[([^\]]+)\]\((https?:[^)]+)\)/g,'<a href="$2" target="_blank" rel="noopener">$1</a>').replace(/\[\[([^\]]+)\]\]/g,(m,t)=>{const k=noteId(t);return NOTES[k]?wlSpan(k):t});
  const back=VN.filter(n=>n.id!==id&&NOTES[n.id].md.includes("[["+id+"]]")).map(n=>wlSpan(n.id)).join("");
  html+='<div class="bl"><h2>Linked from</h2>'+(back||'<span class="muted">nothing yet</span>')+'</div>';
  $("vnote").innerHTML=html;$("vnote").scrollTop=0;
  $("vnote").querySelectorAll(".wl:not(.locked)").forEach(e=>{const go=()=>vrender(e.dataset.n);
    e.onclick=go;e.onkeydown=ev=>{if(ev.key==="Enter"||ev.key===" "){ev.preventDefault();go()}}});
  if(vctx)vdraw();
}
// The header line describes what is on screen, so it follows the Graph and
// Tech tree switch rather than the moment the vault opened.
function vhint(){const n=vaultMode()==="grow"?VN.length+" of "+Object.keys(NOTES).length+" notes unlocked":VN.length+" notes";
  return n+" · "+VL.length+" links · "+(treeOn?"pick a topic to read it":"tap a node, drag to arrange")}
window.openVault=function(){NOTES["Your path"].md=pathMd();NOTES["Artifacts"].md=artifactsMd();MENTORS.forEach(m=>{NOTES[m.name].md=mentorMd(m)});$("sheet").classList.remove("on");$("vault").classList.add("on");fx($("vault"));buildGraph();setTimeout(()=>$("vault").scrollIntoView({behavior:"smooth",block:"start"}),30);$("vcount").textContent=vhint();
  const cv=$("vg");const pos=e=>{const r=cv.getBoundingClientRect();return [e.clientX-r.left,e.clientY-r.top]};let moved=false;
  let pan=null;vfit();
  cv.onpointerdown=e=>{const [sx,sy]=pos(e);const [x,y]=vToWorld(sx,sy);const i=vpick(x,y);moved=false;cv.setPointerCapture(e.pointerId);if(i!==null){vdrag=VN[i];vdrag.fx=vdrag.x;vdrag.fy=vdrag.y}else pan={sx,sy,tx:vtx,ty:vty}};
  cv.onpointermove=e=>{const [sx,sy]=pos(e);if(vdrag){if(!moved){moved=true;VSIM.alphaTarget(.25).restart()}const [x,y]=vToWorld(sx,sy);vdrag.fx=x;vdrag.fy=y}else if(pan){moved=true;vtx=pan.tx+(sx-pan.sx);vty=pan.ty+(sy-pan.sy);vdraw()}};
  cv.onpointerup=e=>{if(vdrag){if(!moved)vrender(vdrag.id);else VSIM.alphaTarget(0);vdrag.fx=vdrag.fy=null;vdrag=null}pan=null};
  cv.onwheel=e=>{e.preventDefault();const [sx,sy]=pos(e);const f=Math.exp(-e.deltaY*.0015);const nz=Math.max(.4,Math.min(3,vz*f));const k=nz/vz;vtx=sx-(sx-vtx)*k;vty=sy-(sy-vty)*k;vz=nz;vdraw()};
  vrender("Tonight");VSIM.alpha(.6).restart()};
let treeOn=false;
window.openTree=function(){openVault();if(!treeOn)toggleTree();vrender("Tech tree");renderTree()};
window.toggleTree=function(){treeOn=!treeOn;$("vtree").classList.toggle("on",treeOn);$("vg").style.display=treeOn?"none":"block";$("vmode").innerHTML=icon(treeOn?"book-open":"git-branch")+(treeOn?"Graph":"Tech tree");$("vcount").textContent=vhint();if(treeOn)renderTree()};
window.treeScroll=function(d){const el=$("vtree");el.scrollBy({left:d*el.clientWidth*.8,behavior:motionOff()?"auto":"smooth"})};
// Chosen shelves come first and keep their colour; the rest stay in the same
// list, dimmed. Nothing is hidden or locked: an interest is an order, not a gate.
function treeShelves(){const cats=CATS.slice();if(interestsAll())return cats;
  return cats.filter(([c])=>wantsShelf(c)).concat(cats.filter(([c])=>!wantsShelf(c)))}
function renderTree(){const cur=vsel!==null&&VN[vsel]?VN[vsel].id:"";
  $("vtree").innerHTML='<div class="treenav"><button onclick="treeScroll(-1)" aria-label="Earlier ages">Earlier</button><button onclick="treeScroll(1)" aria-label="Later ages">Later</button><span class="small muted">'+(interestsAll()?"Eleven shelves, side by side. Scroll or use the buttons.":"Your shelves first, the rest dimmed and still open. Settings changes them.")+'</span></div><div class="ages">'+treeShelves().map(([c,cn,d])=>`<div class="age${wantsShelf(c)?"":" faded"}"><div class="lvl">${TREE[c].length} topics</div><h4>${cn}</h4><p>${d}</p>${TREE[c].map(t=>`<button class="tech${t.n===cur?' sel':''}${noteLocked(t.n)?' locked':''}" data-n="${t.n}"${noteLocked(t.n)?` title="${LOCK_WHY}"`:""}><i style="background:${CAT_COL[c]}"></i>${t.n}<em class="d d${t.d}">${DEPTHS[t.d]}</em></button>`).join("")}</div>`).join("")+'</div>';
  $("vtree").querySelectorAll(".tech").forEach(b=>b.onclick=()=>{vrender(b.dataset.n);renderTree();$("vnote").scrollIntoView({behavior:"smooth",block:"start"})})}
// Only a file:// game knows where the vault folder is; over http the button
// sends you to the same notes on GitHub, and says so.
window.openObsidian=function(){
  if(location.protocol==="file:"){const dir=decodeURIComponent(location.pathname).replace(/\/game\/[^/]*$/,"");location.href="obsidian://open?path="+encodeURIComponent(dir+"/vault/Camp/Tonight.md");
    $("vcount").textContent="Opening Obsidian. First time: Open folder as vault, pick vault/.";return}
  window.open((CONFIG.repo||"https://github.com/tpetedb/vibe-map")+"/tree/main/vault/Camp","_blank","noopener")};
// Open the vault on a note; inline handlers and tests reach it by name.
window.openNote=function(title){openVault();vrender(title)};
// Read-only seam for the tests: the graph is a canvas, so its selection, its
// unlocked set and where its nodes landed have no DOM to assert on.
window.__vault=()=>({sel:vsel,unlocked:VN.length,total:Object.keys(NOTES).length,
  has:t=>!!(UNLOCKED&&UNLOCKED.has(t)),nodes:VN.map(n=>({x:n.x,y:n.y})),width:vSW,height:vSH});
window.closeVault=function(){const was=$("vault").classList.contains("on");$("vault").classList.remove("on");if(VSIM)VSIM.stop();if(was)window.scrollTo({top:0,behavior:"smooth"})};

/* ---------------- workstream logic ---------------- */
