from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import shutil
import tempfile
import xml.etree.ElementTree as ET

DOCX = Path("docs/MajorProjectReport_Revised_QML_CMB.docx")
TARGET_BREAKS = 65
NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}

tmp_dir = Path(tempfile.mkdtemp())
work = tmp_dir / "work"
with ZipFile(DOCX, "r") as z:
    z.extractall(work)

xml_path = work / "word" / "document.xml"
tree = ET.parse(xml_path)
root = tree.getroot()
breaks = []
for parent in root.iter():
    for child in list(parent):
        if child.tag == f"{{{NS['w']}}}br" and child.attrib.get(f"{{{NS['w']}}}type") == "page":
            breaks.append((parent, child))

remove_count = max(0, len(breaks) - TARGET_BREAKS)
if remove_count:
    # Keep early front-matter and major chapter spacing. Compact later repeated section breaks.
    candidates = breaks[12:]
    step = max(1, len(candidates) // remove_count)
    picked = []
    idx = 0
    while len(picked) < remove_count and idx < len(candidates):
        picked.append(candidates[idx])
        idx += step
    if len(picked) < remove_count:
        for item in reversed(candidates):
            if item not in picked:
                picked.append(item)
                if len(picked) == remove_count:
                    break
    for parent, child in picked:
        parent.remove(child)

tree.write(xml_path, encoding="UTF-8", xml_declaration=True)

backup = DOCX.with_suffix(".before_compact.docx")
shutil.copy2(DOCX, backup)
with ZipFile(DOCX, "w", ZIP_DEFLATED) as out:
    for path in work.rglob("*"):
        if path.is_file():
            out.write(path, path.relative_to(work).as_posix())

print(f"removed={remove_count}")
print(DOCX)
