import json
import falcon
from .logger import logEvent
from ast import literal_eval
from collections import defaultdict


###NOTE: MongoDB should have indices built, otherwise this can be really slow
##TODO: Use actual predictions and not gold standards 
class_var = "gold_label"

class GetPredictions(object):

    def __init__(self, database):
        self.db = database

    def on_get(self, req, resp, encounterid, modelid="current"):
        
        def _run_query(level, encounterid):
            return self.db[level].find( { "encounter_id": str(encounterid) }, {"text": 0} ) \
                            .sort([("date",1)])

        def _clean_row(row):
            row["_id"] = str(row["_id"])
            row['rationales'] = literal_eval(row['rationales'])
            row['class'] = row[class_var]

            return row

        #TODO: Handle model revisions

        if encounterid != None:

            enc = self.db.encounters.find_one( { "encounter_id": str(encounterid) })

            if (enc):

                message = {
                    "class": enc[class_var],
                    "rationales": literal_eval(enc['rationales']),
                
                    "reports": defaultdict(list),
                    "sections": defaultdict(list),
                    "sentences": defaultdict(list),

                    "pos_reports": [],
                    "pos_sections": [],
                    "pos_sentences": []
                }


                #Reports
                for row in _run_query("reports", encounterid):
                    row_ = _clean_row(row)
                    id_ = row_["report_id"]

                    message["reports"][id_] = row_
                    message["reports"][id_]["pos_sections"] = []
                    message["reports"][id_]["pos_sentences"] = []

                    if(row_["class"] == "pos"):
                        message["pos_reports"].append(id_)

                #Sections
                for row in _run_query("sections", encounterid):
                    row_ = _clean_row(row)
                    id_ = row_["section_id"]

                    message["sections"][id_] = row_
                    message["sections"][id_]["pos_sentences"] = []

                    if(row_["class"] == "pos"):
                        message["pos_sections"].append(id_)
                        message["reports"][row_["report_id"]]["pos_sections"].append(id_)


                #Sentences
                for row in _run_query("sentences", encounterid):
                    row_ = _clean_row(row)
                    id_ = row_["sentence_id"]

                    message["sentences"][id_] = row_

                    if(row_["class"] == "pos"):
                        message["pos_sentences"].append(id_)
                        message["reports"][row_["report_id"]]["pos_sentences"].append(id_)
                        message["sections"][row_["section_id"]]["pos_sentences"].append(id_)


                logEvent("getPredictionsByEncounter", str(message))
                
                resp.body = json.dumps(message, ensure_ascii=False)
                resp.status = falcon.HTTP_200

            else:
                logEvent("getPredictionsByEncounter", '{"encounterid": encounterid}', level=40)