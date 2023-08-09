import json
from typing import Annotated

# NOTE: ignore the import not resolved errors here; as it would be fine as we execute it from the app directory
from database import getSession, rd
from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from utils.endPointMappings import batterApiMappings
from utils.getSQLQuery import executeSQLQuery

batterRouter = APIRouter(prefix="/batter", tags=["batter"])


def generateDynamicRoute(batterKey: str):
    endPoint = batterApiMappings[batterKey]["endPoint"]
    schema = batterApiMappings[batterKey]["schema"]
    columnPosition = list(
        batterApiMappings[batterKey]["schema"].__fields__.keys()
    ).index(batterApiMappings[batterKey]["columnName"])
    generateSQLQuery = batterApiMappings[batterKey]["getSQLMethod"]
    havingClause = batterApiMappings[batterKey]["havingClause"]
    description = batterApiMappings[batterKey]["description"]

    @batterRouter.get(
        f"/{endPoint}",
        response_model=dict[str, dict[str, str | int] | list[schema]],
        description=description,
        name=endPoint,
    )
    async def dynamicRoute(
        season: Annotated[str | None, "season"] = None,
        session=Depends(getSession),
    ):
        # TODO: understand how the json.dumps, json.loads and jsonable_encoder works
        redisKey = f"batter_{batterKey}_{season}"
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
                            session,
                            columnPosition,
                            havingClause,
                        )
                    )
                )
            ),
        )
        return json.loads(rd.get(redisKey))


batterMapKeys = list(batterApiMappings.keys())
for batterKey in batterMapKeys:
    generateDynamicRoute(batterKey)
