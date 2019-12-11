from flask import Flask, jsonify, request
from kubernetes import client, config


app = Flask(__name__)

# config.load_incluster_config()
config.load_kube_config()
conf=client.Configuration()
api_client=client.ApiClient(configuration=conf)

@app.route('/validate', methods=['POST'])
def validate():
    try:
        # リクエストから必要な情報を抜き出す
        req = request.get_json()
        new_hosts = req['request']['object']['spec']['hosts']
        apiserver_resp = api_client.call_api(
                '/apis/networking.istio.io/v1alpha3/virtualservices','GET',
                auth_settings=['BearerToken'],
                response_type='object',
        )
        nested_existing_hosts = {
            tuple(item['spec']['hosts']) for item in apiserver_resp[0]['items']
        }
        existing_hosts = {item for sublist in nested_existing_hosts for item in sublist}

        print(f'existing_hosts: {existing_hosts}')
        print(f'new_hosts: {new_hosts}')

        # UPDATEのときは、oldに入っているものは検査対象から除外する
        operation = req['request']['operation']
        if operation == 'UPDATE':
            old_hosts = req['request']['oldObject']['spec']['hosts']
            for host in old_hosts:
                existing_hosts.remove(host)
            print(f'updated existing_hosts: {existing_hosts}')

        # hostsの被りがないかチェックする
        pair = has_collision(new_hosts, existing_hosts)

        if pair:
            allowed = False
            message = f'{pair[0]} collides with {pair[1]}'
        else:
            allowed = True
            message = f'No collision detected'


        # 結果を返す
        return jsonify({
            'apiVersion': 'admission.k8s.io/v1',
            'kind': 'AdmissionReview',
            'response': {
                'uid': request.get_json()['request']['uid'],
                'allowed': allowed,
                'status': {'message': message}
            }
        }), 200

    except (TypeError, KeyError):
        return jsonify({'message': 'Invalid request'}), 400

def has_collision(new_hosts, existing_hosts):
    for new_host in new_hosts:
        for existing_host in existing_hosts:
            if new_host == existing_host:
                return (new_host, existing_host)
