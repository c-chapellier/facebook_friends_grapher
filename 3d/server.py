
import json
import sys

import community_detection
import gexf_to_json
from flask import Flask, jsonify, render_template
from flask_cors import CORS, cross_origin

app = Flask(__name__, template_folder='templates')


cors = CORS(app, resources={r'/foo': {'origins': '*'}})
app.config['CORS_HEADERS'] = 'Content-Type'


@app.route('/')
@cross_origin(origins='*',expose_headers=['Content-Type','Authorization'])
def index():
    return render_template('index.html')


@app.route('/all_data', methods=['POST', 'OPTIONS'])
@cross_origin(origins='*',expose_headers=['Content-Type','Authorization'])
def get_data():
    try:
        graph = gexf_to_json.gexf_to_json(sys.argv[1])
        graph = community_detection.community_detection(graph)
        with open('data.json', 'w') as f:
            f.write(json.dumps(graph))
        return jsonify(graph)
    
    except Exception as ex:
        print('Error:', ex)
        return jsonify({ 'Message' : str(ex) })


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f'format: python {sys.argv[0]} <gexf_file>')
        exit(1)
    app.run(port=5000)
