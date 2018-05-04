import falcon
from falcon_cors import CORS

import pymongo
from pymongo import MongoClient

from .login import Login
from .getreport import *
from .annotator import *
from .getencounter import *
from .putlogevent import *

from .settings import *

#settings
client = MongoClient(MONGODB_HOST, MONGODB_PORT)
database = client[DATABASE_NAME]

cors = CORS(allow_origins_list=['http://localhost:'+UI_PORT],
            allow_all_headers=True,
            allow_all_methods=True)

application = falcon.API(middleware=[cors.middleware])

#api
login = Login()
application.add_route('/login', login)

putLogEvent = PutLogEvent()
application.add_route('/logEvent/{event_name}', putLogEvent)

getReport = GetReportById(database)
application.add_route('/getReport/{report_id}', getReport)

getEncounter = GetReportsByEncounter(database)
application.add_route('/getEncounter/{encounterid}', getEncounter)

annotator = Annotator(database)
application.add_route('/annotator/{event}/{uid}', annotator)