# lemr-nlp-server

## Getting Started

To get started, get the lemr-nlp-server code, install the pre-requisites, and then launch the server as described below:

### Prerequisites

Install the Python modules required by this project. You may also do this within a virtualenv:

    pip install -r requirements.txt


### Running the server
  
    gunicorn --reload server.app
    
`--reload` option restarts the server automatically if you make any changes.
