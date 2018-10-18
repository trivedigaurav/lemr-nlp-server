import json
import falcon

class GetReportById(object):

    def __init__(self, database):
        self.db = database

    def on_get(self, req, resp, report_id):
        report = None
        
        if report_id != None:

            row = self.db.rads_trauma_deid.find_one( { "id": str(report_id) } )

            if (row):
                text = row["report"]
            else:
                text = ""

            message = {
                'reportText': text
            }

            resp.body = json.dumps(message, ensure_ascii=False)

            resp.status = falcon.HTTP_200