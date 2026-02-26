# Pomelli-Style Capability Stack (Customizable)

This repository contains a lightweight framework to clone a Google-Pomelli-style capability set and then layer in your own custom capabilities.

## What you get

- A baseline capability profile (`capabilities/base_capabilities.json`) inspired by modern Google assistant/productivity features.
- A custom override file (`capabilities/custom_capabilities.json`) where you define your own capabilities.
- A merge/export tool (`scripts/merge_capabilities.py`) that combines baseline + your custom additions into one production-ready spec.
- A management CLI (`scripts/capability_tool.py`) to add capabilities, build merged output, and list capabilities.
- A URL-ready API server (`scripts/capability_api.py`) so you can run the tool over HTTP.

## Quick start (CLI)

```bash
python3 scripts/capability_tool.py build
python3 scripts/capability_tool.py list --file capabilities/final_capabilities.json
```

## Run it via URL (HTTP API)

Start server:

```bash
python3 scripts/capability_api.py --host 0.0.0.0 --port 8080
```

Now call it by URL:

```bash
# Health
curl http://localhost:8080/health

# Add/update capability
curl -X POST http://localhost:8080/capabilities/add \
  -H 'Content-Type: application/json' \
  -d '{
    "id": "persona-mapper",
    "name": "Persona Mapper",
    "description": "Creates customer personas from market notes.",
    "category": "marketing",
    "status": "enabled"
  }'

# Build merged output
curl -X POST http://localhost:8080/build

# Read final capabilities
curl http://localhost:8080/capabilities/final
```

## Publish on the internet

To make this reachable from the public internet, deploy this server on a cloud VM/container and expose port 8080 through your load balancer/reverse proxy.
