UI_PORT = "8000"

MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017
DATABASE_NAME = 'lemr-study'

CONDITIONS = {
    "control": {"path_prefix": "models/intervention/", "db": "lemr-control"},
    "intervention": {"path_prefix": "models/control/", "db": DATABASE_NAME}
}
