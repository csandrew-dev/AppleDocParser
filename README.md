# AppleDocParser

A Python script that automatically generates JSON schemas from Apple Developer documentation pages. This tool was developed to help create schemas for the [micromdm/apple-device-services](https://github.com/micromdm/apple-device-services) project.

## Overview

The script uses Selenium WebDriver to fetch Apple Developer documentation pages (which require JavaScript rendering), parses the content using BeautifulSoup, and generates JSON Schema files based on a predefined template.

## Features

- **Automatic Schema Generation**: Extracts title, description, API version, and property definitions from Apple Developer documentation
- **Type Detection**: Automatically detects standard JSON Schema types vs. custom object references
- **Required Field Detection**: Identifies required properties from the documentation
- **Custom Output Directory**: Save generated schemas to any directory
- **JSON Schema 2020-12 Compliant**: Uses the latest JSON Schema specification

## Prerequisites

- Python 3.13+
- Firefox browser
- UV Python package manager

## Installation

1. **Install [UV](https://github.com/astral-sh/uv):**
    ```bash
    brew install uv
    ```

2. **Create a virtual environment:**
    ```bash
    uv venv
    ```

3. **Activate the virtual environment:**
      ```bash
      source .venv/bin/activate
      ```

4. **Install dependencies:**
    ```bash
    uv pip install -r pyproject.toml
    ```

## Usage

```bash
uv run schemer.py <Apple Developer Doc URL> [output_directory (relative path)]
```

### Examples

Generate schema in current directory:
```bash
uv run schemer.py https://developer.apple.com/documentation/appleschoolmanagerapi/documentlinks
```

Generate schema in specific directory:
```bash
uv run schemer.py https://developer.apple.com/documentation/appleschoolmanagerapi/documentlinks ./asm/schemas
```

If you want to see more about UV, check here: [https://docs.astral.sh/uv/](https://docs.astral.sh/uv/)

## How It Works

1. **Fetch Page**: Uses Selenium Firefox WebDriver to load the Apple Developer documentation page with JavaScript rendered
2. **Parse Content**: Extracts structured information using BeautifulSoup:
   - Title from `.title` class
   - Description from `.abstract.content` class
   - API version from `.platform` class
   - Properties from `.row.param` sections
3. **Generate Schema**: Creates JSON Schema with:
   - Standard types (`string`, `number`, `boolean`, etc.) use `"type"` field
   - Custom objects use `"$ref"` field pointing to `{ObjectName}.json`
   - Required fields detected from property requirement text
4. **Save File**: Outputs to specified directory with filename matching the documentation title

## Schema Template

The script uses `SchemaTemplate.json` as a base template following JSON Schema 2020-12 specification:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "",
  "description": "",
  "x-apple-developer-api-uri": "",
  "x-apple-developer-api-version": "",
  "type": "",
  "required": [ "" ],
  "properties": {
    "": {
      "description": "",
      "type": "",
      "$ref": ""
    }
  }
}
```

## Supported Documentation Types

The script is designed to work with Apple Developer API documentation pages that follow the standard format, including:
- Apple School Manager API
- Apple Business Manager API  
- Device Enrollment Program API
- And other Apple enterprise APIs

## Contributing

This tool was created to support the [micromdm/apple-device-services](https://github.com/micromdm/apple-device-services) project. Contributions and improvements are welcome!
