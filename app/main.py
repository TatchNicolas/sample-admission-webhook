import base64
import json

from flask import Flask, jsonify, request

app = Flask(__name__)

VALIDATION_OK_MSG = 'Validation succeeded'
VALIDATION_ERROR_MSG = 'Required label env is not set or its value is invalid'

@app.route('/validate', methods=['POST'])
def validate():
    try:
        req = request.get_json()
        env = req['request']['object']['metadata'].get('labels',{}).get('env')
        # env ラベルが dev,stg,prd のいずれかであることをチェック
        if env in ('dev', 'stg', 'prd'):
            is_valid = True
            message = VALIDATION_ERROR_MSG
        else:
            is_valid = False
            message = VALIDATION_ERROR_MSG
        return jsonify({
              'apiVersion': 'admission.k8s.io/v1',
              'kind': 'AdmissionReview',
              'response': {
                'uid': request.get_json()['request']['uid'],
                'allowed': is_valid,
                'status': {'message': message}
                }
        }), 200
    except (TypeError, KeyError):
        return jsonify({'message': 'Invalid request'}), 400

@app.route('/mutate', methods=['POST'])
def mutate():
    try:
        req = request.get_json()
        name = req['request']['object']['metadata']['name']
        operation = [{
            'op': 'replace',
            'path': '/metadata/name',
            'value': 'dummy-suffix-' + name
        }]
        patch = base64.b64encode(json.dumps(operation).encode()).decode()
        return jsonify({
              'apiVersion': 'admission.k8s.io/v1',
              'kind': 'AdmissionReview',
              "response": {
                "uid": request.get_json()['request']['uid'],
                "allowed": True,
                "patchType": 'JSONPatch',
                "patch": patch,
              }
        }), 200
    except (TypeError, KeyError):
        return jsonify({'message': 'Invalid request'}), 400
