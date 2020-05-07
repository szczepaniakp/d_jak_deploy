import pytest
from fastapi.testclient import TestClient
from main import app

import json

client = TestClient(app)

def test_get_tracks():
    response = client.get('/tracks')
    assert response.status_code == 200
    json = response.json()
    print(json)
    assert response.json() == [{'TrackId': 1, 'Name': 'For Those About To Rock (We Salute You)', 'AlbumId': 1, 'MediaTypeId': 1, 'GenreId': 1, 'Composer': 'Angus Young, Malcolm Young, Brian Johnson', 'Milliseconds': 343719, 'Bytes': 11170334, 'UnitPrice': 0.99}, {'TrackId': 2, 'Name': 'Balls to the Wall', 'AlbumId': 2, 'MediaTypeId': 2, 'GenreId': 1, 'Composer': None, 'Milliseconds': 342562, 'Bytes': 5510424, 'UnitPrice': 0.99}, {'TrackId': 3, 'Name': 'Fast As a Shark', 'AlbumId': 3, 'MediaTypeId': 2, 'GenreId': 1, 'Composer': 'F. Baltes, S. Kaufman, U. Dirkscneider & W. Hoffman', 'Milliseconds': 230619, 'Bytes': 3990994, 'UnitPrice': 0.99}, {'TrackId': 4, 'Name': 'Restless and Wild', 'AlbumId': 3, 'MediaTypeId': 2, 'GenreId': 1, 'Composer': 'F. Baltes, R.A. Smith-Diesel, S. Kaufman, U. Dirkscneider & W. Hoffman', 'Milliseconds': 252051, 'Bytes': 4331779, 'UnitPrice': 0.99}, {'TrackId': 5, 'Name': 'Princess of the Dawn', 'AlbumId': 3, 'MediaTypeId': 2, 'GenreId': 1, 'Composer': 'Deaffy & R.A. Smith-Diesel', 'Milliseconds': 375418, 'Bytes': 6290521, 'UnitPrice': 0.99}, {'TrackId': 6, 'Name': 'Put The Finger On You', 'AlbumId': 1, 'MediaTypeId': 1, 'GenreId': 1, 'Composer': 'Angus Young, Malcolm Young, Brian Johnson', 'Milliseconds': 205662, 'Bytes': 6713451, 'UnitPrice': 0.99}, {'TrackId': 7, 'Name': "Let's Get It Up", 'AlbumId': 1, 'MediaTypeId': 1, 'GenreId': 1, 'Composer': 'Angus Young, Malcolm Young, Brian Johnson', 'Milliseconds': 233926, 'Bytes': 7636561, 'UnitPrice': 0.99}, {'TrackId': 8, 'Name': 'Inject The Venom', 'AlbumId': 1, 'MediaTypeId': 1, 'GenreId': 1, 'Composer': 'Angus Young, Malcolm Young, Brian Johnson', 'Milliseconds': 210834, 'Bytes': 6852860, 'UnitPrice': 0.99}, {'TrackId': 9, 'Name': 'Snowballed', 'AlbumId': 1, 'MediaTypeId': 1, 'GenreId': 1, 'Composer': 'Angus Young, Malcolm Young, Brian Johnson', 'Milliseconds': 203102, 'Bytes': 6599424, 'UnitPrice': 0.99}, {'TrackId': 10, 'Name': 'Evil Walks', 'AlbumId': 1, 'MediaTypeId': 1, 'GenreId': 1, 'Composer': 'Angus Young, Malcolm Young, Brian Johnson', 'Milliseconds': 263497, 'Bytes': 8611245, 'UnitPrice': 0.99}]

