# Arena of Valor

#XML & Bytes Converter

#This tool or software is designed for converting XML and Bytes data under the terms and conditions of the provider:

# github: https://github.com/warayutlumina

#Features

#- Convert XML data to Bytes format.
#- Convert Bytes data to XML format.
#- Convert AssetRefs data.
#- Convert Model data.
#- Easy to use.
#- Includes installation instructions.

#Requirements

#Before using this tool, make sure to install the required dependency:

#pip install tqdm

#Python Version

#This tool was developed using Python version 3.9.7.

#However, it is compatible with all Python versions and can be used across different environments without modification.

#Notes

#This software is intended for educational, research, and asset conversion purposes only. Users are responsible for ensuring that their use complies with all applicable terms, conditions, and licensing requirements of the original content provider.

import os
import struct
import shutil
import zipfile
import xml.etree.ElementTree as ET
from xml.dom import minidom
from tqdm import tqdm

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BYTES_DIR = os.path.join(BASE_DIR, "Bytes")
XML_DIR = os.path.join(BASE_DIR, "Xml")
TEMP_DIR = os.path.join(BASE_DIR, "tools")

os.makedirs(BYTES_DIR, exist_ok=True)
os.makedirs(XML_DIR, exist_ok=True)

class colors:
    GREEN = "\033[1;92m"
    RED = "\033[1;91m"
    YELLOW = "\033[1;93m"
    LIGHT_GRAY = "\033[37m"
    DARK_GRAY = "\033[90m"
    RESET = "\033[0m"

RESET = colors.RESET
GREEN_GLOW = colors.GREEN
RED_GLOW = colors.RED

def log_info(msg):
    print(f"[{GREEN_GLOW}INFO{RESET}] {msg}")

def log_error(msg):
    print(f"[{RED_GLOW}ERROR{RESET}] {msg}")

def byteint(i):
    return struct.pack("<I", i)

def indent(elem, level=0):
    i = "\n" + level * "    "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "    "
        for e in elem:
            indent(e, level + 1)
        if not e.tail or not e.tail.strip():
            e.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

class BinaryParser:
    def __init__(self, filepath):
        self.filepath = filepath
        self.byt = open(filepath, "rb")
        self.root = None

    def read_int(self):
        return int.from_bytes(self.byt.read(4), "little")

    def read_string(self):
        length = self.read_int()
        return self.byt.read(length - 4).decode("utf-8", errors="ignore")

    def read_attribute(self):
        pos = self.byt.tell()
        offset = self.read_int()
        attr_type = self.read_int()

        data = self.byt.read(offset - 8).decode("utf-8", errors="ignore")            
        self.byt.seek(pos + offset, 0)

        if attr_type == 5:
            return data[1:]
        elif attr_type == 6:
            return {"Var": data.replace("JT", "")}
        elif attr_type == 8:
            return {"Type": data.replace("Type", "")}
        else:
            return {str(attr_type): data}

    def parse_node(self):
        node_size = self.read_int()
        start = self.byt.tell()

        tag = self.read_string()            
        if tag == "Element":            
            tag = "Item"            
        
        node = ET.Element(tag)            
        
        self.read_int()            
        attr_count = self.read_int()            
        
        for _ in range(attr_count):            
            attr = self.read_attribute()            
            if isinstance(attr, str):            
                node.text = attr            
            else:            
                node.attrib.update(attr)            
        
        self.read_int()            
        
        child_block = self.read_int()            
        if child_block and child_block > 4:            
            child_count = self.read_int()            
            for _ in range(child_count):            
                child = self.parse_node()            
                node.append(child)            
        
        self.byt.seek(start + node_size - 4)            
        return node

    def parse(self):
        self.root = self.parse_node()

    def save(self, output_path):
        xml_str = minidom.parseString(
            ET.tostring(self.root)
        ).toprettyxml(indent="    ")

        os.makedirs(os.path.dirname(output_path), exist_ok=True)            
        with open(output_path, "w", encoding="utf-8") as f:            
            f.write(xml_str)

    def close(self):
        self.byt.close()

def process_root(root, skinpos, copyright_text):
    rm = 0
    l = ''

    for i, child in enumerate(root):
        if child.tag == 'LobbyScale':
            rm += i
            l += (child.text or '')
        else:
            if child.tag == 'SkinPrefab':
                break

    if rm > 0 and rm < len(root):
        root.remove(root[rm])
        for i, child in enumerate(root):
            if i > rm and child.tag == 'LobbyScale':
                child.text = l

    a = {}
    a['Var'], a['Type'] = ('Array', 'System.String[]')

    parent = None
    for child in root:
        if child.tag == 'copyright':
            parent = child
            break

    if parent is None:
        parent = ET.Element('copyright', a)

    elements = [
        ('Github', 'https://github.com/jkbnmzx'),
        ('Youtube', 'https://www.youtube.com/jkbnmzx'),
        ('Discord', 'https://discord.gg/3bPVkMAUmc')
    ]

    for i, child in enumerate(root):
        if child.tag == 'ActorName':
            if not (child.text or '').endswith('_XmlBytes'):
                child.text = (child.text or '') + '_XmlBytes'

            if not any(c.tag == 'Item' for c in parent):            
                ET.SubElement(parent, 'Item', child.attrib).text = copyright_text            
            
            for subtag, subvalue in elements:            
                if not any(c.tag == subtag for c in parent):            
                    ET.SubElement(parent, subtag, child.attrib).text = subvalue            
            
            if parent not in root:            
                root.insert(i + 1, parent)            
            
            break

    return root

def clean_empty_directories(base_dir):
    
    for root_dir, dirs, files in os.walk(base_dir, topdown=False):
        for d in dirs:
            dir_path = os.path.join(root_dir, d)
            try:
                
                if not os.listdir(dir_path):
                    os.rmdir(dir_path)
            except Exception:
                pass

#: bytes -> xml

def convert_single_bytes_to_xml(bytes_path, xml_path):
    parser = BinaryParser(bytes_path)            
    parser.parse()            
    process_root(parser.root, None, "COPYRIGHT JKBNMZX. ALL RIGHTS RESERVED")            
    parser.save(xml_path)            
    parser.close()

def mode_bytes_to_xml():
    tmplist = []
    for root_dir, _, files in os.walk(BYTES_DIR):
        for file in files:
            if file.endswith(".bytes"):
                tmplist.append((root_dir, file))
                
    if not tmplist:
        log_info("ไม่พบไฟล์ .bytes ในโฟลเดอร์ bytes")
        return

    ncols = 80
    desc_str = f'{colors.YELLOW}[{colors.GREEN}INFO   {colors.LIGHT_GRAY}] {colors.DARK_GRAY}xml  {colors.RESET}'
    
    for root_dir, file in tqdm(tmplist, bar_format='{desc} {percentage:3.0f}%{r_bar}', desc=desc_str, ncols=ncols):
        input_path = os.path.join(root_dir, file)
        relative = os.path.relpath(input_path, BYTES_DIR)
        
        if file.endswith(".pkg.bytes"):
            unique_temp = os.path.join(TEMP_DIR, file + "_extracted")
            try:
                os.makedirs(unique_temp, exist_ok=True)
                
                with zipfile.ZipFile(input_path, 'r') as zip_ref:
                    zip_ref.extractall(unique_temp)
                
                for sub_root, _, sub_files in os.walk(unique_temp):
                    for sub_file in sub_files:
                        if sub_file.endswith(".bytes"):
                            s_bytes_path = os.path.join(sub_root, sub_file)
                            s_xml_path = os.path.join(sub_root, sub_file.replace(".bytes", ".xml"))
                            
                            convert_single_bytes_to_xml(s_bytes_path, s_xml_path)
                            os.remove(s_bytes_path)
                
                output_pkg_path = os.path.join(XML_DIR, relative)
                os.makedirs(os.path.dirname(output_pkg_path), exist_ok=True)
                
                with zipfile.ZipFile(output_pkg_path, 'w', zipfile.ZIP_DEFLATED) as zip_out:
                    for sub_root, _, sub_files in os.walk(unique_temp):
                        for sub_file in sub_files:
                            full_p = os.path.join(sub_root, sub_file)
                            rel_p = os.path.relpath(full_p, unique_temp)
                            zip_out.write(full_p, rel_p)
                
                shutil.rmtree(unique_temp)
                os.remove(input_path)
                
            except Exception as e:
                tqdm.write(f"\n[{RED_GLOW}ERROR{RESET}] เกิดข้อผิดพลาดกับไฟล์แพ็คเกจ {file} ({e})")
                if os.path.exists(unique_temp):
                    shutil.rmtree(unique_temp)
        
        else:
            try:
                output_path = os.path.join(XML_DIR, relative.replace(".bytes", ".xml"))
                convert_single_bytes_to_xml(input_path, output_path)
                os.remove(input_path)
            except Exception as e:            
                tqdm.write(f"\n[{RED_GLOW}ERROR{RESET}] {file} ({e})")
                
    clean_empty_directories(BYTES_DIR)

def bytestr(s):
    return byteint(len(s) + 4) + s.encode()

def byteattr(key, attr):
    if key == "Var":
        aid = 6
        s = "JT" + attr[key]
    elif key == "Type":
        aid = 8
        s = "Type" + attr[key]
    else:
        aid = int(key)
        s = attr[key]
    b = s.encode()
    return byteint(len(b) + 8) + byteint(aid) + b

def bytenode(node):
    name = "Element" if node.tag == "Item" else node.tag
    data = bytestr(name)

    attr_data = b""
    count = len(node.attrib)

    for k in node.attrib:
        attr_data += byteattr(k, node.attrib)

    if node.text and node.text.strip():
        v = ("V" + node.text).encode()
        attr_data += byteint(len(v) + 8) + byteint(5) + v
        count += 1

    attr_block = byteint(len(attr_data) + 8) + byteint(count) + attr_data + byteint(4)

    child_data = b""
    if len(node):
        for c in node:
            child_data += bytenode(c)
        child_data = byteint(len(child_data) + 8) + byteint(len(node)) + child_data
    else:
        child_data = byteint(4)

    body = data + attr_block + child_data
    return byteint(len(body) + 4) + body


#  xml -> bytes

def convert_single_xml_to_bytes(xml_path, bytes_path):
    tree = ET.parse(xml_path)            
    byt = bytenode(tree.getroot())            
    with open(bytes_path, "wb") as f:            
        f.write(byt)

def mode_xml_to_bytes():
    tmplist = []
    for root_dir, _, files in os.walk(XML_DIR):
        for file in files:
            if file.endswith(".pkg.bytes") or file.endswith(".xml"):
                tmplist.append((root_dir, file))
                
    if not tmplist:
        log_info("ไม่พบไฟล์ในโฟลเดอร์ output")
        return

    ncols = 80
    desc_str = f'{colors.YELLOW}[{colors.GREEN}INFO   {colors.LIGHT_GRAY}] {colors.DARK_GRAY}bytes  {colors.RESET}'

    for root_dir, file in tqdm(tmplist, bar_format='{desc} {percentage:3.0f}%{r_bar}', desc=desc_str, ncols=ncols):
        input_path = os.path.join(root_dir, file)
        relative = os.path.relpath(input_path, XML_DIR)
        
        if file.endswith(".pkg.bytes"):
            unique_temp = os.path.join(TEMP_DIR, file + "_rebuilt")
            try:
                os.makedirs(unique_temp, exist_ok=True)
                
                with zipfile.ZipFile(input_path, 'r') as zip_ref:
                    zip_ref.extractall(unique_temp)
                    
                for sub_root, _, sub_files in os.walk(unique_temp):
                    for sub_file in sub_files:
                        if sub_file.endswith(".xml"):
                            s_xml_path = os.path.join(sub_root, sub_file)
                            s_bytes_path = os.path.join(sub_root, sub_file.replace(".xml", ".bytes"))
                            
                            convert_single_xml_to_bytes(s_xml_path, s_bytes_path)
                            os.remove(s_xml_path)
                            
                output_pkg_path = os.path.join(BYTES_DIR, relative)
                os.makedirs(os.path.dirname(output_pkg_path), exist_ok=True)
                
                with zipfile.ZipFile(output_pkg_path, 'w', zipfile.ZIP_DEFLATED) as zip_out:
                    for sub_root, _, sub_files in os.walk(unique_temp):
                        for sub_file in sub_files:
                            full_p = os.path.join(sub_root, sub_file)
                            rel_p = os.path.relpath(full_p, unique_temp)
                            zip_out.write(full_p, rel_p)
                            
                shutil.rmtree(unique_temp)
                os.remove(input_path)
            except Exception as e:
                tqdm.write(f"\n[{RED_GLOW}ERROR{RESET}] เกิดข้อผิดพลาดในการแปลงกลับไฟล์แพ็คเกจ {file} ({e})")
                if os.path.exists(unique_temp):
                    shutil.rmtree(unique_temp)

        elif file.endswith(".xml"):
            try:
                output_path = os.path.join(BYTES_DIR, relative.replace(".xml", ".bytes"))
                os.makedirs(os.path.dirname(output_path), exist_ok=True)            
                
                convert_single_xml_to_bytes(input_path, output_path)
                os.remove(input_path)
            except Exception as e:            
                tqdm.write(f"\n[{RED_GLOW}ERROR{RESET}] {file} ({e})")
                
   
    clean_empty_directories(XML_DIR)

if os.path.exists(TEMP_DIR):
    shutil.rmtree(TEMP_DIR)

while True:
    print("\n[INFO] 1: Bytes -> Xml")
    print("[INFO] 2: Xml -> Bytes")
    print("[INFO] 0: Exit")

    mode = input("[เลือก]: ").strip()
    print("")

    if mode == "1":
        mode_bytes_to_xml()
    elif mode == "2":
        mode_xml_to_bytes()
    elif mode == "0":
        break
    else:
        log_error("The selected mode is incorrect")

while True:
    ans = input("\n[INFO] Select Y/N: ").strip().lower()
    if ans == "y":
        break
    elif ans == "n":
        exit()
    else:
        print("Select Y/N")
        