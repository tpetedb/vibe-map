/* ---------------- Galaxy model ---------------- */
// Pure view data. PLACES and TREE are injected package data; callers provide
// the completed topic ids so tests and the accessible twin need no DOM or 3D.
function galaxyModel(data=PLACES,tree=TREE,done=[]){
  const placeById=Object.fromEntries(data.places.map(place=>[place.id,place]));
  const completed=new Set(done),topics=[];
  Object.entries(tree).forEach(([shelf,items])=>items.forEach(topic=>{
    const origins=data.origins[topic.id]||[];
    const primary=origins.find(origin=>origin.primary);
    if(!primary)return;
    const place=placeById[primary.place];
    if(!place)throw new Error("Galaxy topic "+topic.id+" names unknown place "+primary.place);
    topics.push({id:topic.id,name:topic.n,depth:topic.d,shelf,place:place.id,
      year:primary.year,what:primary.what,source:primary.source,
      state:completed.has(topic.id)?"done":"ahead"})
  }));
  const next=topics.find(topic=>topic.state!=="done");if(next)next.state="next";
  const topicByPlace=new Map();
  topics.forEach(topic=>{
    if(!topicByPlace.has(topic.place))topicByPlace.set(topic.place,[]);
    topicByPlace.get(topic.place).push(topic)
  });
  const places=data.places.filter(place=>topicByPlace.has(place.id)).map(place=>{
    const at=topicByPlace.get(place.id),doneCount=at.filter(topic=>topic.state==="done").length;
    return Object.assign({},place,{topics:at,count:at.length,done:doneCount,
      state:at.some(topic=>topic.state==="next")?"next":doneCount===at.length?"done":"ahead"})
  });
  return {eras:data.eras.map(era=>Object.assign({},era)),places,topics,next:next||null}
}
