import json
import falcon
from .logger import logEvent
from ast import literal_eval
from collections import defaultdict

class GetPredictions(object):

    def __init__(self, database):
        self.db = database

    def on_get(self, req, resp, encounterid, modelid="current"):
        
        #TODO: Handle models
        ##TODO: Use actual predictions and not gold standards 


        if encounterid != None:

            row = self.db.encounters.find_one( { "encounter_id": str(encounterid) })

            if (row):

                message = {
                    "class": row['gold_label'],
                    "rationales": literal_eval(row['rationales'])
                }


                levels = ["reports", "sections", "sentences"]

                for level in levels:
                    l_list = defaultdict(list)

                    for row in self.db[level].find( { "encounter_id": str(encounterid) }, {"text": 0} ).sort([("date",1)]):
                        row["_id"] = str(row["_id"])
                        row['rationales'] = literal_eval(row['rationales'])

                        report_id = row.pop("report_id")
                        
                        l_list[report_id].append(row)
                        
                    message[level] = l_list


                logEvent("getPredictionsByEncounter", str(message))
                
                resp.body = json.dumps(message, ensure_ascii=False)
                resp.status = falcon.HTTP_200

            else:
                logEvent("getPredictionsByEncounter", '{"encounterid": encounterid}', level=40)