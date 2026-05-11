# Agentic AI News Showcase

A multi-agent demo built on the [Agentic Layer](https://agentic-layer.ai/) platform: a News agent fetches articles via an MCP server, delegates summarisation to a sub-agent over A2A, and all interactions are traced through the observability dashboard.

![demo.png](docs/modules/ROOT/images/demo.png)

📖 **Step-by-step tutorial:** https://docs.agentic-layer.ai/showcase-news/

## Development

### Prerequisites

- **[mise](https://mise.jdx.dev/)** (pins every tool to the version this repo uses)
- A local **Kubernetes** cluster (Docker Desktop, kind, colima, ...) with `kubectl` pointing at it
- A **`GOOGLE_API_KEY`** for Gemini models

### Build and run locally

```shell
# Install Tilt, kubectl, helm, etc.
mise install
# Provide the Gemini API key
export GOOGLE_API_KEY=<your-key>
# Start the showcase
tilt up
```

Wait until all components are green in the Tilt UI.

### Verify the local deploy

Once Tilt reports everything healthy, exercise the news agent end-to-end. The [tutorial](https://docs.agentic-layer.ai/showcase-news/) walks through the available endpoints and example questions. For GUI-based agent interaction try the [a2a-inspector](https://github.com/a2aproject/a2a-inspector).
