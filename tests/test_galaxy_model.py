"""Pure contract tests for the Galaxy model and procedural planet kit."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _node(script: str) -> None:
    node = shutil.which("node")
    if not node:
        pytest.skip("node is needed for the pure JavaScript contract")
    subprocess.run([node, "-e", script], cwd=ROOT, check=True)


def test_galaxy_model_derives_stable_progress_without_mutating_data() -> None:
    _node(
        """
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const context=vm.createContext({});
vm.runInContext(fs.readFileSync('src/galaxy/00-model.js','utf8')+';globalThis.make=galaxyModel',context);
const data={eras:[{id:'mainframe',name:'Mainframes'}],places:[
  {id:'mit',name:'MIT',globe:'earth',look:'campus'},
  {id:'cloud',name:'The cloud',globe:'cloud',look:'station'}],origins:{
  unix:[{place:'mit',year:1969,what:'Unix begins',source:'https://example.test/unix',primary:true}],
  cloud:[{place:'cloud',year:2006,what:'Cloud launches',source:'https://example.test/cloud',primary:true}]}};
const tree={shell:[{id:'unix',n:'Unix',d:1}],
  ship:[{id:'cloud',n:'Cloud',d:2},{id:'later',n:'Later',d:3}]};
const before=JSON.stringify({data,tree}),model=context.make(data,tree,['unix']);
assert.equal(JSON.stringify({data,tree}),before);
assert.deepEqual(Array.from(model.topics,t=>t.state),['done','next']);
assert.equal(model.next.id,'cloud');
assert.equal(model.places[0].done,1);assert.equal(model.places[0].state,'done');
assert.equal(model.places[1].count,1);assert.equal(model.places[1].state,'next');
assert.equal(model.topics[1].source,'https://example.test/cloud');
const bad={...data,origins:{unix:[{place:'missing',primary:true}]}};
assert.throws(()=>context.make(bad,tree,[]),/unknown place/);
"""
    )


def test_galaxy_visuals_keep_true_pins_and_independent_resources() -> None:
    _node(
        """
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const T=require('./src/vendor/three.min.js'),context=vm.createContext({THREE:T});
vm.runInContext(fs.readFileSync('src/config/00-config.js','utf8')+
  fs.readFileSync('src/galaxy/10-planet-kit.js','utf8')+
  ';globalThis.palette=PALETTE;globalThis.factory=createGalaxyVisuals',context);
const V=context.factory({three:T,palette:context.palette,
  material:(color,opts={})=>new T.MeshStandardMaterial({color,...opts}),finish:()=>{}});
const close=(a,b)=>assert.ok(a.distanceTo(b)<1e-9);
close(V.surface(0,0),new T.Vector3(1,0,0));close(V.surface(90,0),new T.Vector3(0,1,0));
const places=[{id:'a',globe:'earth',look:'campus',lat:37.4,lon:-122.15},
  {id:'b',globe:'earth',look:'lab',lat:37.41,lon:-122.14}];
const before=JSON.stringify(places);
const planet=V.makePlanet(places,{states:{a:'next',b:'done'}});
assert.equal(JSON.stringify(places),before);
planet.sites.forEach((site,i)=>{close(site.pin,V.surface(places[i].lat,places[i].lon,1.012));
  assert.ok(site.displayNormal.angleTo(site.normal)>.1)});
assert.throws(()=>V.makeDome({id:'bad',look:'logo'}),/Unsupported Galaxy look/);
V.makeDome({id:'hall',look:'hall'});V.makeDome({id:'lanes',look:'lanes'});
assert.throws(()=>V.makePlanet([{id:'bad',globe:'earth',look:'campus'}]),/coordinates/);
const mixed=[places[0],{id:'dc',globe:'datacentre',look:'racks'}];
assert.throws(()=>V.makePlanet(mixed),/globe kinds/);
const roots=[planet.root,V.makeDome({id:'racks',look:'racks'},'next'),
  V.makePlanet([{id:'dc',globe:'datacentre',look:'racks'}]).root];
const resources=new Set();roots.forEach(root=>root.traverse(object=>{
  if(object.geometry){
    for(const value of object.geometry.attributes.position.array)
      assert.ok(Number.isFinite(value));
    assert.ok(!resources.has(object.geometry));resources.add(object.geometry)}
  if(object.material){assert.ok(!resources.has(object.material));resources.add(object.material)}}));
resources.forEach(resource=>resource.dispose());
const looks=['campus','lab','tower','racks','station','house','harbour','hall','lanes'];
const dense=Array.from({length:20},(_,i)=>({id:'p'+i,globe:'earth',
  look:looks[i%looks.length],lat:37.4,lon:-122.15}));
const crowded=V.makePlanet(dense),radius=Math.asin((.62/Math.sqrt(20))/1.025);
for(let i=0;i<crowded.sites.length;i++)for(let j=0;j<i;j++)
  assert.ok(crowded.sites[i].displayNormal.angleTo(crowded.sites[j].displayNormal)>radius*2);
let draws=0;crowded.root.traverse(object=>{if(object.material)draws++});
assert.ok(draws<300,'dense planet drawables: '+draws);
"""
    )
