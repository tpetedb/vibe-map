- `vibe new --name` writes your name through a real TOML serialiser and reads
  the file back, so a quote, a backslash, an accent or a newline no longer
  leaves a camp whose `config/camp.toml` refuses to parse.
- A very long `--name` is cut to a folder name the filesystem accepts instead
  of ending in an `OSError`.
- `vibe new --github` says the GitHub CLI is missing before it builds half a
  camp, instead of raising `FileNotFoundError`.
- `vibe name` refuses an empty name, prints a name that looks like markup
  without crashing, and says `config/camp.toml` the same way `vibe interests`
  does.
- A command that writes the configuration refuses when there is no camp at
  `VIBE_HOME`, instead of scattering a config, a state file and a vault at a
  typo.
- `vibe config --help` promises only what it has.
- The persona recipes name `workspace/data/examples/`, the folder
  `vibe persona` actually writes to.
- In a camp, `just done n "note" --force` forwards the flag its own error
  advises, and `just break` refuses to carry uncommitted work onto the play
  branch.
- The retired `vibe.toml` is gone from the theme file header, the `vibe start`
  welcome and `env.example`.
