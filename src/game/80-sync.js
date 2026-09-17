window.exportProgress=function(){const code=btoa(unescape(encodeURIComponent(JSON.stringify({v:2,name:S.name,done:S.doneW.campus,doneW:S.doneW,path:S.path,artifacts:S.artifacts})))).replace(/\+/g,"-").replace(/\//g,"_").replace(/=+$/,"");$("impcode").value=code;$("syncmsg").textContent="Code is in the box. Copy it, then in the repo: uv run vibe import "+code.slice(0,12)+"…";if(navigator.clipboard&&navigator.clipboard.writeText)navigator.clipboard.writeText(code).catch(()=>{})};
window.importProgress=function(){try{let c=$("impcode").value.trim().replace(/-/g,"+").replace(/_/g,"/");c+="=".repeat((4-c.length%4)%4);const d=JSON.parse(decodeURIComponent(escape(atob(c))));
    // The progress code is versioned: an unknown version is refused loudly.
    if(d.v!==2){$("syncmsg").textContent="That code is version "+(d.v===undefined?"1 or older":d.v)+"; this game reads version 2. Run uv run vibe export again with an up-to-date vibe.";return}
    const dw=d.doneW||{campus:d.done||[]};Object.keys(dw).forEach(w=>{if(!S.doneW[w])S.doneW[w]=[];dw[w].forEach(n=>{n=+n;if(n>=1&&n<=8&&!S.doneW[w].includes(n)){S.doneW[w].push(n);if(started&&w===S.world)placeBuilding(n,true)}})});Object.assign(S.path,d.path||{});(d.artifacts||[]).forEach(a=>{if(!S.artifacts.includes(a))S.artifacts.push(a)});if(d.name)S.name=d.name;save();hud();renderMap();if(started)applySky(S.done.length,false);$("syncmsg").textContent="Imported: "+S.done.length+"/8 workstreams."}catch(e){$("syncmsg").textContent="That is not a valid code."}};
const playerPlate=()=>{const sp=chars.lotte&&chars.lotte.g.children.find(c=>c.isSprite);return sp?{text:sp.userData.text,fs:sp.userData.fs}:null};
window.__S=()=>S;
// Test seam: the data the build injects, read-only, for the Playwright battery.
window.__data=()=>({worlds:WORLDS,artifacts:ARTIFACTS,config:CONFIG});
// Test seam: read-only view of the walker for the Playwright battery, never written to.
window.__debug=()=>({pos:chars.lotte?chars.lotte.g.position.toArray():null,label:playerPlate(),near:nearK,started,world:S.world,draws:renderer?renderer.info.render.calls:0,mentors:MENTORS.map(m=>({id:m.id,world:m.world})),vault:()=>VSIM?{alpha:VSIM.alpha(),n:VN.length,sample:VN.slice(0,4).map(n=>[Math.round(n.x),Math.round(n.y)])}:null});
window.reset=function(){if(!confirm("Decommission the campus and reset to greenfield?"))return;try{localStorage.removeItem(KEY);localStorage.removeItem(OLD_KEY)}catch(e){}location.reload()};

