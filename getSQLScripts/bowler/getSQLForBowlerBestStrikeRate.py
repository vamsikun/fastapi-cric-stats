from getSQLScripts.bowler.bowlerSQLHelper import bowlerStatsTable
from sqlalchemy import (Integer, Numeric, String, asc, cast, func, nulls_last,
                        select)


def getSQLForBowlerBestStrikeRate(season, limit=10, minBalls=60):
    selectStmt = select(
        func.row_number()
        .over(
            order_by=nulls_last(
                asc(
                    func.round(
                        func.sum(bowlerStatsTable.c.legal_deliveries)
                        / func.sum(bowlerStatsTable.c.wickets),
                        2,
                    )
                )
            )
        )
        .label("pos"),
        bowlerStatsTable.c.player,
        func.count().label("matches"),
        func.sum(bowlerStatsTable.c.bowled_in_match).label("innings"),
        func.sum(bowlerStatsTable.c.wickets).label("wickets"),
        func.round(
            (
                func.sum(bowlerStatsTable.c.dot_balls)
                / func.sum(bowlerStatsTable.c.legal_deliveries)
            )
            * 100,
            2,
        ).label("dots_percentage"),
        cast(
            cast(
                cast(func.sum(bowlerStatsTable.c.legal_deliveries) / 6, Integer), String
            )
            + "."
            + cast(func.sum(bowlerStatsTable.c.legal_deliveries) % 6, String),
            Numeric,
        ).label("overs"),
        func.round(
            func.sum(bowlerStatsTable.c.runs_conceded)
            * 6
            / func.sum(bowlerStatsTable.c.legal_deliveries),
            2,
        ).label("econ"),
        func.round(
            func.sum(bowlerStatsTable.c.legal_deliveries)
            / func.sum(bowlerStatsTable.c.wickets),
            2,
        ).label("sr"),
        func.round(
            func.sum(bowlerStatsTable.c.runs_conceded)
            / func.sum(bowlerStatsTable.c.wickets),
            2,
        ).label("avg"),
        func.sum(bowlerStatsTable.c.runs_conceded).label("runs"),
    )
    if season is not None:
        selectStmt = selectStmt.where(bowlerStatsTable.c.season == season)
    selectStmt = selectStmt.group_by(bowlerStatsTable.c.player)
    selectStmt = selectStmt.having(
        func.sum(bowlerStatsTable.c.legal_deliveries) >= minBalls
    )
    selectStmt = selectStmt.order_by(nulls_last(asc("sr")))
    selectStmt = selectStmt.limit(limit)
    return selectStmt
