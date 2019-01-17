import json
import falcon
from .logger import logEvent
from ast import literal_eval
from collections import defaultdict
import re

from sklearn.externals.joblib import dump, load
import os

###NOTE: MongoDB should have indices built, otherwise this can be really slow
##TODO: Use actual predictions and not gold standards 
class_var = "class"
PATH_PREFIX = "models/"

class SetEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return json.JSONEncoder.default(self, obj)

class GetPredictions(object):

    def __init__(self, database):
        self.db = database

        model = 0

        self.levels = ["encounter", "report", "section", "sentence"]

        self.classifier = {}
        self.count_vect = {}
        self.tfidf_transformer = {}

        # print os.getcwd()

        for level in self.levels:

            path = PATH_PREFIX + level + "s_" + str(model) + ".model" 
            self.classifier[level] = load(path)       
        
            path = PATH_PREFIX + level + "s_" + str(model) + ".count_vect" 
            self.count_vect[level] = load(path)        
        
            path = PATH_PREFIX + level + "s_" + str(model) + ".tfidf_transformer" 
            self.tfidf_transformer[level] = load(path)    
        
    def predict_one(self, level, row):

        if (class_var in row):
            return row[class_var]
        else:
            texts = [row["text"]]

            X_test_counts = self.count_vect[level].transform(texts)
            X_test_tfidf = self.tfidf_transformer[level].transform(X_test_counts)
            y_pred = self.classifier[level].predict(X_test_tfidf)

            return y_pred[0]

    def on_get(self, req, resp, encounterid, modelid="current"):

        def _clean_row(level, row):
            row["_id"] = str(row["_id"])
            row['rationales'] = literal_eval(row['rationales'])
            row['class'] = self.predict_one(level, row)

            return row

        #TODO: Handle model revisions

        if encounterid != None:

            enc = self.db.encounters.find_one( { "encounter_id": str(encounterid) })

            if (enc):

                message = {
                    "class": self.predict_one("encounter", enc),
                    "rationales": literal_eval(enc['rationales']),
                
                    "reports": defaultdict(list),
                    "sections": defaultdict(list),
                    "sentences": defaultdict(list),

                    "pos_reports": set(),
                    "pos_sections": set(),
                    "pos_sentences": set()
                }


                #Reports
                for row in self.db["reports"].find( { "encounter_id": str(encounterid) } ) \
                            .sort([("date",1)]):
                    row_ = _clean_row("report", row)
                    id_ = row_["report_id"]

                    message["reports"][id_] = row_
                    message["reports"][id_]["pos_sections"] = set()
                    message["reports"][id_]["pos_sentences"] = set()
                    message["reports"][id_]["sections"] = []
                    message["reports"][id_]["sentences"] = []

                    if(row_["class"] == 1):
                        message["pos_reports"].add(id_)
                        message["class"] = 1


                #Sections
                for row in self.db["sections"].find( { "encounter_id": str(encounterid) } ) \
                            .sort([("start",1)]):
                    row_ = _clean_row("section", row)
                    id_ = row_["section_id"]

                    message["sections"][id_] = row_
                    message["sections"][id_]["pos_sentences"] = set()
                    message["sections"][id_]["sentences"] = []


                    if(row_["class"] == 1):
                        message["pos_sections"].add(id_)
                        message["reports"][row_["report_id"]]["pos_sections"].add(id_)

                        message["reports"][row_["report_id"]]["class"] = 1
                        message["pos_reports"].add(row_["report_id"])
                        message["class"] = 1

                    message["reports"][row_["report_id"]]["sections"].append(id_)


                #Sentences
                for row in self.db["sentences"].find( { "encounter_id": str(encounterid) } ) \
                            .sort([("start",1)]):
                    row_ = _clean_row("sentence", row)
                    id_ = row_["sentence_id"]

                    message["sentences"][id_] = row_

                    if(row_["class"] == 1):
                        message["pos_sentences"].add(id_)
                        message["reports"][row_["report_id"]]["pos_sentences"].add(id_)
                        message["sections"][row_["section_id"]]["pos_sentences"].add(id_)

                        message["reports"][row_["report_id"]]["class"] = 1
                        message["pos_reports"].add(row_["report_id"])

                        message["sections"][row_["section_id"]]["class"] = 1
                        message["pos_sections"].add(row_["section_id"])

                        message["class"] = 1


                    message["reports"][row_["report_id"]]["sentences"].append(id_)
                    message["sections"][row_["section_id"]]["sentences"].append(id_)                    


                logEvent("getPredictionsByEncounter", str(message), level=10) #DEBUG=10
                
                # print message

                resp.body = json.dumps(message, ensure_ascii=False, cls=SetEncoder)
                resp.status = falcon.HTTP_200

            else:
                logEvent("getPredictionsByEncounter", '{"encounterid": encounterid}', level=40)


    def find_text(self, text, report):
        
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
        return ret


    def on_put(self, req, resp, modelid, override):
       feedbackList = json.loads(req.stream.read(), 'utf-8')
       
       print feedbackList

       levels = ["encounter", "report", "section", "sentence", "text"]

       for feedback in feedbackList:
            for level in levels:
                if feedback[level]:
                    if level == "text":
                        print
                        print level, feedback[level]["id"], "report=", feedback["report"].id, "enc=", feedback["encounter"].id
                        print self.find_text(text=feedback[level]["id"], report=feedback["report"])
                        print
                    else:
                        print level, feedback[level]["id"], feedback[level]["class"]



       resp.body = json.dumps({"status": "OK"}, ensure_ascii=False)
       resp.status = falcon.HTTP_200

