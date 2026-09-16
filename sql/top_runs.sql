-- Which were the five best runs tonight, and who played them?
select played_at, player, score
from 'data/scores.csv'
order by score desc
limit 5;
