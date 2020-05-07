from fastapi import APIRouter, Request, Response, status
import sqlite3
import os.path
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

router = APIRouter()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "./chinook.db")


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


@router.get("/tracks")
def get_tracks(request: Request, response: Response, per_page: int = 10, page: int = 0):
    tracks = {}
    with sqlite3.connect(db_path) as connection:
        connection.row_factory = dict_factory
        cursor = connection.cursor()
        tracks = cursor.execute(
            f"SELECT TrackId, Name, AlbumId, MediaTypeId, GenreId, Composer, Milliseconds, Bytes, UnitPrice FROM tracks WHERE TrackId > {page * per_page} and TrackId <= { page * per_page + per_page }").fetchall()

    json_data = jsonable_encoder(tracks)
    return JSONResponse(content=json_data, status_code= status.HTTP_200_OK)


    
