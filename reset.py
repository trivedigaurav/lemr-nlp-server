# import argparse
import json
import os

from ast import literal_eval

from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.externals.joblib import dump, load

import pymongo
from pymongo import MongoClient

from server import settings

PATH_PREFIX = "models/"
USER = "user"

#settings
client = MongoClient(settings.MONGODB_HOST, settings.MONGODB_PORT)
db = client[settings.DATABASE_NAME]
levels = ["encounters", "reports", "sections", "sentences"]

with open('initial_ids.json') as json_file:  
    initial_ids = json.load(json_file)


def add_feedback():
    #Populate feedbacks
    db["feedbacks"].remove({})

    for enc in initial_ids:
        for level in levels:
            for row in db[level].find({"encounter_id": enc}):
                if (row["gold_label"] == "neg"):
                    class_ = 0
                else:
                    class_ = 1
                
                #Update levels
                db[level].update_one({ '_id': row['_id']},
                                     {"$set":{
                                         "class": class_,
                                         "model": 0
                                     }}
                                    )
                
                feedback = {
                    'level': level,
                    'id': row[level[:-1]+"_id"],
                    'class': class_,
                    'model': 0,
                    'user': USER
                }

                #save in feedbacks for logging
                db["feedbacks"].find_one_and_update( {
                        "level": feedback["level"],
                        "id": feedback["id"],
                        "model": feedback["model"]
                    },
                    {"$set": feedback},
                    upsert=True)


def create_models():
    #Delete exisiting
    for file in os.listdir(PATH_PREFIX):
        file_path = os.path.join(PATH_PREFIX, file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(e)

    #Create model 0
    for level in levels:
        
        texts_ = []
        classes_ = []
        rationales_ = []
        
        for row in db[level].find({"class":{"$ne":None}}):
            texts_.append(row['text'])
            rationales_.append(literal_eval(row['rationales']))
            classes_.append(row['class'])
            
        count_vect = CountVectorizer()
        tfidf_transformer = TfidfTransformer()
        
        clf = LinearSVC(penalty="l2", dual=False, tol=1e-3)
        classifier = CalibratedClassifierCV(clf)
        
        X_train_counts = count_vect.fit_transform(texts_)
        X_train_tfidf = tfidf_transformer.fit_transform(X_train_counts)
        
        classifier.fit(X_train_tfidf, classes_)
        
        model = 0

        path = PATH_PREFIX + level + "_" + str(model) + ".classifier" 
        if os.path.exists(path):
            print path + "  already exists!"
            os.remove(path)
        dump(classifier, path)        
        
        path = PATH_PREFIX + level + "_" + str(model) + ".count_vect" 
        if os.path.exists(path):
            print path + "  already exists!"
            os.remove(path)
        dump(count_vect, path)        
        
        path = PATH_PREFIX + level + "_" + str(model) + ".tfidf_transformer" 
        if os.path.exists(path):
            print path + "  already exists!"
            os.remove(path)
        dump(tfidf_transformer, path)


if __name__ == '__main__':
    add_feedback()
    create_models()
    