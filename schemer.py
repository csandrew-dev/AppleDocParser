import sys
import json
from time import sleep
from bs4 import BeautifulSoup
from selenium import webdriver
import re

def main():

    if len(sys.argv) < 2:
        print("Usage: python schemer.py <Apple Developer Doc URL> [output_directory]")
        sys.exit(1)

    url = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "."

    # Use Selenium to fetch the documentation page with JS rendered
    driver = webdriver.Firefox()
    driver.get(url)
    sleep(.05)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    driver.quit()

    # Start with minimal schema containing only required fields
    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "x-apple-developer-api-uri": url
    }

    print("================================================================")
    # Print title via class="title"
    title_tag = soup.find(class_="title")
    if title_tag:
        print("Title:", title_tag.text)
        schema['title'] = title_tag.text
    else:
        print("Title: NOT FOUND - skipping")
        
    # Print description via class="abstract content"
    desc_tag = soup.find(class_="abstract content")
    if desc_tag:
        print("Description:", desc_tag.text)
        schema['description'] = desc_tag.text
    else:
        print("Description: NOT FOUND - skipping")

    # Print type via class="eyebrow"
    type_tag = soup.find(class_="eyebrow")
    if type_tag:
        print("Type:", type_tag.text)
        schema['type'] = type_tag.text.lower()
    else:
        print("Type: NOT FOUND - skipping")

    # Print x-apple-developer-api-version via class="platform"
    version_tag = soup.find(class_="platform")
    if version_tag:
        print("x-apple-developer-api-version:", version_tag.text)
        # Extract only the version number (e.g., '1.1+') from the version tag
        version_text = version_tag.text
        match = re.search(r'[0-9]+\.[0-9]+\+?', version_text)
        if match:
            schema['x-apple-developer-api-version'] = match.group(0)
    else:
        print("x-apple-developer-api-version: NOT FOUND - skipping")

    # For each property in class="row param"
    property_sections = soup.find_all(class_="row param")
    print(f"Found {len(property_sections)} property sections")
    properties = {}
    required = []

    for section in property_sections:
        # Name and type inside class="col param-symbol large-3 small-12"
        symbol_col = section.find(class_="col param-symbol large-3 small-12")
        if not symbol_col:
            continue

        # Name inside class="property-name"
        name_tag = symbol_col.find(class_="property-name")
        if not name_tag:
            continue
        prop_name = name_tag.text.strip()

        # Type inside class="property-metadata property-type"
        type_tag = symbol_col.find(class_="property-metadata property-type")
        prop_type = type_tag.text.strip().lower() if type_tag else "string"

        # Default value inside class="property-metadata" (if present)
        default_tag = symbol_col.find(class_="property-metadata")
        default_value = None
        if default_tag and "default" in default_tag.text.lower():
            match = re.search(r'Default:\s*([^\s]+)', default_tag.text)
            if match:
                default_value = match.group(1)

        # Requirement and Description inside class="col param-content large-9 small-12"
        content_col = section.find(class_="col param-content large-9 small-12")
        is_required = False
        description = ""
        if content_col:
            # Required if this class="property-text" field exists
            required_tag = content_col.find(class_="property-text")
            if required_tag and "required" in required_tag.text.lower():
                is_required = True

            # Description inside class="content"
            desc_tag = content_col.find(class_="content")
            if desc_tag:
                description = desc_tag.text.strip()
            else:
                # Sometimes the type is in this field if no description
                description = content_col.text.strip()

        # Build property schema
        prop_schema = {"type": prop_type}
        if description:
            prop_schema["description"] = description
        if default_value is not None:
            prop_schema["default"] = default_value

        properties[prop_name] = prop_schema
        if is_required:
            required.append(prop_name)

    if properties:
        schema['properties'] = properties
    else:
        print("Properties: NOT FOUND - skipping")
        
    if required:
        schema['required'] = required
    else:
        print("Required fields: NONE FOUND - skipping")

    print("================================================================")
        
    # Save the populated schema
    import os
    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    filename = title_tag.text if title_tag else "UnknownSchema"
    output_file = os.path.join(output_dir, f'{filename}.json')
    with open(output_file, 'w') as f:
        json.dump(schema, f, indent=2)
    print(f"Schema generated and saved to {output_file}")

if __name__ == "__main__":
    main()