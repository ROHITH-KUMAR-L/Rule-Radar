import json
import re
import uuid

def parse_delhi_rules(input_file, output_file):
    rules = []
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f.readlines() if line.strip() != '' and line.strip() != '\t']
    
    i = 0
    # skip header
    while i < len(lines):
        if re.match(r'^\d+\.$', lines[i]):
            break
        i += 1
        
    while i < len(lines):
        if re.match(r'^\d+\.$', lines[i]):
            # Start of a record
            try:
                record_id = str(uuid.uuid4())
                offense_name = lines[i+1]
                mva = lines[i+2]
                first_offense = lines[i+3]
                subsequent_offense = lines[i+4]
                
                rules.append({
                    "id": record_id,
                    "offense_name_en": offense_name,
                    "offense_section": mva,
                    "fine": first_offense,
                    "repetitive_fine": subsequent_offense
                })
                i += 5
            except IndexError:
                print("Reached end of list abruptly")
                break
        else:
            i += 1

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(rules, f, indent=4, ensure_ascii=False)
    
    print(f"Successfully extracted {len(rules)} rules to {output_file}")

if __name__ == "__main__":
    parse_delhi_rules('delhi_rules.txt', 'frontend/src/data/delhi_rules.json')
