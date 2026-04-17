import json
import os

METADATA_FILE = "books/metadata.json"
BOOKS_DIR = "books"
REPORT_FILE = "books/metadata_final_report.md"

def sync_metadata():
    if not os.path.exists(METADATA_FILE):
        return "Metadata file not found."

    with open(METADATA_FILE, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    # Actual files in the folder (THE TRUSTED SOURCE)
    actual_files = set(f for f in os.listdir(BOOKS_DIR) if f.lower().endswith(".epub"))
    
    cleaned_metadata = {}
    removed_entries = []
    
    # Clean the metadata: Keep only if file exists
    for filename, data in metadata.items():
        if filename in actual_files:
            cleaned_metadata[filename] = data
        else:
            removed_entries.append(filename)

    # Find what's missing in Metadata but present on disk
    missing_files = sorted(list(actual_files - set(cleaned_metadata.keys())))

    # Write cleaned metadata back
    with open(METADATA_FILE, "w", encoding="utf-8") as f:
        json.dump(cleaned_metadata, f, indent=4, ensure_ascii=False)

    # Generate Report
    report = []
    report.append("# 🎯 Metadata Sync & Cleanup Report\n")
    report.append(f"We have synchronized `metadata.json` with the physical files in your `books/` folder.\n")
    
    report.append(f"## 📊 Statistics")
    report.append(f"- **Physical Books on Disk**: {len(actual_files)}")
    report.append(f"- **Valid Entries Kept**: {len(cleaned_metadata)}")
    report.append(f"- **Stray Entries Removed**: {len(removed_entries)}")
    report.append(f"- **New Books Missing Info**: {len(missing_files)}\n")

    if removed_entries:
        report.append("## 🗑️ Removed (Not found on disk)")
        report.append("These entries were removed from `metadata.json` because the files don't exist in the folder (likely due to typos or deletions):\n")
        for f in removed_entries:
            report.append(f"- {f}")
        report.append("\n")

    if missing_files:
        report.append("## 🔎 Missing Information")
        report.append("The following physical files are present but have NO description in `metadata.json` yet:\n")
        for f in missing_files:
            report.append(f"- {f}")
        report.append("\n")

    with open(REPORT_FILE, "w", encoding="utf-8") as rf:
        rf.write("\n".join(report))

    return f"Metadata cleaned and report generated at {REPORT_FILE}"

if __name__ == "__main__":
    print(sync_metadata())
