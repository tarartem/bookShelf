import json
import os

METADATA_FILE = "books/metadata.json"
BOOKS_DIR = "books"
REPORT_FILE = "books/metadata_report.md"

def analyze_metadata():
    if not os.path.exists(METADATA_FILE):
        return "Metadata file not found."

    with open(METADATA_FILE, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    actual_files = [f for f in os.listdir(BOOKS_DIR) if f.lower().endswith(".epub")]
    
    missing_description = []
    missing_from_json = []
    invalid_entries = []
    duplicate_titles = {}
    
    # Check for duplicates and missing data in JSON
    for filename, data in metadata.items():
        # Check if file exists
        if filename not in actual_files:
            invalid_entries.append(filename)
        
        # Check description
        if not data.get("description") or data["description"].strip() == "":
            missing_description.append(filename)
            
        # Check for duplicate titles
        title = data.get("title", "Unknown")
        if title in duplicate_titles:
            duplicate_titles[title].append(filename)
        else:
            duplicate_titles[title] = [filename]

    # Check for files missing from JSON
    for f in actual_files:
        if f not in metadata:
            missing_from_json.append(f)

    # Filter duplicate titles
    actual_duplicates = {t: files for t, files in duplicate_titles.items() if len(files) > 1}

    # Generate Report
    report = []
    report.append("# 📊 Book Metadata Analysis Report\n")
    
    report.append(f"## Summary")
    report.append(f"- **Total Books in folder**: {len(actual_files)}")
    report.append(f"- **Total Entries in JSON**: {len(metadata)}")
    report.append(f"- **Books missing descriptions**: {len(missing_description)}")
    report.append(f"- **Books missing from JSON**: {len(missing_from_json)}")
    report.append(f"- **Invalid entries (JSON refers to non-existent file)**: {len(invalid_entries)}")
    report.append(f"- **Duplicate titles**: {len(actual_duplicates)}\n")

    if missing_description:
        report.append("## ❌ Missing Descriptions")
        report.append("The following books have no description defined:\n")
        for f in missing_description:
            report.append(f"- {f}")
        report.append("\n")

    if missing_from_json:
        report.append("## ⚠️ Missing from JSON")
        report.append("These files exist in the `books/` folder but are not listed in `metadata.json`:\n")
        for f in missing_from_json:
            report.append(f"- {f}")
        report.append("\n")

    if actual_duplicates:
        report.append("## 👯 Duplicate Titles")
        report.append("The following titles appear multiple times (might be different editions or errors):\n")
        for title, files in actual_duplicates.items():
            report.append(f"- **{title}**: {', '.join(files)}")
        report.append("\n")

    if invalid_entries:
        report.append("## 👻 Invalid Entries")
        report.append("These entries in `metadata.json` do not match any file in the `books/` folder:\n")
        for f in invalid_entries:
            report.append(f"- {f}")
        report.append("\n")

    with open(REPORT_FILE, "w", encoding="utf-8") as rf:
        rf.write("\n".join(report))

    return f"Report generated at {REPORT_FILE}"

if __name__ == "__main__":
    print(analyze_metadata())
