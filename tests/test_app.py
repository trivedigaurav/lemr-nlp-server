import falcon
from falcon import testing
import json
import pytest

from server.app import application


@pytest.fixture
def client():
    return testing.TestClient(application)


# pytest will inject the object returned by the "client" function
# as an additional parameter.
def test_login(client):
    message = '{"message": "OK"}'
    response = client.simulate_get('/login')

    assert response.content == message, "Can't login"
    assert response.status == falcon.HTTP_OK, "Problems setting up Falcon server"

def test_mongo(client):
    report = "151966"
    response = client.simulate_get('/getReport/'+str(report))
    report = json.loads(response.content, encoding='utf-8')

    assert response.status == falcon.HTTP_OK, "Can't connect to database"
    assert report['reportText'] != "", "Can't read report " + str(report)