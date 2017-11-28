import json
import falcon
from .logger import logEvent
from bson.objectid import ObjectId

current_userid = "test"

class Annotator(object):

    def __init__(self, database):
        self.collection = database.annotations

    #read
    def on_get(self, req, resp, event, uid):

        if (event != "read"):
            resp.status = falcon.HTTP_405
        else:

            annotations = self.collection.Annotation.find({
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

            logEvent(event, str(message))

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
                'annotation': annotation
            }

            p = self.collection.Annotation.find_and_modify(
                query=record, update={"$set": record}, new=True, upsert=True)

            j = json.loads(annotation)
            j["id"] = str(p["_id"])

            logEvent(event, str(j))

            resp.body = json.dumps(j, ensure_ascii=False)
            resp.status = falcon.HTTP_200

    #update
    def on_put(self, req, resp, event, uid):
        if (event != "update"):
            resp.status = falcon.HTTP_405
        else:

            updated_annotation = unicode(req.stream.read(), 'utf-8')

            row = self.collection.Annotation.find_one(ObjectId(str(uid)))
            row['annotation'] = updated_annotation
            row.save()

            message = {
                'event': event,
                'annotationId': uid,
                'annotation': updated_annotation
            }

            logEvent(event, str(message))

            resp.body = json.dumps({"id": uid})
            resp.status = falcon.HTTP_200

    #destroy
    def on_delete(self, req, resp, event, uid):
        if (event != "destroy"):
            resp.status = falcon.HTTP_405
        else:
            row = self.collection.Annotation.find_one(ObjectId(str(uid)))
            if(row):
                row.delete()

            message = {
                'event': event,
                'annotationId': uid,
            }

            logEvent(event, str(message))

            resp.body = ""
            resp.status = falcon.HTTP_204 