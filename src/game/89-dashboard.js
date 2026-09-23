/* ---------------- dashboard ---------------- */
// Every number on this panel is derived from S: the progress object plus the
// event log in 00-state.js. Nothing is stored twice, so a reset empties the
// dashboard with the rest of the state. Charts are inline SVG: they scale to
// a phone, print, and need no library. One hue per meaning, as in the rest of
// the game: green done, yellow in progress, blue neutral, orange XP, red only
// for a problem.
const DAY_MS=864e5;
// One XP rule for the panel and for the terminal: a stop is the base times
// the difficulty multiplier (vibemap/quests.py XP_BASE, vibemap/config.py
// DIFFICULTIES), a mentor verified or an artifact built for real is half of
// one, and inspecting an artifact pays nothing. A test holds the two tables
// together, so this tile cannot drift from `vibe status`.
const DASH_XP_BASE=100;
const DASH_XP_MULT={beginner:0.8,easy:0.9,normal:1,hard:1.5,expert:2,god:3};
function dashStopXp(){return Math.round(DASH_XP_BASE*(DASH_XP_MULT[difficulty()]||1))}
function dashXp(kind){const full=dashStopXp();
  return kind==="claim"?full:(kind==="verified"||kind==="built")?Math.floor(full/2):0}
// A streak day is a day something was delivered. The report counts the same
// kinds (vibemap/dashboard.py), so one label never means two things: opening
// the game is not progress.
const DASH_DELIVERED=["claim","verified","built"];
const DASH_LABEL={session:"Session started",open:"Stop opened",claim:"Stop delivered",dwell:"Time on a screen",play:"Time on the island",artifact:"Artifact inspected",built:"Artifact built for real",mentor:"Mentor met",verified:"Mentor verified",chat:"Question asked",item:"Item collected",achievement:"Achievement unlocked",interests:"Shelves chosen",world:"Island reached",bottle:"Message in a bottle"};
const DASH_HUE={claim:"var(--green-bright)",built:"var(--green-bright)",verified:"var(--green-bright)",open:"var(--yellow)",dwell:"var(--yellow)",achievement:"var(--yellow)",play:"var(--blue-bright)",session:"var(--blue-bright)",chat:"var(--blue-bright)",world:"var(--blue-bright)",artifact:"var(--orange)",mentor:"var(--orange)",item:"var(--orange)",bottle:"var(--orange)",interests:"var(--blue)"};
// The screens a dwell can be measured on, named the way the game names them.
// s-gen stands for whichever stop was opened last, so it is named from the
// log by dashStopAt() and only falls back to this entry when no stop was.
const DASH_SCREEN={"s-0":"Pre-flight","s-map":"Roadmap","s-dash":"Stats","s-settings":"Settings","s-setup":"Setup","s-mentor":"A mentor","s-artifact":"An artifact","s-chat":"Ask","s-pack":"A topic pack","s-gen":"A stop"};
const STOP_SHEET=/^s-(\d+)$/;
function dashEvents(){return Array.isArray(S.events)?S.events:[]}
function dayStart(ts){const d=new Date(ts);return new Date(d.getFullYear(),d.getMonth(),d.getDate()).getTime()}
function fmtDur(s){s=Math.round(s||0);if(s<60)return s+"s";const m=Math.round(s/60);return m<60?m+"m":Math.floor(m/60)+"h "+(m%60)+"m"}
function fmtDay(ts){const d=new Date(ts);return d.toLocaleDateString(undefined,{month:"short",day:"numeric"})}
function fmtClock(ts){const d=new Date(ts);return String(d.getHours()).padStart(2,"0")+":"+String(d.getMinutes()).padStart(2,"0")}
// The island a world id names, and the one word a chart labels it with.
function dashIsland(w){return String((WORLDS[w]||{name:w}).name||w)}
function dashShort(w){return dashIsland(w).split(" ")[0]}
// A name is read, not hovered: cut it on a word when it is too long for the
// gutter and say so with an ellipsis, never mid-word and never silently.
function dashCut(text,max){const s=String(text);if(s.length<=max)return s;
  const cut=s.slice(0,max-1),at=cut.lastIndexOf(" ");
  return (at>8?cut.slice(0,at):cut).replace(/[ ,]+$/,"")+"…"}
// What a feed line names: a screen and an island by their name, a shelf by
// the name Settings shows, everything else by the id the game already prints.
function dashWhat(e){
  if(e.kind==="world")return dashIsland(e.id);
  if(e.kind==="dwell")return DASH_SCREEN[e.id]||e.id;
  if(e.kind==="interests")return e.id==="all"?"everything":String(e.id).split(",").map(shelfName).join(", ");
  return e.id}
// Which stop a dwell measured, and on which island. A campus stop has its
// number in the sheet id; every other island renders into s-gen, so the
// "open" event just before it is what names the stop. Without that pair
// three of the four islands would report their time as one screen.
function dashStopAt(e,open){const m=STOP_SHEET.exec(e.id),n=m?+m[1]:0;
  return n>=1?{n:n,world:e.world}:(e.id==="s-gen"?open:null)}
// The log with the name every view shows already resolved, because a dwell
// only knows its stop from the event before it. One pass, one shape.
function dashRows(ev){
  const out=[];let open=null;
  ev.forEach(e=>{
    if(e.kind==="open"){const n=+e.id;open=n>=1?{n:n,world:e.world}:null}
    const at=e.kind==="dwell"?dashStopAt(e,open):null;
    out.push({kind:e.kind,ts:e.ts,v:e.v,world:e.world,at:at,
      id:at?dashShort(at.world)+" "+at.n:dashWhat(e)})});
  return out}
function dashDwell(rows){
  const out={};
  rows.forEach(r=>{if(!r.at)return;
    const k=r.at.world+":"+r.at.n;out[k]=(out[k]||0)+(r.v||0)});
  return out}

// One pass over the log; every chart below reads from what it returns.
function dashStats(){
  const ev=dashEvents(),rows=dashRows(ev),today=dayStart(Date.now());
  const stops=Object.keys(S.doneW||{}).reduce((n,w)=>n+(S.doneW[w]||[]).length,0);
  const perDay={},xpDay={},doneDay={};
  ev.forEach(e=>{const k=dayStart(e.ts);perDay[k]=(perDay[k]||0)+1;
    const xp=dashXp(e.kind);if(xp)xpDay[k]=(xpDay[k]||0)+xp;
    if(DASH_DELIVERED.indexOf(e.kind)>=0)doneDay[k]=(doneDay[k]||0)+1});
  // A streak is days in a row with something delivered on them, ending today
  // or, if nothing has been delivered yet today, yesterday.
  let streak=0,cursor=doneDay[today]?today:today-DAY_MS;
  while(doneDay[cursor]){streak++;cursor-=DAY_MS}
  const days=[];for(let i=6;i>=0;i--)days.push(today-i*DAY_MS);
  return {
    ev:ev,rows:rows,stops:stops,total:32,
    xp:ev.reduce((n,e)=>n+dashXp(e.kind),0),
    streak:streak,
    played:ev.filter(e=>e.kind==="play").reduce((n,e)=>n+(e.v||60),0),
    artifacts:(S.artifacts||[]).length,built:(S.artifactsBuilt||[]).length,
    mentors:(S.mentors||[]).length,
    // Met on the islands or verified in the camp: both are an encounter.
    met:Object.keys(S.met||{}).concat(S.mentors||[]).filter((id,i,all)=>all.indexOf(id)===i).length,
    days:days,perDay:perDay,xpDay:xpDay,doneDay:doneDay,dwell:dashDwell(rows),
    claims:ev.filter(e=>e.kind==="claim"),
    items:ev.filter(e=>e.kind==="item"||e.kind==="achievement").length
  };
}

// ---- chart primitives: viewBox only, so every one of them is fluid --------
function svgWrap(w,h,label,inner){return `<svg class="ch" viewBox="0 0 ${w} ${h}" preserveAspectRatio="xMidYMid meet" role="img" aria-label="${esc(label)}">${inner}</svg>`}
function dashEmpty(msg){return `<p class="small muted dash-empty">${msg}</p>`}

// A sparkline is a shape, not a reading, so the label carries the reading:
// what the line counts and its seven days, in order (docs/DESIGN.md).
function dashReading(name,values){return name+", last seven days: "+values.map(v=>Math.round(v)).join(", ")}
function dashSpark(values,hue,name){
  const w=120,h=26,max=Math.max(...values),n=values.length;
  // A flat line at zero says nothing; an empty tile says it honestly.
  if(n<2||!(max>0))return "";
  const reading=dashReading(name,values);
  const pts=values.map((v,i)=>[2+i*(w-4)/(n-1),h-2-(v/max)*(h-6)]);
  const line=pts.map((p,i)=>(i?"L":"M")+p[0].toFixed(1)+" "+p[1].toFixed(1)).join(" ");
  const area=line+` L ${(w-2).toFixed(1)} ${h-1} L 2 ${h-1} Z`;
  return svgWrap(w,h,reading,`<path d="${area}" fill="${hue}" fill-opacity=".12"/><path d="${line}" fill="none" stroke="${hue}" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"><title>${esc(reading)}</title></path>`);
}

function dashTile(label,value,caption,spark){
  return `<div class="tile"><span class="tl">${label}</span><b class="tv">${value}</b><span class="tc">${caption}</span>${spark||""}</div>`;
}

// One ring per island: the arc is the stops delivered, the track is the rest.
function dashRing(name,done,total,hue){
  const r=26,c=2*Math.PI*r,frac=total?done/total:0;
  const arc=`<circle cx="32" cy="32" r="${r}" fill="none" stroke="${hue}" stroke-width="7" stroke-linecap="round" stroke-dasharray="${(c*frac).toFixed(1)} ${c.toFixed(1)}" transform="rotate(-90 32 32)"/>`;
  const svg=svgWrap(64,64,`${name}: ${done} of ${total} stops`,
    `<circle cx="32" cy="32" r="${r}" fill="none" stroke="var(--hairline-2)" stroke-width="7"/>${frac>0?arc:""}`+
    `<text x="32" y="36" text-anchor="middle" class="rt">${done}</text>`);
  return `<div class="ring">${svg}<span class="rl">${name}</span><span class="rn">${done}/${total}</span></div>`;
}

// XP over time: one line, one axis, days on the bottom. A single day of play
// is a number, not a line, so it says so instead of drawing one point.
function dashXpLine(st){
  const keys=Object.keys(st.xpDay).map(Number).sort((a,b)=>a-b);
  if(keys.length<2)return dashEmpty("Play on a second day and the line appears here. So far: "+st.xp+" XP.");
  const series=[];let sum=0;
  keys.forEach(k=>{sum+=st.xpDay[k];series.push([k,sum])});
  const w=320,h=120,l=36,r=10,t=12,b=22,max=series[series.length-1][1]||1;
  const x=i=>l+i*(w-l-r)/(series.length-1),y=v=>h-b-(v/max)*(h-t-b);
  const line=series.map((s,i)=>(i?"L":"M")+x(i).toFixed(1)+" "+y(s[1]).toFixed(1)).join(" ");
  const dots=series.map((s,i)=>`<circle cx="${x(i).toFixed(1)}" cy="${y(s[1]).toFixed(1)}" r="3" fill="var(--orange)"><title>${fmtDay(s[0])}: ${s[1]} XP</title></circle>`).join("");
  return svgWrap(w,h,`Total XP over time, ${max} XP after ${series.length} days`,
    `<line x1="${l}" y1="${y(max)}" x2="${w-r}" y2="${y(max)}" class="grid"/>`+
    `<line x1="${l}" y1="${h-b}" x2="${w-r}" y2="${h-b}" class="axis"/>`+
    `<text x="${l-6}" y="${y(max)+4}" text-anchor="end" class="at">${max}</text>`+
    `<text x="${l-6}" y="${h-b+4}" text-anchor="end" class="at">0</text>`+
    `<path d="${line}" fill="none" stroke="var(--orange)" stroke-width="2" stroke-linejoin="round"/>${dots}`+
    `<text x="${l}" y="${h-6}" class="at">${fmtDay(series[0][0])}</text>`+
    `<text x="${w-r}" y="${h-6}" text-anchor="end" class="at">${fmtDay(series[series.length-1][0])}</text>`);
}

// Day by hour: one hue, light to dark by count, the sequential rule.
function dashHeat(st){
  if(!st.ev.length)return dashEmpty("Nothing recorded yet. Walk to a stop and open it.");
  const grid={};st.ev.forEach(e=>{const d=dayStart(e.ts);if(d<st.days[0])return;const h=new Date(e.ts).getHours();grid[d+":"+h]=(grid[d+":"+h]||0)+1});
  const max=Math.max(1,...Object.values(grid));
  const w=320,l=34,cw=(w-l-4)/24,ch=13,gap=2,h=st.days.length*(ch+gap)+18;
  let cells="";
  st.days.forEach((d,row)=>{
    cells+=`<text x="${l-6}" y="${row*(ch+gap)+ch-3}" text-anchor="end" class="at">${new Date(d).toLocaleDateString(undefined,{weekday:"short"})}</text>`;
    for(let hr=0;hr<24;hr++){const n=grid[d+":"+hr]||0;
      cells+=`<rect x="${(l+hr*cw).toFixed(2)}" y="${row*(ch+gap)}" width="${(cw-gap).toFixed(2)}" height="${ch}" rx="3" fill="var(--green-bright)" fill-opacity="${n?(0.2+0.8*n/max).toFixed(2):"0.06"}">${n?`<title>${fmtDay(d)} ${String(hr).padStart(2,"0")}:00, ${n} events</title>`:""}</rect>`}
  });
  const axis=[0,6,12,18].map(hr=>`<text x="${(l+hr*cw).toFixed(2)}" y="${st.days.length*(ch+gap)+12}" class="at">${String(hr).padStart(2,"0")}</text>`).join("");
  return svgWrap(w,h,`Activity by day and hour, busiest hour ${max} events`,cells+axis)+
    `<p class="small muted legend"><span class="sw" style="opacity:.2"></span><span class="sw" style="opacity:.5"></span><span class="sw" style="opacity:1"></span> quiet to busy, last seven days</p>`;
}

// Time per stop: horizontal bars, the neutral hue, direct labels. A row is
// one stop on one island, so the four islands never share a bar.
function dashBars(st){
  const order=Object.keys(WORLDS);
  const rows=Object.keys(st.dwell).map(k=>{const at=k.split(":");
    return {world:at[0],n:+at[1],v:st.dwell[k]}}).filter(r=>r.v>0)
    .sort((a,b)=>(order.indexOf(a.world)-order.indexOf(b.world))||(a.n-b.n));
  if(!rows.length)return dashEmpty("Open a stop and stay a moment; the time you spend lands here.");
  const w=320,rh=22,max=Math.max(...rows.map(r=>r.v)),l=74,rgt=52;
  const bars=rows.map((r,i)=>{
    const len=Math.max(3,(w-l-rgt)*r.v/max),y=i*rh;
    const done=(S.doneW[r.world]||[]).includes(r.n);
    const name=dashShort(r.world)+" "+r.n;
    return `<text x="0" y="${y+14}" class="at">${esc(name)}</text>`+
      `<rect x="${l}" y="${y+3}" width="${len.toFixed(1)}" height="12" rx="4" fill="${done?"var(--green)":"var(--blue)"}"><title>${esc(dashIsland(r.world)+", stop "+r.n)}: ${fmtDur(r.v)}</title></rect>`+
      `<text x="${w}" y="${y+14}" text-anchor="end" class="at v">${fmtDur(r.v)}</text>`});
  return svgWrap(w,rows.length*rh,"Time spent in each stop, island by island",bars.join(""))+
    `<p class="small muted legend"><span class="sw green"></span> delivered <span class="sw blue"></span> open, not delivered</p>`;
}

// The path taken: the stops in the order they were delivered.
function dashPath(st){
  if(!st.claims.length)return dashEmpty("Deliver a stop and the path starts here.");
  return `<div class="path">`+st.claims.map(e=>
    `<span class="step" title="${esc(dashIsland(e.world)+", stop "+e.id+", "+fmtDay(e.ts)+" "+fmtClock(e.ts))}">${esc(dashShort(e.world))} ${esc(e.id)}</span>`).join(`<span class="arrow" aria-hidden="true">&rsaquo;</span>`)+
    `</div><p class="small muted legend">Island and stop, in the order you delivered them.</p>`;
}

function dashFeed(st){
  // The rows carry the name already: a line never prints an internal id.
  const recent=st.rows.slice(-12).reverse();
  if(!recent.length)return dashEmpty("The feed fills as you play.");
  return `<ul class="feed">`+recent.map(e=>
    `<li><i style="background:${DASH_HUE[e.kind]||"var(--muted)"}"></i><span>${esc(DASH_LABEL[e.kind]||e.kind)}${e.id&&e.kind!=="session"?" <b>"+esc(e.id)+"</b>":""}${typeof e.v==="number"?" <span class='muted'>"+fmtDur(e.v)+"</span>":""}</span><span class="when">${fmtDay(e.ts)} ${fmtClock(e.ts)}</span></li>`).join("")+`</ul>`;
}

// Progress on the shelves you chose. The collectibles are the tree's own
// topics lying on the islands, so "found of there" is a real count per shelf
// rather than a new number to keep.
function dashShelves(){
  if(typeof ITEMS==="undefined"||typeof TREE==="undefined")return "";
  const shelf={};Object.keys(TREE).forEach(c=>TREE[c].forEach(t=>{shelf[t.id]=c}));
  // Every chosen shelf gets a row, including one nothing lies on: 0 of 0 is
  // an answer, and an empty panel would read as "you picked no shelf".
  const per={},rows=(typeof CATS==="undefined"?[]:CATS).map(x=>x[0]).filter(wantsShelf);
  rows.forEach(c=>{per[c]={n:0,of:0}});
  const got=sl("items");
  ITEMS.items.forEach(i=>{const p=per[shelf[i.topic]];if(!p)return;
    p.of++;if(got.includes(i.id))p.n++});
  if(!rows.length)return dashEmpty("No shelves in this camp's tech tree yet.");
  const w=320,rh=22,l=134;
  const bars=rows.map((c,i)=>{const y=i*rh,frac=per[c].of?per[c].n/per[c].of:0;
    return `<text x="0" y="${y+14}" class="at">${esc(dashCut(shelfName(c),24))}</text>`+
      `<rect x="${l}" y="${y+3}" width="${(w-l-34)}" height="12" rx="4" fill="var(--hairline-2)"/>`+
      `<rect x="${l}" y="${y+3}" width="${((w-l-34)*frac).toFixed(1)}" height="12" rx="4" fill="${CAT_COL[c]}"><title>${esc(shelfName(c))}: ${per[c].n} of ${per[c].of}</title></rect>`+
      `<text x="${w}" y="${y+14}" text-anchor="end" class="at v">${per[c].n}/${per[c].of}</text>`}).join("");
  return svgWrap(w,rows.length*rh,"Things found on the shelves you chose",bars)+
    `<p class="small muted legend">Collectibles on your shelves, found of what is out there. Nothing is locked; the other shelves are simply not counted here.</p>`;
}
function renderDashboard(){
  const st=dashStats();
  const per=k=>st.days.map(d=>{const day=d;return st.ev.filter(e=>e.kind===k&&dayStart(e.ts)===day).length});
  const xpSeries=st.days.map(d=>st.xpDay[d]||0);
  const playSeries=st.days.map(d=>st.ev.filter(e=>e.kind==="play"&&dayStart(e.ts)===d).reduce((n,e)=>n+(e.v||60),0)/60);
  const stopXp=dashStopXp();
  const tiles=[
    dashTile("Stops delivered",`${st.stops}<span class="of">/${st.total}</span>`,Math.round(st.stops/st.total*100)+" percent of the campaign",dashSpark(per("claim"),"var(--green-bright)","Stops delivered per day")),
    dashTile("XP earned",String(st.xp),stopXp+" a stop, "+Math.floor(stopXp/2)+" a mentor or a build, at "+esc(difficulty())+" difficulty",dashSpark(xpSeries,"var(--orange)","XP earned per day")),
    dashTile("Day streak",String(st.streak),st.streak?"days in a row with something delivered":"nothing delivered today yet",dashSpark(st.days.map(d=>st.doneDay[d]||0),"var(--yellow)","Things delivered per day")),
    dashTile("Time played",fmtDur(st.played),"counted a minute at a time",dashSpark(playSeries,"var(--blue-bright)","Minutes played per day")),
    dashTile("Artifacts",`${st.artifacts}<span class="of">/${(typeof ARTIFACTS!=="undefined"?ARTIFACTS.length:21)}</span>`,st.built+" built for real in your camp",dashSpark(per("artifact"),"var(--orange)","Artifacts inspected per day")),
    dashTile("Mentors met",`${esc(st.met)}<span class="of">/${(typeof MENTORS!=="undefined"?MENTORS.length:12)}</span>`,st.mentors+" verified in your camp",dashSpark(per("mentor"),"var(--orange)","Mentors met per day"))
  ].join("");
  const rings=Object.keys(WORLDS).map(w=>dashRing(WORLDS[w].name,(S.doneW[w]||[]).length,8,(S.doneW[w]||[]).length===8?"var(--green-bright)":"var(--yellow)")).join("");
  $("s-dash").innerHTML=`<h2>Dashboard</h2>
   <p class="small muted">Everything this browser has watched you do. It stays here: the progress code carries your stops, never your log. ${st.ev.length}${st.ev.length===1?" event":" events"} recorded.</p>
   <div class="tiles" aria-live="polite">${tiles}</div>
   <div class="card"><h3>${icon("globe")}Progress by island</h3><div class="rings">${rings}</div></div>
   <div class="card"><h3>${icon("trophy")}XP over time</h3>${dashXpLine(st)}</div>
   <div class="card"><h3>${icon("git-branch")}Your shelves</h3>${dashShelves()}</div>
   <div class="card"><h3>${icon("flag")}Activity by day and hour</h3>${dashHeat(st)}</div>
   <div class="card"><h3>${icon("milestone")}Time per stop</h3>${dashBars(st)}</div>
   <div class="card"><h3>${icon("map")}The path you took</h3>${dashPath(st)}</div>
   <div class="card"><h3>${icon("rss")}Recent events</h3>${dashFeed(st)}</div>
   <div class="row"><button data-icon="download" onclick="openSheet('s-map')">Export progress</button><button onclick="closeSheet()">Back to the island</button></div>`;
  iconize($("s-dash"));
}
window.openDashboard=function(){renderDashboard();openSheet("s-dash")};
// Time played is the one metric with no click behind it, so the panel counts
// it: one event a minute while the island is on screen and the tab is visible.
setInterval(()=>{if(typeof started!=="undefined"&&started&&!document.hidden)track("play","tick",60)},60000);
/* ---------------- the break card ---------------- */
// After about fifty minutes on screen in one sitting Rolinda says, once, that
// this is a good place to stop, and where the player is. It never blocks: it
// waits until no stop or panel is open, it goes with one click or Escape, and
// it can be switched off. The sitting is read from the play ticks above, which
// only count while the tab is visible, so a locked phone earns nothing; a gap
// of ten minutes between ticks ends a sitting. A card nobody is there to read
// is not shown: some key or touch in the last two minutes is the proof.
const BREAK_AFTER_S=50*60,BREAK_GAP_MS=10*60000,BREAK_AWAY_MS=2*60000,BREAK_EVERY_MS=3000;
let breakInputAt=0,breakChecks=0;
const breakHere=()=>{breakInputAt=Date.now()};
addEventListener("keydown",breakHere,{capture:true,passive:true});
addEventListener("pointerdown",breakHere,{capture:true,passive:true});
// The current sitting: its seconds on screen and the time of its first tick.
function breakSitting(){const now=Date.now(),ticks=dashEvents().filter(e=>e.kind==="play"&&e.id==="tick");
  let s=0,from=0,next=now;
  for(let i=ticks.length-1;i>=0;i--){const e=ticks[i];if(next-e.ts>BREAK_GAP_MS)break;s+=e.v||60;from=e.ts;next=e.ts}
  return {s:s,from:from}}
function breakDue(){if(settings().breaks==="off")return false;const st=breakSitting();
  return st.s>=BREAK_AFTER_S&&!(typeof S.breakAt==="number"&&S.breakAt>=st.from)}
// Between stops: the island is on screen and nothing stands in front of it.
function breakClear(){return typeof started!=="undefined"&&started&&!flight&&
  !document.querySelector("#sheet.on,#vault.on,#pal.on,#title:not(.off)")&&!(typeof photoOn==="function"&&photoOn())}
function breakCheck(){breakChecks++;
  if($("breakcard")||!breakDue()||!breakClear()||Date.now()-breakInputAt>BREAK_AWAY_MS)return;
  showBreak(breakSitting().s)}
function breakClose(){const el=$("breakcard");if(el)el.remove()}
function breakButton(label,primary,fn){const b=document.createElement("button");b.type="button";b.textContent=label;
  if(primary)b.className="primary";b.style.minHeight="44px";b.addEventListener("click",fn);return b}
// Where the player is, in Rolinda's words: the island, the stops, the next one.
function breakWhere(){const n=S.done.length,total=stopCount(),next=CH.findIndex((c,i)=>!S.done.includes(i+1));
  return "You are on "+dashIsland(S.world||"campus")+", "+n+" of "+total+" stops delivered"+
    (next<0?", which is all of them.":", and "+CH[next].h+" "+CH[next].n+" is next.")}
function showBreak(secs){S.breakAt=Date.now();save();
  const card=document.createElement("div");card.id="breakcard";card.className="card";
  card.setAttribute("role","region");card.setAttribute("aria-label","A good place to stop");
  // Just under the HUD, whose height is the width's business (one row on a
  // laptop, three on a phone): measured once, as the card appears.
  const hudEl=$("hud"),top=Math.round(hudEl.getBoundingClientRect().bottom-$("stage").getBoundingClientRect().top+12);
  card.style.cssText="position:absolute;z-index:41;left:16px;right:16px;margin:0 auto;max-width:420px;"+
    "top:"+top+"px;box-shadow:var(--lift);pointer-events:auto";
  const who=document.createElement("p");who.className="small muted";who.style.margin="0 0 4px";who.textContent=roleName("rolinda");
  const h=document.createElement("h3");h.style.margin="0 0 6px";h.textContent=Math.floor(secs/60)+" minutes. A good place to stop.";
  // The words are a status line, so a screen reader hears them once as they
  // arrive; the buttons follow in the tab order right after the HUD.
  const p=document.createElement("p");p.className="small";p.setAttribute("role","status");
  const due=exportDue().n>0;
  p.textContent="You have been at it for a while. "+breakWhere()+" Everything is saved in this browser, so it will be right here when you come back."+
    (due?" If you might carry on somewhere else, export a code first.":"");
  const row=document.createElement("div");row.className="row";
  row.appendChild(breakButton("Keep going",true,breakClose));
  if(due)row.appendChild(breakButton("Export progress",false,()=>{breakClose();openSheet("s-map");exportProgress()}));
  row.appendChild(breakButton("Stop reminding me",false,()=>{breakClose();setSetting("breaks","off")}));
  card.append(who,h,p,row);
  hudEl.parentNode.insertBefore(card,hudEl.nextSibling);fx(card)}
addEventListener("keydown",e=>{if(e.key==="Escape"&&!e.defaultPrevented&&$("breakcard")&&!document.querySelector("#sheet.on,#vault.on,#pal.on")){breakClose();e.preventDefault()}});
setInterval(breakCheck,BREAK_EVERY_MS);
// Test seams: the break check as it stands, and a player who walked away.
window.__breaks=()=>({checks:breakChecks,due:breakDue(),sitting:breakSitting().s});
window.__breakAway=()=>{breakInputAt=0};
// Test seam: the derived numbers, so a test can assert on them without
// re-deriving the shapes by hand.
window.__dash=()=>{const st=dashStats();return {events:st.ev.length,stops:st.stops,xp:st.xp,stopXp:dashStopXp(),streak:st.streak,played:st.played,dwell:st.dwell,met:st.met,claims:st.claims.length}};
