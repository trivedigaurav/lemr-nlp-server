# lemr-nlp-server

## Getting Started

To get started, get the lemr-nlp-server code, install the pre-requisites, and then launch the server as described below:

### Prerequisites

Install the Python modules required by this project. You may also do this within a virtualenv:

    pip install -r requirements.txt


### Running the server
  
  You can run the above example using any WSGI server, such as uWSGI or Gunicorn. For example:
    
    pip install gunicorn
    gunicorn --reload -b 127.0.0.1:10000 server.app --reload-extra-file models/control/sentences_0.classifier --reload-extra-file models/intervention/sentences_0.classifier

On Windows where Gunicorn and uWSGI don’t work yet you can use Waitress server

    pip install waitress
    waitress-serve --port=10000 server.app
    
### Running tests
     
    pytest tests/


