# This Tiltfile sets up a local development environment for the Agentic Layer project.

update_settings(max_parallel_updates=10)

# Create Kubernetes secrets from environment variables
load('ext://secret', 'secret_from_dict')
load('ext://dotenv', 'dotenv')
dotenv()

v1alpha1.extension_repo(name='agentic-layer', url='https://github.com/agentic-layer/tilt-extensions', ref='v0.3.2')

v1alpha1.extension(name='cert-manager', repo_name='agentic-layer', repo_path='cert-manager')
load('ext://cert-manager', 'cert_manager_install')
cert_manager_install()

v1alpha1.extension(name='agent-runtime', repo_name='agentic-layer', repo_path='agent-runtime')
load('ext://agent-runtime', 'agent_runtime_install')
agent_runtime_install(version='0.10.0')

v1alpha1.extension(name='ai-gateway-litellm', repo_name='agentic-layer', repo_path='ai-gateway-litellm')
load('ext://ai-gateway-litellm', 'ai_gateway_litellm_install')
ai_gateway_litellm_install(version='0.2.0')

v1alpha1.extension(name='agent-gateway-krakend', repo_name='agentic-layer', repo_path='agent-gateway-krakend')
load('ext://agent-gateway-krakend', 'agent_gateway_krakend_install')
agent_gateway_krakend_install(version='0.1.4')


google_api_key = os.environ.get('GOOGLE_API_KEY', '')
if not google_api_key:
    fail('GOOGLE_API_KEY environment variable is required. Please set it in your shell or .env file.')

k8s_yaml(secret_from_dict(
    name = "api-keys",
    namespace = "showcase-news",
    inputs = { "GOOGLE_API_KEY": google_api_key }
))

# Configure Tilt to work with Agent Runtime Operator's custom Agent CRDs
# Without these configurations, Tilt cannot properly manage Agent resources created by the operator:
# image_json_path: Required because Agent CRDs store image references in a custom field ({.spec.image})
#                  rather than standard Kubernetes image fields that Tilt knows about by default.
#								   Note that this must be removed if the image is created externally!
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

# Expose services
k8s_resource('lgtm', port_forwards=['3000:3000'])

k8s_resource('news-workforce', resource_deps=['agent-runtime'], pod_readiness='ignore')
k8s_resource('news-agent', port_forwards='8001:8000', labels=['workforce'], resource_deps=['news-fetcher', 'summarizer-agent'])
k8s_resource('summarizer-agent', port_forwards='8002:8000', labels=['workforce'], resource_deps=['news-fetcher'])

docker_build('news-fetcher', context='./mcp-servers/news-fetcher', dockerfile='./mcp-servers/news-fetcher/Dockerfile')
k8s_resource('news-fetcher', port_forwards='8003:8000', labels=['workforce'], resource_deps=['agent-runtime'])

k8s_resource('agent-gateway-krakend', port_forwards='8004:8080', labels=['agentic-layer'], resource_deps=['agent-runtime', 'news-agent'])

# Expose the Monitoring stack (Grafana)
k8s_resource('lgtm', port_forwards=['3000:3000', '4318:4318', '4317:4317'], labels=['monitoring'])

k8s_resource('observability-dashboard', port_forwards='8100:8000', labels=['agentic-layer'])
