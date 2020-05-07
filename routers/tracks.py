from fastapi import APIRouter, Request, Response, status
import sqlite3
import os.path

router = APIRouter()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "./chinook.db")


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


@router.get("/tracks", tags=["tracks"])
def get_tracks(request: Request, response: Response, per_page: int = 10, page: int = 0):
    tracks = {}
    with sqlite3.connect(db_path) as connection:
        connection.row_factory = dict_factory
# lambda cursor, x: x[0]
        cursor = connection.cursor()
        tracks = cursor.execute(
            f"SELECT TrackId, Name, AlbumId, MediaTypeId, GenreId, Composer, Milliseconds, Bytes, UnitPrice FROM tracks WHERE TrackId >= {page * per_page} and TrackId < { page * per_page + per_page }").fetchall()
        print(len(tracks))
        print(tracks[:2])
    response.json = tracks
    response.status_code = status.HTTP_200_OK
    return tracks


    
