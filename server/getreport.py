import json
import falcon
# import mysql.connector

# cnx = mysql.connector.connect(user='lemr', password='Lx16022!HKCQ', database='PSO')
# cursor = cnx.cursor()

class GetReportById(object):

    def __init__(self, database):
        self.collection = database.reports

    def on_get(self, req, resp, report_id):
        report = None
        
        if report_id != None:

            row = self.collection.Reports.find_one( { "id": str(report_id) } )
            # cursor.execute("SELECT * FROM PSO.reports WHERE id='"+ report_id + "' LIMIT 1")
            # for (text) in cursor:
            #     report = text[4]

            if (row):
                text = row["report"]
            else:
                text = ""

            message = {
                'reportText': text
            }

            resp.body = json.dumps(message, ensure_ascii=False)

            resp.status = falcon.HTTP_200