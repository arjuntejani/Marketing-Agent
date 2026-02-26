# Pomelli-Style Capability Stack (Customizable)

This repository contains a lightweight framework to clone a Google-Pomelli-style capability set and then layer in your own custom capabilities.

## What you get

- A baseline capability profile (`capabilities/base_capabilities.json`) inspired by modern Google assistant/productivity features.
- A custom override file (`capabilities/custom_capabilities.json`) where you define your own capabilities.
- A merge/export tool (`scripts/merge_capabilities.py`) that combines baseline + your custom additions into one production-ready spec.
- A management CLI (`scripts/capability_tool.py`) to add capabilities, build merged output, and list capabilities.

## Quick start

```bash
python3 scripts/merge_capabilities.py \
  --base capabilities/base_capabilities.json \
  --custom capabilities/custom_capabilities.json \
  --out capabilities/final_capabilities.json
```

## Use the capability tool

Add (or update) a custom capability:

```bash
python3 scripts/capability_tool.py add \
  --id audience-intent-miner \
  --name "Audience Intent Miner" \
  --description "Finds audience segments, intent patterns, and messaging angles." \
  --category marketing \
  --status enabled
```

Build final merged output:

```bash
python3 scripts/capability_tool.py build
```

List final capabilities:

```bash
python3 scripts/capability_tool.py list --file capabilities/final_capabilities.json
```

## Add your own capabilities manually

Edit `capabilities/custom_capabilities.json`:

- Add new items under `capabilities`.
- Optionally list `enabled` and `disabled` capability IDs to turn features on/off.
- Add your own tools/providers under `integrations`.

Then re-run the merge/build command.
