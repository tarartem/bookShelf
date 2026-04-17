import re

file_path = "books/metadata.json"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Remove the multiple roots by replacing "}\n{" with ","
# We look for a pattern where an object ends and a new one starts
# Using a regex that handles potential whitespace
fixed_content = re.sub(r'\}\s*\{', ',', content)

# Ensure it starts with { and ends with }
# (Regex replacement might have messed up the outermost ones if not careful)
fixed_content = fixed_content.strip()
if not fixed_content.startswith('{'):
    fixed_content = '{' + fixed_content
if not fixed_content.endswith('}'):
    fixed_content = fixed_content + '}'

with open(file_path, "w", encoding="utf-8") as f:
    f.write(fixed_content)

print("JSON fixed via regex merging.")
