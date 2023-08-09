from getSQLScripts.batter.batterSQLHelper import batStats, teamsTable
from sqlalchemy import (Integer, String, case, desc, distinct, func,
                        nulls_last, select)


def getSQLForBatterBestHighScore(season, limit=10):
    t1, t2 = teamsTable.alias(), teamsTable.alias()
    selectStmt = select(
        func.row_number()
        .over(
            order_by=nulls_last(
                desc(
                    func.max(
                        func.cast(
                            func.cast(func.coalesce(batStats.c.runs, 0), String)
                            + case((batStats.c.player_out == 1, "0"), else_="1"),
                            Integer,
                        )
                    )
                )
            )
        )
        .label("pos"),
        batStats.c.player,
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
        func.sum(batStats.c.fours).label("fours"),
        func.sum(batStats.c.sixes).label("sixes"),
        func.string_agg(distinct(t1.c.team_shortcut), ",").label("team"),
        func.string_agg(distinct(t2.c.team_shortcut), ",").label("opposition"),
    )
    selectStmt = selectStmt.join_from(batStats, t1, batStats.c.team == t1.c.team_id)
    selectStmt = selectStmt.join_from(
        batStats, t2, batStats.c.opposition == t2.c.team_id
    )
    selectStmt = selectStmt.where(batStats.c.season == season)
    selectStmt = selectStmt.group_by(batStats.c.player, batStats.c.match_id)
    selectStmt = selectStmt.order_by(desc("hs"))
    selectStmt = selectStmt.limit(limit)
    return selectStmt
