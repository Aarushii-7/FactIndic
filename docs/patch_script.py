import re

with open("/Users/aarushi/factIndic/docs/make_handbook.py", "r") as f:
    content = f.read()

# Add clean_xml definition near top of make_handbook.py
clean_xml_func = '''
def clean_xml(s):
    if not isinstance(s, str):
        return s
    tokens = re.split(r'(</?[bi]>|<br\s*/>|</?code>)', s)
    out = []
    for t in tokens:
        if t in ['<b>', '</b>', '<i>', '</i>', '<br/>', '<br />', '<code>', '</code>']:
            out.append(t)
        else:
            t = t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            out.append(t)
    return ''.join(out)

def SafeParagraph(text, style, **kwargs):
    return Paragraph(clean_xml(text), style, **kwargs)
'''

content = content.replace("class NumberedCanvas(canvas.Canvas):", clean_xml_func + "\nclass NumberedCanvas(canvas.Canvas):")
# Replace Paragraph( with SafeParagraph(
content = content.replace("Paragraph(", "SafeParagraph(")
# But keep the import Paragraph intact
content = content.replace("from reportlab.platypus import (\n    SimpleDocTemplate, SafeParagraph,", "from reportlab.platypus import (\n    SimpleDocTemplate, Paragraph,")

with open("/Users/aarushi/factIndic/docs/make_handbook.py", "w") as f:
    f.write(content)

print("make_handbook.py patched successfully!")
