import json

from flask import Flask, jsonify, request


app = Flask(__name__)

VALIDATION_OK_MSG = 'Validation succeeded'
VALIDATION_ERROR_MSG = 'FOO collides with existing host settings'

@app.route('/validate', methods=['POST'])
def validate():
    try:
        req = request.get_json()
        return jsonify({
              'apiVersion': 'admission.k8s.io/v1',
              'kind': 'AdmissionReview',
              'response': {
                'uid': request.get_json()['request']['uid'],
                'allowed': True,
                'status': {'message': json.dumps(req)}
                }
        }), 200
    except (TypeError, KeyError):
        return jsonify({'message': 'Invalid request'}), 400
