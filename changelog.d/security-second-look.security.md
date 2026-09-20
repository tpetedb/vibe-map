- A pasted progress code can no longer put markup on the page. Shelf ids and
  mentor choices in a code went raw into the Roadmap, Settings and the title
  screen, so a code from a stranger ran script on import and again on every
  load. The game now checks every id in a code before it merges anything and
  refuses a code that fails, naming the field; the panels escape those values
  on their own as well, along with the dashboard feed and the setup commands.
- The build writes data into the game through one helper, `js_json()`, so a
  value in `config/camp.toml` that contains a closing script tag is a string
  again instead of running, and a feed headline containing a comment opener
  can no longer leave the built game dead. `tools/build.py` also refuses any
  script that could end its own element.
- `vibe news` leaves no angle bracket in a title, a name or a summary (a tag
  the feed never closed used to survive), requires a host in a link and
  encodes the characters that would end a Markdown link or an attribute.
- Notes reach the game character for character: a backslash or `${` in a
  topic is text. Two CSV notes were showing `\n` as a line break and had lost
  the backslashes of a quoted command.
- The chat bridge refuses a `Content-Length` that is not a plain number (a
  negative one held a thread until the peer hung up) and marks its JSON
  answers `nosniff`.
- New: `docs/SECURITY-MODEL.md`, ADR 0014 on why the game ships no
  Content-Security-Policy yet, and `just sinks-check`, which fails when a new
  value reaches HTML without `esc()` (`tools/reviewed_sinks.json` is the
  register of the ones that were looked at).
