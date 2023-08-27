from sqlalchemy import (
    NUMERIC,
    Numeric,
    String,
    and_,
    case,
    cast,
    desc,
    distinct,
    func,
    literal,
    select,
    union,
)

from database import ormMetaData
from utils.getSQLQuery import getWherePredicate

matches = ormMetaData.tables["matches"]
firstUnionSelect = select(
    matches.c.season,
    matches.c.team1.label("team"),
    func.count("*").label("matches"),
    literal(1).label("innings"),
    func.max(
        func.lpad(
            matches.c.m_team1_score
            + "-"
            + func.lpad(cast(matches.c.team2, String), 3, "0"),
            10,
            "0",
        )
    ).label("high_score"),
    func.min(
        case(
            (
                and_(
                    matches.c.team_won != None,
                    matches.c.dls != 1,
                    matches.c.overs_reduced != 1,
                ),
                func.lpad(
                    matches.c.m_team1_score
                    + "-"
                    + func.lpad(cast(matches.c.team2, String), 3, "0"),
                    10,
                    "0",
                ),
            ),
            else_=literal("ffffff"),
        )
    ).label("low_score"),
    func.sum(matches.c.team1_score).label("runs"),
    func.sum(matches.c.team1_fours).label("fours"),
    func.sum(matches.c.team1_sixes).label("sixes"),
    func.sum(matches.c.team1_legal_deliveries_faced).label("legal_deliveries_faced"),
    func.sum(matches.c.team1_wickets).label("wickets"),
    func.max(
        func.lpad(
            matches.c.m_team2_score
            + "-"
            + func.lpad(cast(matches.c.team2, String), 3, "0"),
            10,
            "0",
        )
    ).label("opp_high_score"),
    func.min(
        case(
            (
                and_(
                    matches.c.team_won != None,
                    matches.c.dls != 1,
                    matches.c.overs_reduced != 1,
                ),
                func.lpad(
                    matches.c.m_team2_score
                    + "-"
                    + func.lpad(cast(matches.c.team2, String), 3, "0"),
                    10,
                    "0",
                ),
            ),
            else_=literal("ffffff"),
        )
    ).label("opp_low_score"),
    func.sum(matches.c.team2_score).label("opp_runs"),
    func.sum(matches.c.team2_fours).label("opp_fours"),
    func.sum(matches.c.team2_sixes).label("opp_sixes"),
    func.sum(matches.c.team2_legal_deliveries_faced).label(
        "opp_legal_deliveries_faced"
    ),
    func.sum(matches.c.team2_wickets).label("opp_wickets"),
    func.sum(case((matches.c.team_won == matches.c.team1, 1), else_=literal(0))).label(
        "wins"
    ),
    func.sum(case((matches.c.team_won == matches.c.team2, 1), else_=literal(0))).label(
        "losses"
    ),
)

firstUnionSelect = firstUnionSelect.group_by(matches.c.season, matches.c.team1)

secondUnionSelect = select(
    matches.c.season,
    matches.c.team2.label("team"),
    func.count("*").label("matches"),
    literal(2).label("innings"),
    func.max(
        func.lpad(
            matches.c.m_team2_score
            + "-"
            + func.lpad(cast(matches.c.team1, String), 3, "0"),
            10,
            "0",
        )
    ).label("high_score"),
    func.min(
        case(
            (
                and_(
                    matches.c.team_won != None,
                    matches.c.dls != 1,
                    matches.c.overs_reduced != 1,
                ),
                func.lpad(
                    matches.c.m_team2_score
                    + "-"
                    + func.lpad(cast(matches.c.team1, String), 3, "0"),
                    10,
                    "0",
                ),
            ),
            else_=literal("ffffff"),
        )
    ).label("low_score"),
    func.sum(matches.c.team2_score).label("runs"),
    func.sum(matches.c.team2_fours).label("fours"),
    func.sum(matches.c.team2_sixes).label("sixes"),
    func.sum(matches.c.team2_legal_deliveries_faced).label("legal_deliveries_faced"),
    func.sum(matches.c.team2_wickets).label("wickets"),
    func.max(
        func.lpad(
            matches.c.m_team1_score
            + "-"
            + func.lpad(cast(matches.c.team1, String), 3, "0"),
            10,
            "0",
        )
    ).label("opp_high_score"),
    func.min(
        case(
            (
                and_(
                    matches.c.team_won != None,
                    matches.c.dls != 1,
                    matches.c.overs_reduced != 1,
                ),
                func.lpad(
                    matches.c.m_team1_score
                    + "-"
                    + func.lpad(cast(matches.c.team1, String), 3, "0"),
                    10,
                    "0",
                ),
            ),
            else_=literal("ffffff"),
        )
    ).label("opp_low_score"),
    func.sum(matches.c.team1_score).label("opp_runs"),
    func.sum(matches.c.team1_fours).label("opp_fours"),
    func.sum(matches.c.team1_sixes).label("opp_sixes"),
    func.sum(matches.c.team1_legal_deliveries_faced).label(
        "opp_legal_deliveries_faced"
    ),
    func.sum(matches.c.team1_wickets).label("opp_wickets"),
    func.sum(case((matches.c.team_won == matches.c.team2, 1), else_=literal(0))).label(
        "wins"
    ),
    func.sum(case((matches.c.team_won == matches.c.team1, 1), else_=literal(0))).label(
        "losses"
    ),
)

secondUnionSelect = secondUnionSelect.group_by(matches.c.season, matches.c.team2)

selectStmt = union(firstUnionSelect, secondUnionSelect).subquery()


def getSQLForTeamSummary(season: str, team: int, teamType: str, innings: int | None):
    if teamType == "opp":
        stmt = select(
            selectStmt.c.season,
            func.sum(selectStmt.c.matches).label("matches"),
            (
                cast(func.sum(selectStmt.c.losses), String)
                + "/"
                + cast(func.sum(selectStmt.c.wins), String)
            ).label("w_l"),
            func.max(selectStmt.c.opp_high_score).label("high_score"),
            func.min(selectStmt.c.opp_low_score).label("low_score"),
            func.sum(selectStmt.c.opp_wickets).label("wickets"),
            func.sum(selectStmt.c.opp_fours).label("fours"),
            func.sum(selectStmt.c.opp_sixes).label("sixes"),
            func.round(
                cast(
                    func.div(
                        func.sum((selectStmt.c.opp_runs)),
                        func.sum(selectStmt.c.opp_legal_deliveries_faced),
                    ),
                    Numeric,
                )
                * 6,
                3,
            ).label("run_rate"),
        )
    else:
        stmt = select(
            selectStmt.c.season,
            func.sum(selectStmt.c.matches).label("matches"),
            (
                cast(func.sum(selectStmt.c.wins), String)
                + "/"
                + cast(func.sum(selectStmt.c.losses), String)
            ).label("w_l"),
            func.max(selectStmt.c.high_score).label("high_score"),
            func.min(selectStmt.c.low_score).label("low_score"),
            func.sum(selectStmt.c.wickets).label("wickets"),
            func.sum(selectStmt.c.fours).label("fours"),
            func.sum(selectStmt.c.sixes).label("sixes"),
            func.round(
                cast(
                    func.div(
                        func.sum((selectStmt.c.runs)),
                        func.sum(selectStmt.c.legal_deliveries_faced),
                    ),
                    Numeric,
                )
                * 6,
                3,
            ).label("run_rate"),
        )

    if innings is not None:
        stmt = stmt.where(selectStmt.c.innings == innings)
    stmt = stmt.where(selectStmt.c.team == team)
    stmt = stmt.group_by(selectStmt.c.season)
    stmt = stmt.order_by(desc(selectStmt.c.season))
    print(stmt)
    return stmt
