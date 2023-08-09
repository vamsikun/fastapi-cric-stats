from pydantic import BaseModel
from sqlalchemy import select, func, String, case, Integer
from database import ormMetaData

# NOTE: minimum qualification for stats such as average, strikerate
havingFilter = "SUM(runs)>=100"

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

# ----------------------------------------------------------


class SelectStatementConfig(BaseModel):
    player: bool = False
    matches: bool = False
    innings: bool = False
    runs: bool = False
    hs: bool = False
    sr: bool = False
    avg: bool = False
    fours: bool = False
    sixes: bool = False

    # NOTE:
    # 1) when you add any other method don't forget to register the method name here
    methods: list[str] = [
        "getPlayer",
        "getMatches",
        "getInnings",
        "getRuns",
        "getHs",
        "getSr",
        "getAvg",
        "getFours",
        "getSixes",
    ]

    # comma is necessary in the return statements
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
            return "SUM(played_in_match) AS innings,"
        return ""

    def getRuns(self):
        if self.runs:
            return "SUM(runs) as runs,"
        return ""

    def getHs(self):
        if self.hs:
            return "MAX(cast(cast(coalesce(runs,0) as text)  || (case player_out when 1 then 0 else 1 end ) as int)) AS hs,"
        return ""

    def getSr(self):
        if self.sr:
            srCalculation = (
                "ROUND(CAST( SUM(runs) AS numeric )/NULLIF(SUM(balls_faced),0),4)*100 "
            )
            return f"{srCalculation} AS sr,"
        return ""

    def getAvg(self):
        if self.avg:
            avgCalculation = (
                "ROUND( CAST( SUM(runs) AS numeric)/NULLIF(SUM(player_out),0) ,2) "
            )
            return f"{avgCalculation} AS avg,"
        return ""

    def getFours(self):
        if self.fours:
            return "SUM(fours) AS fours,"
        return ""

    def getSixes(self):
        if self.sixes:
            return "SUM(sixes) AS sixes,"
        return ""

    # when we call this method on the object, it goes through the methodOrder variable and execute those methods in order
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
        # when there are extra columns from external joins
        allCols += extraCols
        statement = f"SELECT {allCols[:-1]} FROM batter_stats_each_match "
        # don't need the check for joinPredicate
        if joinPredicate != "":
            statement += f"{joinPredicate}"
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
    runs=True,
    hs=True,
    sr=True,
    avg=True,
    fours=True,
    sixes=True,
)
# to get team details
selectTeamDetails = {
    "selectStatement": "STRING_AGG(DISTINCT t1.team_shortcut, ',') as team,",
    "joinStatement": """LEFT JOIN teams as t1 on batter_stats_each_match.team=t1.team_id LEFT JOIN teams as t2 on batter_stats_each_match.opposition=t2.team_id """,
}
