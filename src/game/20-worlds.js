const WORLDS={
 campus:{name:"Innovation Campus",tag:"Green island, harbour, airstrip. The default environment.",swatch:"#79CC72",
  grass:"#79CC72",dirt:"#9C7A4E",bank:"#E3D2B0",water:"#2E9BD6",river:"#3FB0E8",fog:"#9BD3F5",tree:"mixed",
  sky:["#9BD3F5","#F7C88A","#E58C78","#7C6BA8","#2E3468","#171C48","#0B1230","#070B22","#04061A"],
  land:[[0,0,15],[10,-9,6],[-12,7,5.5],[7,13,5],[-9,-12,5.5],[4,-16,6],[15,4,5]],
  plots:[[0,10],[-9,8],[-13,-1],[-7,-11],[3,-13],[12,-8],[14,3],[8,11]],
  way:[[2.5,5],[0,10],[-9,8],[-13,-1],[-7,-11],[3,-13],[12,-8],[14,3],[8,11],[3.5,6]],
  annex:[[0,17.5],[-14.2,12.6],[-20,-1.5],[-5,-18.5],[4,-21],[17,-13],[18.5,-3],[8.5,19]],
  river:[[-21,6],[-16,4.5],[-11,3.5],[-7,3.6],[-4,4]],lake:[-4,4],bridge:[-11,3.5,.22],
  extras:["harbour","airstrip","windmill","lighthouse","balloon","mountain","stall","well","birds","flowers"]},
 winter:{name:"Cold Storage Cluster",tag:"Snow, ice, pines, aurora at night. Data at rest.",swatch:"#E8F1FA",
  grass:"#EAF2F8",dirt:"#7C8B9A",bank:"#D6E3EC",water:"#4C8FD1",river:"#A9D5F2",fog:"#C7DCEB",tree:"pine",
  sky:["#C7DCEB","#E9C9B4","#C58AA1","#6C6AA6","#2A3660","#12203F","#0A1530","#060D24","#04081A"],
  land:[[0,0,15],[11,8,6],[-12,-8,6],[-8,12,5],[8,-14,6],[-16,3,4.5],[15,-5,5]],
  plots:[[0,10],[-9,9],[-14,3],[-11,-8],[-2,-13],[9,-12],[15,-3],[10,8]],
  way:[[2.5,5],[0,10],[-9,9],[-14,3],[-11,-8],[-2,-13],[9,-12],[15,-3],[10,8],[3.5,6]],
  annex:[[0,17],[-14,14],[-20.8,4.5],[-16.7,-12.1],[-3,-20],[7,-19.5],[20,2],[15.5,12.4]],
  river:[[-20,-2],[-15,-1],[-10,1],[-6,3]],lake:[-4,4],bridge:[-12.5,-.2,.2],
  extras:["harbour","mountain","snowmen","aurora","snow","well","birds","icefloes"]},
 desert:{name:"Sandbox Environment",tag:"Dunes, mesas, an oasis, tumbleweed. Non-prod.",swatch:"#E9C46A",
  grass:"#E9C46A",dirt:"#B07D3A",bank:"#F1DDA2",water:"#2AA7B8",river:"#3FC1CF",fog:"#F4D9A6",tree:"palm",
  sky:["#F4D9A6","#F7B267","#E8845C","#9B5C8E","#4A3D7A","#25234E","#141634","#0B0C24","#06071A"],
  land:[[0,0,15],[12,-7,6],[-13,5,6],[6,13,5],[-8,-13,5.5],[16,6,5]],
  plots:[[2,10],[-8,9],[-14,1],[-9,-10],[2,-13],[12,-9],[15,2],[9,10]],
  way:[[2.5,5],[2,10],[-8,9],[-14,1],[-9,-10],[2,-13],[12,-9],[15,2],[9,10],[3.5,6]],
  annex:[[3.4,16.9],[-12.6,14.2],[-21,1.5],[-16,-12],[3,-20],[19,-11],[22,3],[14.2,15.8]],
  river:null,lake:[-4,4],bridge:null,
  extras:["mesas","cacti","tumbleweed","balloon","stall","well","dunes","flowers"]},
 prod:{name:"Production Environment",tag:"Volcano, lava, ash. Do not touch anything.",swatch:"#3A3A46",
  grass:"#4A4A58",dirt:"#26262E",bank:"#5B5B6A",water:"#1B3A5C",river:"#FF6A1A",fog:"#5A3C46",tree:"dead",
  sky:["#5A3C46","#8B4A3E","#6B2E3C","#3F2245","#24173A","#150E2B","#0B0720","#07051A","#040312"],
  land:[[0,0,15],[10,-9,6],[-12,7,5.5],[7,13,5],[-9,-12,5.5],[15,4,5]],
  plots:[[0,10],[-9,8],[-13,-1],[-7,-11],[3,-13],[12,-8],[14,3],[8,11]],
  way:[[2.5,5],[0,10],[-9,8],[-13,-1],[-7,-11],[3,-13],[12,-8],[14,3],[8,11],[3.5,6]],
  annex:[[0,17.5],[-12,15],[-20,-1.5],[-5,-18.5],[4,-21],[17,-13],[18.5,-3],[8.5,19]],
  river:[[-21,6],[-16,4.5],[-11,3.5],[-7,3.6],[-4,4]],lake:[-4,4],bridge:[-11,3.5,.22],
  extras:["volcano","embers","harbour","lighthouse","well","birds"]}
};
// One scale for the whole map, applied once here to every coordinate the data
// carries (WORLDS, MENTORS, ARTIFACTS); the literal positions in the world
// builder go through P(). Meshes keep their size, so the island grows around
// the walker rather than the walker shrinking. Speed, camera, fog and sky
// distances scale with it in their own modules so the feel stays the same.
const WORLD_SCALE=1.6;
const P=(x,z)=>[x*WORLD_SCALE,z*WORLD_SCALE];
// Each plot has an annex: a small land blob 6 to 8 data units outward, reached
// by a spur off the ring, hidden until that stop is done. Its radius, scaled.
const ANNEX_R=3.2*WORLD_SCALE;
function scaleWorld(w){const s=WORLD_SCALE,pt=p=>[p[0]*s,p[1]*s];
  w.land=w.land.map(b=>[b[0]*s,b[1]*s,b[2]*s]);w.plots=w.plots.map(pt);w.way=w.way.map(pt);w.annex=w.annex.map(pt);
  if(w.river)w.river=w.river.map(pt);w.lake=pt(w.lake);if(w.bridge)w.bridge=[w.bridge[0]*s,w.bridge[1]*s,w.bridge[2]]}
Object.values(WORLDS).forEach(scaleWorld);
MENTORS.forEach(m=>{m.pos=P(m.pos[0],m.pos[1])});
// The cafe is the inn's terrace, and the inn stays unscaled at the origin.
(typeof ARTIFACTS==="undefined"?[]:ARTIFACTS).forEach(a=>{if(a.id==="cafe")return;a.pos=P(a.pos[0],a.pos[1]);a.r*=WORLD_SCALE});
let W=WORLDS.campus,obstacles=[],annexes=[];
CAMPAIGN.campus.ws=CH.map(c=>({h:c.h,n:c.n,d:c.d}));
let CHW=CH;
