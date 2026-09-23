/* ---------------- photo mode ---------------- */
// A clean picture of the island to keep or send. Photo mode hides everything
// laid over the scene except the zoom column, pulls the camera back one step,
// and takes the frame as a PNG with a caption band: saved through a download
// link everywhere, shared through the share sheet where the browser can share
// files (MDN, Web Share API: navigator.canShare({files}) first, and share()
// only inside a click of its own).
// The canvas has no preserveDrawingBuffer, which would cost every frame, so
// the frame is rendered and copied in one task: the drawing buffer holds it
// until the browser composites, and nothing else draws in between.
// Built with createElement and textContent: nothing here goes through HTML.
const PHOTO_HIDE=["#hud","#bottom","#talk","#joy","#jump","#toast","#minimap","#minimap-btn","#breakcard"];
let photo=null,photoShots=0;
function photoOn(){return !!photo}
function photoBtn(label,primary,fn){const b=document.createElement("button");b.type="button";b.textContent=label;
  if(primary)b.className="primary";b.style.minHeight="44px";b.addEventListener("click",fn);return b}
// Floating panels share one frame: centred, a 16 px gutter on a phone, clear
// of the home indicator.
function photoPanel(id,label){const el=document.createElement("div");el.id=id;el.className="card";
  el.setAttribute("role","dialog");el.setAttribute("aria-label",label);
  el.style.cssText="position:fixed;z-index:45;left:16px;right:16px;margin:0 auto;max-width:440px;"+
    "bottom:calc(16px + env(safe-area-inset-bottom,0px));box-shadow:var(--lift)";
  return el}
// Only between things: never over a panel, the title or a flight.
function photoCanOpen(){return typeof started!=="undefined"&&started&&!flight&&
  !document.querySelector("#sheet.on,#vault.on,#pal.on,#title:not(.off)")}
window.openPhoto=function(){if(photo||!photoCanOpen())return;
  if(typeof closeHudMenu==="function")closeHudMenu();
  if(typeof breakClose==="function")breakClose();
  const hidden=PHOTO_HIDE.map(s=>document.querySelector(s)).filter(Boolean).map(el=>[el,el.style.visibility]);
  hidden.forEach(([el])=>{el.style.visibility="hidden"});
  // One step further out than the player stands, not written to Settings:
  // leaving photo mode goes back to the level the player chose.
  zoomTo=Math.min(CAM.zoom.max,zoomTo+CAM.zoom.step);zoomHud();
  const bar=photoPanel("photobar","Photo mode");
  const hint=document.createElement("p");hint.className="small muted";hint.style.margin="0 0 8px";
  hint.textContent="Walk and zoom until the island looks right. P or Escape leaves.";
  const row=document.createElement("div");row.className="row";row.style.marginTop="0";
  row.append(photoBtn("Take photo",true,photoTake),photoBtn("Done",false,closePhoto));
  bar.append(hint,row);document.body.appendChild(bar);fx(bar);
  photo={hidden:hidden,bar:bar,view:null,url:""};
  bar.querySelector("button").focus()};
window.closePhoto=function(){if(!photo)return;photoDrop();photo.bar.remove();
  photo.hidden.forEach(([el,v])=>{el.style.visibility=v});
  photo=null;syncZoom();if(document.activeElement)document.activeElement.blur()};
function photoDrop(){if(photo.view){photo.view.remove();photo.view=null}
  if(photo.url){URL.revokeObjectURL(photo.url);photo.url=""}}
// The caption: who, where, how far, in the text colour of the palette on a
// band that fades up from the bottom, so the island stays the picture. Two
// lines on the left, sized from the short side, so a phone held upright has
// the same caption as a laptop and nothing is squeezed.
function photoCaption(g,w,h){const css=getComputedStyle(document.documentElement);
  const ink=css.getPropertyValue("--text").trim()||"white",mute=css.getPropertyValue("--muted").trim()||"gray";
  const fs=Math.max(14,Math.round(Math.min(w,h)*.034)),pad=Math.round(fs*1.1),band=fs*5;
  const grad=g.createLinearGradient(0,h-band,0,h);grad.addColorStop(0,"rgba(0,0,0,0)");grad.addColorStop(1,"rgba(0,0,0,.72)");
  g.fillStyle=grad;g.fillRect(0,h-band,w,band);
  const who=typeof playerLabel==="function"?playerLabel():S.name;
  const where=(who?who+" · ":"")+dashIsland(S.world||"campus")+" · "+S.done.length+" of "+stopCount()+" stops";
  const font=px=>"600 "+px+"px system-ui,-apple-system,sans-serif";
  g.textBaseline="alphabetic";g.textAlign="left";
  g.font=font(Math.round(fs*.75));g.fillStyle=mute;g.fillText("Vibe Code Camp",pad,h-pad-fs*1.35,w-2*pad);
  g.font=font(fs);g.fillStyle=ink;g.fillText(where,pad,h-pad,w-2*pad)}
function photoTake(){if(!photo)return;photoDrop();
  renderer.render(scene,camera);
  const src=renderer.domElement,w=src.width,h=src.height,c=document.createElement("canvas");c.width=w;c.height=h;
  const g=c.getContext("2d");g.drawImage(src,0,0);photoCaption(g,w,h);photoShots++;
  photoFlash();
  c.toBlob(blob=>{if(!photo||!blob){if(photo)toast("No photo","This browser would not hand over the picture. A screenshot works just as well.");return}
    photoShow(blob)},"image/png")}
// A short white flash says the picture was taken; under reduced motion the
// preview appearing says it instead.
function photoFlash(){if(reducedMotion())return;const f=document.createElement("div");f.id="photoflash";
  f.style.cssText="position:fixed;inset:0;z-index:46;background:var(--text);opacity:.55;pointer-events:none;transition:opacity .35s ease-out";
  document.body.appendChild(f);requestAnimationFrame(()=>{f.style.opacity="0"});setTimeout(()=>f.remove(),450)}
function photoName(){return "vibe-map-"+(S.world||"campus")+".png"}
function photoShow(blob){photo.url=URL.createObjectURL(blob);
  const file=new File([blob],photoName(),{type:"image/png"});
  const view=photoPanel("photoview","Your photo");
  const img=document.createElement("img");img.src=photo.url;img.alt="The island, as the photo shows it";
  img.style.cssText="display:block;width:100%;max-height:52vh;object-fit:contain;border-radius:12px;background:var(--bg);margin-bottom:10px";
  const row=document.createElement("div");row.className="row";row.style.marginTop="0";
  const share=!!(navigator.canShare&&navigator.share&&navigator.canShare({files:[file]}));
  if(share)row.appendChild(photoBtn("Share",true,()=>{navigator.share({files:[file],title:"Vibe Code Camp"}).catch(e=>{
      if(e&&e.name!=="AbortError")toast("Not shared","The share sheet said no. Save the image instead and send it from your photos.")})}));
  const save=document.createElement("a");save.href=photo.url;save.download=photoName();save.textContent="Save image";
  // A link dressed as a button; the first action of the row is the primary
  // one, so without a share sheet it is this one.
  save.style.cssText="display:inline-flex;align-items:center;min-height:44px;padding:0 18px;border-radius:12px;"+
    "text-decoration:none;font-weight:600;font-size:.875em;"+
    (share?"border:1px solid var(--line2);background:var(--panel2);color:var(--ink)":"border:1px solid transparent;background:var(--accent);color:#000");
  row.append(save,photoBtn("Take another",false,()=>{photoDrop();photo.bar.style.visibility="";photo.bar.querySelector("button").focus()}),photoBtn("Done",false,closePhoto));
  view.append(img,row);photo.bar.style.visibility="hidden";document.body.appendChild(view);photo.view=view;fx(view);
  row.firstChild.focus()}
// P opens and closes photo mode, Escape closes it; a key typed into a field
// belongs to the field.
addEventListener("keydown",e=>{if(e.metaKey||e.ctrlKey||e.altKey||inField(e.target))return;
  if((e.key==="p"||e.key==="P")&&(photo||photoCanOpen())){photo?closePhoto():openPhoto();e.preventDefault()}
  else if(e.key==="Escape"&&photo&&!e.defaultPrevented){closePhoto();e.preventDefault()}});
// The HUD entry lives with the other secondary buttons, so on a phone it is
// in the More menu and on a laptop in the pill.
(()=>{const sec=$("hud-sec");if(!sec)return;const b=document.createElement("button");b.id="hud-photo";b.type="button";
  b.textContent="Photo";b.title="Photo mode: the island without the HUD (P)";b.addEventListener("click",openPhoto);sec.appendChild(b)})();
// Test seam: whether photo mode is on, how many frames it took, and that the
// canvas still runs without a preserved buffer.
window.__photo=()=>({on:!!photo,shots:photoShots,
  preserve:!!(renderer&&renderer.getContext().getContextAttributes().preserveDrawingBuffer)});
