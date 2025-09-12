import sys
import json
from time import sleep
from bs4 import BeautifulSoup
from selenium import webdriver
import re

schemaTemplate = "./SchemaTemplate.json"

def main():

    if len(sys.argv) < 2:
        print("Usage: python schemer.py <Apple Developer Doc URL> [output_directory]")
        sys.exit(1)

    url = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "."

    # Use Selenium to fetch the documentation page with JS rendered
    driver = webdriver.Firefox()
    driver.get(url)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    driver.quit()

    # Load the schema template
    with open(schemaTemplate, 'r') as f:
        schema = json.load(f)

    print("================================================================")
    # Print title via class="title"
    title_tag = soup.find(class_="title")
    print("Title:", title_tag.text)
    schema['title'] = title_tag.text if title_tag else ""

    # Print description via class="abstract content"
    desc_tag = soup.find(class_="abstract content")
    print("Description:", desc_tag.text)
    schema['description'] = desc_tag.text if desc_tag else ""

    schema['x-apple-developer-api-uri'] = url

    # Print type via class="eyebrow"
    type_tag = soup.find(class_="eyebrow")
    print("Type:", type_tag.text)
    schema['type'] = type_tag.text.lower() if type_tag else ""

    # Print x-apple-developer-api-version via class="platform"
    version_tag = soup.find(class_="platform")
    print("x-apple-developer-api-version:", version_tag.text)
    # Extract only the version number (e.g., '1.1+') from the version tag
    version_text = version_tag.text if version_tag else ""
    match = re.search(r'[0-9]+\.[0-9]+\+?', version_text)
    schema['x-apple-developer-api-version'] = match.group(0) if match else ""

    # For each property in class="row param"
    property_sections = soup.find_all(class_="row param")
    print(f"Found {len(property_sections)} property sections")
    properties = {}
    required = []

    for idx, section in enumerate(property_sections, 1):
        
        # Get property's name from within this section
        property_name_tag = section.find(class_="property-name")
        property_name = property_name_tag.text.strip()
        print(f"\nProperty {idx}: {property_name}")

        # Print property's requirement via class="property-text"
        property_req_tag = section.find(class_="property-text")
        print("  Requirement:", property_req_tag.text)

        # Print property's description via class="content"
        property_desc_tag = section.find(class_="content")
        property_desc = property_desc_tag.text.strip()
        print("  Description:", property_desc)

        # Print property's type via class="property-metadata property-type"
        property_type_tag = section.find(class_="property-metadata property-type")
        property_type = property_type_tag.text.strip()
        print("  Type:", property_type)

        # Check if it's a standard JSON Schema type or a custom object reference
        standard_types = ["string", "number", "integer", "boolean", "object", "array", "null"]
        if property_type.lower() in standard_types:
            properties[property_name] = {
                "description": property_desc,
                "type": property_type.lower()
            }
        else:
            properties[property_name] = {
                "description": property_desc,
                "$ref": f"{property_type}.json"
            }

        # Check if property is required
        if "required" in property_req_tag.text.lower():
            required.append(property_name)

    schema['properties'] = properties
    schema['required'] = required

    print("================================================================")
        
    # Save the populated schema
    import os
    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f'{title_tag.text}.json')
    with open(output_file, 'w') as f:
        json.dump(schema, f, indent=2)
    print(f"Schema generated and saved to {output_file}")

if __name__ == "__main__":
    main()