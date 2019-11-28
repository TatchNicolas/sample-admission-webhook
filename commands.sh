cat <<EOF | cfssl genkey - | cfssljson -bare server
{
  "hosts": [
    "sample-admission-webhook.default.svc"
  ],
  "CN": "sample-admission-webhook.default.svc",
  "key": {
    "algo": "ecdsa",
    "size": 256
  }
}
EOF

cat <<EOF | kubectl apply -f -
apiVersion: certificates.k8s.io/v1beta1
kind: CertificateSigningRequest
metadata:
  name: sample-admission-webhook.default
spec:
  request: $(cat server.csr | base64 | tr -d '\n')
  usages:
  - digital signature
  - key encipherment
  - server auth
EOF

kubectl certificate approve sample-admission-webhook.default

kubectl get csr sample-admission-webhook.default -o jsonpath='{.status.certificate}' \
        | base64 --decode > server.crt

kubectl create secret tls --save-config sample-admission-webhook-secret \
        --key server-key.pem  \
        --cert server.crt
