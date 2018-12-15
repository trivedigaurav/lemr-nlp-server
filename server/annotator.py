# from __future__ import print_function
# import sys

import json
import falcon
from .logger import logEvent
from bson.objectid import ObjectId
from datetime import datetime
from pymongo.collection import ReturnDocument

current_userid = "pso"

class Annotator(object):

    def __init__(self, database):
        self.db= database

    #read
    def on_get(self, req, resp, event, uid):

        if (event != "read"):
            resp.status = falcon.HTTP_405
        else:

            annotations = self.db.annotations.find({
                'uid': current_userid,
                'report': uid
            })

            records = []
            for a in list(annotations):
                j = json.loads(a['annotation'])
                j["id"] = str(a['_id'])
                records.append(j)

            message = {
                'event': event,
                'reportId': uid,
                'records': str(records)
            }

            logEvent(event+"Annotation", str(message))

            resp.body = json.dumps(records, ensure_ascii=False)
            resp.status = falcon.HTTP_200

    #create
    def on_post(self, req, resp, event, uid):
        if (event != "create"):
            resp.status = falcon.HTTP_405
        else:

            annotation = unicode(req.stream.read(), 'utf-8')

            record = {
                'uid': current_userid,
                'report': uid,
                'annotation': annotation,
                'date': datetime.now()
            }

            #http://api.mongodb.com/python/current/api/pymongo/collection.html#pymongo.collection.Collection.find_one_and_update
            #upsert - returns the new object
            #return_document - creates a new object, if no match
            p = self.db.annotations.find_one_and_update(
                record, {'$set': record}, upsert=True, return_document=ReturnDocument.AFTER)

            # print('p: ' + str(p), file=sys.stderr)

            j = json.loads(annotation)
            j["id"] = str(p["_id"])

            logEvent(event+"Annotation", str(j))

            resp.body = json.dumps(j, ensure_ascii=False)
            resp.status = falcon.HTTP_200

    #update
    def on_put(self, req, resp, event, uid):
        if (event != "update"):
            resp.status = falcon.HTTP_405
        else:

            updated_annotation = unicode(req.stream.read(), 'utf-8')

            record = {
                "_id": ObjectId(str(uid))
            }

            row = self.db.annotations.find_one_and_update(
                record, { "$set": {"annotation": updated_annotation} })
            
            message = {
                'event': event,
                'annotationId': uid,
                'annotation': updated_annotation
            }

            logEvent(event+"Annotation", str(message))

            resp.body = json.dumps({"id": uid})
            resp.status = falcon.HTTP_200

    #destroy
    def on_delete(self, req, resp, event, uid):
        if (event != "destroy"):
            resp.status = falcon.HTTP_405
        else:
            row = self.db.annotations.delete_one({ "_id": ObjectId(str(uid)) })

            message = {
                'event': event,
                'annotationId': uid,
            }

            logEvent(event+"Annotation", str(message))

            resp.body = ""
            resp.status = falcon.HTTP_204 