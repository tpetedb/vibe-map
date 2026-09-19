window.exportProgress=function(){const code=btoa(unescape(encodeURIComponent(JSON.stringify({v:2,name:S.name,done:S.doneW.campus,doneW:S.doneW,path:S.path,artifacts:S.artifacts,mentors:S.mentors,artifactsBuilt:S.artifactsBuilt,items:sl("items"),ach:sl("ach"),wear:sl("wear"),interests:interestList(),topics:sl("topics"),pet:petId()})))).replace(/\+/g,"-").replace(/\//g,"_").replace(/=+$/,"");$("impcode").value=code;const paste="Code is in the box. In your camp: uv run vibe import, then paste it.";
  if(navigator.clipboard&&navigator.clipboard.writeText)navigator.clipboard.writeText(code).then(()=>{$("syncmsg").textContent="Code copied to your clipboard. In your camp: uv run vibe import, then paste it."},()=>{$("syncmsg").textContent=paste});else $("syncmsg").textContent=paste};
window.importProgress=function(){try{let c=$("impcode").value.trim().replace(/-/g,"+").replace(/_/g,"/");c+="=".repeat((4-c.length%4)%4);const d=JSON.parse(decodeURIComponent(escape(atob(c))));
    // The progress code is versioned: an unknown version is refused loudly.
    if(d.v!==2){$("syncmsg").textContent="That code is version "+(d.v===undefined?"1 or older":d.v)+"; this game reads version 2. Run uv run vibe export again with an up-to-date vibe.";return}
    // The companion is a single choice, not a set, so a code overwrites it;
    // an id this game has no pixels for is refused by name, never defaulted.
    if(d.pet!==undefined&&d.pet!==""){if(!petKnown(d.pet)){$("syncmsg").textContent="That code carries a companion this game does not have: \""+d.pet+"\". This game knows "+petOptions().join(", ")+".";return}S.pet=d.pet}
    const dw=d.doneW||{campus:d.done||[]};Object.keys(dw).forEach(w=>{if(!S.doneW[w])S.doneW[w]=[];dw[w].forEach(n=>{n=+n;if(n>=1&&n<=8&&!S.doneW[w].includes(n)){S.doneW[w].push(n);if(started&&w===S.world)placeBuilding(n,true)}})});Object.assign(S.path,d.path||{});(d.artifacts||[]).forEach(a=>{if(!S.artifacts.includes(a))S.artifacts.push(a)});(d.mentors||[]).forEach(m=>{if(!S.mentors.includes(m)){S.mentors.push(m);track("verified",m)}});(d.artifactsBuilt||[]).forEach(a=>{if(!S.artifactsBuilt.includes(a)){S.artifactsBuilt.push(a);track("built",a)}if(!S.artifacts.includes(a))S.artifacts.push(a)});if(started)placePlaques(true);
    // Added inside version 2: an older code carries none of these keys and a
    // newer reader simply finds nothing to merge.
    ["items","ach","wear","topics"].forEach(k=>(d[k]||[]).forEach(v=>{if(!sl(k).includes(v))sl(k).push(v)}));
    // An interest is a set: a code adds a shelf and never removes one, so a
    // choice made in the terminal is news here rather than a correction.
    if(Array.isArray(d.interests)&&d.interests.length){const cur=interestList().slice();
      d.interests.forEach(c=>{if(cur.indexOf(c)<0)cur.push(c)});S.interests=cur}
    if(started){(props.items||[]).filter(it=>sl("items").includes(it.id)).forEach(it=>{scene.remove(it.m);props.items=props.items.filter(x=>x!==it)});applyWear(chars.lotte,sl("wear"))}
    if(d.name)S.name=d.name;save();hud();renderMap();if(started)applySky(S.done.length,false);$("syncmsg").textContent="Imported: "+S.done.length+"/8 workstreams."}catch(e){$("syncmsg").textContent="That is not a valid code."}};
const playerPlate=()=>{const sp=chars.lotte&&chars.lotte.g.children.find(c=>c.isSprite);return sp?{text:sp.userData.text,fs:sp.userData.fs}:null};
window.__S=()=>S;
window.__plaques=()=>props.plaques||{};
// Test seam: the data the build injects, read-only, for the Playwright battery.
window.__data=()=>({worlds:WORLDS,artifacts:ARTIFACTS,mentors:MENTORS,config:CONFIG});
// Test seam: the demo scripts behind the artifact terminal, so a test can wait
// for the last line a demo types instead of guessing how long typing takes.
window.__demos=()=>ART_DEMOS;
// Test seam: read-only view of the walker for the Playwright battery, never written to.
// frame is the renderer's own frame counter: proximity, the camera and the pop-ins
// are sampled in the frame loop, so a test waits for frames, never for a wall clock.
// Test seam: the avatar's pose and the furniture on this island, read-only.
window.__avatar=()=>({pose:chars.lotte?chars.lotte.pose:null,seat:chars.lotte?chars.lotte.seatH||0:0,
  laptop:!!(chars.lotte&&chars.lotte.lap&&chars.lotte.lap.visible),
  onGround:(props.items||[]).map(i=>({id:i.id,x:i.x,z:i.z})),seats:(props.seats||[]).filter(s=>!s.taken).map(s=>({x:s.x,z:s.z})),
  sitting:(props.mentors||[]).filter(c=>c.pose==="sit").length,
  items:sl("items"),ach:sl("ach"),wear:sl("wear"),wearing:chars.lotte&&chars.lotte.wearG?chars.lotte.wearG.children.length:0});
window.__debug=()=>({pos:chars.lotte?chars.lotte.g.position.toArray():null,label:playerPlate(),near:nearK,started,world:S.world,bridges:bridges.map(b=>({a:b.a,b:b.b,open:b.open,near:b.near,len:b.len,pa:[b.pa.x,b.pa.z],pb:[b.pb.x,b.pb.z],mid:[b.mid.x,b.mid.z]})),onBridge:chars.lotte?!!onBridge(chars.lotte.g.position.x,chars.lotte.g.position.z):false,onLand:chars.lotte?onLandW(chars.lotte.g.position.x,chars.lotte.g.position.z):false,flying:!!flight,draws:renderer?renderer.info.render.calls:0,frame:renderer?renderer.info.render.frame:0,mentors:MENTORS.map(m=>({id:m.id,world:m.world,exercise:m.encounter.exercise.file,done:S.mentors.includes(m.id),seen:S.met[m.id]||0})),vault:()=>VSIM?{alpha:VSIM.alpha(),n:VN.length,sample:VN.slice(0,4).map(n=>[Math.round(n.x),Math.round(n.y)])}:null});
window.reset=function(){if(!confirm("Decommission the campus and reset to greenfield?"))return;try{localStorage.removeItem(KEY);localStorage.removeItem(OLD_KEY)}catch(e){}location.reload()};

