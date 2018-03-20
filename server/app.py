import falcon
from falcon_cors import CORS
from falcon_auth import FalconAuthMiddleware, BasicAuthBackend

from .test import Resource
from .login import Login
from .getreport import *
from .logger import *
from .annotator import *
from .getencounter import *

from .database import *
database = connection['lemr']

# For dev use only
# disable Cross-Origin Resource Sharing (CORS) in prod
cors = CORS(allow_origins_list=['http://localhost:8000'],
            allow_all_headers=True,
            allow_all_methods=True)

#falcon-auth
user_loader = lambda username, password: { 'username': username }
auth_middleware = FalconAuthMiddleware(BasicAuthBackend(user_loader))

application = falcon.API(middleware=[cors.middleware, auth_middleware])

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