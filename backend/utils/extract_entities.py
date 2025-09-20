import re

def extract_emails(text: str):
    return re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)

def extract_phones(text: str):
    return re.findall(r"\+?\d[\d -]{8,}\d", text)
