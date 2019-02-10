from .settings import *
from .logger import logEvent

import json
import falcon
import re
import os

from collections import defaultdict

from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.externals.joblib import dump, load

###NOTE: MongoDB should have indices built, otherwise this can be really slow 
class_var = "class"
USER = "user"


class GetPredictions(object):

    def __init__(self, client):
        with open('data/control.json', 'r') as fp:
            self.enc_control = set(json.load(fp))

        # with open('data/intervention.json', 'r') as fp:
        #     self.enc_intervention = json.load(fp)

        self.control = GetPredictionsControl(client[CONDITIONS["control"]["db"]])
        self.intervention = GetPredictionsIntervention(client[CONDITIONS["intervention"]["db"]])
        

    def on_get(self, req, resp, encounterid, modelid="current"):
        if encounterid != None:
            if encounterid in self.enc_control:
                message = self.control.predict(encounterid)
            else:
                message = self.intervention.predict(encounterid)

        if (message):
            resp.body = json.dumps(message, ensure_ascii=False, cls=SetEncoder)
            resp.status = falcon.HTTP_200


    def on_put(self, req, resp, modelid, override):
        feedbackObj = json.loads(req.stream.read(), 'utf-8')

        if feedbackObj["encounter_id"] in self.enc_control:
            message = self.control.parse_feedback(feedbackObj)
        else:
            message = self.intervention.parse_feedback(feedbackObj)

        if (message):
            resp.body = json.dumps({"status": "OK"}, ensure_ascii=False)
            resp.status = falcon.HTTP_200


class SetEncoder(json.JSONEncoder):
    
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return json.JSONEncoder.default(self, obj)


class GetPredictionsBase(object):

    def predict(self, encounterid):

        print self.condition, encounterid

        if encounterid != None:

            enc = self.db.encounters.find_one( { "encounter_id": str(encounterid) })

            if (enc):

                message = {
                    "class": 1,
                    # "rationale_list": enc['rationale_list'],
                
                    "reports": defaultdict(list),
                    "sections": defaultdict(list),
                    "sentences": defaultdict(list),

                    "pos_reports": set(),
                    "pos_sections": set(),
                    "pos_sentences": set(),

                    "model": str(self.version)+"."+self.condition_version
                }


                #Reports
                for row in self.db["reports"].find( { "encounter_id": str(encounterid) } ) \
                            .sort([("date",1)]):
                    row_ = self._clean_row("report", row)
                    id_ = row_["report_id"]

                    message["reports"][id_] = row_
                    message["reports"][id_]["pos_sections"] = set()
                    message["reports"][id_]["pos_sentences"] = set()
                    message["reports"][id_]["sections"] = []
                    message["reports"][id_]["sentences"] = []

                    if(row_["class"] == 1):
                        message["pos_reports"].add(id_)
                        message["class"] = 1 #Bubble up


                #Sections
                for row in self.db["sections"].find( { "encounter_id": str(encounterid) } ):
                    row_ = self._clean_row("section", row)
                    id_ = row_["section_id"]

                    message["sections"][id_] = row_
                    message["sections"][id_]["pos_sentences"] = set()
                    message["sections"][id_]["sentences"] = []


                    if(row_["class"] == 1):
                        message["pos_sections"].add(id_)
                        message["reports"][row_["report_id"]]["pos_sections"].add(id_)

                        #Bubble up
                        message["reports"][row_["report_id"]]["class"] = 1
                        message["pos_reports"].add(row_["report_id"])
                        message["class"] = 1

                    message["reports"][row_["report_id"]]["sections"].append(id_)


                #Sentences
                for row in self.db["sentences"].find( { "encounter_id": str(encounterid) } ):
                    row_ = self._clean_row("sentence", row)
                    id_ = row_["sentence_id"]

                    message["sentences"][id_] = row_

                    if(row_["class"] == 1):
                        message["pos_sentences"].add(id_)
                        message["reports"][row_["report_id"]]["pos_sentences"].add(id_)
                        message["sections"][row_["section_id"]]["pos_sentences"].add(id_)

                        #Bubble up
                        message["reports"][row_["report_id"]]["class"] = 1
                        message["pos_reports"].add(row_["report_id"])

                        message["sections"][row_["section_id"]]["class"] = 1
                        message["pos_sections"].add(row_["section_id"])
                        message["reports"][row_["report_id"]]["pos_sections"].add(row_["section_id"])


                        message["class"] = 1


                    message["reports"][row_["report_id"]]["sentences"].append(id_)
                    message["sections"][row_["section_id"]]["sentences"].append(id_)                    


                logEvent("getPredictionsByEncounter", str({"encounterid": encounterid})) #DEBUG=10
                
                # print message

                return message
            else:
                logEvent("getPredictionsByEncounter", str({"encounterid": encounterid}), level=40)


    def parse_feedback(self, feedbackObj):
        
        # print feedbackList

        logEvent("parseFeedbackObj", str({"condition": self.condition, 
                                    "feedbackObj": feedbackObj})) #DEBUG=10
        
        # print self.condition, feedbackObj["encounter_id"]

        levels = ["encounter", "report", "section", "sentence", "text"]

        self.version += 1

        self._set_neg_feedback(feedbackObj["encounter_id"])

        for level in levels[:-1]:
            for pos_id in feedbackObj["pos_"+level+"s"]:
                self._add_pos_feedback(pos_id, level)

        for feedback in feedbackObj["list"]:
            for level in levels:
                if feedback[level]:
                    
                    if (level != "text"):
                        record = {
                                'level': level,
                                'id': feedback[level]["id"],
                                'class': feedback[level]["class"]
                        }

                        if (feedback["text"]):
                            record["text"] = feedback["text"]["id"]

                        self._add_feedback(record)
                    else:
                        found = self._find_text(text=feedback[level]["id"], report=feedback["report"]["id"])

                        # import pdb; pdb.set_trace()
                        # print found

                        for sent in found["sentences"]:
                            self._add_feedback({'level': "sentence", "id": sent, "class": 1, "text": feedback[level]["id"]}) #sent

                        for sect in found["sections"]:
                            self._add_feedback({'level': "section", "id": sect, "class": 1, "text": feedback[level]["id"]}) #sect


        self._retrain()
        dump(self.version, self.path_prefix + "version")

        logEvent("newModel", str({"version": self.version, "path": self.path_prefix, "condition": self.condition}))
        
        return True


    def _clean_row(self, level, row):
        row["_id"] = str(row["_id"])
        row.pop('rationales', None)
        row['class'] = self._predict_one(level, row)

        return row


    def _find_text(self, text, report):
        
        ret = {
            "sections": set(),
            "sentences": set()
        }

        if report:

            report_text = None
            row = self.db["rads_trauma_deid"].find_one( { "id": str(report) } )
            if (row):
                report_text = row["report"]

            # import pdb; pdb.set_trace()

            if report_text:
                    find_all = re.finditer(re.escape(text), report_text)
                    
                    for match in find_all:

                        pos = match.span()

                        for sent in self.db["sentences"].find( { "report_id": str(report) }, \
                            {"sentence_id":1, "section_id": 1, "start": 1, "end": 1} ):
                            
                            # print sentence["start"], sentence["end"]

                            #Sentence is inside big annotation
                            if(pos[0] <= sent["start"] and 
                                pos[1] >= sent["end"]):
                                ret["sections"].add(sent["section_id"])
                                ret["sentences"].add(sent["sentence_id"])
                                continue

                            #Annotation starts in the middle
                            if(pos[0] >= sent["start"] and pos[0] < sent["end"] and
                               pos[1] >= sent["end"]):
                                ret["sections"].add(sent["section_id"])
                                ret["sentences"].add(sent["sentence_id"])
                                continue

                            #Annotation is contained in sentence
                            if(pos[0] >= sent["start"] and 
                               pos[1] < sent["end"]): 
                                ret["sections"].add(sent["section_id"])
                                ret["sentences"].add(sent["sentence_id"])
                                continue

                            #Annotation ends in the middle
                            if(pos[0] < sent["start"] and
                               pos[1] >= sent["start"] and pos[1] < sent["end"]):
                                ret["sections"].add(sent["section_id"])
                                ret["sentences"].add(sent["sentence_id"])
                                continue

                        # for row in self.db["sentences"].find( { "report_id": str(report) }, \
                        #     {"sentence_id":1, "start": 1, "end": 1} ):
                        #     print row["start"], row["end"]

                        #     #search for start and end
        

        if len(ret["sections"]) == 0:
            logEvent("getPredictionsByEncounter", "Feedback not found in any section - " + text, level=40)

        if len(ret["sentences"]) == 0:
            logEvent("getPredictionsByEncounter", "Feedback not found in any sentence - " + text, level=40)

        return ret


    def _add_feedback(self, feedback):

        feedback['model'] = self.version
        feedback['user'] = USER
        feedback["level"] += "s"

        # import pdb; pdb.set_trace()
        # print feedback
        
        update_obj = {
            "$set":{
                 "class": feedback["class"],
                 "model": self.version,
            }
        }

        if ("text" in feedback):
            update_obj["$push"] = {
                'rationale_list': feedback["text"]
            }

        
        #Propagate high-level negative feedback
        #All positive feedbacks are handled by the UI

        if (feedback["class"] == 0):

            # import pdb; pdb.set_trace();

            try:
                index = self.levels.index(feedback["level"][:-1])

                while (index < len(self.levels)):

                    level = self.levels[index]

                    self.db[level+"s"].update_many({ 
                        feedback["level"][:-1]+'_id': feedback["id"]
                    }, update_obj)

                    index += 1
            except:
                logEvent("getPredictionsByEncounter", "Unable to process feedback: " + str(feedback), level=40)
        else:
            self.db[feedback["level"]].update_one({ 
                        feedback["level"][:-1]+'_id': feedback["id"]
                    }, update_obj)


        # return self.db["feedbacks"].find_one_and_update( {
        #             "level": feedback["level"],
        #             "id": feedback["id"],
        #             "model": feedback["model"]
        #         },
        #         {"$set": feedback}, upsert=True)


    def _set_neg_feedback(self, encounter_id):
        update_obj = {
            "$set":{
                "class": 0,
                "model": self.version
            }
        }

        # ["encounter", "report", "section", "sentence"]
        for level in self.levels:
            self.db[level+"s"].update_many({ 
                    "encounter_id": encounter_id
                    }, update_obj)


    def _add_pos_feedback(self, pos_id, level):
        update_obj = {
            "$set":{
                "class": 1,
                "model": self.version
            }
        }
        

        self.db[level+"s"].update_one({ 
            level+"_id": pos_id
        }, update_obj)


    def _retrain(self):

        for level in ["reports", "sections", "sentences"]:

            texts_ = []
            classes_ = []
            rationales_ = []
            
            for row in self.db[level].find({"class":{"$ne":None}}):
                texts_.append(row['text'])
                classes_.append(row['class'])

                #add rationales for sentences
                if (level == "sentences" and "rationale_list" in row):
                    for rationale in row['rationale_list']:
                        texts_.append(rationale)
                        classes_.append(row['class'])

                
            count_vect = CountVectorizer()
            tfidf_transformer = TfidfTransformer()
            
            classifier = LinearSVC(penalty="l2", dual=False, tol=1e-3)
            # classifier = CalibratedClassifierCV(classifier)
            
            X_train_counts = count_vect.fit_transform(texts_)
            X_train_tfidf = tfidf_transformer.fit_transform(X_train_counts)
            
            classifier.fit(X_train_tfidf, classes_)
            
            #Save models to file

            path =self.path_prefix + level + "_" + str(self.version) + ".classifier" 
            if os.path.exists(path):
                print path + "  already exists!"
                os.remove(path)
            dump(classifier, path)
            self.classifier[level] = classifier
            
            path =self.path_prefix + level + "_" + str(self.version) + ".count_vect" 
            if os.path.exists(path):
                print path + "  already exists!"
                os.remove(path)
            dump(count_vect, path)        
            self.count_vect[level] = count_vect
            
            path =self.path_prefix + level + "_" + str(self.version) + ".tfidf_transformer" 
            if os.path.exists(path):
                print path + "  already exists!"
                os.remove(path)
            dump(tfidf_transformer, path)
            self.tfidf_transformer[level] = tfidf_transformer
            


class GetPredictionsControl(GetPredictionsBase):

    def __init__(self, database):
        self.condition = "control"
        self.condition_version = "0"

        self.db = database
        self.path_prefix = CONDITIONS["control"]["path_prefix"]

        print self.condition, self.path_prefix

        self.levels = ["encounter", "report", "section", "sentence"]

        self.classifier = {}
        self.count_vect = {}
        self.tfidf_transformer = {}

        try:
            self.version = load(self.path_prefix + "version")
        except:
            self.version = 0

        # print os.getcwd()

        for level in ["report", "section", "sentence"]:

            path = self.path_prefix + level + "s_" + str(self.version) + ".classifier" 
            self.classifier[level] = load(path)       
        
            path = self.path_prefix + level + "s_" + str(self.version) + ".count_vect" 
            self.count_vect[level] = load(path)        
        
            path = self.path_prefix + level + "s_" + str(self.version) + ".tfidf_transformer" 
            self.tfidf_transformer[level] = load(path)    
        
    
    def _predict_one(self, level, row):

        # import pdb; pdb.set_trace();

        if (class_var in row):
            return row[class_var] #Force user feedback
        else:     
            return 0 #No predictions
            

class GetPredictionsIntervention(GetPredictionsBase):

    def __init__(self, database):
        
        self.condition = "intervention"
        self.condition_version = "1"

        self.db = database
        self.path_prefix = CONDITIONS["intervention"]["path_prefix"]

        print self.condition, self.path_prefix

        self.levels = ["encounter", "report", "section", "sentence"]

        self.classifier = {}
        self.count_vect = {}
        self.tfidf_transformer = {}

        try:
            self.version = load(self.path_prefix + "version")
        except:
            self.version = 0

        # print os.getcwd()

        for level in ["report", "section", "sentence"]:

            path = self.path_prefix + level + "s_" + str(self.version) + ".classifier" 
            self.classifier[level] = load(path)       
        
            path = self.path_prefix + level + "s_" + str(self.version) + ".count_vect" 
            self.count_vect[level] = load(path)        
        
            path = self.path_prefix + level + "s_" + str(self.version) + ".tfidf_transformer" 
            self.tfidf_transformer[level] = load(path)    
        
    
    def _predict_one(self, level, row):

        if (class_var in row):
            return row[class_var] #Force user feedback
        else:
            texts = [row["text"]]

            X_test_counts = self.count_vect[level].transform(texts)
            X_test_tfidf = self.tfidf_transformer[level].transform(X_test_counts)
            y_pred = self.classifier[level].predict(X_test_tfidf)

            return y_pred[0]

