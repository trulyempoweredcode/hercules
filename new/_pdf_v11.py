from pypdf import PdfReader
r = PdfReader(r"D:/claude-custom-projects/Ai-Editor-Sites/hurcules-development.com-bespoke/new/Hercules-Development-Presentation-Overview-v11.pdf")
out = []
for i, p in enumerate(r.pages):
    out.append(f"\n===== PAGE {i+1} =====\n")
    try:
        out.append(p.extract_text() or "")
    except Exception as e:
        out.append(f"[ERR: {e}]")
with open(r"D:/claude-custom-projects/Ai-Editor-Sites/hurcules-development.com-bespoke/new/_pdf_v11.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(out))
print("OK pages:", len(r.pages))
