import falcon
from falcon_cors import CORS

from .test import Resource
from .login import Login
from .getreport import *
from .annotator import *
from .getencounter import *
from .putlogevent import *

from .database import *
database = connection['lemr']

UI_PORT = "8000"

cors = CORS(allow_origins_list=['http://localhost:'+UI_PORT],
            allow_all_headers=True,
            allow_all_methods=True)

application = falcon.API(middleware=[cors.middleware])

test = Resource()
application.add_route('/test', test)

login = Login()
application.add_route('/login', login)

getReport = GetReportById(database)
application.add_route('/getReport/{report_id}', getReport)

putLogEvent = PutLogEvent()
application.add_route('/logEvent/{event_name}', putLogEvent)

annotator = Annotator(database)
application.add_route('/annotator/{event}/{uid}', annotator)

getEncounter = GetReportsByEncounter(database)
application.add_route('/getEncounter/{encounterid}', getEncounter)