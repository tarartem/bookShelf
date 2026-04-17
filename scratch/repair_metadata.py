import json
import re

file_path = "books/metadata.json"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Remove all extra characters that might break splitting
# But keep the content. 
# Strategy: find all top-level keys like "Filename.epub": { ... }

# First, let's just try to extract all key-value pairs from all potential objects.
all_metadata = {}

# This regex tries to find "Key.epub": { ... } patterns
# It's a bit risky, let's try a better way: 
# Find all occurrences of individual book objects and merge them.

# Actually, the user probably has something like:
# { "book1": ... } { "book2": ... }
# Or worse: { "book1": ... , } { "book2": ... }

# Let's try to remove everything that isn't a key-value or brace,
# then wrap everything in one { ... } and fix commas.

def repair_json(text):
    # Remove any outer brackets first to start clean
    text = text.strip()
    # Remove leading/trailing brackets recursively
    while text.startswith('{') and text.endswith('}'):
        # Only strip if it's the ENTIRE thing. 
        # But we might have multiple roots.
        break 

    # Find all sequences of "filename": { ... }
    # Since we know the structure, we can try to find entries.
    entries = re.findall(r'"([^"]+\.epub)":\s*({(?:[^{}]|{[^{}]*})*})', text, re.DOTALL)
    
    result = {}
    for filename, raw_body in entries:
        try:
            # Clean up the body if needed
            body = json.loads(raw_body)
            result[filename] = body
        except Exception as e:
            print(f"Skipping {filename} due to parse error: {e}")
            continue
    return result

final_dict = repair_json(content)

if final_dict:
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(final_dict, f, indent=4, ensure_ascii=False)
    print(f"Repair successful. Processed {len(final_dict)} books.")
else:
    print("Could not find any valid book entries in the file.")
