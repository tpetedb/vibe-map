// Artifacts: props on the island that explain one idea each when you walk up
// and press Inspect. The list, the copy and Rolinda's question come from
// campaign.json (ARTIFACTS); the button demos live here because they are
// presentation. Found artifacts persist in S.artifacts and travel in the
// progress code, so the CLI can note them and hand out the collector badge.
const ART_DEMOS={
  cafe:[
    {l:"Order a coffee",o:["you   ->  GET /coffee HTTP/1.1","cafe  <-  200 OK  (412 ms)","          body: one coffee, oat milk on the side","The client asks, the server answers, in words both agreed on. That is a protocol."]},
    {l:"Ask for unicorn milk",o:["you   ->  GET /flat-white?milk=unicorn","cafe  <-  404 Not Found  (38 ms)","A 4xx means the request was wrong. Fix the request, not the server."]},
    {l:"Order five in one second",o:["you   ->  GET /coffee  x5","cafe  <-  429 Too Many Requests  Retry-After: 3","Servers protect themselves. Back off, wait, then try again."]},
    {l:"Order while the machine descales",o:["you   ->  GET /coffee","cafe  <-  503 Service Unavailable","A 5xx means the server is at fault. Wait, or fail over to the stall."]}
  ],
  fountain:[
    {l:"Fill a cup",o:["fountain:  MISS   walking to the well ... 1800 ms","cup filled. copy kept for 60 s"]},
    {l:"Fill it again",o:["fountain:  HIT    3 ms","Same question, same answer, no walk. That is a cache. The prompt cache keeps the start of your prompt the same way."]},
    {l:"Wait a minute (the TTL expires)",o:["60 s later ...  copy is stale","fountain:  MISS   walking to the well ... 1800 ms","A cache without an expiry serves yesterday's water forever."]},
    {l:"Change the recipe (invalidate)",o:["recipe changed:  cache cleared for /water","The hard part is not keeping a copy. It is knowing when the copy is wrong."]}
  ],
  well:[
    {l:"Pull a bucket",o:["SELECT * FROM scores WHERE player = 'Lotte';","scanning 120 000 rows ...  840 ms   3 rows"]},
    {l:"Add an index",o:["CREATE INDEX scores_player ON scores(player);","SELECT * FROM scores WHERE player = 'Lotte';","index seek ...  4 ms   3 rows","An index is a rope with marks: you go straight to the bucket instead of down the whole well."]},
    {l:"Two buckets at once",o:["BEGIN;","UPDATE scores SET score = score + 10 WHERE player = 'Lotte';","UPDATE scores SET score = score - 10 WHERE player = 'Tom';","COMMIT;","Both changes, or neither. Never one of them. That is a transaction."]}
  ],
  lighthouse:[
    {l:"Ask for vibe-map.local",o:["resolver:  vibe-map.local  ->  127.0.0.1   (A record, from /etc/hosts)","A name is for people. An address is for packets."]},
    {l:"Ask for tpetedb.github.io",o:["resolver:  tpetedb.github.io  ->  CNAME  ->  185.199.108.153   (TTL 3600 s)","The lighthouse does not carry you. It tells you where the harbour is, and remembers for an hour."]},
    {l:"Ask for a name that does not exist",o:["resolver:  vibe-map.nope  ->  NXDOMAIN","No such name. Check the spelling before you blame the network."]}
  ],
  dock:[
    {l:"Pack a crate (build)",o:["docker build -t vibe-map:0.3.0 .","Step 1/4  FROM python:3.12-slim","Step 2/4  COPY pyproject.toml uv.lock .","Step 3/4  RUN uv sync --frozen","Step 4/4  COPY . .      =>  image 210 MB"]},
    {l:"Ship it (push)",o:["docker push ghcr.io/tpetedb/vibe-map:0.3.0","layers uploaded.  The crate is byte for byte the same on every island."]},
    {l:"Unload on the other island (run)",o:["docker run -p 8000:8000 ghcr.io/tpetedb/vibe-map:0.3.0","listening on :8000","It works on my machine. And now on this one, because the machine came with it."]}
  ],
  windmill:[
    {l:"Turn every minute",o:["* * * * *   uv run vibe check","tick 09:00 ... tick 09:01 ... tick 09:02","Five fields: minute, hour, day of month, month, day of week."]},
    {l:"Monday mornings only",o:["0 9 * * 1   uv run vibe vault build","next run: Monday 09:00.  The mill turns while you sleep."]},
    {l:"Turn when the wind blows (an event)",o:["on: push        (GitHub Actions)","on: PostToolUse (Claude Code hook)","A schedule is time-driven. A hook is event-driven. Neither needs you in the room."]}
  ],
  balloon:[
    {l:"Rent a balloon",o:["aws ec2 run-instances --instance-type t3.small --region eu-west-1","running.  meter: 0.0208 USD per hour","The cloud is a computer you rent by the hour and never see."]},
    {l:"Forget to land it",o:["30 days later ...  15.00 USD  (and 2.10 USD for the storage it was tied to)","The meter runs whether you use it or not. Set a budget alarm before the first launch."]},
    {l:"Land it",o:["aws ec2 terminate-instances ...  meter stopped","Region, instance, storage, traffic out: four meters, not one."]}
  ],
  mountain:[
    {l:"Climb",o:["1  hardware      Apple M4, 10 cores, 16 GB","2  operating system   macOS: files, processes, ports","3  runtime       Python 3.12, managed by uv","4  libraries     click, rich, polars, duckdb, textual","5  your app      vibe","6  the agent     Claude Code, reading and writing all of it","Every layer stands on the one below. A bug can live on any of them."]},
    {l:"Look down from the summit",o:["the agent edits vibe/cli.py  (layer 5)","which imports polars       (layer 4)","which calls into Python    (layer 3)","which asks macOS for a file (layer 2)","which reads the disk        (layer 1)","One keystroke at the top touches every layer on the way down."]}
  ],
  stall:[
    {l:"Read the menu (the docs)",o:["GET /openapi.json","endpoints:  GET /coffee   GET /scores   POST /scores   GET /status","auth:       Authorization: Bearer <token>","An API is a menu: what you may ask for, in which words, and what comes back."]},
    {l:"Order without reading it",o:["POST /scoresss  {\"player\": 1}","400 Bad Request:  unknown path; and player must be a string","Read the menu first. Then order exactly."]},
    {l:"Show your key",o:["GET /scores   Authorization: Bearer ****","200 OK   3 rows","Keys live in .env, never in the code, never in the vault."]}
  ],
  bridge:[
    {l:"Cross the bridge",o:["agent   ->  tools/list                       (MCP)","server  <-  read_scores, write_note, run_sql","agent   ->  tools/call read_scores {player: 'Lotte'}","server  <-  3 rows","First ask what is on the other side. Then call it by name. That rulebook is MCP."]},
    {l:"Try a tool that is not there",o:["agent   ->  tools/call delete_everything","server  <-  error: unknown tool","The bridge only carries what the other side declared. Nothing else crosses."]}
  ]
};
function placeArtifacts(){props.artifacts=[];(typeof ARTIFACTS==="undefined"?[]:ARTIFACTS).filter(a=>a.world===S.world).forEach(a=>{
  const found=S.artifacts.includes(a.id);
  const ring=new T.Mesh(new T.TorusGeometry(1.2,.06,6,24),new T.MeshBasicMaterial({color:found?"#00D084":"#FFBF00",transparent:true,opacity:.55}));ring.rotation.x=Math.PI/2;ring.position.set(a.pos[0],.05,a.pos[1]);scene.add(ring);
  props.artifacts.push({a,ring})})}
function nearArtifact(pos){let best=null,bd=99;(props.artifacts||[]).forEach(x=>{const d=Math.hypot(x.a.pos[0]-pos.x,x.a.pos[1]-pos.z);if(d<x.a.r&&d<bd){bd=d;best=x.a}});return best}
window.openArtifact=function(id){const a=ARTIFACTS.find(x=>x.id===id);if(!a)return;
  if(!S.artifacts.includes(id)){S.artifacts.push(id);save();hud();(props.artifacts||[]).forEach(x=>{if(x.a.id===id)x.ring.material.color.set("#00D084")})}
  const demos=ART_DEMOS[id]||[];
  $("s-artifact").innerHTML=`<div class="hour">${icon("compass")}Artifact ${S.artifacts.length} of ${ARTIFACTS.length}</div><h2>${a.name}</h2><p class="small muted">${a.prop} · ${a.concept}</p><p>${a.what}</p>`+
    `<div class="row">${demos.map((d,i)=>`<button data-demo="${i}" onclick="runDemo('${id}',${i})">${icon("play")}${d.l}</button>`).join("")}</div>`+
    `<pre class="term" id="art-term">Press a button. Watch what comes back.</pre>`+
    `<div class="rolinda"><b>Rolinda asks</b>${a.rolinda}</div>`+
    `<p class="small muted">In the vault: ${a.links.map(n=>`<span class="wl" onclick='openNote(${JSON.stringify(n)})'>${n}</span>`).join(" · ")}</p>`;
  $("bub-face").innerHTML=FACE.rolinda;$("bub-who").textContent="Rolinda, "+CONFIG.theme.guideRole;typeOut($("bub-text"),a.rolinda);
  openSheet("s-artifact")};
window.runDemo=function(id,i){const d=(ART_DEMOS[id]||[])[i];if(!d)return;const el=$("art-term");if(!el)return;el.textContent="";
  d.o.forEach((line,k)=>setTimeout(()=>{el.textContent+=(k?"\n":"")+line;el.scrollTop=el.scrollHeight},k*320))};
function artifactsMd(){return "# Artifacts\nThings on the island that explain one idea each. Walk up to the yellow ring and press Inspect; a found one turns green.\n"+
  ARTIFACTS.map(a=>`- ${S.artifacts.includes(a.id)?"found":"not yet"}: **${a.name}** (${a.prop}): ${a.concept}. See ${a.links.map(l=>"[["+l+"]]").join(", ")}.`).join("\n")+"\n- Back: [[Tonight]]\n#concept"}
window.__artifacts=()=>ARTIFACTS;
