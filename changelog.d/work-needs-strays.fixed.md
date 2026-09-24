- `work.py check` and `work.py ci` no longer count as strays the files an order
  carries unchanged from the branch of an order it lists in `needs`, which it
  builds on before that one lands. A file of the needed order changed on top,
  or a needed branch that cannot be found, is still a stray.
