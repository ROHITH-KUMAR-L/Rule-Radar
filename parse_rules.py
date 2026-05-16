import re
import json

def parse_rules(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # We will split by the Sr. No which appears at the beginning of a line.
    # Like: ^\d+\s+Sec
    # But sometimes the Sr. No is just \d+ followed by space.
    
    # Let's use a simpler heuristic. We know the fine is usually at the end of the entry block.
    # We can split the text by the Sr. No. 1 to 233.
    
    rules = []
    
    matches = list(re.finditer(r'^(\d{1,3})\s+(.*?)(?=^\d{1,3}\s+|$)', content, re.MULTILINE | re.DOTALL))
    
    for i in range(len(matches)):
        num = matches[i].group(1)
        text = matches[i].group(2).replace('\n', ' ').strip()
        
        # Now text contains the whole block for this rule.
        # It ends with Fine and Repetitive Fine.
        # Fines can be "5,000 Same", "500 1,500", "0 Non-Compoundable", "Same"
        
        # Let's extract the last two tokens if they match fine patterns
        tokens = text.split()
        
        rep_fine = tokens[-1]
        fine = tokens[-2] if len(tokens) > 1 else ""
        
        # If the fine is a Marathi word, it might be an issue, but let's assume fines are numbers or specific words
        
        # For Offense Section and Name:
        # It usually starts with "Sec " or "CMVR " or "MMVR " or "MVDR "
        # Let's extract the first few tokens that look like a section
        
        section_tokens = []
        name_tokens = []
        
        parsing_section = True
        for token in tokens:
            if parsing_section:
                # If it has English characters and numbers, or slashes, it might be section
                if re.match(r'^[a-zA-Z0-9\/\-\(\)]+$', token) and not re.match(r'^[a-z]+$', token, re.I) and not (token.lower() in ['driving', 'without', 'license', 'vehicle']):
                    section_tokens.append(token)
                else:
                    parsing_section = False
                    name_tokens.append(token)
            else:
                name_tokens.append(token)
                
        # The name_tokens now contains English Name + Marathi Name + Fines
        # Let's try to filter out the Marathi text to just get the English name.
        # We can keep everything until we hit the first character outside ASCII.
        
        english_name = []
        for word in name_tokens[:-2]: # Skip the last two fine tokens
            # Check if word contains Marathi/Devanagari characters
            if any(ord(c) > 127 for c in word):
                break
            english_name.append(word)
            
        rules.append({
            "id": f"MUM-{num.zfill(3)}",
            "offense_section": " ".join(section_tokens),
            "offense_name_en": " ".join(english_name).strip(' -'),
            "fine": fine,
            "repetitive_fine": rep_fine,
            "raw_text": text # Keep raw text for debugging
        })
        
    return rules

rules = parse_rules('extracted_mumbai_rules_utf8.txt')
with open('frontend/src/data/mumbai_rules.json', 'w', encoding='utf-8') as f:
    json.dump(rules, f, indent=2, ensure_ascii=False)
print(f"Successfully extracted {len(rules)} rules.")
