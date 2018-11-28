import json
import falcon
from .logger import logEvent

# from .admitdate_map import *
# from .discharge_map import *
from .incidental_map import *

with open('server/admitdate_map.json', 'r') as fp:
    admitdate_map = json.load(fp)

with open('server/discharge_map.json', 'r') as fp:
    discharge_map = json.load(fp)

# cnx = mysql.connector.connect(user='lemr', password='Lx16022!HKCQ', database='PSO')
# cursor = cnx.cursor()

class GetReportsByEncounter(object):

    def __init__(self, database):
        self.db = database
        # self.database = database

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


            # cursor.execute("SELECT * FROM PSO.reports WHERE encounterid=" + encounterid + 
            #        " AND type='RAD' AND date>=" + str(admit) +
            #        " AND date<=" + str(discharge) +
            #        " ORDER BY date ASC")
    
            # cursor.execute("SELECT * FROM PSO.rads_incidentals WHERE encounterid=" + encounterid + 
            #     " ORDER BY date ASC")

            # rows = cursor.fetchall()

            # for (text) in rows:
                # row = {
                #     "id": text[0],
                #     "encounterid": text[1],
                #     "date": text[2],
                #     "type": text[3],
                #     "text": text[4],
                # }

                # reports.append(row)


            # print 'db.rads_trauma_deid.find( { "encounterid":'+ str(encounterid) + ' } ).sort([("date",1)])'
            
            for row in self.db.rads_trauma_deid.find( { "encounterid": str(encounterid) } ).sort([("date",1)]):
                row["_id"] = str(row["_id"])
                row["text"] = row.pop("report")
                reports.append(row)
 
        message = {}
        message['reports'] = reports
        message['incidental'] = str(incidental)
        message['admit'] = admit
        message['discharge'] = discharge

        logEvent("getEncounter", str(message))
        
        resp.body = json.dumps(message, ensure_ascii=False)
        resp.status = falcon.HTTP_200