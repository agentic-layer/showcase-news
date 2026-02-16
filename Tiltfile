update_settings(max_parallel_updates=10)

# Load .env file for environment variables
load('ext://dotenv', 'dotenv')
dotenv()

load('ext://helm_remote', 'helm_remote')

v1alpha1.extension_repo(name='agentic-layer', url='https://github.com/agentic-layer/tilt-extensions', ref='v0.9.2')

v1alpha1.extension(name='cert-manager', repo_name='agentic-layer', repo_path='cert-manager')
load('ext://cert-manager', 'cert_manager_install')
cert_manager_install()

v1alpha1.extension(name='agent-runtime', repo_name='agentic-layer', repo_path='agent-runtime')
load('ext://agent-runtime', 'agent_runtime_install')
agent_runtime_install(version='0.17.2')

v1alpha1.extension(name='ai-gateway-litellm', repo_name='agentic-layer', repo_path='ai-gateway-litellm')
load('ext://ai-gateway-litellm', 'ai_gateway_litellm_install')
ai_gateway_litellm_install(version='0.4.1', instance=False)

v1alpha1.extension(name='agent-gateway-krakend', repo_name='agentic-layer', repo_path='agent-gateway-krakend')
load('ext://agent-gateway-krakend', 'agent_gateway_krakend_install')
agent_gateway_krakend_install(version='0.5.3', instance=False)

helm_remote(
    'observability-dashboard',
    repo_url='oci://ghcr.io/agentic-layer/charts',
    version='0.3.0',
    namespace='observability-dashboard',
)

v1alpha1.extension(name='librechat', repo_name='agentic-layer', repo_path='librechat')
load('ext://librechat', 'librechat_install')
librechat_install(port='8101')

# Docker builds
docker_build('news-fetcher', context='./mcp-servers/news-fetcher')

# Install showcase-news via Helm chart
k8s_yaml(helm(
    'chart',
    name='showcase-news',
    namespace='showcase-news',
    values=['chart/values.yaml'],
    set=[
        'images.newsFetcher.repository=news-fetcher',
    ],
))

# Install local-only resources via Kustomize
k8s_yaml(kustomize('deploy'))

# Showcase Components
k8s_resource('news-workforce', labels=['showcase'], resource_deps=['agent-runtime'], pod_readiness='ignore')
k8s_resource('news-agent', labels=['showcase'], resource_deps=['agent-runtime', 'news-fetcher', 'summarizer-agent'], port_forwards='8001:8000')
k8s_resource('summarizer-agent', labels=['showcase'], resource_deps=['agent-runtime', 'news-fetcher'], port_forwards='8002:8000')
k8s_resource('news-fetcher', labels=['showcase'], resource_deps=['agent-runtime'], port_forwards='8003:8000')

# Agentic Layer Components
k8s_resource('ai-gateway', labels=['agentic-layer'], resource_deps=['agent-runtime'], port_forwards=['8005:4000'])
k8s_resource('agent-gateway', labels=['agentic-layer'], resource_deps=['agent-runtime'], port_forwards='8004:8080')
k8s_resource('observability-dashboard', labels=['agentic-layer'], port_forwards='8100:8000')

# Monitoring
k8s_resource('lgtm', labels=['monitoring'], resource_deps=[], port_forwards=['3000:3000'])

# Secrets for LLM API keys
google_api_key = os.environ.get('GOOGLE_API_KEY', '')
if not google_api_key:
    warn('GOOGLE_API_KEY environment variable is not set. Please set it in your shell or .env file.')

# Create Kubernetes secrets from environment variables
load('ext://secret', 'secret_from_dict')
k8s_yaml(secret_from_dict(
    name = "api-key-secrets",
    namespace = "ai-gateway",
    # The ai-gateway expects the API key to be called <provider>_API_KEY
    inputs = { "GEMINI_API_KEY": google_api_key }
))
