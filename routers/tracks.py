from fastapi import APIRouter, Request, Response, status, HTTPException
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
def get_tracks(request: Request, per_page: int = 10, page: int = 0):
    tracks = {}
    with sqlite3.connect(db_path) as connection:
        connection.row_factory = dict_factory
        cursor = connection.cursor()
        tracks = cursor.execute(
            f"SELECT TrackId, Name, AlbumId, MediaTypeId, GenreId, Composer, Milliseconds, Bytes, UnitPrice FROM tracks WHERE TrackId > {page * per_page} and TrackId <= { page * per_page + per_page }").fetchall()

    return JSONResponse(content=jsonable_encoder(tracks), status_code= status.HTTP_200_OK)

@router.get("/tracks/composers/")
def get_tracks_of_composer(request: Request, composer_name: str = ''):
    data = []
    print(composer_name)
    with sqlite3.connect(db_path) as connection:
        # connection.row_factory = dict_factory
        cursor = connection.cursor()
        tracks = cursor.execute(
            f"SELECT Name FROM tracks WHERE Composer == '{composer_name}'").fetchall()
        # t = tracks.fetchone()
        # while tracks.fetchone() is not None:
        #     data.append(t[0])
        #     t = tracks.fetchone()
        for t in tracks:
            data.append(t[0])
        if any(data):
            data.sort()
            return JSONResponse(content=jsonable_encoder(data), status_code= status.HTTP_200_OK)

    raise HTTPException(status_code=404, detail={"error": "Composer does not exist in database."})



    
