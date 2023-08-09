from pydantic import BaseModel
from typing import Annotated

# order of the columns in response data depends on these models


class MostWickets(BaseModel):
    # here I am not using camelcase as psql is case sensitive on columns, so it was creating some issues when pydantic checks the column names
    pos: Annotated[int, "position"]
    player: Annotated[str, "player"]
    matches: Annotated[int, "matches"]
    innings: Annotated[int, "innings"]
    wickets: Annotated[int | None, "wickets"] = None
    dots_percentage: Annotated[float, "dots_percentage"]
    overs: Annotated[float, "overs"]
    econ: Annotated[float | None, "econ"] = None
    sr: Annotated[float | None, "sr"] = None
    avg: Annotated[float | None, "avg"] = None
    runs: Annotated[int | None, "runs_conceded"] = None
    # bbi: Annotated[str,'best bowling in innings']


class BestAverage(MostWickets):
    pass


class BestEcon(MostWickets):
    pass


class BestStrikeRate(MostWickets):
    pass


class BestDotsPercentage(MostWickets):
    pass
