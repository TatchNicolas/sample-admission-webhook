import requests
from kubernetes import client, config


config.load_incluster_config()
v1 = client.CoreV1Api()
ret = v1.list_namespaced_pod('default')
print([pod.metadata.name for pod in ret.items])

api_client=client.ApiClient()
host = api_client.configuration.host
token = ''

requests.get('https://10.96.0.1:443/api/v1/namespaces/default/pods', verify=False, headers={'Authorization': 'Bearer '+ token})

conf=client.Configuration()
api_client=client.ApiClient(configuration=conf)
api_client.call_api('/api/v1/namespaces/default/pods','GET',auth_settings=['BearerToken'])
