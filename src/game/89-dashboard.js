/* ---------------- dashboard ---------------- */
// Every number on this panel is derived from S: the progress object plus the
// event log in 00-state.js. Nothing is stored twice, so a reset empties the
// dashboard with the rest of the state. Charts are inline SVG: they scale to
// a phone, print, and need no library. One hue per meaning, as in the rest of
// the game: green done, yellow in progress, blue neutral, orange XP, red only
// for a problem.
const DAY_MS=864e5;
// The same worth the terminal gives a claim (vibemap/quests.py): a workstream
// is 100, a mentor or an artifact built for real is half of one.
const DASH_XP={claim:100,verified:50,built:50,artifact:10};
const DASH_LABEL={session:"Session started",open:"Stop opened",claim:"Stop delivered",dwell:"Time in a stop",play:"Time on the island",artifact:"Artifact inspected",built:"Artifact built for real",mentor:"Mentor met",verified:"Mentor verified",chat:"Question asked",item:"Item collected",achievement:"Achievement unlocked",interests:"Shelves chosen"};
const DASH_HUE={claim:"var(--green-bright)",built:"var(--green-bright)",verified:"var(--green-bright)",open:"var(--yellow)",dwell:"var(--yellow)",achievement:"var(--yellow)",play:"var(--blue-bright)",session:"var(--blue-bright)",chat:"var(--blue-bright)",artifact:"var(--orange)",mentor:"var(--orange)",item:"var(--orange)",interests:"var(--blue)"};
function dashEvents(){return Array.isArray(S.events)?S.events:[]}
function dayStart(ts){const d=new Date(ts);return new Date(d.getFullYear(),d.getMonth(),d.getDate()).getTime()}
function fmtDur(s){s=Math.round(s||0);if(s<60)return s+"s";const m=Math.round(s/60);return m<60?m+"m":Math.floor(m/60)+"h "+(m%60)+"m"}
function fmtDay(ts){const d=new Date(ts);return d.toLocaleDateString(undefined,{month:"short",day:"numeric"})}
function fmtClock(ts){const d=new Date(ts);return String(d.getHours()).padStart(2,"0")+":"+String(d.getMinutes()).padStart(2,"0")}

// One pass over the log; every chart below reads from what it returns.
function dashStats(){
  const ev=dashEvents(),today=dayStart(Date.now());
  const stops=Object.keys(S.doneW||{}).reduce((n,w)=>n+(S.doneW[w]||[]).length,0);
  const perDay={},xpDay={};
  ev.forEach(e=>{const k=dayStart(e.ts);perDay[k]=(perDay[k]||0)+1;xpDay[k]=(xpDay[k]||0)+(DASH_XP[e.kind]||0)});
  // A streak is days in a row with something on them, ending today or, if
  // nothing has happened yet today, yesterday.
  let streak=0,cursor=perDay[today]?today:today-DAY_MS;
  while(perDay[cursor]){streak++;cursor-=DAY_MS}
  const days=[];for(let i=6;i>=0;i--)days.push(today-i*DAY_MS);
  const dwell={};ev.filter(e=>e.kind==="dwell").forEach(e=>{const m=/^s-(\d)$/.exec(e.id);if(m)dwell[+m[1]]=(dwell[+m[1]]||0)+(e.v||0)});
  return {
    ev:ev,stops:stops,total:32,
    xp:ev.reduce((n,e)=>n+(DASH_XP[e.kind]||0),0),
    streak:streak,
    played:ev.filter(e=>e.kind==="play").reduce((n,e)=>n+(e.v||60),0),
    artifacts:(S.artifacts||[]).length,built:(S.artifactsBuilt||[]).length,
    mentors:(S.mentors||[]).length,met:Object.keys(S.met||{}).length,
    days:days,perDay:perDay,xpDay:xpDay,dwell:dwell,
    claims:ev.filter(e=>e.kind==="claim"),
    items:ev.filter(e=>e.kind==="item"||e.kind==="achievement").length
  };
}

// ---- chart primitives: viewBox only, so every one of them is fluid --------
function svgWrap(w,h,label,inner){return `<svg class="ch" viewBox="0 0 ${w} ${h}" preserveAspectRatio="xMidYMid meet" role="img" aria-label="${escAttr(label)}">${inner}</svg>`}
function escAttr(s){return String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/"/g,"&quot;")}
function dashEmpty(msg){return `<p class="small muted dash-empty">${msg}</p>`}

// A sparkline is a shape, not a reading: no axis, no dots, one hue.
function dashSpark(values,hue){
  const w=120,h=26,max=Math.max(...values),n=values.length;
  // A flat line at zero says nothing; an empty tile says it honestly.
  if(n<2||!(max>0))return "";
  const pts=values.map((v,i)=>[2+i*(w-4)/(n-1),h-2-(v/max)*(h-6)]);
  const line=pts.map((p,i)=>(i?"L":"M")+p[0].toFixed(1)+" "+p[1].toFixed(1)).join(" ");
  const area=line+` L ${(w-2).toFixed(1)} ${h-1} L 2 ${h-1} Z`;
  return svgWrap(w,h,"Last seven days",`<path d="${area}" fill="${hue}" fill-opacity=".12"/><path d="${line}" fill="none" stroke="${hue}" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>`);
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

// Time per stop: horizontal bars, the neutral hue, direct labels.
function dashBars(st){
  const rows=[1,2,3,4,5,6,7,8].map(n=>({n:n,v:st.dwell[n]||0})).filter(r=>r.v>0);
  if(!rows.length)return dashEmpty("Open a stop and stay a moment; the time you spend lands here.");
  const w=320,rh=22,max=Math.max(...rows.map(r=>r.v)),l=28,rgt=52;
  const bars=rows.map((r,i)=>{
    const len=Math.max(3,(w-l-rgt)*r.v/max),y=i*rh;
    const done=S.done.includes(r.n);
    return `<text x="0" y="${y+14}" class="at">${r.n}</text>`+
      `<rect x="${l}" y="${y+3}" width="${len.toFixed(1)}" height="12" rx="4" fill="${done?"var(--green)":"var(--blue)"}"><title>Stop ${r.n}: ${fmtDur(r.v)}</title></rect>`+
      `<text x="${w}" y="${y+14}" text-anchor="end" class="at v">${fmtDur(r.v)}</text>`});
  return svgWrap(w,rows.length*rh,"Time spent in each stop",bars.join(""))+
    `<p class="small muted legend"><span class="sw green"></span> delivered <span class="sw blue"></span> open, not delivered</p>`;
}

// The path taken: the stops in the order they were delivered.
function dashPath(st){
  if(!st.claims.length)return dashEmpty("Deliver a stop and the path starts here.");
  const name=e=>(WORLDS[e.world]||{name:e.world}).name;
  return `<div class="path">`+st.claims.map(e=>
    `<span class="step" title="${escAttr(name(e)+", stop "+e.id+", "+fmtDay(e.ts)+" "+fmtClock(e.ts))}">${name(e).split(" ")[0]} ${e.id}</span>`).join(`<span class="arrow" aria-hidden="true">&rsaquo;</span>`)+
    `</div><p class="small muted legend">Island and stop, in the order you delivered them.</p>`;
}

function dashFeed(st){
  const recent=st.ev.slice(-12).reverse();
  if(!recent.length)return dashEmpty("The feed fills as you play.");
  return `<ul class="feed">`+recent.map(e=>
    `<li><i style="background:${DASH_HUE[e.kind]||"var(--muted)"}"></i><span>${DASH_LABEL[e.kind]||e.kind}${e.id&&e.kind!=="session"?" <b>"+escAttr(e.id)+"</b>":""}${typeof e.v==="number"?" <span class='muted'>"+fmtDur(e.v)+"</span>":""}</span><span class="when">${fmtDay(e.ts)} ${fmtClock(e.ts)}</span></li>`).join("")+`</ul>`;
}

// Progress on the shelves you chose. The collectibles are the tree's own
// topics lying on the islands, so "found of there" is a real count per shelf
// rather than a new number to keep.
function dashShelves(){
  if(typeof ITEMS==="undefined"||typeof TREE==="undefined")return "";
  const shelf={};Object.keys(TREE).forEach(c=>TREE[c].forEach(t=>{shelf[t.id]=c}));
  const byId={};(typeof CATS==="undefined"?[]:CATS).forEach(([c,n])=>byId[c]=n);
  const got=sl("items");const per={};
  ITEMS.items.forEach(i=>{const c=shelf[i.topic];if(!c||!wantsShelf(c))return;
    if(!per[c])per[c]={n:0,of:0};per[c].of++;if(got.includes(i.id))per[c].n++});
  const rows=Object.keys(per);
  if(!rows.length)return dashEmpty("Pick a shelf under Settings and this fills with what you found on it.");
  const w=320,rh=22,l=124;
  const bars=rows.map((c,i)=>{const y=i*rh,frac=per[c].of?per[c].n/per[c].of:0;
    return `<text x="0" y="${y+14}" class="at">${escAttr(byId[c]||c).slice(0,18)}</text>`+
      `<rect x="${l}" y="${y+3}" width="${(w-l-34)}" height="12" rx="4" fill="var(--hairline-2)"/>`+
      `<rect x="${l}" y="${y+3}" width="${((w-l-34)*frac).toFixed(1)}" height="12" rx="4" fill="${CAT_COL[c]}"><title>${escAttr(byId[c]||c)}: ${per[c].n} of ${per[c].of}</title></rect>`+
      `<text x="${w}" y="${y+14}" text-anchor="end" class="at v">${per[c].n}/${per[c].of}</text>`}).join("");
  return svgWrap(w,rows.length*rh,"Things found on the shelves you chose",bars)+
    `<p class="small muted legend">Collectibles on your shelves, found of what is out there. Nothing is locked; the other shelves are simply not counted here.</p>`;
}
function renderDashboard(){
  const st=dashStats();
  const per=k=>st.days.map(d=>{const day=d;return st.ev.filter(e=>e.kind===k&&dayStart(e.ts)===day).length});
  const xpSeries=st.days.map(d=>st.xpDay[d]||0);
  const playSeries=st.days.map(d=>st.ev.filter(e=>e.kind==="play"&&dayStart(e.ts)===d).reduce((n,e)=>n+(e.v||60),0)/60);
  const tiles=[
    dashTile("Stops delivered",`${st.stops}<span class="of">/${st.total}</span>`,Math.round(st.stops/st.total*100)+" percent of the campaign",dashSpark(per("claim"),"var(--green-bright)")),
    dashTile("XP earned",String(st.xp),"100 a stop, 50 a mentor or a build",dashSpark(xpSeries,"var(--orange)")),
    dashTile("Day streak",String(st.streak),st.streak?"days in a row":"nothing today yet",dashSpark(st.days.map(d=>st.perDay[d]||0),"var(--yellow)")),
    dashTile("Time played",fmtDur(st.played),"counted a minute at a time",dashSpark(playSeries,"var(--blue-bright)")),
    dashTile("Artifacts",`${st.artifacts}<span class="of">/${(typeof ARTIFACTS!=="undefined"?ARTIFACTS.length:21)}</span>`,st.built+" built for real in your camp",dashSpark(per("artifact"),"var(--orange)")),
    dashTile("Mentors",`${st.mentors}<span class="of">/${(typeof MENTORS!=="undefined"?MENTORS.length:12)}</span>`,st.met+" met on the islands, verified here",dashSpark(per("mentor"),"var(--orange)"))
  ].join("");
  const rings=Object.keys(WORLDS).map(w=>dashRing(WORLDS[w].name,(S.doneW[w]||[]).length,8,(S.doneW[w]||[]).length===8?"var(--green-bright)":"var(--yellow)")).join("");
  $("s-dash").innerHTML=`<h2>Dashboard</h2>
   <p class="small muted">Everything this browser has watched you do. It stays here: the progress code carries your stops, never your log. ${st.ev.length} events recorded.</p>
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
// Test seam: the derived numbers, so a test can assert on them without
// re-deriving the shapes by hand.
window.__dash=()=>{const st=dashStats();return {events:st.ev.length,stops:st.stops,xp:st.xp,streak:st.streak,played:st.played,dwell:st.dwell,claims:st.claims.length}};
