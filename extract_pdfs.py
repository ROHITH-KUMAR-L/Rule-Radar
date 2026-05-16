import pypdf

def extract_pdf(input_pdf, output_txt):
    try:
        reader = pypdf.PdfReader(input_pdf)
        with open(output_txt, 'w', encoding='utf-8') as out:
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    out.write(text + "\n")
        print(f"Extracted {input_pdf} to {output_txt}")
    except Exception as e:
        print(f"Failed to extract {input_pdf}: {e}")

if __name__ == "__main__":
    extract_pdf('banglore_traffic_rules.pdf', 'extracted_banglore.txt')
    extract_pdf('chennai_traffic_rules.pdf', 'extracted_chennai.txt')
    extract_pdf('kolkata_traffic_rules.pdf', 'extracted_kolkata.txt')
