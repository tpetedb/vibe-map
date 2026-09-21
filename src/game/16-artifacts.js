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
    // One region, one rate: t3.small is dearer in Ireland than in Virginia,
    // and a demo about regions that charges another region's price teaches
    // the opposite of its own lesson. 0.0228 USD is the eu-west-1 on-demand
    // rate; the month below is that rate times 24 hours times 30 days. The
    // walkthrough has the learner look today's rate up for themselves.
    {l:"Rent a balloon",o:["aws ec2 run-instances --instance-type t3.small --region eu-west-1","running.  meter: 0.0228 USD per hour","The cloud is a computer you rent by the hour and never see."]},
    {l:"Forget to land it",o:["30 days later ...  16.42 USD  (and 2.10 USD for the storage it was tied to)","The meter runs whether you use it or not. Set a budget alarm before the first launch."]},
    {l:"Land it",o:["aws ec2 terminate-instances ...  meter stopped","Region, instance, storage, traffic out: four meters, not one."]}
  ],
  mountain:[
    {l:"Climb",o:["1  hardware      Apple M4, 10 cores, 16 GB","2  operating system   macOS: files, processes, ports","3  runtime       Python 3.12, managed by uv","4  libraries     click, rich, polars, duckdb, textual","5  your app      vibe","6  the agent     Claude Code, reading and writing all of it","Every layer stands on the one below. A bug can live on any of them."]},
    {l:"Look down from the summit",o:["the agent edits vibemap/cli.py  (layer 5)","which imports polars       (layer 4)","which calls into Python    (layer 3)","which asks macOS for a file (layer 2)","which reads the disk        (layer 1)","One keystroke at the top touches every layer on the way down."]}
  ],
  stall:[
    {l:"Read the menu (the docs)",o:["GET /openapi.json","endpoints:  GET /coffee   GET /scores   POST /scores   GET /status","auth:       Authorization: Bearer <token>","An API is a menu: what you may ask for, in which words, and what comes back."]},
    {l:"Order without reading it",o:["POST /scoresss  {\"player\": 1}","400 Bad Request:  unknown path; and player must be a string","Read the menu first. Then order exactly."]},
    {l:"Show your key",o:["GET /scores   Authorization: Bearer ****","200 OK   3 rows","Keys live in .env, never in the code, never in the vault."]}
  ],
  bridge:[
    {l:"Cross the bridge",o:["agent   ->  tools/list                       (MCP)","server  <-  read_scores, write_note, run_sql","agent   ->  tools/call read_scores {player: 'Lotte'}","server  <-  3 rows","First ask what is on the other side. Then call it by name. That rulebook is MCP."]},
    {l:"Try a tool that is not there",o:["agent   ->  tools/call delete_everything","server  <-  error: unknown tool","The bridge only carries what the other side declared. Nothing else crosses."]}
  ],
  factory:[
    {l:"Run the pipeline",o:["run 40   raw     ->  bronze   12 files landed as they came (CSV, 3 with odd rows)","run 40   bronze  ->  silver   3 rows quarantined, 2 columns typed, dates parsed","run 40   silver  ->  gold     one table: score per player per evening","Raw is what arrived. Bronze keeps it. Silver cleans it. Gold answers a question."]},
    {l:"A run fails halfway",o:["run 41   raw     ->  bronze   ok","run 41   bronze  ->  silver   ERROR: scores_2026-09-25.csv, column score is 'four hundred'","run 41   failed after silver. gold untouched: it still shows last night's numbers.","A failed step must not leave half a table behind. Write to a temp table, then swap."]},
    {l:"Rerun it",o:["fix: cast score to integer, park the odd row in quarantine","run 42   raw     ->  bronze   skipped, nothing new","run 42   bronze  ->  silver   ok      silver  ->  gold   ok","Same input, same output, no duplicates. That is idempotent: rerun without fear."]},
    {l:"Batch or stream?",o:["batch:   every night at 02:00   120 000 rows   4 minutes","stream:  one row each time a game ends   30 ms each","Batch is cheap and late. Stream is fresh and fiddly. Choose by how old the answer may be."]}
  ],
  "post-office":[
    {l:"Drop a letter",o:["you    ->  PUBLISH scores.finished {player: 'Lotte', score: 412}","queue  <-  accepted, id 8813, 2 subscribers","You are done the moment the letter is in the box. Who reads it, and when, is not your problem."]},
    {l:"Deliver to a reader that was offline",o:["subscriber vault-writer: offline since 20:14","20:31  vault-writer is back","queue  ->  deliver 8813 to vault-writer","vault-writer  <-  ack","The letter waited on the shelf. The sender never noticed. That is decoupling."]},
    {l:"Deliver twice",o:["queue  ->  deliver 8813 to leaderboard","leaderboard ...  no ack within 30 s","queue  ->  deliver 8813 to leaderboard   (retry 1)","leaderboard  <-  ack","At-least-once delivery: the same letter can arrive twice. The reader checks the id and does the work once."]},
    {l:"A letter nobody can read",o:["queue  ->  deliver 8814 to leaderboard   ERROR: score is 'four hundred'","retry 1 ... retry 2 ... retry 3 ... gave up","8814   ->  dead-letter shelf   (kept for a human to look at)","A poison letter is parked, not dropped and not retried forever."]}
  ],
  switchboard:[
    {l:"Read the labels",o:["just --list","Available recipes:","    build     # rebuild the game from src/","    test      # the whole pytest battery","    verify    # what CI runs: lint + tests + build check","The comment above a recipe is what --list prints. The project explains itself."]},
    {l:"Connect one line",o:["just greet Lotte","hello Lotte","A parameter with a default: greet name='camp'. One recipe, many calls."]},
    {l:"Pull two plugs at once",o:["just verify","  -> lint    (dependency, runs first)","  -> test    (dependency, runs first)","verify OK","A dependency runs before the recipe that names it, and only once per invocation."]},
    {l:"Hand the board to an agent",o:['.claude/settings.json:  "allow": ["Bash(just *)"]',"agent  ->  just verify","agent  <-  verify OK: lint clean, 412 passed","One allow rule reaches the recipes you wrote and nothing else. The wildcard goes after the program."]},
    {l:"Guard the switch that cuts the power",o:["[confirm]","reset-scores:","    rm workspace/data/scores.csv","just reset-scores","Run recipe `reset-scores`? y/n  >","A destructive recipe asks first, so the allow rule stays safe to hand out."]}
  ],
  shop:[
    {l:"Buy a library",o:["uv add polars","Resolved 2 packages in 140 ms"," + polars==1.33.0","Installed 1 package in 210 ms","pyproject.toml:  polars>=1.33      uv.lock:  polars 1.33.0  sha256:9f2c...","The shelf is PyPI. The wish goes in pyproject.toml. The receipt is the lockfile."]},
    {l:"Look at the shelf",o:["polars, versions on the shelf:","  1.33.0    2026-08","  1.32.3    2026-07","  1.31.0    2026-06","  0.20.31   2024-06   (old API)","Major.minor.patch. A new major may break you; a patch should not."]},
    {l:"Install from the receipt",o:["uv sync --frozen","Resolved from uv.lock: polars 1.33.0, duckdb 1.4.0, click 8.2.1 ...","Bit for bit what you had on the evening it worked. The lockfile is why it works on CI too."]},
    {l:"Take a yanked version",o:["uv add polars==1.32.0","warning: polars 1.32.0 was yanked (reason: broken wheel on macOS arm64)","The shop keeps it on the shelf so old receipts still resolve, and tells you not to take it. Take 1.32.3."]}
  ],
  bank:[
    {l:"Show your key",o:["cat .env","ANTHROPIC_API_KEY=sk-ant-****...****7Qf","curl https://api.anthropic.com/v1/messages -H 'x-api-key: $ANTHROPIC_API_KEY'","200 OK","A token is a key. Whoever holds it is you, as far as the server can tell. .env is the safe."]},
    {l:"Commit the safe by accident",o:["git add .env","pre-commit: .env is listed in .gitignore and .aiignore, refusing","The safe stays on your machine. The repo holds env.example: the names, never the values."]},
    {l:"A leaked key",o:["21:02   sk-ant-...7Qf seen in a public gist","21:03   console: revoke sk-ant-...7Qf      revoked","21:04   every request with it:  401 Unauthorized","A leaked key is dead the minute you revoke it. Revoke first, then go looking for the leak."]},
    {l:"Rotate",o:["console: create key   ->  sk-ant-****...****Lm2","edit .env: 7Qf  ->  Lm2      (or the keychain)","old key: revoked.  new key: in the safe.  vault notes: no key in any of them, ever.","Rotate on a schedule, not only after a scare."]}
  ],
  "data-centre":[
    {l:"Send one request",o:["you (Amsterdam)  ->  POST /v1/messages   1 200 tokens in","edge eu-west     ->  auth ok, rate ok           2 ms","queue            ->  GPU node 14, 8 x H100     waited 40 ms","prefill  1 200 tokens                         90 ms","decode   350 tokens, one at a time         2 100 ms","you  <-  200 OK   total 2.3 s","The answer is typed out one token at a time. Most of the wait is the typing."]},
    {l:"Same request from far away",o:["you (Sydney)  ->  edge us-east   180 ms each way","total 2.7 s. The GPUs were just as fast; the cable is longer.","Latency by region is geography, not load."]},
    {l:"Cold start",o:["node 22: model not loaded. loading 140 GB of weights ...  38 s","first request:  40.3 s      second request:  2.3 s","A cold start is the model being carried into the room. Keep it warm, or accept the first hit."]},
    {l:"Batch instead",o:["batch job: 10 000 requests, deadline 24 h","GPU utilisation 92 %  (interactive: 35 %)      price: half","Interactive pays for the empty seats. Batch fills the room and waits."]}
  ],
  "energy-grid":[
    {l:"Read the meter",o:["evening 1:  84 requests   312 000 tokens in   41 000 tokens out","price:  3 USD per million in, 15 USD per million out   (an example; check the model's page)","bill:   0.94 + 0.62 = 1.56 USD","Tokens are the watts of this grid. Output tokens cost more: they are generated, not read."]},
    {l:"Blow the fuse",o:["request 61 ...  429 Too Many Requests   Retry-After: 12","limit on this key: 50 requests per minute","A fuse trips before the wiring melts. Back off, wait, retry."]},
    {l:"Add turbines (autoscale)",o:["08:00   40 req/s    2 replicas","09:00  340 req/s    scale up  ->  9 replicas   (90 s to warm)","22:00   12 req/s    scale down  ->  2","Autoscaling adds turbines when the whole town switches the kettle on."]},
    {l:"Budget alarm",o:["budget: 20 USD per month   alert at 80 %","day 19:  16.02 USD   ALERT sent","action: the nightly job moves to a smaller model   0.40  ->  0.06 per run","Set the alarm before the first run, not after the first invoice."]}
  ],
  library:[
    {l:"Ask a question",o:["q: 'why did the Monday run fail?'","embed(q)  ->  [0.021, -0.113, 0.087, ...]   1 536 numbers","A sentence becomes a point in space. Nearby points say similar things."]},
    {l:"Fetch the nearest shelves",o:["nearest 3 of 100 notes (cosine):","  0.91   Headless agents and scheduling","  0.88   CI-CD and automation","  0.79   Git hooks","prompt = the question + those three notes. The model reads them, then answers."]},
    {l:"Answer with a citation",o:["'The Monday 09:00 job runs vibe vault build; it failed because uv was missing on the runner.'","  source: Headless agents and scheduling, section 'Try in five minutes'","An answer with a shelf number can be checked. One without is a guess with good grammar."]},
    {l:"A stale index",o:["note edited 20:40.   index built 18:00.","q: 'what changed tonight?'   ->   nearest: yesterday's note","Retrieval is only as fresh as the last rebuild. Re-index after every session, or on a hook."]}
  ],
  office:[
    {l:"Hand out the work",o:["planner   reads AGENTS.md, the issue, the file map","planner   ->  plan: 3 steps, files: vibemap/scores.py, tests/test_scores.py","worker    ->  edits both, runs just test-one tests/test_scores.py    green","reviewer  ->  reads the diff against the plan and the handbook","One brief, three roles. The handbook is AGENTS.md; nobody has to be told twice."]},
    {l:"The review gate says no",o:["reviewer:  REJECT   'workspace/data/scores.csv rewritten without asking; AGENTS.md says never'","worker    ->  reverts the rewrite, keeps the new column, reruns the test    green","reviewer:  APPROVE","A gate that never says no is a rubber stamp. This one had read the handbook."]},
    {l:"Departments (subagents)",o:["main  ->  spawn scorekeeper   (its own context: the scores only)","main  ->  spawn docs-sync     (its own context: the docs only)","each reports back in one paragraph; main merges and moves on","A subagent is a department: a fresh desk, a narrow brief, a written report."]}
  ],
  households:[
    {l:"Look at one house",o:["SELECT * FROM players WHERE id = 7;","id 7 | Lotte | l.***@***.nl | born 1991-**-** | last_seen 2026-09-25","Every row is a person. The columns are their belongings. You are holding them."]},
    {l:"Ask only what you need",o:["-- the leaderboard needs a name and a score, nothing else","SELECT name, score FROM players JOIN scores USING (id);","Data minimisation: collect less, keep less, show less. What you do not hold cannot leak."]},
    {l:"Anonymise for the chart",o:["SELECT md5(id) AS who, avg(score) FROM scores GROUP BY 1;","who 3f9a...   avg 402","Aggregates are safe to share. A hash of an id is still that person to someone determined; a count is not."]},
    {l:"A request under the GDPR",o:["21:10   l.***@***.nl asks: what do you hold on me? delete it.","export:  1 row in players, 14 rows in scores   ->  sent (the law says within 30 days)","DELETE FROM scores WHERE id = 7;  DELETE FROM players WHERE id = 7;   backups expire in 30 days","Consent can be withdrawn. Design the delete before you design the insert."]}
  ],
  school:[
    {l:"Split the data",o:["120 000 rows  ->  train 96 000    test 24 000    (at random, once)","The test set is the exam. The model never sees it while it learns."]},
    {l:"Train",o:["epoch 1    loss 2.31   train 41 %   test 40 %","epoch 5    loss 0.92   train 78 %   test 76 %","epoch 20   loss 0.11   train 99 %   test 71 %","weights.bin written   (410 MB of numbers)","Data in, weights out. The weights are the model: a very long list of numbers."]},
    {l:"Catch the overfit",o:["train 99 %, test 71 %: it memorised the homework and failed the exam.","keep the epoch 5 weights (test 76 %). More training made it worse.","The test set is the only honest witness. Never train on it."]},
    {l:"Score on a benchmark",o:["benchmark scores-qa-v2:  1 000 questions nobody trained on","this model  76.4 %     last month  71.2 %     a person on a good day  92 %","One number, the same questions for everyone. That is what a benchmark is, and all it is."]}
  ]
};
// High enough to lie on top of the flat ground the ring crosses: the path
// slabs, the river and the lake disc, and the inn's terrace deck.
const RING_Y=.2;
// The ring is the zone, not a decoration around the model: it is drawn at the
// radius nearArtifact() tests, so "walk up to the yellow ring and press
// Inspect" is true wherever you cross it. A smaller ring sits inside whatever
// the walker is pushed out of (the lake around the fountain, the mountain
// itself) and is never seen at all.
function placeArtifacts(){props.artifacts=[];(typeof ARTIFACTS==="undefined"?[]:ARTIFACTS).filter(a=>a.world===S.world).forEach(a=>{
  const found=S.artifacts.includes(a.id);
  const ring=new T.Mesh(new T.TorusGeometry(a.r,.06,6,24),new T.MeshBasicMaterial({color:found?PALETTE.greenBright:PALETTE.yellow,transparent:true,opacity:.55}));ring.rotation.x=Math.PI/2;ring.position.set(a.pos[0],RING_Y,a.pos[1]);scene.add(ring);
  props.artifacts.push({a,ring})})}
function nearArtifact(pos){let best=null,bd=99;(props.artifacts||[]).forEach(x=>{const d=Math.hypot(x.a.pos[0]-pos.x,x.a.pos[1]-pos.z);if(d<x.a.r&&d<bd){bd=d;best=x.a}});return best}
// The task behind the demo: a walkthrough written from the official
// documentation of the thing, the commands that documentation gives, and the
// one check that looks at what was built. Rendered inside .lesson so the
// commands get the same Commands disclosure every lesson uses.
// Every word of it is meant to be reproduced: a step says to print a line
// exactly and the check reads that line back, and the commands are typed as
// they stand. So the block is drawn with ligatures off, because Inter and SF
// draw "->" as one arrow glyph and "--" as one dash, and what is copied from
// the screen then never matches.
function artifactReal(a){const r=a.real;const built=S.artifactsBuilt.includes(a.id);
  return `<div class="lesson" style="font-variant-ligatures:none"><h3>${icon("milestone")}Do it for real: ${r.title}</h3>
   <p class="small muted">About ${r.minutes} minutes, in <code>${r.dir}/</code> in your camp. Written from <a href="${r.doc.url}" target="_blank" rel="noopener">${esc(r.doc.title)}</a>.</p>
   <ol class="small">${r.steps.map(s=>`<li>${esc(s)}</li>`).join("")}</ol>
   <pre><code>${r.commands.map(esc).join("\n")}</code></pre>
   <p class="small"><b>Done when</b> ${esc(r.done)}, checked by <code>vibe check --artifact ${a.id}</code>.</p>
   <p class="small ${built?"":"muted"}">${built?"Built for real, and verified in your camp.":"Not built yet. Do it in your camp, run the check, then bring the progress code back here."}</p></div>`}
window.openArtifact=function(id){const a=ARTIFACTS.find(x=>x.id===id);if(!a)return;
  if(!S.artifacts.includes(id)){S.artifacts.push(id);save();track("artifact",id);hud();(props.artifacts||[]).forEach(x=>{if(x.a.id===id)x.ring.material.color.set(PALETTE.greenBright)})}
  const demos=ART_DEMOS[id]||[];
  demoStop($("art-term"));
  $("s-artifact").innerHTML=`<div class="hour">${icon("compass")}${S.artifacts.length} of ${ARTIFACTS.length} artifacts found</div><h2>${a.name}</h2><p class="small muted">${a.prop} · ${a.concept}</p><p>${a.what}</p>`+
    `<div class="row">${demos.map((d,i)=>`<button data-demo="${i}" onclick="runDemo('${id}',${i})">${icon("play")}${d.l}</button>`).join("")}</div>`+
    // The terminal answers a button press, so it is a live region: a reader
    // that is not looking at it hears what came back. It prints command lines,
    // so it gets the walkthrough's ligature rule: a terminal shows two
    // hyphens in front of a flag, never one long dash.
    `<pre class="term" id="art-term" aria-live="polite" style="font-variant-ligatures:none">Press a button. Watch what comes back.</pre>`+
    `<div class="rolinda"><b>Rolinda asks</b>${a.rolinda}</div>`+
    artifactReal(a)+
    `<p class="small muted" id="art-links">In the vault: </p>`;
  // A vault link is a link: an anchor carries the page's link colour, its
  // underline, the focus ring and Enter, where a span with a click handler
  // has none of them. The href is a placeholder the handler swallows, because
  // the note opens in the vault overlay and not at a URL. Built as nodes, so
  // the title is text and never markup.
  const links=$("art-links");a.links.forEach((n,k)=>{if(k)links.append(" · ");
    const el=document.createElement("a");el.className="wl";el.href="#";el.textContent=n;
    el.onclick=ev=>{ev.preventDefault();openNote(n)};links.append(el)});
  // The sheet is built after boot, so its command block is wrapped and folded here.
  wrapCommands();$("s-artifact").querySelectorAll("details.cmds").forEach(d=>{d.open=cmdsOpen()});
  $("bub-face").innerHTML=FACE.rolinda;$("bub-who").textContent=roleName("rolinda");typeOut($("bub-text"),a.rolinda);
  openSheet("s-artifact")};
// One transcript at a time: the lines a demo still owes are cancelled before
// the next one starts, or two demos print into the same terminal at once.
function demoStop(el){if(!el)return;(el._demo||[]).forEach(clearTimeout);el._demo=[]}
window.runDemo=function(id,i){const d=(ART_DEMOS[id]||[])[i];if(!d)return;const el=$("art-term");if(!el)return;
  demoStop(el);el.textContent="";
  // Typing is the animation; reduced motion gets the whole transcript at once,
  // which is also the one announcement a screen reader hears.
  if(reducedMotion()){el.textContent=d.o.join("\n");el.scrollTop=el.scrollHeight;return}
  el._demo=d.o.map((line,k)=>setTimeout(()=>{el.textContent+=(k?"\n":"")+line;el.scrollTop=el.scrollHeight},k*320))};
// Test seam: the ring each artifact of this island is drawn with, the radius
// the walk-up test uses, and the radius the walker is pushed out of at the
// same centre, so a test can assert the ring is the zone and can be stood on.
window.__rings=()=>(props.artifacts||[]).map(x=>({id:x.a.id,zone:x.a.r,
  r:x.ring.geometry.parameters.radius,tube:x.ring.geometry.parameters.tube,y:x.ring.position.y,
  block:(obstacles||[]).filter(o=>Math.hypot(o[0]-x.a.pos[0],o[1]-x.a.pos[1])<.01)
    .reduce((m,o)=>Math.max(m,o[2]),0)}));
function artifactsMd(){return "# Artifacts\nThings on the island that explain one idea each. Walk up to the yellow ring and press Inspect; a found one turns green. Each one also sets a task from the official documentation of the thing, checked in your camp.\n"+
  ARTIFACTS.map(a=>`- ${S.artifactsBuilt.includes(a.id)?"built for real":S.artifacts.includes(a.id)?"found":"not yet"}: **${a.name}** (${a.prop}): ${a.concept}. Do it for real: ${a.real.title} (\`vibe check --artifact ${a.id}\`). See ${a.links.map(l=>"[["+l+"]]").join(", ")}.`).join("\n")+"\n- Back: [[Tonight]]\n#concept"}
window.__artifacts=()=>ARTIFACTS;
