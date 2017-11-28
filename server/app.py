import falcon
from falcon_cors import CORS
from .test import Resource
from .login import Login
from .getreport import *
from .logger import *
from .annotator import *

from .database import *

# For developement only
# disable Cross-Origin Resource Sharing (CORS) in prod
cors = CORS(allow_origins_list=['http://localhost:8000'],
            allow_all_headers=True,
            allow_all_methods=True)
api = application = falcon.API(middleware=[cors.middleware])

test = Resource()
api.add_route('/test', test)

login = Login()
api.add_route('/login', login)

getReport = GetReportById()
api.add_route('/getReport/{report_id}', getReport)

putLogEvent = PutLogEvent()
api.add_route('/logEvent/{event_name}', putLogEvent)

annotator = Annotator(database)
api.add_route('/annotator/{event}/{uid}', annotator)