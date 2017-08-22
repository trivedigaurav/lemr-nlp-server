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
def test_hello_world(client):
    doc = {
        'hello': [
            {
                'data': 'world'
            }
        ]
    }

    response = client.simulate_get('/test')
    result_doc = json.loads(response.content, encoding='utf-8')

    assert result_doc == doc, "Can't return a JSON object"
    assert response.status == falcon.HTTP_OK, "Problems setting up Falcon server"

def test_scikit(client):
    try:
        from sklearn.datasets import fetch_20newsgroups
        from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
        from sklearn import metrics
        from sklearn.svm import LinearSVC
    except:
        assert False, 'Missing requirements. Try installing pre-requisites with pip'

    try:
        categories = ['sci.med', 'comp.graphics']
        twenty_train = fetch_20newsgroups(subset='train', categories=categories, shuffle=True, random_state=42)
    except:
        assert False, "Can't download sample dataset for building test models"


    try:
        count_vect = CountVectorizer()
        tfidf_transformer = TfidfTransformer()

        X_train_counts = count_vect.fit_transform(twenty_train.data)
        X_train_tfidf = tfidf_transformer.fit_transform(X_train_counts)
    except:
        assert False, "Can't vectorize samples"


    try:
        clf = LinearSVC()
        clf.fit(X_train_tfidf, twenty_train.target)
    except:
        assert False, "Failed to train test LinearSVC model"


    try:
        twenty_test = fetch_20newsgroups(subset='test', categories=categories, shuffle=True, random_state=42)
        docs_test = twenty_test.data


        X_test_counts = count_vect.transform(twenty_test.data)
        X_test_tfidf = tfidf_transformer.transform(X_test_counts)

        predicted = clf.predict(X_test_tfidf)
        metrics.classification_report(twenty_test.target, predicted)
    except:
        assert False, "Failed to make test predictions"

