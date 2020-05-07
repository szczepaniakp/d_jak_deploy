from fastapi import APIRouter, Request, Response, status, HTTPException
import sqlite3
import os.path
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel

class Album(BaseModel):
    title: str
    artist_id: int

class AlbumResponse(BaseModel):
    AlbumId: int
    Title: str
    ArtistId: int

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

    with sqlite3.connect(db_path) as connection:
        cursor = connection.cursor()
        tracks = cursor.execute(
            f"SELECT Name FROM tracks WHERE Composer == '{composer_name}'").fetchall()

        for t in tracks:
            data.append(t[0])

        if any(data):
            data.sort()
            return JSONResponse(content=jsonable_encoder(data), status_code= status.HTTP_200_OK)

    raise HTTPException(status_code=404, detail={"error": "Composer does not exist in database."})


@router.post("/albums", response_model=AlbumResponse)
async def add_album(request: Request, response: Response, album: Album):
    with sqlite3.connect(db_path) as connection:
        connection.row_factory = dict_factory
        cursor = connection.cursor()
        artist_id = cursor.execute(f"SELECT ArtistId FROM artists WHERE ArtistId == { album.artist_id }").fetchone()
        
        if not any(artist_id):
            raise HTTPException(status_code=404, detail={"error": f"Artist with id={ album.artist_id } does not exists."})

        cursor.execute(f"INSERT INTO albums (Title, ArtistId) VALUES ('{ album.title }', '{ album.artist_id }')")
        connection.commit()
        # album_data = connection.cursor().execute(f"SELECT * FROM albums WHERE ArtistId == { album.artist_id }").fetchone()
        # print()
    return AlbumResponse(AlbumId=cursor.lastrowid, Title=album.title, ArtistId=album.artist_id)
    #JSONResponse(content=jsonable_encoder(tracks), status_code= status.HTTP_200_OK)

    
