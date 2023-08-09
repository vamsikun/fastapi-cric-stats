def getSQLForAllPlayers() -> str:
    sql = """SELECT distinct(player) FROM players;"""
    return sql
