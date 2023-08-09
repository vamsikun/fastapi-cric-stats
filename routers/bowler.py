import json
from typing import Annotated

# NOTE: ignore the import not resolved errors here; as it would be fine as we execute it from the app directory
from database import getSession, rd
from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from utils.endPointMappings import bowlerApiMappings
from utils.getSQLQuery import executeSQLQuery

bowlerRouter = APIRouter(prefix="/bowler", tags=["bowler"])


def generateDynamicRoute(bowlerKey: str):
    endPoint = bowlerApiMappings[bowlerKey]["endPoint"]
    schema = bowlerApiMappings[bowlerKey]["schema"]
    columnPosition = list(
        bowlerApiMappings[bowlerKey]["schema"].__fields__.keys()
    ).index(bowlerApiMappings[bowlerKey]["columnName"])
    generateSQLQuery = bowlerApiMappings[bowlerKey]["getSQLMethod"]
    havingClause = bowlerApiMappings[bowlerKey]["havingClause"]
    description = bowlerApiMappings[bowlerKey]["description"]

    @bowlerRouter.get(
        f"/{endPoint}",
        response_model=dict[str, dict[str, str | int] | list[schema]],
        description=description,
        name=endPoint,
    )
    async def dynamicRoute(
        season: Annotated[str | None, "season"] = None,
        cursor=Depends(getSession),
    ):
        # TODO: understand how the json.dumps, json.loads and jsonable_encoder works
        redisKey = f"bowler_{bowlerKey}_{season}"
        if rd.exists(redisKey):
            return json.loads(rd.get(redisKey))
        sqlQuery = generateSQLQuery(season)
        rd.set(
            redisKey,
            json.dumps(
                jsonable_encoder(
                    (
                        executeSQLQuery(
                            sqlQuery,
                            cursor,
                            columnPosition,
                            havingClause,
                        )
                    )
                )
            ),
        )
        return json.loads(rd.get(redisKey))


bowlerMapKeys = list(bowlerApiMappings.keys())
for bowlerKey in bowlerMapKeys:
    generateDynamicRoute(bowlerKey)
