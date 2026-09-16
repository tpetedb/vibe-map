# Obsidian, feature by feature

Every feature the official help documents, in one table, with the exact commands and a five-minute try. `uv run vibe vault feature <id>` writes the matching note (and, for canvases, bases, templates, slides and snippets, a working example file) into the vault; `--all` writes them all. Source: [Obsidian Help](https://help.obsidian.md/).

| id | Feature | Kind | What | Try |
|---|---|---|---|---|
| `links` | [Internal links](https://help.obsidian.md/Linking+notes+and+files/Internal+links) | linking | Internal links point from one note to another note, attachment or file in the vault, in Wikilink or Markdown format. You can also link to a heading or a block inside a note and change the display text. Obsidian updates links when you rename a file. | Create a note, type [[ and pick another note to link it, then add ^my-block at the end of a paragraph and link to it from a third note with [[Note#^my-block]]. Rename the first note and check that the links updated. |
| `backlinks` | [Backlinks](https://help.obsidian.md/Plugins/Backlinks) | core plugin | The Backlinks core plugin lists every note that links to the active note, split into Linked mentions and Unlinked mentions, in a sidebar tab or at the bottom of the note itself. | Open a note that other notes link to, click the Backlinks tab in the right sidebar and read Linked mentions, then expand Unlinked mentions and find a plain-text mention of the note's name that you can turn into a link. |
| `graph-view` | [Graph view](https://help.obsidian.md/Plugins/Graph+view) | core plugin | Graph view draws the notes in a vault as circles and the internal links between them as lines, so you can see how notes relate. A local graph shows only the notes connected to the active note. | Open graph view from the ribbon, click New group under Groups, enter a search term for a set of notes (for example a tag) and pick a colour, then switch Orphans off and see which notes disappear. |
| `tags` | [Tags](https://help.obsidian.md/Editing+and+formatting/Tags) | editing | Tags are keywords or topics that help you find notes quickly. You write them inline with a hash sign or in the tags property, nest them with slashes, and find them with the tag search operator or the Tags view. | Add #inbox/to-read to one note and #inbox/processing to another, then open Search and enter tag:inbox to confirm both notes appear; run Tags: Show tags to see them nested under inbox. |
| `properties` | [Properties](https://help.obsidian.md/Editing+and+formatting/Properties) | editing | Properties store structured data about a note, such as text, links, dates, checkboxes and numbers, as YAML at the top of the file. Each property name has one type across the vault, and Obsidian ships default properties like tags, aliases and cssclasses. | Open a note, press Cmd/Ctrl+; and add a property named status with the value draft, then add a date property and a checkbox property; switch Settings > Editor > Properties in document to Source to see the YAML that was written. |
| `callouts` | [Callouts](https://help.obsidian.md/Editing+and+formatting/Callouts) | editing | Callouts are blockquotes with a type identifier on the first line that render as coloured boxes with an icon, for extra content that does not break the flow of a note. They take custom titles, fold, nest, and can be styled with CSS. | In a note, run Insert callout from the Command palette, change it to [!tip] with a custom title, make it foldable by adding - after the identifier, then nest a [!example] callout inside it. |
| `embeds` | [Embed files](https://help.obsidian.md/Linking+notes+and+files/Embed+files) | linking | Embedding shows a file's content inline in a note and keeps it up to date with the source. An exclamation mark before an internal link embeds notes, headings, blocks, images, audio, PDFs, canvases, lists and search results. | Add ^my-list-id on its own line after a bullet list in one note, then in another note write ![[My note#^my-list-id]] and watch the list appear; edit the source list and confirm the embed updates. |
| `templates` | [Templates](https://help.obsidian.md/Plugins/Templates) | core plugin | Templates is a core plugin that inserts pre-defined text from a template folder into the active note at the cursor, replacing variables such as the title, date and time. | Create a folder named Templates and set it as the Template folder location, add a note there with # {{title}} and a line Created {{date:YYYY-MM-DD}} {{time}}, then open a new note and run Templates: Insert template. |
| `daily-notes` | [Daily notes](https://help.obsidian.md/Plugins/Daily+notes) | core plugin | Daily notes is a core plugin that opens today's note or creates it if it does not exist, for journals, to-do lists or daily logs. It can use a template and a custom folder, and date properties become links to daily notes. | Create a note called Daily template with the heading # {{date:YYYY-MM-DD}} and a Tasks list, set it as Template file location under Daily notes, then run Open today's daily note and add a task. |
| `unique-note` | [Unique note creator](https://help.obsidian.md/Plugins/Unique+note+creator) | core plugin | Unique note creator is a core plugin that creates notes with time-based names, also known as Zettelkasten notes, optionally filled from a template. | Enable Unique note creator, press Ctrl/Cmd+P and run Create new unique note twice, compare the two timestamp names, then point Template file location at one of your templates and create a third. |
| `bookmarks` | [Bookmarks](https://help.obsidian.md/Plugins/Bookmarks) | core plugin | Bookmarks is a core plugin for shortcuts to items you use often: files, folders, graphs, searches, headings, blocks and links, organised into bookmark groups in a sidebar tab. | Open the Bookmarks tab, create a group called Tonight with New bookmark group, bookmark the active note with Bookmark the active tab, then run a search and bookmark it from the three dots menu; drag both into the group. |
| `search` | [Search](https://help.obsidian.md/Plugins/Search) | core plugin | Search is a core plugin that finds text across the vault using search terms, operators, property queries and regular expressions. Results can be sorted, copied, and embedded in a note with a query code block. | Press Ctrl/Cmd+Shift+F, search meeting -work and click Explain search term to read the breakdown, then try task-todo:call, and paste a query code block with one of the terms into a note to embed the results. |
| `quick-switcher` | [Quick switcher](https://help.obsidian.md/Plugins/Quick+switcher) | core plugin | Quick switcher is a core plugin for finding and opening notes by name or alias from the keyboard, and for creating a note when nothing matches. | Press Ctrl/Cmd+O, type part of a note name and open it with Enter; press Ctrl/Cmd+O again, press Down and Enter to jump back; then type a new name and press Shift+Enter to create that note. |
| `command-palette` | [Command palette](https://help.obsidian.md/Plugins/Command+palette) | core plugin | The Command palette core plugin runs any Obsidian command from the keyboard with fuzzy matching, shows each command's hotkey, and lets you pin frequently used commands to the top. | Press Ctrl/Cmd+P, type scf and run Save current file, then open Settings > Command palette and pin Open today's daily note as a New pinned command; open the palette again and see it at the top. |
| `hotkeys` | [Hotkeys](https://help.obsidian.md/User+interface/Hotkeys) | editing | Hotkeys are customisable keyboard shortcuts for Obsidian commands, managed under Settings > Hotkeys, where you add, remove and filter shortcuts and can give one command several combinations. | Open Settings > Hotkeys, search for Templates: Insert template, press + and assign a combination, select Save, then use the filter icon to list only commands with hotkeys and try the new shortcut in a note. |
| `slash-commands` | [Slash commands](https://help.obsidian.md/Plugins/Slash+commands) | core plugin | Slash commands is a core plugin that runs commands from inside the editor: type a forward slash at the start of a line or after a space, search the list of commands, and press Enter. | Enable Slash commands, then in a note type / on a new line, type scf and press Enter to run Save current file; type / again and press Esc to leave the menu without running anything. |
| `workspaces` | [Workspaces](https://help.obsidian.md/Plugins/Workspaces) | core plugin | Workspaces is a core plugin that saves and restores application layouts, including open files and tabs and the width and visibility of each sidebar, so you can switch between setups for journaling, reading or writing. | Arrange two notes side by side with the right sidebar closed, run Manage workspace layouts and save it as Writing; then open the graph and both sidebars, save that as Review, and switch between the two with Load. |
| `outline` | [Outline](https://help.obsidian.md/Plugins/Outline) | core plugin | Outline is a core plugin that lists the headings of the active note; click a heading to jump to that section or drag headings to rearrange sections. | Open a note with at least three headings, open the Outline tab, click a heading to jump to it, then drag the last heading above the first and check that the note's sections moved. |
| `note-composer` | [Note composer](https://help.obsidian.md/Plugins/Note+composer) | core plugin | Note composer is a core plugin that merges two notes or extracts a selection into another or a new note, updating links as it goes, with an optional template for the new content. | Select a paragraph in a note, right-click and choose Extract current selection..., type a new note name and press Ctrl/Cmd+Enter; check that the paragraph moved and a link to the new note was left behind. |
| `slides` | [Slides](https://help.obsidian.md/Plugins/Slides) | core plugin | Slides is a core plugin that turns any Markdown note into a presentation, with slides separated by a horizontal rule line. | Write a note with a title, a --- line, and two more sections each separated by ---, then run Start presentation from the Command palette and step through with the arrow keys; press Escape to leave. |
| `canvas` | [Canvas](https://help.obsidian.md/Plugins/Canvas) | core plugin | Canvas is a core plugin for visual note-taking: an infinite 2D space where you place text cards, notes, media, folders and web pages, connect them with labelled lines and group them. Canvases are .canvas files in the open JSON Canvas format. | Create a canvas from the ribbon, double-click to add a text card, drag two notes in from the File explorer, connect them with a labelled line, group all three with Create group and press Shift+1 to zoom to fit. |
| `bases` | [Introduction to Bases](https://help.obsidian.md/Bases/Introduction+to+Bases) | core plugin | Bases is a core plugin that builds database-like views (table, list, cards, kanban, map) over the notes in a vault, reading data from their properties. A base is a YAML .base file with filters, formulas and views, and can be embedded in a note. | Create a base, open the Filter menu and add the condition file.hasTag("book") in the advanced filter editor, show file.name and file.mtime as properties in the table view, then add a Cards view with Bases: Add view and embed it in a note with ![[Books.base#Cards]]. |
| `web-viewer` | [Web viewer](https://help.obsidian.md/Plugins/Web+viewer) | core plugin | Web viewer is a desktop core plugin that opens external links in Obsidian tabs, with a reader view, a save-to-vault action and ad blocking, for research without leaving the app. | Enable Web viewer, click an external link in a note so it opens in a tab, switch to Reader view with the glasses icon, then use the more actions icon to save the page to your vault and open the resulting note. |
| `obsidian-uri` | [Obsidian URI](https://help.obsidian.md/Extending+Obsidian/Obsidian+URI) | extending | Obsidian URI is a custom obsidian:// protocol that triggers actions from outside the app, such as opening or creating a note, opening the daily note, a unique note, a search or the vault manager, for automation and cross-app workflows. | Find your vault name, then paste obsidian://new?vault=YOUR%20VAULT&name=URI%20test&content=Hello%20World into your browser's address bar (encode spaces as %20) and confirm Obsidian opens a new note called URI test. |
| `obsidian-cli` | [Obsidian CLI](https://help.obsidian.md/Extending+Obsidian/Obsidian+CLI) | extending | Obsidian CLI controls a running Obsidian app from the terminal, for scripting, automation and agent tooling. It offers single commands and a TUI, covering files, daily notes, search, tasks, properties, plugins, bases, sync, publish and developer commands. | Turn on Command line interface under Settings > General, restart your terminal, then run obsidian tags counts, obsidian daily:append content="- [ ] Try the CLI" and obsidian tasks daily to see the new task listed. |
| `community-plugins` | [Community plugins](https://help.obsidian.md/Extending+Obsidian/Community+plugins) | extending | Community plugins extend Obsidian with third-party code, installed from a built-in directory after turning off Restricted Mode. They are enabled, updated and uninstalled from Settings > Community plugins. | Open Settings, select Turn on community plugins, click Browse and filter for a plugin you want, Install and Enable it, then open Installed plugins and try its Settings and Hotkeys icons; finish with Check for updates. |
| `css-snippets` | [CSS snippets](https://help.obsidian.md/Extending+Obsidian/CSS+snippets) | extending | CSS snippets are small CSS files in the vault's configuration folder that change parts of the Obsidian interface without building a full theme, using Obsidian's CSS variables and the cssclasses property for per-note styling. | Open Settings > Appearance > CSS snippets > Open snippets folder, save a headers.css that sets --h1-color: red on body, click Reload snippets and enable it; then give one note a cssclasses property with the value red-border and style .red-border img in the same file. |
| `sync` | [Introduction to Obsidian Sync](https://help.obsidian.md/Obsidian+Sync/Introduction+to+Obsidian+Sync) | service | Obsidian Sync is a paid add-on service that privately syncs a vault across devices, with selective sync, version history, shared vaults, regional servers and a headless mode. | Read the Set up Obsidian Sync page linked from the intro, then check whether another sync tool (Dropbox, Google Drive, OneDrive) already watches your vault folder and make a backup before enabling Sync. |
| `publish` | [Introduction to Obsidian Publish](https://help.obsidian.md/Obsidian+Publish/Introduction+to+Obsidian+Publish) | service | Obsidian Publish is a cloud hosting service that turns selected notes into a public wiki, knowledge base, documentation site or digital garden, hosted at publish.obsidian.md/your-site. | Open the Publish intro and follow the Set up Obsidian Publish link, then pick three notes you would select to share and check each for links to notes you would not publish. |
| `web-clipper` | [Introduction to Obsidian Web Clipper](https://help.obsidian.md/Obsidian+Web+Clipper/Introduction+to+Obsidian+Web+Clipper) | extending | Obsidian Web Clipper is a free, open source browser extension that highlights web pages and saves their content to a vault, with templates, variables, filters, logic and an interpreter for natural language prompts. | Install Web Clipper from your browser's extension store, open an article, highlight one passage with the Highlighter and clip the page into your vault; then open the new note and check the saved content. |
| `ofm` | [Obsidian Flavored Markdown](https://help.obsidian.md/Editing+and+formatting/Obsidian+Flavored+Markdown) | format | Obsidian Flavored Markdown combines CommonMark, GitHub Flavored Markdown and LaTeX with Obsidian's own extensions: wikilinks, embeds, block references, footnotes, comments, highlights, callouts and task lists. Markdown is not rendered inside HTML elements. | In one note write a line with ==highlight==, a %%hidden comment%%, a - [ ] task and a > [!note] callout, switch to Reading view to see which render, then wrap **bold** in a <div> and confirm it stays plain. |
| `file-recovery` | [File recovery](https://help.obsidian.md/Plugins/File+recovery) | core plugin | File recovery is a core plugin that saves complete snapshots of notes at regular intervals so you can restore or copy an earlier version after an accidental deletion or unwanted change. It is not a full backup solution. | Edit a note, wait a few minutes, edit it again, then open Settings > File recovery > Snapshots > View, type the note name, toggle Show changes to compare the two snapshots and use Copy to paste the older text into a new note. |
| `page-preview` | [Page preview](https://help.obsidian.md/Plugins/Page+preview) | core plugin | Page preview is a core plugin that shows a popup preview of a note when you hover over an internal link, without navigating to it. | Open a note with an internal link, hover the link while holding Ctrl (Cmd on macOS) to see the preview popup, then hover a result in Search without the key and compare. |
| `random-note` | [Random note](https://help.obsidian.md/Plugins/Random+note) | core plugin | Random note is a core plugin that opens a random note from the vault, to rediscover old notes and link to recently added ones. | Click Open random note in the ribbon five times; for each note that appears, add one [[wikilink]] to a related note or a tag before moving on. |
| `footnotes` | [Footnotes view](https://help.obsidian.md/Plugins/Footnotes+view) | core plugin | Footnotes view is a core plugin that lists all footnotes in the active note, lets you edit a footnote's text and jump to its position in the note. | Add two footnotes to a note, open the Footnotes view tab, click one footnote to edit its text, then use it to jump to where that footnote sits in the note. |

## Syntax cheatsheet

### Internal links

```
[[Three laws of motion]]
[[Projects/Three laws of motion]]
[[About Obsidian#Links are first-class citizens]]
[[2023-01-01#^quote-of-the-day]]
[[Example|Custom name]]
```

### Tags

```
---
tags:
  - recipe
  - cooking
---
```

### Properties

```
---
title: A New Hope
link: "[[Episode IV]]"
url: https://www.example.com
---
```

### Callouts

```
> [!info] Here's a callout title
> Here's a callout block.
> It supports **Markdown**, [[Internal link|Wikilinks]], and [[Embed files|embeds]]!
> ![[Engelbart.jpg]]
```

### Embed files

```
![[Internal links]]
![[Internal links#^b15695]]
![[Engelbart.jpg|100x145]]
![[Document.pdf#page=3]]
![[My canvas.canvas]]
```

### Templates

```
---
topic: 
date: "{{date}}"
course: 
tags:
  - studies
---

# {{title}}

## Key Concepts
```

### Daily notes

```
# {{date:YYYY-MM-DD}}

## Tasks

- [ ]
```

### Search

~~~
```query
embed OR search
```
~~~

### Slides

```
# Presentations using Slides

A demo on how to build presentations using Slides.

---

## Formatting

You can use regular Markdown formatting, like *emphasised* and **bold** text.
```

### Introduction to Bases

```yaml
filters:
  and:
    - file.hasTag("tag")
views:
  - type: table
    name: "My table"
    limit: 10
    order:
      - file.name
      - file.ext
```

### Obsidian URI

```
obsidian://action?param1=value&param2=value
obsidian://open?vault=my%20vault&file=my%20note
obsidian://new?vault=my%20vault&name=my%20note
obsidian://daily?vault=my%20vault
obsidian://search?vault=my%20vault&query=Obsidian
```

### Obsidian CLI

```
# Open today's daily note
obsidian daily

# Add a task to your daily note
obsidian daily:append content="- [ ] Buy groceries"

# Search your vault
obsidian search query="meeting notes"

# List all tags in your vault with counts
obsidian tags counts
```

### CSS snippets

```
body {
  --h1-color: red;
  --h2-color: orange;
  --h3-color: yellow;
  --h4-color: green;
  --h5-color: blue;
  --h6-color: pink;
}
```

### Obsidian Flavored Markdown

```
[[Link]]
![[Link]]
![[Link#^id]]
^id
[^id]
%%Text%%
~~Text~~
==Text==
- [ ]
- [x]
> [!note]
```
