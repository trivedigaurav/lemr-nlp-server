from mongokit import Connection, Document
import datetime

MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017

#Begin database schema
class Annotation(Document):
    # __collection__ = 'annotations'
    # __database__ = 'lemr'
    structure = {
        'uid': unicode,         #annotator_user_id
        'report': basestring,   #reportid
        'annotation': unicode,
        'date': datetime.datetime
    }

# class Reports(Document):
#     # __collection__ = 'reports'
#     # __database__ = 'lemr'
#     structure = {
#         "id": int,
#         "encounterid": int,
#         "date": int,
#         "type": basestring,
#         "report": basestring
#     }

# class Rads_Incidentals(Document):
#     # __collection__ = 'rads_incidentals'
#     # __database__ = 'lemr'
#     structure = {
#         "id": int,
#         "encounterid": int,
#         "date": int,
#         "type": basestring,
#         "report": basestring
#     }

class Rads_Trauma_Clean(Document):
    # __collection__ = 'rads_trauma_clean'
    # __database__ = 'lemr'
    structure = {
        "id": int,
        "encounterid": int,
        "date": int,
        "type": basestring,
        "report": basestring
    }

class Signouts(Document):
    # __collection__ = 'signouts'
    # __database__ = 'lemr'
    structure = {
        "reportid": int,
        "admitdate": datetime.datetime,
        "createdtimestamp": datetime.datetime,
        "createdtimestamp1": datetime.datetime,
        "createdtimestamp2": datetime.datetime,
        "createdtimestamp3": datetime.datetime,
        "createdtimestamp4": datetime.datetime,
        "createdtimestamp5": datetime.datetime,
        "createdtimestamp6": datetime.datetime,
        "createdtimestamp7": datetime.datetime,
        "encounterid": int,
        "organization": int,
        "serviceid": int,
        "text": basestring,
        "text1": basestring,
        "text2": basestring,
        "text3": basestring,
        "text4": basestring,
        "text5": basestring,
        "text6": basestring
    }

connection = Connection(MONGODB_HOST, MONGODB_PORT)
connection.register([Annotation, Rads_Trauma_Clean, Signouts])