from mongokit import Connection, Document

MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017

#Begin database schema
class Annotation(Document):
    # __collection__ = 'annotations'
    # __database__ = 'lemr'
    structure = {
        'uid': unicode,         #annotation_id
        'report': basestring,   #reportid
        'annotation': unicode,
    }

connection = Connection(MONGODB_HOST, MONGODB_PORT)
connection.register([Annotation])
database = connection['lemr']