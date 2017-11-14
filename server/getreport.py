import json
import falcon
import mysql.connector

cnx = mysql.connector.connect(user='lemr', password='Lx16022!HKCQ', database='PSO')
cursor = cnx.cursor()

class GetReportById(object):

    def on_get(self, req, resp, report_id):
        report = None
        
        if report_id != None:
            cursor.execute("SELECT * FROM PSO.reports WHERE id='"+ report_id + "' LIMIT 1")


            for (text) in cursor:
                report = text[4]

            message = {
                'reportText': report
            }

            resp.body = json.dumps(message, ensure_ascii=False)

            resp.status = falcon.HTTP_200