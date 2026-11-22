with open("/Users/aarushi/factIndic/docs/make_handbook.py", "r") as f:
    text = f.read()

# Replace def SafeSafeParagraph(text, style, **kwargs):\n    return SafeParagraph(clean_xml(text), style, **kwargs)
old_block = """def SafeSafeParagraph(text, style, **kwargs):
    return SafeParagraph(clean_xml(text), style, **kwargs)"""

new_block = """import re

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
"""

# Replace any existing clean_xml / SafeSafeParagraph definitions
import re
text = re.sub(r'def clean_xml[\s\S]*?def SafeSafeParagraph[\s\S]*?\n\n', '', text)
text = re.sub(r'def clean_xml[\s\S]*?def SafeParagraph[\s\S]*?\n\n', '', text)

text = text.replace("class NumberedCanvas(canvas.Canvas):", new_block + "\nclass NumberedCanvas(canvas.Canvas):")

with open("/Users/aarushi/factIndic/docs/make_handbook.py", "w") as f:
    f.write(text)

print("Fixed make_handbook.py")
