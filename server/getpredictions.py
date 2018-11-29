import json
import falcon
from .logger import logEvent

class GetPredictions(object):

    def __init__(self, database):
        self.db = database

    def on_get(self, req, resp, encounterid, modelid="current"):
        
        #TODO: Handle models
        ##TODO: Use actual predictions and not gold standards 


        if encounterid != None:

            row = self.db.encounters.find_one( { "enc_id": str(encounterid) })

            if (row):

                message = {
                    "class": row['gold_label'],
                    "rationales": row['rationales']
                }


                levels = ["reports", "sections", "sentences"]

                for level in levels:
                    l_list = []

                    for row in self.db[level].find( { "enc_id": str(encounterid) }, {"text": 0} ).sort([("date",1)]):
                        row.pop("_id")
                        l_list.append(row)

                    message[level] = l_list


                logEvent("getPredictionsByEncounter", str(message))
                
                resp.body = json.dumps(message, ensure_ascii=False)
                resp.status = falcon.HTTP_200

            else:
                logEvent("getPredictionsByEncounter", '{"encounterid": encounterid}', level=40)