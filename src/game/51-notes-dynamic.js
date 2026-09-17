Object.keys(CAMPAIGN).forEach(k=>{const ev=CAMPAIGN[k];if(k==="campus")return;const title=ev.title.split(": ")[0];
  NOTES[title]={t:"ws",md:`# ${ev.title}\n${ev.blurb}\n`+ev.ws.map(w=>`- ${w.h} [[${w.n}]]: ${w.d}`).join("\n")+`\nMentors on this island: `+MENTORS.filter(m=>m.world===k).map(m=>`[[${m.name}]]`).join(", ")+`\nPart of [[Tonight]] · [[The campaign]]\n#overview`};
  ev.ws.forEach(w=>{const tmp=document.createElement("div");tmp.innerHTML=w.html;const links=[...tmp.querySelectorAll("a")].map(a=>`- [${a.textContent}](${a.href})`).join("\n");const steps=[...tmp.querySelectorAll("li")].map(l=>"- "+l.textContent).join("\n");const ps=[...tmp.querySelectorAll(":scope > p")].map(p=>p.textContent).join("\n\n");
    NOTES[w.n]={t:"ws",md:`# ${w.n}\n${w.h}, ${title}. ${w.d}\n\n${ps}\n\n**Do this**\n${steps}\n\n**Sources**\n${links}\n\nBack to [[${title}]]\n#workstream`}})});
NOTES["The campaign"]={t:"ws",md:`# The campaign\nFour islands, four evenings. Split them over as many nights as you like; the game and the CLI keep the state.\n- [[Tonight]] (Evening 1): ship first, then discipline\n- [[Evening 2]]: history, and how the models work\n- [[Evening 3]]: from vibes to determinism\n- [[Evening 4]]: terminal, git and the toolbelt\nMentors: [[Your path]]\n#overview`};
function pathMd(){return `# Your path\nThe people you met, and what you chose. Change it any time on the island.\n`+MENTORS.map(m=>`- [[${m.name}]] (${WORLDS[m.world].name}): ${S.path[m.id]==="deep"?"on your path":S.path[m.id]==="skip"?"skipped for now":"not met yet"}`).join("\n")+`\n#people`}
function encounterMd(m){const ex=m.encounter.exercise;
  return `\n\n**The encounter**\n`+m.encounter.dialogue.map(d=>`- ${d.you}\n- ${m.name}: ${d.m} [${m.src[d.src][0]}](${m.src[d.src][1]})`).join("\n")
   +`\n\n**Your exercise: ${ex.title}**\nAbout ${ex.minutes} minutes, in \`${ex.dir}/\`. Status: ${S.mentors.includes(m.id)?"done":"not yet"}.\n`
   +ex.steps.map((s,i)=>`${i+1}. ${s}`).join("\n")
   +`\nChecked by \`vibe check --mentor ${m.id}\`: ${ex.done}.\nThe plaque reads: ${m.encounter.plaque}.`}
function mentorMd(m){return `# ${m.name}\n*${m.role}*\n\n${m.bio}\n\n**What they would tell you**\n`+m.ideas.map(i=>"- "+i).join("\n")+encounterMd(m)+(S.path[m.id]==="deep"?`\n\n**Going deeper**\n${m.deep}`:"")+`\n\n**Sources**\n`+m.src.map(([t,u])=>`- [${t}](${u})`).join("\n")+`\n\nMet on [[${m.world==="campus"?"Tonight":CAMPAIGN[m.world].title.split(": ")[0]}]] · [[Your path]]\n#people`}
NOTES["Your path"]={t:"p",md:pathMd()};
NOTES["Artifacts"]={t:"c",md:artifactsMd()};
MENTORS.forEach(m=>{NOTES[m.name]={t:"p",md:mentorMd(m)}});
