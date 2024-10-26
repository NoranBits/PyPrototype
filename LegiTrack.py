import os
import json
from collections import Counter
import xml.etree.ElementTree as ET

# Print the current working directory
print("Current Working Directory:", os.getcwd())

# Load the JSON data from a file
with open('billsum.json', 'r') as file:
    data = json.load(file)

# Extract NumberCode entries
number_codes = [bill['NumberCode'] for bill in data]

# Count the occurrences of each NumberCode
number_code_counts = Counter(number_codes)

# Determine letter-number relations
letter_number_relations = {}
for number_code in number_codes:
    letter, number = number_code.split('-')
    if letter not in letter_number_relations:
        letter_number_relations[letter] = []
    letter_number_relations[letter].append(number)  # Store number as string

# Create XML structure
root = ET.Element("NumberCodeSummary")

# Add summary to XML
summary = ET.SubElement(root, "Summary")
for letter, numbers in letter_number_relations.items():
    ranges = []
    sorted_numbers = sorted(numbers, key=lambda x: (int(x) if x.isdigit() else float('inf'), x))
    start = sorted_numbers[0]
    end = sorted_numbers[0]
    for num in sorted_numbers[1:]:
        if num.isdigit() and int(num) == int(end) + 1:
            end = num
        else:
            ranges.append(f"{start}-{end}" if start != end else f"{start}")
            start = num
            end = num
    ranges.append(f"{start}-{end}" if start != end else f"{start}")
    ET.SubElement(summary, "Letter", name=letter).text = f"range({', '.join(ranges)})"

# Add raw data to XML
raw_data = ET.SubElement(root, "RawData")
for number_code in number_codes:
    ET.SubElement(raw_data, "NumberCode").text = number_code

# Write XML to file
tree = ET.ElementTree(root)
with open("number_code_summary.xml", "wb") as xml_file:
    tree.write(xml_file)

print("XML file 'number_code_summary.xml' created successfully.")