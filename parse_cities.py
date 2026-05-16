import re
import json
import uuid

def parse_chennai(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]
        
    rules = []
    current_rule = []
    for line in lines:
        if re.match(r'^\d+\.\s+', line):
            if current_rule:
                rules.append(" ".join(current_rule))
            current_rule = [line]
        elif current_rule:
            current_rule.append(line)
    if current_rule:
        rules.append(" ".join(current_rule))
        
    parsed = []
    for rule in rules:
        # e.g. "1. Contravention of any provision... 177 500 1,500"
        match = re.match(r'^(\d+)\.\s+(.*?)\s+(\S+)\s+(\S+)\s+(\S+)$', rule)
        if match:
            if re.match(r'^[\d\,\-]+$', match.group(4)):
                parsed.append({
                    "id": str(uuid.uuid4()),
                    "offense_name_en": match.group(2).strip(),
                    "offense_section": match.group(3).strip(),
                    "fine": match.group(4).strip(),
                    "repetitive_fine": match.group(5).strip()
                })
        else:
            # Maybe one fine?
            match2 = re.match(r'^(\d+)\.\s+(.*?)\s+(\S+)\s+(\S+)$', rule)
            if match2:
                if re.match(r'^[\d\,\-]+$', match2.group(4)):
                    parsed.append({
                        "id": str(uuid.uuid4()),
                        "offense_name_en": match2.group(2).strip(),
                        "offense_section": match2.group(3).strip(),
                        "fine": match2.group(4).strip(),
                        "repetitive_fine": ""
                    })
                
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(parsed, f, indent=4, ensure_ascii=False)
    print(f"Chennai: Extracted {len(parsed)} rules.")

def parse_kolkata(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f.readlines() if line.strip() and not line.startswith('SL Under') and not line.startswith('Offence') and not line.startswith('OFFENCES AND PENALTIES')]
        
    rules = []
    current_rule = []
    for line in lines:
        if re.match(r'^\d+\s+[A-Za-z0-9\(\)\/]+', line):
            if current_rule:
                rules.append(" ".join(current_rule))
            current_rule = [line]
        elif current_rule:
            current_rule.append(line)
    if current_rule:
        rules.append(" ".join(current_rule))
        
    parsed = []
    for rule in rules:
        # e.g. "1 100(2)CMVR/177MVA Glass ... 500 1500"
        # Wait, there could be 3 fines if 2nd and subsequent are separated? Like 2000 5000 , 10000
        tokens = rule.split()
        if len(tokens) >= 4:
            # find where the description ends and fines begin.
            # Usually fines are digits or commas.
            fine_start = len(tokens) - 1
            while fine_start > 2 and re.match(r'^[0-9\,\-]+$', tokens[fine_start - 1]):
                fine_start -= 1
            
            section = tokens[1]
            desc = " ".join(tokens[2:fine_start])
            fines = " ".join(tokens[fine_start:])
            
            # separate first and repetitive fine if possible
            fine_tokens = fines.split()
            first_fine = fine_tokens[0] if fine_tokens else ""
            rep_fine = " ".join(fine_tokens[1:]) if len(fine_tokens) > 1 else first_fine
            
            parsed.append({
                "id": str(uuid.uuid4()),
                "offense_name_en": desc.strip(),
                "offense_section": section,
                "fine": first_fine,
                "repetitive_fine": rep_fine
            })
            
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(parsed, f, indent=4, ensure_ascii=False)
    print(f"Kolkata: Extracted {len(parsed)} rules.")

def parse_bangalore(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f.readlines() if line.strip() and not line.startswith('Details of')]
        
    rules = []
    current_rule = []
    for line in lines:
        if re.match(r'^\d+\s+', line):
            if current_rule:
                rules.append(" ".join(current_rule))
            current_rule = [line]
        elif current_rule:
            current_rule.append(line)
    if current_rule:
        rules.append(" ".join(current_rule))
        
    parsed = []
    for rule in rules:
        # e.g. "1 Negligence Driving sec 184 IMV Act 1000/-"
        # We need to find "sec" or "Rule" or "CMV" to split name and section
        match = re.search(r'\s+(sec|Rule|CMV|R\.R\.)\s+', rule, re.IGNORECASE)
        if match:
            desc = rule[:match.start()].strip()
            # remove the leading number
            desc = re.sub(r'^\d+\s+', '', desc)
            
            rest = rule[match.start():].strip()
            # try to split section and fine. Fine usually has digits or "Court" or "Rs"
            # It's at the end.
            match_fine = re.search(r'\s+((?:\d+|\d+w|\d+/-|Court|Rs\.|Cancellation).*)$', rest, re.IGNORECASE)
            if match_fine:
                section = rest[:match_fine.start()].strip()
                fine = match_fine.group(1).strip()
            else:
                section = rest
                fine = ""
                
            parsed.append({
                "id": str(uuid.uuid4()),
                "offense_name_en": desc,
                "offense_section": section,
                "fine": fine,
                "repetitive_fine": fine # usually Bangalore lists one fine
            })
            
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(parsed, f, indent=4, ensure_ascii=False)
    print(f"Bangalore: Extracted {len(parsed)} rules.")

if __name__ == "__main__":
    parse_chennai('extracted_chennai.txt', 'frontend/src/data/chennai_rules.json')
    parse_kolkata('extracted_kolkata.txt', 'frontend/src/data/kolkata_rules.json')
    parse_bangalore('extracted_banglore.txt', 'frontend/src/data/banglore_rules.json')
