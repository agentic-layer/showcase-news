# This Tiltfile sets up a local development environment for the Agentic Layer project.

update_settings(max_parallel_updates=10)

# Create Kubernetes secrets from environment variables
load('ext://secret', 'secret_from_dict')
load('ext://dotenv', 'dotenv')
dotenv()

google_api_key = os.environ.get('GOOGLE_API_KEY', '')
if not google_api_key:
    fail('GOOGLE_API_KEY environment variable is required. Please set it in your shell or .env file.')

k8s_yaml(secret_from_dict(
    name = "api-keys",
    namespace = "showcase-news",
    inputs = { "GOOGLE_API_KEY": google_api_key }
))

# Cert manager is required for Agent Runtime Operator to support webhooks
load('ext://cert_manager', 'deploy_cert_manager')
deploy_cert_manager()

def deploy_agent_runtime_operator():
    print("Installing agent-runtime-operator")
    local("kubectl apply -f https://github.com/agentic-layer/agent-runtime-operator/releases/download/v0.7.0/install.yaml")

    print("Waiting for agent-runtime-operator to start")
    local("kubectl wait --for=condition=Available --timeout=60s -n agent-runtime-operator-system deployment/agent-runtime-operator-controller-manager")

deploy_agent_runtime_operator()

# Configure Tilt to work with Agent Runtime Operator's custom Agent CRDs
# Without these configurations, Tilt cannot properly manage Agent resources created by the operator:
# image_json_path: Required because Agent CRDs store image references in a custom field ({.spec.image})
#                  rather than standard Kubernetes image fields that Tilt knows about by default
# pod_readiness: Required because the operator creates pods asynchronously after Agent CRD creation,
#                and Tilt must wait for operator-managed pods rather than assuming immediate readiness
k8s_kind(
    'Agent',
    pod_readiness='wait'
)

k8s_kind(
    'ToolServer',
    image_json_path='{.spec.image}',
    pod_readiness='wait'
)

# Apply Kubernetes manifests
k8s_yaml(kustomize('deploy'))


k8s_resource('news-agent', port_forwards='8001:8000', labels=['workforce'], resource_deps=['news-fetcher', 'summarizer-agent'])
k8s_resource('summarizer-agent', port_forwards='8002:8000', labels=['workforce'], resource_deps=['news-fetcher'])

docker_build('news-fetcher', context='./mcp-servers/news-fetcher', dockerfile='./mcp-servers/news-fetcher/Dockerfile')
k8s_resource('news-fetcher', port_forwards='8003:8000', labels=['workforce'])

# Expose the Monitoring stack (Grafana)
k8s_resource('lgtm', port_forwards=['3000:3000', '4318:4318', '4317:4317'], labels=['monitoring'])
k8s_resource('observability-dashboard', port_forwards='8100:8000', labels=['agentic-layer'])
