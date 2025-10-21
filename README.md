# Architect Review Context

This repository provides tools and templates for conducting structured architectural reviews of Azure resources and repositories.

## Features

- **Parameterized Azure Identifiers**: All subscription IDs and resource group names use placeholders to avoid leaking sensitive information
- **Template Rendering**: Render documentation with actual Azure identifiers for local use
- **Azure Resource Graph Collection**: Automated script to collect resource inventory for architectural review

## Setup

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and fill in your Azure details:
   ```bash
   AZURE_SUBSCRIPTION_ID=your-subscription-id
   AZURE_RESOURCE_GROUP=your-resource-group
   # ... other variables
   ```

3. Source the environment file:
   ```bash
   source .env
   ```

## Usage

### Render Templates

To render templates with your Azure identifiers:

```bash
# Using environment variables from .env
source .env
./scripts/render-templates.sh rendered

# Or specify variables inline
AZURE_SUBSCRIPTION_ID=xxx AZURE_RESOURCE_GROUP=yyy ./scripts/render-templates.sh rendered
```

This will create a `rendered/` directory with all markdown, KQL, and JSON files with placeholders replaced.

### Collect Azure Resource Graph Inventory

To collect resource inventory for architectural review:

```bash
# Using environment variables
AZURE_SUBSCRIPTION_ID=xxx AZURE_RESOURCE_GROUP=yyy ./tools/architecture/collect_arg_inventory.sh

# Using command-line arguments
./tools/architecture/collect_arg_inventory.sh -s <subscription-id> -g <resource-group>

# Using both (command-line overrides environment variables)
AZURE_SUBSCRIPTION_ID=xxx ./tools/architecture/collect_arg_inventory.sh -g <resource-group>
```

The script will:
- Create a timestamped directory under `architecture/evidence/`
- Query Azure Resource Graph for resource inventory
- Save results as JSON files for analysis
- Redact subscription IDs in metadata using placeholders

**Note**: The `architecture/evidence/` directory is gitignored to prevent committing sensitive data.

## Repository Structure

```
.
├── .env.example              # Environment variable template
├── .gitignore               # Ignores .env and architecture/evidence/
├── scripts/
│   └── render-templates.sh  # Template rendering script
├── tools/
│   └── architecture/
│       └── collect_arg_inventory.sh  # Azure Resource Graph collection script
└── .github/
    ├── chatmodes/           # AI architect chat modes
    ├── prompts/             # Architectural review prompts (with placeholders)
    └── workflows/           # GitHub Actions workflows
```

## Security

- Never commit `.env` files (gitignored by default)
- Never commit `architecture/evidence/` data (gitignored by default)
- All committed files use `{SUBSCRIPTION_ID}` and `{RESOURCE_GROUP}` placeholders
- Render templates locally for actual usage

## Development

### Testing

Run shellcheck on scripts:

```bash
shellcheck scripts/render-templates.sh
shellcheck tools/architecture/collect_arg_inventory.sh
```

### Prerequisites

- Bash 4.0+
- Azure CLI (for resource collection)
- Git (for template rendering)
