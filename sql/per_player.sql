-- How did each player do: runs, best, average?
-- New construct: group by folds many rows into one per player.
select player,
       count(*)        as runs,
       max(score)      as best,
       round(avg(score), 1) as mean
from 'data/scores.csv'
group by player
order by best desc;
