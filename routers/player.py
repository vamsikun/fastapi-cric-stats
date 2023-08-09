from fastapi import APIRouter, Depends
from database import getCursorForPGDB
from getSQLScripts.player.getSQLForAllPlayers import getSQLForAllPlayers
from utils.getSQLQuery import executeSQLQuery
from database import rd
from fastapi.encoders import jsonable_encoder
import json

playerRouter = APIRouter(prefix="/player", tags=["players"])


# TODO: add validation
@playerRouter.get("/")
async def getAllPlayers(cursor=Depends(getCursorForPGDB)):
    redisKey = "player"
    if rd.exists(redisKey):
        return json.loads(rd.get(redisKey))
    sql = getSQLForAllPlayers()
    cursor.execute(sql)
    results = cursor.fetchall()
    columnNames = [desc[0] for desc in cursor.description]
    returnData = {columnNames[0]: results}
    rd.set(redisKey, json.dumps(jsonable_encoder(returnData)), ex=3600)
    return json.loads(rd.get(redisKey))
