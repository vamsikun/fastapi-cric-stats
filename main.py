from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers.batter import batterRouter
from routers.bowler import bowlerRouter
from routers.match import matchRouter
from routers.player import playerRouter

app = FastAPI()

origins = [
    "http://192.168.184.6:3000",
    "http://localhost:3000",
    "http://localhost",
    "https://nextjs-cric-stats.vercel.app",
    "https://nextjs-cric-stats-pwah54eoi-vamsi81523-gmailcom.vercel.app/"
    # Add more origins as needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(batterRouter)
app.include_router(bowlerRouter)
app.include_router(matchRouter)
app.include_router(playerRouter)
