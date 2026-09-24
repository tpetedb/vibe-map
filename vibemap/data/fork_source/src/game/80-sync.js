// The command a camp really has: `vibe import` takes the code as its argument,
// there is nothing to paste into. The box shows about thirty of two thousand
// characters, so the code is selected as well as copied and a browser that
// refuses the clipboard still leaves one keystroke that works.
const IMPORT_CMD="in your camp: vibe import <code>, with the code pasted in place of <code>.";
window.exportProgress=function(){const code=btoa(unescape(encodeURIComponent(JSON.stringify({v:2,name:S.name,done:S.doneW.campus,doneW:S.doneW,path:S.path,artifacts:S.artifacts,mentors:S.mentors,artifactsBuilt:S.artifactsBuilt,items:sl("items"),ach:sl("ach"),wear:sl("wear"),interests:interestList(),topics:sl("topics"),pet:petId()})))).replace(/\+/g,"-").replace(/\//g,"_").replace(/=+$/,"");
  // The moment a code exists is the moment the evening has a copy outside
  // this browser, so the export line in the Roadmap can stand down.
  S.exportedAt=Date.now();S.exportedN=totalDone();save();
  const box=$("impcode");box.value=code;box.focus();box.select();
  const paste="Code is in the box and selected. Press "+copyKey()+" to copy it, then "+IMPORT_CMD;
  if(navigator.clipboard&&navigator.clipboard.writeText)navigator.clipboard.writeText(code).then(()=>{$("syncmsg").textContent="Code copied to your clipboard. Then "+IMPORT_CMD},()=>{$("syncmsg").textContent=paste});else $("syncmsg").textContent=paste};
// A code is pasted from a mail or a chat, so it is outside data. Every id in
// it is checked before anything is merged: the name of the first field that
// is not what the format says, or "" when the code is sound.
const CODE_ID_LISTS=["artifacts","mentors","artifactsBuilt","items","ach","wear","topics","interests"];
function progressFault(d){
  const bad=CODE_ID_LISTS.find(k=>d[k]!==undefined&&!(Array.isArray(d[k])&&d[k].every(plainId)));if(bad)return bad;
  if(d.name!==undefined&&typeof d.name!=="string")return "name";
  if(d.pet!==undefined&&typeof d.pet!=="string")return "pet";
  if(d.done!==undefined&&!(Array.isArray(d.done)&&d.done.every(n=>typeof n==="number")))return "done";
  if(d.doneW!==undefined&&!(isMap(d.doneW)&&Object.keys(d.doneW).every(w=>plainId(w)&&Array.isArray(d.doneW[w])&&d.doneW[w].every(n=>typeof n==="number"))))return "doneW";
  if(d.path!==undefined&&!(isMap(d.path)&&Object.keys(d.path).every(m=>plainId(m)&&(d.path[m]==="deep"||d.path[m]==="skip"))))return "path";
  return ""}
window.importProgress=function(){try{let c=$("impcode").value.trim().replace(/-/g,"+").replace(/_/g,"/");c+="=".repeat((4-c.length%4)%4);const d=JSON.parse(decodeURIComponent(escape(atob(c))));
    // The progress code is versioned: an unknown version is refused loudly,
    // and the refusal names the side that is behind. A version that is not a
    // number is not a version, so it is refused too, the way the CLI does.
    if(typeof d.v!=="number"&&d.v!==undefined){$("syncmsg").textContent="That code does not say which version it is, so this game cannot read it. Run vibe export again and paste the whole code.";return}
    if(d.v>2){$("syncmsg").textContent="That code is version "+d.v+" and this game reads version 2, so the game is the old side. Rebuild it with just build, or open a newer copy.";return}
    if(d.v!==2){$("syncmsg").textContent="That code is version "+(d.v===undefined?"1 or older":d.v)+"; this game reads version 2. Run vibe export again with an up-to-date vibe.";return}
    // Refused whole and by name: a code that fails here merges nothing.
    const fault=progressFault(d);if(fault){$("syncmsg").textContent="That code carries a value this game cannot read, in \""+fault+"\". Nothing was imported. Run vibe export again and paste the whole code.";return}
    // An island this game does not build has no stops to unlock and no
    // buildings to place, so it is refused by name rather than written in.
    const dw=d.doneW||{campus:d.done||[]};
    const alien=Object.keys(dw).find(w=>!CAMPAIGN[w]);
    if(alien){$("syncmsg").textContent="That code carries an island this game does not have: \""+alien+"\". This game has "+Object.keys(CAMPAIGN).join(", ")+".";return}
    // The companion is a single choice, not a set, so a code overwrites it;
    // an id this game has no pixels for is refused by name, never defaulted.
    if(d.pet!==undefined&&d.pet!==""){if(!petKnown(d.pet)){$("syncmsg").textContent="That code carries a companion this game does not have: \""+d.pet+"\". This game knows "+petOptions().join(", ")+".";return}S.pet=d.pet}
    // What the merge actually added, counted as it goes: a code carrying only
    // mentors or only artifacts merged something, and the confirmation says so
    // instead of reporting the workstreams it never touched.
    const got={};const won=(k,n)=>{got[k]=(got[k]||0)+(n===undefined?1:n)};
    // Stops that arrive in a code already live in one, so the export line
    // counts them as carried: only what this browser added on its own is not.
    const carried=totalDone()-exportDue().n;
    // How many stops an island has is the campaign's to say, so a camp that
    // adds a ninth stop can send it and a code cannot invent one.
    Object.keys(dw).forEach(w=>{const stops=CAMPAIGN[w].ws.length;if(!S.doneW[w])S.doneW[w]=[];dw[w].forEach(n=>{if(n>=1&&n<=stops&&!S.doneW[w].includes(n)){S.doneW[w].push(n);won("stop");if(started&&w===S.world)placeBuilding(n,true)}})});Object.assign(S.path,d.path||{});(d.artifacts||[]).forEach(a=>{if(!S.artifacts.includes(a)){S.artifacts.push(a);won("artifact")}});(d.mentors||[]).forEach(m=>{if(!S.mentors.includes(m)){S.mentors.push(m);won("mentor");track("verified",m)}});(d.artifactsBuilt||[]).forEach(a=>{if(!S.artifactsBuilt.includes(a)){S.artifactsBuilt.push(a);won("build");track("built",a)}if(!S.artifacts.includes(a))S.artifacts.push(a)});if(started)placePlaques(true);
    // Added inside version 2: an older code carries none of these keys and a
    // newer reader simply finds nothing to merge.
    [["items","collectible"],["ach","badge"],["topics","topic"]].forEach(([k,n])=>(d[k]||[]).forEach(v=>{if(!sl(k).includes(v)){sl(k).push(v);won(n)}}));
    // A wearable is worn only once its badge is earned: a code and the Wardrobe
    // answer to the same rule, so the walker never carries what the pack calls
    // locked. The badges are merged first, so a code that brings both works.
    (d.wear||[]).forEach(v=>{if(wearOwned(v)&&!sl("wear").includes(v)){sl("wear").push(v);won("worn item")}});
    // An interest is a set: a code adds a shelf and never removes one, so a
    // choice made in the terminal is news here rather than a correction.
    if(Array.isArray(d.interests)&&d.interests.length){const cur=interestList().slice();
      d.interests.forEach(c=>{if(cur.indexOf(c)<0)cur.push(c)});S.interests=cur}
    if(started){(props.items||[]).filter(it=>sl("items").includes(it.id)).forEach(it=>{discard(it.m);props.items=props.items.filter(x=>x!==it)});applyWear(chars.lotte,sl("wear"))}
    // A camp nobody named exports the placeholder, which is not a person: the
    // same rule as a saved record, so the HUD never reads "<YOUR_NAME>".
    if(d.name!==undefined){const n=cleanName(d.name);if(n)S.name=n}if(got.stop)S.exportedN=carried+got.stop;save();hud();renderMap();if(started)applySky(S.done.length,false);
    const parts=Object.keys(got).map(k=>got[k]+" "+k+(got[k]===1?"":"s"));
    $("syncmsg").textContent=(parts.length?"Imported: "+parts.join(", ")+". ":"That code held nothing new. ")+
      S.done.length+"/"+stopCount()+" workstreams on this island."}catch(e){$("syncmsg").textContent="That is not a valid code."}};
const playerPlate=()=>{const sp=chars.lotte&&chars.lotte.g.children.find(c=>c.isSprite);return sp?{text:sp.userData.text,fs:sp.userData.fs}:null};
window.__S=()=>S;
// Test seam: the field of the saved record that had to be repaired on load,
// "" when the record was sound.
window.__loadFault=()=>loadFault;
window.__plaques=()=>props.plaques||{};
// Test seam: the data the build injects, read-only, for the Playwright battery.
window.__data=()=>({worlds:WORLDS,artifacts:ARTIFACTS,mentors:MENTORS,campaign:CAMPAIGN,config:CONFIG,scale:WORLD_SCALE});
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
window.__debug=()=>({pos:chars.lotte?chars.lotte.g.position.toArray():null,vel:chars.lotte&&chars.lotte.vel?chars.lotte.vel.toArray():[0,0,0],label:playerPlate(),near:nearK,started,world:S.world,bridges:bridges.map(b=>({a:b.a,b:b.b,open:b.open,near:b.near,len:b.len,pa:[b.pa.x,b.pa.z],pb:[b.pb.x,b.pb.z],mid:[b.mid.x,b.mid.z]})),onBridge:chars.lotte?!!onBridge(chars.lotte.g.position.x,chars.lotte.g.position.z):false,onLand:chars.lotte?onLandW(chars.lotte.g.position.x,chars.lotte.g.position.z):false,flying:!!flight,draws:renderer?renderer.info.render.calls:0,frame:renderer?renderer.info.render.frame:0,mentors:MENTORS.map(m=>({id:m.id,world:m.world,exercise:m.encounter.exercise.file,done:S.mentors.includes(m.id),seen:S.met[m.id]||0})),vault:()=>VSIM?{alpha:VSIM.alpha(),n:VN.length,sample:VN.slice(0,4).map(n=>[Math.round(n.x),Math.round(n.y)])}:null});
/* ---------------- continuity: the export line ---------------- */
// The whole evening is one record in one browser's localStorage, so while
// stops exist that no exported code carries, the Roadmap's sync card says so.
// The mark that says a write happened is the save() tick in 00-state.js; this
// is only the line, a view of S rebuilt on every write.
// What has not left this browser, {n, since}: the stops beyond the number a
// code is known to carry (S.exportedN, set by an export and by an import), or
// every stop when no code ever did. A record from before S.exportedN counts
// the claims since S.exportedAt, which is right until the event log, capped
// at EVENT_CAP, lets them go.
function exportDue(){const total=totalDone();
  if(typeof S.exportedN==="number")return {n:Math.max(0,total-S.exportedN),since:true};
  const at=typeof S.exportedAt==="number"?S.exportedAt:0;
  if(!at)return {n:total,since:false};
  return {n:(S.events||[]).filter(e=>e.kind==="claim"&&e.ts>at).length,since:true}}
function exportLine(){const d=exportDue();if(!d.n)return "";
  const stops=d.n+(d.n===1?" stop":" stops");
  return d.since?stops+" since your last export. Export again so the code you keep is the whole evening."
    :stops+" so far, and they live only in this browser. Export a code and keep it somewhere safe: clearing this browser's data clears them."}
// The line is made once, above the Export button, and afterwards only its
// text and its hidden flag change, and only when they differ.
function exportNudge(){let el=$("exportnudge");
  if(!el){const btn=document.querySelector('#s-map button[onclick="exportProgress()"]');if(!btn)return;
    el=document.createElement("p");el.id="exportnudge";el.className="small";el.hidden=true;
    el.style.cssText="border-left:3px solid var(--yellow);padding-left:10px;margin:8px 0";
    btn.parentNode.parentNode.insertBefore(el,btn.parentNode)}
  const t=exportLine();if(el.textContent!==t)el.textContent=t;if(el.hidden!==!t)el.hidden=!t}
// save() stays the one write and keeps its own arguments and result: the
// line follows it, and nothing else about a write changes here.
const saveRecord=save;
save=function(){const r=saveRecord.apply(this,arguments);exportNudge();return r};
exportNudge();
// A reset is the one thing that clears the record on purpose, so its confirm
// says what no code carries yet.
window.reset=function(){const d=exportDue(),one=d.n===1;
  const warn=!d.n?"":"\n\n"+d.n+(one?" stop ":" stops ")+(d.since?"delivered since your last export "+(one?"is":"are")+" in no code yet."
    :(one?"has":"have")+" never been exported, so nothing can bring "+(one?"it":"them")+" back.")+" Export progress in the Roadmap first to keep a copy.";
  if(!confirm("Decommission the campus and reset to greenfield?"+warn))return;try{localStorage.removeItem(KEY);localStorage.removeItem(OLD_KEY)}catch(e){}location.reload()};

