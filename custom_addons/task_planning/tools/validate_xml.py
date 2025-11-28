import os
import sys
import glob
from xml.etree import ElementTree as ET

root = os.path.dirname(os.path.dirname(__file__))
xml_files = glob.glob(os.path.join(root, "views", "*.xml")) + glob.glob(os.path.join(root, "data", "*.xml"))

errors = False
for f in xml_files:
    try:
        ET.parse(f)
        print(f"OK: {f}")
    except ET.ParseError as e:
        print(f"ERROR parsing {f}: {e}")
        errors = True

if errors:
    sys.exit(1)
else:
    print("All XML files are well-formed (ElementTree parse).")
