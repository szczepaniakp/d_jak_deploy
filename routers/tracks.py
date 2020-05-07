from fastapi import APIRouter, Request, Response, status, HTTPException
import sqlite3
import os.path
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List


class Album(BaseModel):
    title: str
    artist_id: int


class Customer(BaseModel):
    company: str = None
    address: str = None
    city: str = None
    state: str = None
    country: str = None
    postalcode: str = None
    fax: str = None


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
def tracks(request: Request, per_page: int = 10, page: int = 0):
    tracks = {}
    with sqlite3.connect(db_path) as connection:
        connection.row_factory = dict_factory
        cursor = connection.cursor()
        tracks = cursor.execute(
            f"SELECT TrackId, Name, AlbumId, MediaTypeId, GenreId, Composer, Milliseconds, Bytes, UnitPrice FROM tracks WHERE TrackId > {page * per_page} and TrackId <= { page * per_page + per_page }").fetchall()

    return JSONResponse(content=jsonable_encoder(tracks), status_code=status.HTTP_200_OK)


@router.get("/tracks/composers/")
def tracks_of_composer(request: Request, composer_name: str = ''):
    data = []

    with sqlite3.connect(db_path) as connection:
        cursor = connection.cursor()
        tracks = cursor.execute(
            f"SELECT Name FROM tracks WHERE Composer == '{composer_name}'").fetchall()

        for t in tracks:
            data.append(t[0])

        if any(data):
            data.sort()
            return JSONResponse(content=jsonable_encoder(data), status_code=status.HTTP_200_OK)

    raise HTTPException(status_code=404, detail={
                        "error": "Composer does not exist in database."})


@router.post("/albums", response_model=AlbumResponse, status_code=status.HTTP_201_CREATED)
async def album(request: Request, album: Album):
    with sqlite3.connect(db_path) as connection:
        connection.row_factory = dict_factory
        cursor = connection.cursor()
        artist_id = cursor.execute(
            f"SELECT ArtistId FROM artists WHERE ArtistId == { album.artist_id }").fetchone()

        if artist_id is None:
            raise HTTPException(status_code=404, detail={
                                "error": f"Artist with id={ album.artist_id } does not exist."})

        cursor.execute(
            f"INSERT INTO albums (Title, ArtistId) VALUES ('{ album.title }', '{ album.artist_id }')")
        connection.commit()

    return AlbumResponse(AlbumId=cursor.lastrowid, Title=album.title, ArtistId=album.artist_id)


@router.get("/albums/{album_id}", response_model=AlbumResponse, status_code=status.HTTP_200_OK)
def albums(album_id: int):
    album = []

    with sqlite3.connect(db_path) as connection:
        connection.row_factory = dict_factory
        cursor = connection.cursor()
        album = cursor.execute(
            f"SELECT AlbumId, Title, ArtistId FROM albums WHERE AlbumId == {album_id}").fetchone()
        if album is None:
            raise HTTPException(status_code=404, detail={
                                "error": f"Album with id={ album_id } does not exist."})

    return AlbumResponse(**album)


@router.put("/customers/{customer_id}")
def customers(customer_id: int, customer_data: Customer):
    with sqlite3.connect(db_path) as connection:
        cursor = connection.cursor()

        if cursor.execute(f"SELECT * FROM customers WHERE CustomerId == { customer_id }").fetchone() is None:
            raise HTTPException(status_code=404, detail={
                                "error": f"Customer with id={ customer_id } does not exist."})

        for key, value in customer_data.dict().items():
            if value is not None:
                cursor.execute(
                    f"UPDATE customers SET { key }='{ value }' WHERE CustomerId == { customer_id }").fetchone()

        connection.row_factory = dict_factory
        cursor = connection.cursor()
        customer = cursor.execute(
            f"SELECT * FROM customers WHERE CustomerId == { customer_id }").fetchone()

        return JSONResponse(content=jsonable_encoder(customer), status_code=status.HTTP_200_OK)


@router.get("/sales")
def sales(request: Request, category: str = ''):
    if category == "customers":
        with sqlite3.connect(db_path) as connection:
            connection.row_factory = dict_factory
            cursor = connection.cursor()
            result = cursor.execute(
                #f"SELECT c.CustomerId, IFNULL(c.Email,'') AS 'Email', IFNULL(c.Phone,'') AS 'Phone', ROUND(SUM(i.Total), 2) AS 'Sum' FROM customers c LEFT JOIN invoices i ON c.CustomerId = i.CustomerId GROUP BY i.CustomerId ORDER BY  ROUND(SUM(i.Total),2) DESC, c.CustomerId ASC").fetchall()
                f"SELECT c.CustomerId, c.Email, c.Phone, ROUND(SUM(i.Total), 2) AS 'Sum' FROM customers c JOIN invoices i ON c.CustomerId = i.CustomerId GROUP BY i.CustomerId ORDER BY  ROUND(SUM(i.Total),2) DESC, c.CustomerId ASC").fetchall()
            if len(result) != 0:
                return JSONResponse(content=jsonable_encoder(result), status_code=status.HTTP_200_OK)

    raise HTTPException(status_code=404, detail={
                        "error": f"Cannot provide stats for category '{ category }'"})
