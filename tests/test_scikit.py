import os
import warnings 


def test_scikit():
    try:
        from sklearn.datasets import fetch_20newsgroups
        from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
        from sklearn import metrics
        from sklearn.svm import LinearSVC
        from sklearn.externals.joblib import dump, load
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

        if os.path.exists("pytest_model.joblib"):
            warnings.warn(UserWarning("pytest_model.joblib already exists"))
            os.remove("pytest_model.joblib")
        
        dump(clf, 'pytest_model.joblib')
        clf = load('pytest_model.joblib') 
        os.remove("pytest_model.joblib") 
    except:
        assert False, "Can't serialize test model"

    try:
        twenty_test = fetch_20newsgroups(subset='test', categories=categories, shuffle=True, random_state=42)
        docs_test = twenty_test.data


        X_test_counts = count_vect.transform(twenty_test.data)
        X_test_tfidf = tfidf_transformer.transform(X_test_counts)

        predicted = clf.predict(X_test_tfidf)
        metrics.classification_report(twenty_test.target, predicted)
    except:
        assert False, "Failed to make test predictions"

