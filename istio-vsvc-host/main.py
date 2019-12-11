import json

from flask import Flask, jsonify, request
from kubernetes import client, config


app = Flask(__name__)

VALIDATION_OK_MSG = 'Validation succeeded'
VALIDATION_ERROR_MSG = 'FOO collides with existing host settings'

# config.load_incluster_config()
config.load_kube_config()
conf=client.Configuration()
api_client=client.ApiClient(configuration=conf)

@app.route('/validate', methods=['POST'])
def validate():
    try:
        req = request.get_json()
        hosts = req['request']['object']['spec']['hosts']
        print(hosts)
        apiserver_resp = api_client.call_api(
                '/apis/networking.istio.io/v1alpha3/virtualservices','GET',
                auth_settings=['BearerToken'],
                response_type='object',
        )
        nested_existing_host_list = [
            item['spec']['hosts'] for item in apiserver_resp[0]['items']
        ]
        flat_existing_host_list = [item for sublist in nested_existing_host_list for item in sublist]
        print(flat_existing_host_list)
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
