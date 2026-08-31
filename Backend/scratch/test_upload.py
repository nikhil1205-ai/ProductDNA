import requests

pdf_content = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kinds [] /Count 0 >>\nendobj\ntrailer\n<< /Root 1 0 R >>\n%%EOF"

files = {
    'file': ('sample.pdf', pdf_content, 'application/pdf')
}
data = {
    'request_id': 'REQ-TEST-123',
    'type': 'pdf',
    'name': 'sample.pdf',
    'subtype': 'technical_datasheet'
}

response = requests.post('http://localhost:8000/api/resources', data=data, files=files)
print("STATUS:", response.status_code)
print("RESPONSE:", response.text)
