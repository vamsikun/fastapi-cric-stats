from pydantic import BaseModel
from sqlalchemy import Integer, String, case, func, select

from database import ormMetaData

# NOTE: for high score, a extra number is being concatenated to the original high score
# which reflects whether the player is out or not-out 0 means out and 1 means not-out


batStats = ormMetaData.tables["batter_stats_each_match"]
teamsTable = ormMetaData.tables["teams"]

playerExpr = batStats.c.player
inningsExpr = func.sum(batStats.c.played_in_match).label("innings")
runsExpr = func.sum(batStats.c.runs).label("runs")
individualHsExpr = func.max(
    func.cast(
        func.cast(func.coalesce(batStats.c.runs, 0), String)
        + case((batStats.c.player_out == 1, "0"), else_="1"),
        Integer,
    )
).label("hs")
srExpr = func.round(
    func.sum(batStats.c.runs) / func.nullif(func.sum(batStats.c.balls_faced), 0), 2
).label("sr")
avgExpr = func.round(
    func.sum(batStats.c.runs) / func.nullif(func.sum(batStats.c.player_out), 0), 2
).label("avg")
foursExpr = func.sum(batStats.c.fours).label("fours")
sixesExpr = func.sum(batStats.c.sixes).label("sixes")

selectStmt = select(
    playerExpr,
    func.count().label("matches"),
    inningsExpr,
    runsExpr,
    individualHsExpr,
    srExpr,
    avgExpr,
    foursExpr,
    sixesExpr,
)
