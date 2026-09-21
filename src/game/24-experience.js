/* ---------------- the experience contract ---------------- */
// An experience is a view over one shared core (docs/adr/0015). It registers
// under an id and implements seven things, and everything else (state, saving,
// the progress code, the sheet, the vault, search, settings) is core and never
// names a mesh or an experience:
//
//   name      what this view is called
//   build     make the scene from S and the data; idempotent
//   dispose   give back everything it added
//   tick      the per-frame work, honouring reducedMotion()
//   goTo      {island, stop}: bring the player there
//   where     what the player is standing at, or null
//   listing   the same stops as plain data, for the non-3D twin
//
// Nothing calls the registry yet. Boot, the panels and the frame loop go on
// calling buildWorld, openCh and the loop's own helpers by name; this names
// what already exists so a second view can stand next to it. Moving the call
// sites over is the next order's work, and the golden pictures in
// tests/test_game_experience.py are what proves the islands did not move.
const EXPERIENCES={};
const EXPERIENCE_DEFAULT="islands";
// The first stop of a list that is not delivered, or 0 when it is finished:
// nextStop()'s rule, asked of any island rather than only the one underfoot.
function firstUndone(done,count){for(let n=1;n<=count;n++)if(done.indexOf(n)<0)return n;return 0}

EXPERIENCES.islands={
  name:"Islands",
  // The scene is built by init3d the first time (it makes the renderer and
  // starts the frame loop) and by buildWorld on every island after that, so
  // build() is whichever of the two this state asks for. carry hands a walker
  // across a bridge in the new island's coordinates, exactly as a crossing does.
  build(at){at=at||{};
    if(!inited){init3d();return}
    buildWorld(WORLDS[at.island]?at.island:(S.world||"campus"),at.carry);renderWorldPicker()},
  // What a crossing gives back, given back now: the scene goes into the trash
  // a rebuild would put it in, and the frame loop draws nothing until there is
  // another one. The trash is emptied here rather than after the next render,
  // because a disposed experience has no next render to wait for.
  dispose(){if(!scene)return;trash.push(scene);scene=null;island=null;emptyTrash()},
  // The island's frame is still the frame loop's (src/game/31-animate.js), so
  // this is the part of it that belongs to the view and can be advanced on its
  // own: the camera rig, the name plates and the minimap. Each honours
  // reducedMotion() itself, which is what makes a cut a cut.
  tick(dt,t){if(!scene||!chars.lotte)return;
    const pos=chars.lotte.g.position;
    tickCamera(dt,t,pos,chars.lotte.vel||ZERO);tickPlates(pos,dt);tickMinimap(dt)},
  // Bring the player to a stop. Another island is a fast travel first, the
  // same one the World button does, and the walk is asked for again once it
  // lands: the rebuild owns the walker's position, so nothing is held across
  // it. On this island it is the walk-to the ground tap uses, and the lesson
  // opens the way every other way in opens it.
  goTo(to){to=to||{};
    const here=S.world||"campus";
    if(to.island&&to.island!==here){if(!WORLDS[to.island])return false;setWorld(to.island);return true}
    const n=Number(to.stop);if(!started||!n||!PLOT_POS[n-1])return false;
    target.copy(PLOT_POS[n-1]);target.y=0;hasTarget=true;
    marker.position.set(target.x,.06,target.z);marker.material.opacity=1;
    openCh(n);return true},
  // What the player is standing at, for the sheet and for the list twin. The
  // proximity check writes nearK once a frame and is the one place that
  // decides what is near enough; this reads it and never asks again.
  where(){if(!started)return null;
    const k=nearK,at=S.world||"campus";
    if(typeof k==="number"&&k>0)return {kind:"stop",stop:k,island:at};
    if(typeof k==="string"&&k.indexOf("m:")===0)return {kind:"mentor",id:k.slice(2),island:at};
    if(typeof k==="string"&&k.indexOf("a:")===0)return {kind:"artifact",id:k.slice(2),island:at};
    return null},
  // Every stop of the archipelago as plain data, in campaign order. A canvas
  // is one opaque image to a screen reader, so this is what the accessible
  // twin is built from, and it is derived from S like everything else.
  listing(){const here=S.world||"campus",out=[];
    WORLD_IDS.forEach(id=>{const ws=CAMPAIGN[id].ws,done=S.doneW[id]||[],next=firstUndone(done,ws.length);
      ws.forEach((w,i)=>{const n=i+1;
        out.push({id:id+":"+n,stop:n,island:id,here:id===here,title:w.h+", "+w.n,
          state:done.indexOf(n)>=0?"done":n===next?"next":"ahead"})})});
    return out},
};

// Which view the game is in. The preference is S.settings.experience and the
// islands are the default; a URL parameter wins, so a test can ask for a view
// without writing a record. Nothing here writes: choosing is the settings'
// business, and an id this build does not have falls back rather than failing.
function experienceId(){let want="";
  try{want=new URLSearchParams(location.search).get("experience")||""}catch(e){}
  if(!want)want=(S.settings&&S.settings.experience)||"";
  return EXPERIENCES[want]?want:EXPERIENCE_DEFAULT}
function activeExperience(){return EXPERIENCES[experienceId()]}
// Test seam: the registry and the view in force, so the contract can be driven
// from a test the way window.__S and window.__debug are driven.
window.__experiences=()=>EXPERIENCES;
window.__experience=()=>activeExperience();
window.__experienceId=()=>experienceId();
