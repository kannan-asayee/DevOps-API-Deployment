# Simple API - Jenkins CI/CD - Docker Hub - Kubernetes - Kong Gateway

A hands-on DevOps lab project that builds a simple Python REST API and
implements an end-to-end CI/CD and Kubernetes deployment flow using
**Azure DevOps Git, Jenkins, Docker Hub, Kubernetes, Kong Gateway,
Gateway API, JWT authentication, Prometheus, and Grafana**.

> **Project type:** Self-hosted lab / learning implementation\
> The project is intended for hands-on DevOps, Kubernetes, CI/CD, API
> gateway, and observability practice.

## Architecture

### End-to-End Architecture Diagram

![Simple API Jenkins Kubernetes Kong
Architecture](docs/images/simple-api-architecture.png)

> Keep `docs/images/simple-api-architecture.png` in the repository so
> the diagram renders directly in Azure DevOps or GitHub.

### CI/CD and Runtime Flow

``` text
Developer
    |
    | git push
    v
Azure DevOps Git Repository
    |
    v
Jenkins (.12)
    |
    +--> Checkout
    +--> Install dependencies
    +--> Unit tests (pytest)
    +--> Docker build
    +--> Docker push
    |
    v
Docker Hub
    |
    | Kubernetes pulls image
    v
+--------------------------------------------------+
| Kubernetes Cluster - Master .9 / Worker .11      |
|                                                  |
| Client                                           |
|   | HTTPS + JWT                                  |
|   v                                              |
| Kong Gateway                                     |
|   | Gateway API / HTTPRoute                      |
|   v                                              |
| simple-api ClusterIP Service                     |
|   |                                              |
|   +----------+----------+                        |
|              |          |                        |
|           API Pod    API Pod                     |
|           Replica 1  Replica 2                   |
+--------------------------------------------------+
               |
               v
       Prometheus / Grafana
```

### Authentication and MFA Flow

``` text
User / API Client
        |
        | 1. Login
        v
Keycloak / Microsoft Entra ID
        |
        | Password + MFA
        | 2. Issue OIDC/JWT access token
        v
User / API Client
        |
        | 3. Authorization: Bearer <JWT>
        v
Kong Gateway
        |
        | Validate token
        | Apply API policies
        v
Gateway API / HTTPRoute
        |
        v
Kubernetes Service
        |
        v
API Pods
```

**Responsibility separation:** Keycloak or Microsoft Entra ID performs
user authentication and MFA and issues the token. Kong is the API entry
point: it validates the token, applies API policies such as
authorization and rate limiting, and routes accepted requests to the
Kubernetes service. The Flask API does not implement MFA.

### Component Responsibilities

  -----------------------------------------------------------------------
  Component                           Responsibility
  ----------------------------------- -----------------------------------
  Azure DevOps Git                    Stores API source, Jenkinsfile,
                                      Dockerfile and Kubernetes/Kong
                                      manifests

  Jenkins                             Checkout, unit test, Docker build
                                      and image publication

  Docker Hub                          Stores versioned container images

  Kubernetes                          Runs and manages the API workload

  Kong Gateway                        API entry point, routing, JWT
                                      validation and API policies

  Gateway API / HTTPRoute             Defines traffic routing from Kong
                                      to the API service

  Keycloak / Entra ID                 Authentication, MFA and token
                                      issuance

  Prometheus                          Metrics collection

  Grafana                             Dashboards and visualization
  -----------------------------------------------------------------------

## End-to-End Flow

1.  Developer develops and tests the Python REST API.
2.  Source code, Dockerfile, Kubernetes manifests, Kong resources, and
    Jenkinsfile are committed to Azure DevOps Git.
3.  Jenkins checks out the repository and runs unit tests.
4.  Jenkins builds the Docker image and pushes a versioned image to
    Docker Hub.
5.  Kubernetes pulls the image and runs the API as a Deployment.
6.  Kong Gateway receives API requests and Gateway API `HTTPRoute`
    forwards traffic to the Kubernetes Service.
7.  Kong JWT policy rejects requests without a valid token and forwards
    authenticated requests to the API.
8.  Prometheus and Grafana provide Kubernetes/workload monitoring.

## Repository Structure

``` text
simple-api-project/
├── app/
│   ├── app.py
│   ├── requirements.txt
│   ├── test_app.py
│   ├── Dockerfile
│   └── .dockerignore
├── k8s/
│   ├── namespace.yaml
│   ├── deployment.yaml
│   ├── service.yaml
│   └── kustomization.yaml
├── kong/
│   ├── gatewayclass.yaml
│   ├── gateway.yaml
│   ├── httproute.yaml
│   ├── jwt-plugin.yaml
│   ├── consumer.yaml
│   └── jwt-secret.yaml
├── docs/
│   └── images/
│       └── simple-api-architecture.png
├── Jenkinsfile
└── README.md
```

## Sample API Endpoints

  Method   Endpoint                      Purpose
  -------- ----------------------------- ----------------------------------
  GET      `/`                           API information
  GET      `/health`                     Kubernetes health check
  GET      `/api/v1/hello?name=sample-API`   Sample API endpoint
  GET      `/api/v1/info`                Application/platform information

## 1. Test the API

``` bash
cd app
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/pytest -v
```

Expected result:

``` text
2 passed
```

Run the API:

``` bash
.venv/bin/python app.py
```

Test:

``` bash
curl http://127.0.0.1:8080/health
```

Expected:

``` json
{"status":"UP"}
```

## 2. Build and Test the Docker Image

``` bash
docker build -t simple-api:local app
```

Run:

``` bash
docker run -d --name simple-api-test -p 8080:8080 simple-api:local
```

Validate:

``` bash
curl http://127.0.0.1:8080/health
```

Check logs:

``` bash
docker logs simple-api-test
```

Clean up:

``` bash
docker rm -f simple-api-test
```

## 3. Jenkins CI/CD

The Jenkins pipeline performs:

``` text
Checkout
   |
   v
Install/Test
   |
   v
Docker Build
   |
   v
Docker Hub Push
```

### Jenkins prerequisites

Verify on the Jenkins node:

``` bash
git --version
docker --version
python3 --version
java -version
```

If Jenkins is using the local Docker daemon in this dedicated lab:

``` bash
sudo usermod -aG docker jenkins
sudo systemctl restart jenkins
```

> **Security:** Docker group membership effectively provides privileged
> access to the Docker host. Use this only as appropriate for your
> dedicated lab; production environments should use a more tightly
> controlled build architecture.

### Docker Hub credentials

In Jenkins:

**Manage Jenkins -\> Credentials -\> System -\> Global credentials -\>
Add Credentials**

Create:

-   Kind: `Username with password`
-   Username: Docker Hub username
-   Password: Docker Hub access token
-   ID: `dockerhub-creds`

Do not commit Docker Hub passwords or tokens to Git.

### Jenkinsfile

Before running the pipeline, replace:

``` text
YOUR_DOCKERHUB_USERNAME
```

with your actual Docker Hub username.

The pipeline uses Jenkins `BUILD_NUMBER` as a versioned image tag and
also publishes `latest` for the initial lab.

For a production-style process, prefer immutable version tags/digests
rather than deploying `latest`.

## 4. Deploy to Kubernetes

Update the image in:

``` text
k8s/deployment.yaml
```

Replace:

``` text
YOUR_DOCKERHUB_USERNAME/simple-api:latest
```

with your Docker Hub repository.

Validate:

``` bash
kubectl apply --dry-run=server -k k8s/
```

Deploy:

``` bash
kubectl apply -k k8s/
```

Verify:

``` bash
kubectl get pods -n simple-api -o wide
kubectl get svc -n simple-api
kubectl rollout status deployment/simple-api -n simple-api
```

Check logs:

``` bash
kubectl logs -n simple-api deployment/simple-api
```

Test from inside Kubernetes:

``` bash
kubectl run curl-test -n simple-api --image=curlimages/curl --restart=Never --rm -it -- curl http://simple-api:8080/health
```

Expected:

``` json
{"status":"UP"}
```

## 5. Kong Gateway and Gateway API

The traffic path is:

``` text
Client
   |
   v
Kong Gateway
   |
   +--> JWT validation
   |
   v
Gateway API HTTPRoute
   |
   v
simple-api ClusterIP Service
   |
   v
API Pods
```

Install the Gateway API CRDs before using `Gateway` and `HTTPRoute`.

Then install Kong/Kong Ingress Controller according to the deployment
runbook and apply:

``` bash
kubectl apply -f kong/gatewayclass.yaml
kubectl apply -f kong/gateway.yaml
```

Verify:

``` bash
kubectl get gatewayclass
kubectl get gateway -n kong
kubectl get pods -n kong
kubectl get svc -n kong
```

Apply the API route:

``` bash
kubectl apply -f kong/httproute.yaml
```

Verify:

``` bash
kubectl get httproute -n simple-api
kubectl describe httproute simple-api -n simple-api
```

## 6. Kong JWT Authentication

Apply the JWT plugin:

``` bash
kubectl apply -f kong/jwt-plugin.yaml
```

Apply the Kong consumer and JWT credential after replacing the sample
secret:

``` bash
kubectl apply -f kong/consumer.yaml
kubectl apply -f kong/jwt-secret.yaml
```

Apply/reconcile the route:

``` bash
kubectl apply -f kong/httproute.yaml
```

Verify:

``` bash
kubectl get kongplugin -n simple-api
kubectl get kongconsumer -n simple-api
```

### Security warning

`kong/jwt-secret.yaml` contains only a lab placeholder.

Never commit real JWT signing secrets, Docker Hub tokens, passwords,
kubeconfig credentials, or other production secrets to the repository.

### Negative test

A request without a valid JWT should be rejected by Kong:

``` bash
curl -i http://192.168.70.9:8000/api/v1/info
```

### Authenticated request

After generating a valid lab JWT:

``` bash
TOKEN='PASTE_GENERATED_TOKEN_HERE'
curl -i -H "Authorization: Bearer $TOKEN" http://192.168.70.9:8000/api/v1/info
```

Expected result: Kong validates the token and the backend returns HTTP
200.

## 7. MFA Design

MFA is not implemented by the Flask API or by treating the basic Kong
JWT plugin as an MFA system.

Recommended architecture:

``` text
User
 |
 +--> Username / Password
 +--> MFA / OTP / Authenticator
 |
 v
Identity Provider
(Keycloak / Microsoft Entra ID)
 |
 | OIDC/JWT access token
 v
Kong Gateway
 |
 +--> Validate token
 +--> Apply API policy
 +--> Route request
 |
 v
Kubernetes Service
 |
 v
API Pods
```

This can be implemented as a second phase after the basic JWT lab is
working.

## 8. Monitoring

The lab can use the existing Prometheus/Grafana deployment.

Basic validation:

``` bash
kubectl get pods -n simple-api
kubectl top pods -n simple-api
kubectl get pods -n kong
kubectl top pods -n kong
```

A later enhancement can expose application metrics and Kong metrics for
API request rate, errors, and latency.

## 9. Troubleshooting

``` bash
kubectl get pods -A
kubectl get events -n simple-api --sort-by=.lastTimestamp
kubectl describe pod -n simple-api <pod-name>
kubectl logs -n simple-api deployment/simple-api
kubectl get gateway -n kong -o wide
kubectl describe gateway kong -n kong
kubectl describe httproute simple-api -n simple-api
kubectl get svc -n kong
```

Jenkins:

``` bash
sudo journalctl -u jenkins -n 200 --no-pager
```

Docker:

``` bash
docker images
docker ps -a
```

## 10. Validation Checklist

-   [ ] API unit tests pass.
-   [ ] Local Docker container returns `/health`.
-   [ ] Jenkins successfully checks out the Azure DevOps repository.
-   [ ] Jenkins unit-test stage passes.
-   [ ] Jenkins builds a versioned Docker image.
-   [ ] Jenkins pushes the image to Docker Hub.
-   [ ] Kubernetes Deployment has two Ready replicas.
-   [ ] ClusterIP Service reaches the API.
-   [ ] Kong Gateway/controller components are healthy.
-   [ ] Gateway and HTTPRoute are accepted.
-   [ ] Unauthenticated API request is rejected.
-   [ ] Valid JWT request reaches the API.
-   [ ] Prometheus/Grafana can observe the workloads.

## 11. Future Enhancements

After completing the base project:

1.  Add Keycloak or Entra ID with OIDC and MFA.
2.  Add HTTPS/TLS to the Kong Gateway.
3.  Add Kong rate limiting.
4.  Add API authorization/ACL policies.
5.  Add Trivy container-image scanning to Jenkins.
6.  Add SAST/dependency scanning.
7.  Replace `latest` with immutable image tags/digests.
8.  Add application and Kong Prometheus metrics.
9.  Add Argo CD GitOps so Jenkins updates desired state and Argo CD
    performs Kubernetes reconciliation.
10. Add DEV -\> UAT -\> PROD promotion and approval gates.

**DevOps/Kubernetes Lab Project:** Built and containerized a Python REST
API; implemented Jenkins CI for automated unit testing, Docker image
build and Docker Hub publication; deployed the workload to a kubeadm
Kubernetes cluster with health probes and resource controls; configured
Kong Gateway/Kong Ingress Controller with Kubernetes Gateway API
HTTPRoute and JWT-based API authentication; validated workload health
using Prometheus and Grafana.

Use **Lab Project**, **Hands-on Project**, or **Self-hosted Lab
Implementation** unless you have implemented the same architecture in
production.
