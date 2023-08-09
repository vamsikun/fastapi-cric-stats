SELECT *, ROW_NUMBER() OVER (ORDER BY runs DESC NULLS LAST) as row
FROM batter_stats_each_match;