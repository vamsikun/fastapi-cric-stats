from pydantic import BaseModel
from typing import Annotated

# order of the columns in response data depends on these models


class MostRuns(BaseModel):
    pos: Annotated[int, "position"]
    player: Annotated[str, "player"]
    # team: Annotated[str, "team"]
    matches: Annotated[int, "matches"]
    innings: Annotated[int, "innings"]
    runs: Annotated[int, "runs"]
    hs: Annotated[int, "highest score"]
    sr: Annotated[float, "strike rate"]
    avg: Annotated[float, "average"]
    fours: Annotated[int, "fours"]
    sixes: Annotated[int, "sixes"]


class MostSixes(MostRuns):
    pass


class MostFours(MostRuns):
    pass


class BestStrikeRate(MostRuns):
    pass


class BestAverage(MostRuns):
    pass


# This is somewhat different that others
class BestHighScore(BaseModel):
    pos: Annotated[int, "position"]
    player: Annotated[str, "player"]
    team: Annotated[str, "team"]
    opposition: Annotated[str, "opposition team"]
    hs: Annotated[int, "highest score"]
    sr: Annotated[float, "strike rate"]
    fours: Annotated[int, "fours"]
    sixes: Annotated[int, "sixes"]
