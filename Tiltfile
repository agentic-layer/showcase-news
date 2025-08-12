# Tiltfile for news processing system development

# Create Kubernetes secrets from environment variables
load('ext://secret', 'secret_from_dict')
load('ext://dotenv', 'dotenv')

google_api_key = os.environ.get('GOOGLE_API_KEY', '')
if not google_api_key:
    fail('GOOGLE_API_KEY environment variable is required. Please set it in your shell or .env file.')

k8s_yaml(secret_from_dict(
    name = "api-key-secrets",
    namespace = "demo",
    inputs = { "GOOGLE_API_KEY": google_api_key }
))

# Apply Kubernetes manifests
k8s_yaml(kustomize('deploy'))


docker_build("news_agent", context='./agents/news-agent/', dockerfile='./agents/news-agent/Dockerfile')
k8s_resource('news-agent', port_forwards='8000:8000', labels=['demo-workloads'])

docker_build("summarizer_agent", context='./agents/summarizer-agent/',dockerfile='./agents/summarizer-agent/Dockerfile')
k8s_resource('summarizer-agent', port_forwards='10001:8000', labels=['demo-workloads'])

docker_build('news-fetcher', context='.', dockerfile='./mcp-servers/news_fetcher/Dockerfile')
k8s_resource('news-fetcher', port_forwards='8001:8001', labels=['demo-workloads'])

# Expose the Monitoring stack (Grafana)
k8s_resource('lgtm', port_forwards=['3000:3000', '4318:4318', '4317:4317'], labels=['monitoring'])
k8s_resource('observability-dashboard', port_forwards='10005:8000', labels=['agentic-layer'])
