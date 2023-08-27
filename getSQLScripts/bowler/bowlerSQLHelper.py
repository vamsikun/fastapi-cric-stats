from pydantic import BaseModel
from sqlalchemy import Numeric, String, cast, func, select

from database import ormMetaData

# NOTE: minimum qualification for stats such as average, strikerate
# to get team details
bowlerStatsTable = ormMetaData.tables["bowler_stats_each_match"]

inningsExpr = func.sum(bowlerStatsTable.c.bowled_in_match).label("innings")
wicketsExpr = func.sum(bowlerStatsTable.c.wickets).label("wickets")
dotsPercentageExpr = func.round(
    (
        func.sum(bowlerStatsTable.c.dot_balls)
        / func.sum(bowlerStatsTable.c.legal_deliveries)
    )
    * 100,
    2,
).label("dots_percentage")
ballsExpr = func.sum(bowlerStatsTable.c.legal_deliveries).label("balls")

oversExpr = cast(
    cast(func.sum(bowlerStatsTable.c.legal_deliveries) / 6, String)
    + "."
    + cast(func.sum(bowlerStatsTable.c.legal_deliveries) % 6, String),
    Numeric,
).label("overs")
econExpr = func.round(
    func.sum(bowlerStatsTable.c.runs_conceded)
    * 6
    / func.sum(bowlerStatsTable.c.legal_deliveries),
    2,
).label("econ")
srExpr = func.round(
    func.sum(bowlerStatsTable.c.legal_deliveries)
    / func.sum(bowlerStatsTable.c.wickets),
    2,
).label("sr")
avgExpr = func.round(
    func.sum(bowlerStatsTable.c.runs_conceded) / func.sum(bowlerStatsTable.c.wickets), 2
).label("avg")
runsExpr = func.sum(bowlerStatsTable.c.runs_conceded).label("runs")

selectStmt = select(
    bowlerStatsTable.c.player,
    func.count().label("matches"),
    inningsExpr,
    wicketsExpr,
    dotsPercentageExpr,
    oversExpr,
    econExpr,
    srExpr,
    avgExpr,
    runsExpr,
)
