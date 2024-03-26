import os
from datetime import datetime

from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from peewee import *

app = FastAPI()
db_name = os.environ.get("POSTGRES_DB", "my_data_base")
user = os.environ.get("POSTGRES_USER", "constantin")
password = os.environ.get("POSTGRES_PASSWORD", "1234")
host = os.environ.get("POSTGRES_HOST", "localhost")

psql_db = PostgresqlDatabase(db_name, user=user, password=password, host=host)


class PsqlModel(Model):
    class Meta:
        database = psql_db


class PlayerModel(PsqlModel):
    id = AutoField(primary_key=True)
    name = CharField()
    elo = IntegerField()


class GameModel(PsqlModel):
    winnerId = BigIntegerField()
    loserId = BigIntegerField()
    timestamp = DateTimeField()


with psql_db:  # connect
    psql_db.create_tables([PlayerModel, GameModel])


# close.


class Player(BaseModel):
    id: int = PrimaryKeyField()
    name: str
    elo: int


class Game(BaseModel):
    winnerId: int
    loserId: int
    timestamp: datetime


class EloChange(BaseModel):
    elo: int


@app.get("/")
async def root():
    return {"message": "Successful connection to server"}


@app.get("/SendMessage/{msg}")
async def send_message(msg: str):
    return {"message": f"{msg}"}


@app.get("/players")
async def get_players():
    players = list(PlayerModel.select(PlayerModel.name, PlayerModel.elo).order_by(PlayerModel.elo.desc()).dicts())
    return players


@app.get("/player/{name}")
async def get_player_by_name(name: str):
    player = list(PlayerModel.select(PlayerModel.name, PlayerModel.elo).where(PlayerModel.name == name).dicts())
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    return player


@app.get("/games")
async def get_games():
    games = list(GameModel.select().dicts())
    return games


@app.get("/games/{player_name}")
async def get_games_by_player_name(player_name: str):
    try:
        player = PlayerModel.get(PlayerModel.name == player_name)
        games = list(
            GameModel.select().where((GameModel.winnerId == player.id) | (GameModel.loserId == player.id)).dicts())
        if not games:
            raise HTTPException(status_code=404, detail="No games found for this player")
        return games
    except PlayerModel.DoesNotExist:
        raise HTTPException(status_code=404, detail="Player not found")


@app.post("/player")
async def create_player(player: Player):
    # Check if the player already exists
    try:
        existing_player = PlayerModel.get(PlayerModel.name == player.name)
        # If player already exists, return a message indicating the same
        return {"message": f"Player {existing_player.name} already exists."}
    except PlayerModel.DoesNotExist:
        # If player doesn't exist, create a new one
        new_player = PlayerModel.create(name=player.name, elo=player.elo)
        return {"message": f"Successfully created player: {new_player.name}"}


@app.post("/player/{name}")
async def update_player_elo(name: str, elo_change: EloChange):
    try:
        player = PlayerModel.get(PlayerModel.name == name)
        player.elo += elo_change.elo
        player.save()
        return {"message": f"ELO for player {name} updated successfully"}
    except PlayerModel.DoesNotExist:
        raise HTTPException(status_code=404, detail=f"No player named: {name}")


@app.post("/game")
async def create_game(game: Game):
    new_game = GameModel.create(winnerId=game.winnerId, loserId=game.loserId, timestamp=datetime.now())
    return {"message": f"successfully created game between : {new_game.winnerId} and {new_game.loserId}"}


@app.middleware("http")
async def db_connection_handler(request: Request, call_next):
    psql_db.connect()
    response = await call_next(request)
    psql_db.close()
    return response
