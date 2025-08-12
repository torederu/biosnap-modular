import re
from typing import List, Dict
import fitz  # PyMuPDF
import pandas as pd

# --- Helpers -----------------------------------------------------------------

def read_pdf_lines_from_bytes(pdf_bytes: bytes) -> List[str]:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    lines: List[str] = []
    for i in range(doc.page_count):
        page = doc[i]
        text = page.get_text() or ""
        for raw in text.splitlines():
            s = re.sub(r"\s+", " ", raw).strip()
            lines.append(s)
    return lines


def is_result_header(line: str) -> bool:
    return line.strip().lower().startswith("result")


def is_desired_range(line: str) -> bool:
    return "desired range" in line.lower()


def parse_desired_range(line: str) -> str:
    m = re.search(r"desired range\s*:\s*(.*)$", line, flags=re.I)
    return m.group(1).strip() if m else ""


QUAL_KEYWORDS = {
    "NEGATIVE", "POSITIVE", "LOW", "HIGH",
    "DETECTED", "NOT DETECTED",
    "REACTIVE", "NONREACTIVE", "INDETERMINATE",
}


def is_qualifier(line: str) -> bool:
    t = line.strip().upper()
    return t in QUAL_KEYWORDS


PII_HINTS = re.compile(
    r"^(name|dob|date of birth|sex|age|specimen|report status|collected date|phone|physician)\b",
    flags=re.I,
)


def humanize_result_text(text: str) -> str:
    """Capitalize only the first letter of all-uppercase alpha tokens, keep others as-is.
    Examples: 'NEGATIVE' -> 'Negative', '12.6 LOW' -> '12.6 Low', 'mg/dL' stays 'mg/dL'.
    """
    tokens = text.split()
    fixed_tokens = []
    for tok in tokens:
        if tok.isalpha() and tok.isupper():
            fixed_tokens.append(tok.capitalize())
        else:
            fixed_tokens.append(tok)
    return " ".join(fixed_tokens)


def parse_results(lines: List[str]) -> List[Dict[str, str]]:
    out: List[Dict[str, str]] = []
    n = len(lines)
    i = 0
    while i < n:
        line = lines[i]
        if is_result_header(line):
            # Expect next non-empty line to be test name
            i += 1
            while i < n and not lines[i].strip():
                i += 1
            if i >= n:
                break
            test_name = lines[i].strip()
            # Guard against picking up headers that look like PII
            if PII_HINTS.search(test_name):
                i += 1
                continue
            # Advance to desired range
            i += 1
            desired = ""
            while i < n and not is_desired_range(lines[i]):
                # If another 'Result' shows up, bail on this block
                if is_result_header(lines[i]):
                    break
                i += 1
            if i < n and is_desired_range(lines[i]):
                desired = parse_desired_range(lines[i])
                i += 1
            # Next non-empty line(s) should be observed value and maybe a qualifier
            observed_parts: List[str] = []
            while i < n and not lines[i].strip():
                i += 1
            if i < n and not is_result_header(lines[i]) and not is_desired_range(lines[i]):
                observed_parts.append(lines[i].strip())
                i += 1
            if i < n and is_qualifier(lines[i]):
                observed_parts.append(lines[i].strip())
                i += 1
            observed_raw = " ".join(observed_parts).strip()
            observed = humanize_result_text(observed_raw)
            if test_name and desired:
                out.append({
                    "Test Name": test_name,
                    "Desired Range": desired,
                    "Result": observed,
                })
            else:
                i += 1
        else:
            i += 1
    return out


def extract_results_to_dataframe(pdf_bytes: bytes) -> pd.DataFrame:
    """Extract structured test results from a lab PDF (bytes) to a DataFrame."""
    lines = read_pdf_lines_from_bytes(pdf_bytes)
    rows = parse_results(lines)
    df = pd.DataFrame(rows)
    if not df.empty and "Result" in df.columns:
        df["Result"] = df["Result"].apply(humanize_result_text)
    return df 