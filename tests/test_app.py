import falcon
from falcon import testing
import json
import pytest

from server.app import api


@pytest.fixture
def client():
    return testing.TestClient(api)


# pytest will inject the object returned by the "client" function
# as an additional parameter.
def test_list_images(client):
    doc = {
        'hello': [
            {
                'data': 'world'
            }
        ]
    }

    response = client.simulate_get('/test')
    result_doc = json.loads(response.content, encoding='utf-8')

    assert result_doc == doc
    assert response.status == falcon.HTTP_OK