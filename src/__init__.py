import os
import json
from pathlib import Path

ENV = os.environ['ENVIRONMENT']
if ENV == 'DEVELOPMENT':
    # loads environment variables for development
    from dotenv import load_dotenv
    load_dotenv()

# Loads the json data into a dictionary
# only loads when in PRODUCTION environment
data = {}
file_path = Path(__file__).parent.parent.absolute()

if ENV!='TESTING':
    with open(file_path / 'data/text.json', 'r') as f:
        data = json.load(f)

user_ids: dict = {
    'sarvesh': int(os.environ['sarvesh_id']), 'potter': int(os.environ['potter_id']),
    'kataria': int(os.environ['kataria_id']), 'vroon': int(os.environ['vroon_id']),
    'tanay': int(os.environ['tanay_id']), 'ishiboi': int(os.environ['ishiboi_id']),
    'modi': int(os.environ['modi_id']), 'shashwat': int(os.environ['shashwat_id']),
    'tushar': int(os.environ['tushar_id'])
}


from .utils import Utils
from .message import Message
