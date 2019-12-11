# ------------------------
# sample-admission-webhook
# ------------------------

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

# ------------------
# istio-vsvc-host
# ------------------

cat <<EOF | cfssl genkey - | cfssljson -bare server
{
  "hosts": [
    "istio-vsvc-host.default.svc"
  ],
  "CN": "istio-vsvc-host.default.svc",
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
  name: istio-vsvc-host.default
spec:
  request: $(cat server.csr | base64 | tr -d '\n')
  usages:
  - digital signature
  - key encipherment
  - server auth
EOF

kubectl certificate approve istio-vsvc-host.default

kubectl get csr istio-vsvc-host.default -o jsonpath='{.status.certificate}' \
        | base64 --decode > server.crt

kubectl create secret tls --save-config istio-vsvc-host \
        --key server-key.pem  \
        --cert server.crt
