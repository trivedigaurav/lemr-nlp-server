import json
import falcon

class GetReportById(object):

    def __init__(self, database):
        self.db = database

    def on_get(self, req, resp, reportid):
        report = None
        
        if reportid != None:

            row = self.db.rads_trauma_deid.find_one( { "id": str(reportid) } )

            if (row):
                text = row["report"]
            else:
                text = ""
                logEvent("getReport", '{"reportid": reportid}', level=40)

            message = {
                'reportText': text
            }

            logEvent("getReport", str(message))

            resp.body = json.dumps(message, ensure_ascii=False)
            resp.status = falcon.HTTP_200