-- Longest streak of improving scores per player.
-- New construct: lag() looks at the previous row inside a window.
with ordered as (
  select player, played_at, score,
         lag(score) over (partition by player order by played_at) as prev
  from 'workspace/data/scores.csv'
),
flags as (
  select *, case when prev is null or score > prev then 0 else 1 end as brk
  from ordered
),
groups as (
  select *, sum(brk) over (partition by player order by played_at) as grp
  from flags
)
select player, count(*) as streak_len, min(played_at) as started
from groups
group by player, grp
order by streak_len desc
limit 3;
