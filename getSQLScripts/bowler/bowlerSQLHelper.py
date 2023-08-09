from pydantic import BaseModel
from database import ormMetaData
from sqlalchemy import select, func, String, Numeric, cast

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


# ------------------------------------------------------------
selectTeamDetails = {
    "selectStatement": "STRING_AGG(DISTINCT t1.team_shortcut, ',') as team,",
    "joinStatement": """LEFT JOIN teams as t1 on bowler_stats_each_match.team=t1.team_id LEFT JOIN teams as t2 on bowler_stats_each_match.opposition=t2.team_id """,
}


class SelectStatementConfig(BaseModel):
    player: bool = False
    matches: bool = False
    innings: bool = False
    wickets: bool = False
    dots_percentage: bool = False
    overs: bool = False
    econ: bool = False
    sr: bool = False
    avg: bool = False
    runs: bool = False

    methods: list[str] = [
        "getPlayer",
        "getMatches",
        "getInnings",
        "getWickets",
        "getDots_percentage",
        "getOvers",
        "getEcon",
        "getSr",
        "getAvg",
        "getRuns",
    ]

    def getPlayer(self):
        if self.player:
            return "player,"
        return ""

    def getMatches(self):
        if self.matches:
            return "COUNT(*) AS matches,"
        return ""

    def getInnings(self):
        if self.innings:
            return "SUM(bowled_in_match) AS innings,"
        return ""

    def getWickets(self):
        if self.wickets:
            return "SUM(wickets) as wickets,"
        return ""

    def getDots_percentage(self):
        if self.dots_percentage:
            return "ROUND(CAST(SUM(dot_balls)::float/SUM(legal_deliveries) AS NUMERIC)*100, 2) AS dots_percentage,"
        return ""

    def getOvers(self):
        if self.overs:
            return "CAST(CAST( SUM( legal_deliveries )/6 AS VARCHAR)||'.'||CAST( SUM( legal_deliveries )%6 AS VARCHAR) AS numeric) AS overs,"
        return ""

    def getEcon(self):
        if self.econ:
            return "ROUND( CAST( SUM(runs_conceded)*6.0/SUM(legal_deliveries) as NUMERIC) ,2) AS econ,"
        return ""

    def getSr(self):
        if self.sr:
            return "ROUND(CAST(SUM(legal_deliveries)::float/SUM(wickets) as NUMERIC),2) AS sr,"
        return ""

    def getAvg(self):
        if self.avg:
            return "ROUND(CAST(SUM(runs_conceded)::float/SUM(wickets) as NUMERIC),2) AS avg,"
        return ""

    def getRuns(self):
        if self.runs:
            return "SUM(runs_conceded) as runs,"
        return ""

    def getSelectStatement(
        self,
        extraCols: str = "",
        joinPredicate: str = "",
        wherePredicate: str = "",
        groupByPredicate: str = "",
        havingPredicate: str = "",
        orderByPredicate: str = "",
        limit: int = 10,
    ):
        allCols: str = ""
        for methodName in self.methods:
            method = getattr(self, methodName)
            allCols += method()
        allCols += extraCols
        statement = f"SELECT {allCols[:-1]} FROM bowler_stats_each_match "
        # don't need check for joinPredicate
        if joinPredicate != "":
            statement += f"{joinPredicate} "
        if wherePredicate != "":
            statement += f"WHERE {wherePredicate} "
        if groupByPredicate != "":
            statement += f"GROUP BY {groupByPredicate} "
        if havingPredicate != "":
            statement += f"HAVING {havingPredicate} "
        if orderByPredicate != "":
            statement += f"ORDER BY {orderByPredicate} NULLS LAST "
        statement += f"LIMIT {limit}"
        return statement


defaultSelectConfig: SelectStatementConfig = SelectStatementConfig(
    player=True,
    matches=True,
    innings=True,
    wickets=True,
    dots_percentage=True,
    overs=True,
    econ=True,
    sr=True,
    avg=True,
    runs=True,
)
