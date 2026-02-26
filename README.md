# Pomelli-Style Capability Stack (Customizable)

This repository contains a lightweight framework to **clone a Google-Pomelli-style capability set** and then layer in your own custom capabilities.

## What you get

- A baseline capability profile (`capabilities/base_capabilities.json`) inspired by modern Google assistant/productivity features.
- A custom override file (`capabilities/custom_capabilities.json`) where you define your own capabilities.
- A merge/export tool (`scripts/merge_capabilities.py`) that combines baseline + your custom additions into one production-ready spec.

## Quick start

```bash
python3 scripts/merge_capabilities.py \
  --base capabilities/base_capabilities.json \
  --custom capabilities/custom_capabilities.json \
  --out capabilities/final_capabilities.json
```

## Add your own capabilities

Edit `capabilities/custom_capabilities.json`:

- Add new items under `capabilities`.
- Optionally list `enabled` and `disabled` capability IDs to turn features on/off.
- Add your own tools/providers under `integrations`.

Then re-run the merge command.

## Example extension workflow

1. Keep `base_capabilities.json` as the “cloned” reference set.
2. Add your unique differentiators in `custom_capabilities.json`.
3. Generate `final_capabilities.json` for runtime consumption.
4. Integrate the generated file into your app/agent backend.
