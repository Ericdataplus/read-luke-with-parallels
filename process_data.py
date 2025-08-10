import json
import re
from collections import defaultdict

# --- Step 1: Parse the full text of Josephus's Wars ---
def parse_josephus_text(filename):
    josephus_map = {}
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split the text by the reference markers (e.g., "P.1.1", "I.1.2")
        parts = re.split(r'\n([IVXPA-Z0-9]+\.[0-9]+\.[0-9]+)\n', content)
        
        i = 1
        while i < len(parts):
            reference = parts[i].strip()
            text = parts[i+1].strip().replace('\n', ' ') # Clean up newlines in text
            josephus_map[reference] = text
            i += 2
            
    except FileNotFoundError:
        print(f"Error: The file '{filename}' was not found.")
        return None
    return josephus_map

# --- Step 2: Parse the original parallels CSV ---
def parse_parallels_csv(filename):
    parallels = defaultdict(lambda: defaultdict(list))
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            next(f) # Skip header
            for line in f:
                cleaned_line = line.strip().replace('"', '')
                if not cleaned_line: continue
                
                parts = cleaned_line.split()
                if len(parts) >= 5:
                    source_ref_num, josephus_loc, _, _, luke_loc = parts[:5]
                    
                    try:
                        luke_chapter, luke_verse = map(int, luke_loc.split(':'))
                        source_name = "Wars" if source_ref_num.isdigit() else "Antiquities"
                        full_ref = f"{source_name} {josephus_loc}"
                        
                        if full_ref not in parallels[luke_chapter][luke_verse]:
                             parallels[luke_chapter][luke_verse].append(full_ref)
                    except ValueError:
                        continue
    except FileNotFoundError:
        print(f"Error: The file '{filename}' was not found.")
        return None
    return parallels

# --- Step 3: Combine data and generate the final JSON ---
ROMAN_MAP = {1: 'I', 2: 'II', 3: 'III', 4: 'IV', 5: 'V', 6: 'VI', 7: 'VII'}

# NOTE: Using 'josephus.txt' as per your directory structure
josephus_text_data = parse_josephus_text('josephus.txt') 
luke_parallels = parse_parallels_csv('input_file_0.csv')

final_data_for_website = defaultdict(lambda: defaultdict(list))

if josephus_text_data and luke_parallels:
    for chapter, verses in luke_parallels.items():
        for verse, refs in verses.items():
            for ref_str in refs:
                parts = ref_str.split()
                source_name, josephus_loc = parts[0], parts[1]
                loc_parts = josephus_loc.split('.')
                
                if source_name == "Wars" and len(loc_parts) == 3:
                    try:
                        book, chap, para = loc_parts
                        book_roman = ROMAN_MAP.get(int(book))
                        
                        if book_roman:
                            lookup_key = f"{book_roman}.{chap}.{para}"
                            text = josephus_text_data.get(lookup_key, "Text for this reference was not found.")
                            
                            final_data_for_website[chapter][verse].append({
                                "ref": ref_str,
                                "text": text
                            })
                    except (ValueError, KeyError):
                        continue

# Convert to regular dicts for cleaner JSON
final_output = {str(k): {str(vk): vv for vk, vv in v.items()} for k, v in final_data_for_website.items()}

# Save the final JSON to a file
with open('full_parallels.json', 'w', encoding='utf-8') as f:
    json.dump(final_output, f, indent=2)

print("Successfully created 'full_parallels.json'. You can now use this file in your website.")