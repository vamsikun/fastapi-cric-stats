from getSQLScripts.batter.batterSQLHelper import batStats
from sqlalchemy import Integer, String, case, desc, func, nulls_last, select


def getSQLForBatterMostFours(season, limit=10):
    selectStmt = select(
        func.row_number()
        .over(order_by=nulls_last(desc(func.sum(batStats.c.fours))))
        .label("pos"),
        batStats.c.player,
        func.count().label("matches"),
        func.sum(batStats.c.played_in_match).label("innings"),
        func.sum(batStats.c.runs).label("runs"),
        func.max(
            func.cast(
                func.cast(func.coalesce(batStats.c.runs, 0), String)
                + case((batStats.c.player_out == 1, "0"), else_="1"),
                Integer,
            )
        ).label("hs"),
        func.round(
            func.sum(batStats.c.runs)
            * 100
            / func.nullif(func.sum(batStats.c.balls_faced), 0),
            0,
        ).label("sr"),
        func.round(
            func.sum(batStats.c.runs) / func.nullif(func.sum(batStats.c.player_out), 0),
            2,
        ).label("avg"),
        func.sum(batStats.c.fours).label("fours"),
        func.sum(batStats.c.sixes).label("sixes"),
    )
    if season is not None:
        selectStmt = selectStmt.where(batStats.c.season == season)
    selectStmt = selectStmt.group_by(batStats.c.player)
    selectStmt = selectStmt.order_by(nulls_last(desc("fours")))
    selectStmt = selectStmt.limit(limit)
    return selectStmt
