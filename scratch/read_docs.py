import zipfile
import xml.etree.ElementTree as ET
import os

def docx_to_text(path):
    try:
        namespaces = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        text = []
        with zipfile.ZipFile(path) as docx:
            tree = ET.parse(docx.open('word/document.xml'))
            root = tree.getroot()
            for para in root.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p'):
                para_text = []
                for run in para.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t'):
                    if run.text:
                        para_text.append(run.text)
                text.append("".join(para_text))
        return "\n".join(text)
    except Exception as e:
        return f"Error reading {path}: {e}"

base_path = r"d:\Redrob AI hackathon\[PUB] India_runs_data_and_ai_challenge\[PUB] India_runs_data_and_ai_challenge\India_runs_data_and_ai_challenge"
files = ["README.docx", "job_description.docx", "redrob_signals_doc.docx", "submission_spec.docx"]

for f in files:
    full_path = os.path.join(base_path, f)
    print(f"=== {f} ===")
    content = docx_to_text(full_path)
    # Save text representation in the same folder or scratch folder
    txt_name = f.replace(".docx", ".txt")
    out_path = os.path.join(r"C:\Users\USER\.gemini\antigravity\brain\f6d152af-6f94-40e4-be41-05c6c66e22cb\scratch", txt_name)
    with open(out_path, "w", encoding="utf-8") as out:
        out.write(content)
    print(f"Saved to {out_path} (length: {len(content)})")
