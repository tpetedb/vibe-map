- `work.py validate` no longer calls two active orders a collision when they
  share a file and one lists the other in `needs`: they run one after the
  other, as `work.py plan` already puts them. An overlap nobody declared is
  still a collision.
