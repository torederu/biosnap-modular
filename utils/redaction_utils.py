import fitz
import re

def redact_prenuvo_pdf(input_path, output_path):
    doc = fitz.open(input_path)
    patient_name = None
    for i in range(min(3, len(doc))):
        text = doc[i].get_text()
        match = re.search(r"Patient:\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)", text)
        if match:
            patient_name = match.group(1).strip()
            break
    patterns = [
        r"Time of scan:\s?.*",
        r"Sex:\s?.*",
        r"\b(Male|Female|Other|Non-Binary|Transgender|Intersex)\b",
        r"Height:\s?.*",
        r"Weight:\s?.*",
        r"Date of Birth:\s?.*",
        r"\b\d{4}-\d{2}-\d{2}\b",
        r"Facility:\s?.*",
        r"Patient:\s?.*",
        r"Study:\s?[a-f0-9\-]{36}",
        r"REPORT RECIPIENT\(S\):\s?.*",
    ]
    if patient_name:
        escaped = re.escape(patient_name)
        patterns.append(rf"\b{escaped}\b")
        patterns.append(rf"Patient:\s*{escaped}")
    for page in doc:
        text = page.get_text()
        for pattern in patterns:
            for match in re.findall(pattern, text):
                for rect in page.search_for(match):
                    page.add_redact_annot(rect, fill=(0, 0, 0))
        page.apply_redactions()
    doc.save(output_path)
    doc.close()

def remove_leading_sparse_page(doc, min_lines=5):
    if len(doc) > 1:
        first_page = doc[0]
        text = first_page.get_text().strip()
        if len(text.splitlines()) < min_lines:
            doc.delete_page(0)


def redact_trudiagnostic_pdf(input_path, output_path):
    doc = fitz.open(input_path)
    # Remove first page if it is mostly blank (fewer than 5 lines)
    remove_leading_sparse_page(doc, min_lines=5)
    # Read names to redact from redact_names.txt
    try:
        with open('redact_names.txt', 'r') as f:
            names_to_redact = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        names_to_redact = []
    for i, page in enumerate(doc):
        if i == 0:
            body_patterns = [
                r"Sex:\s*\w+",
                r"Age:\s*\d+",
                r"https?://[^\s]+",
                r"www\.[^\s]+"
            ]
            for pattern in body_patterns:
                matches = re.finditer(pattern, page.get_text())
                for match in matches:
                    matched_text = match.group()
                    for rect in page.search_for(matched_text):
                        page.add_redact_annot(rect, fill=(0, 0, 0))
            text_blocks = page.get_text("blocks")
            for j, block in enumerate(text_blocks):
                if "Age:" in block[4]:
                    if j > 0:
                        name_block = text_blocks[j - 1]
                        rect = fitz.Rect(name_block[:4])
                        page.add_redact_annot(rect, fill=(0, 0, 0))
                    break
            for block in text_blocks:
                text = block[4]
                if any(keyword in text for keyword in ["ID#:", "Collected:", "Reported:"]):
                    rect = fitz.Rect(block[:4])
                    page.add_redact_annot(rect, fill=(0, 0, 0))
        for block in page.get_text("blocks"):
            if "PROVIDED BY:" in block[4] or "trudiagnostic.com" in block[4] or "trudiagnostic/apireports.aspx" in block[4]:
                rect = fitz.Rect(block[:4])
                page.add_redact_annot(rect, fill=(0, 0, 0))
        # Redact any name from the fallback list
        for name in names_to_redact:
            for rect in page.search_for(name):
                page.add_redact_annot(rect, fill=(0, 0, 0))
        page.apply_redactions()
    doc.save(output_path)
    doc.close() 