import json
import falcon
import mysql.connector

from .admitdate_map import *
from .discharge_map import *
from .incidental_map import *

cnx = mysql.connector.connect(user='lemr', password='Lx16022!HKCQ', database='PSO')
cursor = cnx.cursor()

class GetReportsByEncounter(object):

    def on_get(self, req, resp, encounterid):
        reports = []

        if encounterid != None:

            if encounterid in admitdate_map:
                admit = admitdate_map[encounterid]
            else:
                admit = 0
                
            if encounterid in discharge_map:
                discharge = discharge_map[encounterid]
            else:
                discharge = -1

            if encounterid in incidental_map:
                incidental = incidental_map[encounterid]
            else:
                incidental = None


            print "SELECT * FROM PSO.reports WHERE encounterid=" + encounterid + \
                   " AND type='RAD' AND date>=" + str(admit) + \
                   " AND date<=" + str(discharge) + \
                   " ORDER BY date ASC"

            cursor.execute("SELECT * FROM PSO.reports WHERE encounterid=" + encounterid + 
                   " AND type='RAD' AND date>=" + str(admit) +
                   " AND date<=" + str(discharge) +
                   " ORDER BY date ASC")

            rows = cursor.fetchall()

            for (text) in rows:

                row = {
                    "id": text[0],
                    "encounterid": text[1],
                    "date": text[2],
                    "type": text[3],
                    "text": text[4],
                }

                reports.append(row)
 
        message = {}
        message['reports'] = reports
        message['incidental'] = str(incidental)
        message['admit'] = admit
        message['discharge'] = discharge

        resp.body = json.dumps(message, ensure_ascii=False)

        resp.status = falcon.HTTP_200