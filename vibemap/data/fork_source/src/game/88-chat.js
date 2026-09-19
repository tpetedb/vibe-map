/* ---------------- chat (your own subscription, answering about the game) ---------------- */
// A browser page cannot reach a terminal subscription, so the answers come from
// a loopback bridge the player starts themselves: vibe chat serve --pair CODE.
// The code below is the shared secret that binds the bridge to this browser;
// without a bridge the panel searches the notes that are already in this file.
// docs/CHAT.md and docs/adr/0009-local-chat-bridge.md.
const CHAT_PORT=7717,CHAT_MAX=20,CHAT_ABC="ABCDEFGHJKLMNPQRSTUVWXYZ23456789";
// A pairing code is a secret, so it comes from the crypto source when there is
// one; Math.random is the fallback for a browser that has none.
function chatCode(){const n=8;const out=[];if(window.crypto&&crypto.getRandomValues){const b=new Uint8Array(n);crypto.getRandomValues(b);for(let i=0;i<n;i++)out.push(CHAT_ABC[b[i]%CHAT_ABC.length])}
  else for(let i=0;i<n;i++)out.push(CHAT_ABC[Math.floor(Math.random()*CHAT_ABC.length)]);return out.join("")}
// The record comes back out of localStorage, so its shape is checked here:
// the port goes into a URL and the code into a command the player copies.
function chatState(){if(!isMap(S.chat))S.chat={};const c=S.chat;if(typeof c.code!=="string"||!/^[A-Z2-9]{4,16}$/.test(c.code))c.code=chatCode();
  const port=parseInt(c.port,10);c.port=port>0&&port<65536?port:CHAT_PORT;if(!Array.isArray(c.hist))c.hist=[];return c}
function chatBase(){return "http://127.0.0.1:"+chatState().port}
// What the question is about: the stop whose sheet is open, else the mentor,
// artifact or plot the walker is standing next to. Identifiers only; the
// bridge looks the lesson up in the course data itself.
let chatWhere={world:"campus",stop:null,mentor:null,artifact:null};
function chatCtx(){const c={world:S.world||"campus",stop:null,mentor:null,artifact:null};
  const scr=document.querySelector("#sheet.on .screen.on"),m=scr&&/^s-([1-9])$/.exec(scr.id);if(m)c.stop=+m[1];
  if(typeof nearK==="string"&&nearK.startsWith("m:"))c.mentor=nearK.slice(2);
  else if(typeof nearK==="string"&&nearK.startsWith("a:"))c.artifact=nearK.slice(2);
  else if(!c.stop&&typeof nearK==="number"&&nearK>0)c.stop=nearK;
  // Nothing under the walker either: the last stop whose sheet was open.
  if(!c.stop&&!c.mentor&&!c.artifact){const last=typeof lastScreen==="string"&&/^s-([1-9])$/.exec(lastScreen);if(last)c.stop=+last[1]}
  return c}
function chatChip(c){const out=[(WORLDS[c.world]&&WORLDS[c.world].name)||c.world];
  if(c.stop&&CH[c.stop-1])out.push("stop "+c.stop+", "+CH[c.stop-1].n);
  if(c.mentor){const m=MENTORS.find(x=>x.id===c.mentor);if(m)out.push(m.name)}
  if(c.artifact){const a=ARTIFACTS.find(x=>x.id===c.artifact);if(a)out.push(a.name)}
  return out.join(" · ")}
function chatSuggest(c){const out=[];
  if(c.stop&&CH[c.stop-1])out.push("What am I meant to build in "+CH[c.stop-1].n+"?","Why does this stop come before the next one?");
  if(c.mentor){const m=MENTORS.find(x=>x.id===c.mentor);if(m)out.push("What is "+m.name+" on record for?","How do I do their exercise?")}
  if(c.artifact){const a=ARTIFACTS.find(x=>x.id===c.artifact);if(a)out.push("What does "+a.name+" teach?","Show me the smallest version of "+a.concept)}
  if(!out.length)out.push("What is this game for?","Which stop should I do next?","How do I use the terminal companion?");
  return out.slice(0,4)}

// No bridge: the same question against the notes and the stops embedded in
// this file. Word overlap, best three passages, each one a link into the vault.
// Words that match everything and mean nothing in a search over our own notes.
const CHAT_STOP=["the","and","what","how","why","does","this","that","for","are","you","can","with","from","should","have","was","not"];
function chatSearch(q){const words=(q.toLowerCase().match(/[a-z0-9]{3,}/g)||[]).filter(w=>!CHAT_STOP.includes(w));if(!words.length)return[];
  const hits=[];
  Object.keys(NOTES).forEach(t=>{const md=NOTES[t].md,low=(t+" "+md).toLowerCase();let sc=0;
    words.forEach(w=>{if(low.indexOf(w)>=0)sc++;if(t.toLowerCase().indexOf(w)>=0)sc+=2});
    if(!sc)return;
    const best=md.split("\n").filter(l=>l.trim()&&!l.startsWith("#")).map(l=>({l:l,s:words.filter(w=>l.toLowerCase().indexOf(w)>=0).length})).sort((a,b)=>b.s-a.s)[0];
    hits.push({t:t,s:sc,p:best?best.l:"",note:true})});
  CH.forEach((ws,i)=>{const low=(ws.n+" "+ws.d).toLowerCase();let sc=0;words.forEach(w=>{if(low.indexOf(w)>=0)sc+=2});
    if(sc)hits.push({t:"Stop "+(i+1)+": "+ws.n,s:sc,p:ws.d})});
  return hits.sort((a,b)=>b.s-a.s).slice(0,3)}
function chatOfflineAnswer(q){const hits=chatSearch(q);
  if(!hits.length)return {text:"Nothing in the notes matches that. Start the bridge and your own Claude or Codex can answer it properly.",links:[]};
  return {text:hits.map(h=>h.t+": "+h.p.replace(/\[\[([^\]]+)\]\]/g,"$1").replace(/\[([^\]]+)\]\((https?:[^)]+)\)/g,"$1").replace(/[*`]/g,"")).join("\n"),links:hits.filter(h=>h.note).map(h=>h.t)}}

// State is data: every exchange lives in S.chat.hist and the panel is drawn
// from it, newest last, capped so a long evening does not fill localStorage.
function chatPush(entry){const c=chatState();c.hist.push(entry);while(c.hist.length>CHAT_MAX)c.hist.shift();save();return entry}
function renderChatLog(){const el=$("chatlog");if(!el)return;const c=chatState();
  el.innerHTML=c.hist.length?c.hist.map(h=>`<div class="cturn"><p class="you">${esc(h.q)}</p><p class="them">${esc(h.a||"...")}</p>${(h.links||[]).map(t=>`<span class="wl" data-n="${esc(t)}">${esc(t)}</span>`).join("")}<span class="src">${h.src==="offline"?"from the notes in this file":h.src==="error"?"not answered":"your "+esc(h.provider||"provider")}</span></div>`).join(""):`<p class="small muted">No questions yet. Pick one below, or type your own.</p>`;
  el.querySelectorAll(".wl").forEach(e=>e.onclick=()=>openNote(e.dataset.n));
  el.scrollTop=el.scrollHeight}
function chatHelp(){const c=chatState();
  return `<div class="card" id="chathelp"><h3>No bridge answered on port ${esc(c.port)}</h3>
   <p class="small">Three lines, in the folder of your camp. Your subscription stays on your machine; the bridge only takes questions, never commands.</p>
   <ol class="small"><li>Open a terminal in your camp.</li><li>Run <code>uv run vibe chat serve --pair ${esc(c.code)}</code></li><li>Ask again here.</li></ol>
   <div class="row"><label class="small muted" for="chatport">Port</label><input type="number" id="chatport" value="${esc(c.port)}" style="width:100px" onchange="chatSetPort(this.value)"><button onclick="chatRetry()">Try again</button></div>
   <p class="small muted">Pairing code <b>${esc(c.code)}</b>. The bridge only answers a page that knows it, so a hosted copy cannot talk to someone else's terminal.</p></div>`}
window.chatSetPort=function(v){const c=chatState();const n=parseInt(v,10);if(n>0&&n<65536){c.port=n;save()}};
window.chatRetry=function(){const c=chatState();const last=c.hist.length?c.hist[c.hist.length-1]:null;if(last)chatAsk(last.q);else $("chatmsg").textContent="Type a question first."};
function renderChat(){const sug=chatSuggest(chatWhere);
  $("s-chat").innerHTML=`<h2>Ask about this</h2>
   <p class="chip" id="chatchip">${esc(chatChip(chatWhere))}</p>
   <div id="chatlog" class="chatlog"></div>
   <div class="row" id="chatsug">${sug.map(q=>`<button class="small" onclick="chatAsk(this.dataset.q)" data-q="${esc(q)}">${esc(q)}</button>`).join("")}</div>
   <div class="row"><input type="text" id="chatq" placeholder="Ask a question about this stop" style="flex:1;min-width:160px" onkeydown="if(event.key==='Enter')chatSend()"><button class="primary" data-icon="message-circle" onclick="chatSend()">Ask</button></div>
   <p class="small muted" id="chatmsg"></p>
   <div id="chatwhy"></div>`;
  iconize($("s-chat"));renderChatLog()}
window.openChat=function(){chatWhere=chatCtx();renderChat();openSheet("s-chat")};
window.chatSend=function(){const el=$("chatq");const q=(el&&el.value||"").trim();if(!q){$("chatmsg").textContent="Type a question first.";return}
  if(el)el.value="";chatAsk(q)};
// One question at a time on this side too: the bridge refuses a second one and
// the panel should not pretend otherwise.
let chatBusy=false;
window.chatAsk=async function(q){if(chatBusy)return;chatBusy=true;
  const c=chatState(),entry=chatPush({q:q,a:"",ctx:chatChip(chatWhere),at:Date.now(),src:"bridge",links:[]});
  // The dashboard counts questions per context, never the question itself.
  if(window.track)track("chat",chatWhere.stop?"stop "+chatWhere.stop:chatWhere.mentor||chatWhere.artifact||chatWhere.world);
  $("chatmsg").textContent="Asking your "+(CONFIG.provider||"provider")+"...";renderChatLog();
  try{
    const r=await fetch(chatBase()+"/ask",{method:"POST",headers:{"Content-Type":"application/json","X-Vibe-Code":c.code},body:JSON.stringify({question:q,world:chatWhere.world,stop:chatWhere.stop,mentor:chatWhere.mentor,artifact:chatWhere.artifact})});
    if(!r.ok){const why=await r.json().catch(()=>({error:"refused"}));throw new Error(why.error||("refused with "+r.status))}
    await chatRead(r,entry);
    $("chatwhy").innerHTML="";$("chatmsg").textContent="";
  }catch(e){chatFallback(entry,e&&e.message||String(e))}
  save();renderChatLog();chatBusy=false};
// Server-sent events, read as they arrive: one frame per blank line.
async function chatRead(r,entry){const rd=r.body.getReader(),dec=new TextDecoder();let buf="";
  for(;;){const step=await rd.read();if(step.done)break;buf+=dec.decode(step.value,{stream:true});
    let i;while((i=buf.indexOf("\n\n"))>=0){chatFrame(buf.slice(0,i),entry);buf=buf.slice(i+2)}}
  if(buf.trim())chatFrame(buf,entry)}
function chatFrame(frame,entry){let ev="message",data="";
  frame.split("\n").forEach(l=>{if(l.indexOf("event: ")===0)ev=l.slice(7).trim();else if(l.indexOf("data: ")===0)data+=l.slice(6)});
  let d={};try{d=JSON.parse(data||"{}")}catch(e){return}
  if(ev==="start"){entry.provider=d.provider;if(d.context)entry.ctx=d.context}
  else if(ev==="delta"){entry.a+=d.text||"";renderChatLog()}
  else if(ev==="error"){entry.src="error";entry.a=d.message||"the provider failed";renderChatLog()}}
// No bridge, or a bridge that refused: say so in three lines and answer from
// the notes that are already in this file, so the panel is never a dead end.
function chatFallback(entry,why){const off=chatOfflineAnswer(entry.q);
  entry.src="offline";entry.a=off.text;entry.links=off.links;
  $("chatmsg").textContent="No answer from the bridge ("+why+"). Searched the notes instead.";
  $("chatwhy").innerHTML=chatHelp();iconize($("chatwhy"))}
// C opens the panel, unless the player is typing somewhere.
addEventListener("keydown",e=>{if(e.key!=="c"&&e.key!=="C")return;if(e.metaKey||e.ctrlKey||e.altKey)return;
  const t=e.target&&e.target.tagName||"";if(/^(input|textarea|select)$/i.test(t))return;
  if($("vault").classList.contains("on"))return;
  if($("sheet").classList.contains("on")&&$("s-chat").classList.contains("on")){closeSheet();return}
  openChat();e.preventDefault()});
