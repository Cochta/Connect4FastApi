from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class Game(BaseModel):
    name: str


class Player(BaseModel):
    name: str


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/SendMSG/{txt}")
async def say_hello(txt: str):
    return {"message": f"{txt}"}


@app.get("/players")
async def get_players():
    return {"message": f"Hello world"}


@app.get("/games")
async def get_games():
    return {"message": f"Hello world"}


@app.post("/games")
async def create_game(game: Game):
    print("post a new game: ", game)
    return game


@app.post("/players")
async def create_player(player: Player):
    print("post a new game: ", player)
    return player



