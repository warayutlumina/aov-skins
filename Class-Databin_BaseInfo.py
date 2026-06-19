#โปรแกรมแปลงข้อมูล Bytes เป็นข้อความ
#ใช้สำหรับแปลงข้อมูลจากรูปแบบ Bytes ให้อยู่ในรูปแบบข้อความ (String) เพื่อให้ง่ายต่อการตรวจสอบ วิเคราะห์ และจัดการข้อมูลภายในไฟล์
#โปรแกรมนี้จัดทำขึ้นเพื่อการใช้งานส่วนบุคคลและผู้ที่ได้รับอนุญาตเท่านั้น
#ห้ามคัดลอก ดัดแปลง แจกจ่าย ส่งต่อ อัปโหลด เผยแพร่ หรือจำหน่ายโปรแกรมนี้ไม่ว่าทั้งหมดหรือบางส่วน โดยไม่ได้รับอนุญาตจากผู้พัฒนา
#สงวนลิขสิทธิ์ทุกประการ @https://www.youtube.com/@JKBNMZX

import os
import sys
import ast
import time


SOURCE_BYTES_DIR = r"Databin"
DEST_VERSTRING_DIR = r"Databin_string"

SOURCE_VERSTRING_DIR = r"Databin_string"
DEST_BYTES_DIR = r"Databin_restored"

TARGET_EXT = ".bytes"   
OUTPUT_EXT = ".txt"     

CREDIT_LINE = "โปรแกรมนี้ทำโดย JKBNMZX สำหรับแปลงข้อมูล"
# -----------------------------------------------------------------------


def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def show_processing_banner(filename: str) -> None:
    clear_screen()
    print(f'Decompression "{filename}"')
    print(CREDIT_LINE)




def convert_file_bytes_to_string(src_path: str, dst_path: str) -> None:
    """อ่านไฟล์ bytes แล้วแปลงเป็น Python repr string แล้วเขียนเป็น UTF-8"""
    with open(src_path, "rb") as f:
        data = f.read()
    string_version = repr(data)
    with open(dst_path, "w", encoding="utf-8") as f:
        f.write(string_version)


def convert_file_string_to_bytes(src_path: str, dst_path: str) -> None:
    """อ่านไฟล์ verstring (Python repr ของ bytes) แล้วแปลงกลับเป็น bytes จริง"""
    with open(src_path, "r", encoding="utf-8") as f:
        content = f.read().strip()
    data = ast.literal_eval(content)
    if not isinstance(data, bytes):
        raise ValueError("เนื้อหาในไฟล์ไม่ใช่ bytes literal ที่ถูกต้อง")
    with open(dst_path, "wb") as f:
        f.write(data)


# ---------------------- ฟังก์ชันเดินลูปทั้งโฟลเดอร์ ----------------------

def mode_bytes_to_verstring(source_dir: str, dest_dir: str):
    total = converted = copied = errors = 0
    for root, dirs, files in os.walk(source_dir):
        rel_path = os.path.relpath(root, source_dir)
        target_dir = os.path.join(dest_dir, rel_path) if rel_path != "." else dest_dir
        os.makedirs(target_dir, exist_ok=True)

        for filename in files:
            total += 1
            src_path = os.path.join(root, filename)
            show_processing_banner(filename)
            try:
                if filename.lower().endswith(TARGET_EXT):
                    dst_filename = filename + OUTPUT_EXT
                    dst_path = os.path.join(target_dir, dst_filename)
                    convert_file_bytes_to_string(src_path, dst_path)
                    converted += 1
                else:
                    dst_path = os.path.join(target_dir, filename)
                    with open(src_path, "rb") as fsrc, open(dst_path, "wb") as fdst:
                        fdst.write(fsrc.read())
                    copied += 1
            except Exception as e:
                errors += 1
                print(f"[ERROR] {src_path}: {e}")
                time.sleep(1)
    return total, converted, copied, errors


def mode_verstring_to_bytes(source_dir: str, dest_dir: str):
    total = converted = copied = errors = 0
    for root, dirs, files in os.walk(source_dir):
        rel_path = os.path.relpath(root, source_dir)
        target_dir = os.path.join(dest_dir, rel_path) if rel_path != "." else dest_dir
        os.makedirs(target_dir, exist_ok=True)

        for filename in files:
            total += 1
            src_path = os.path.join(root, filename)
            show_processing_banner(filename)
            try:
                if filename.lower().endswith(OUTPUT_EXT):
                    dst_filename = filename[: -len(OUTPUT_EXT)]  # ตัด .txt ออก -> heroSkin.bytes
                    dst_path = os.path.join(target_dir, dst_filename)
                    convert_file_string_to_bytes(src_path, dst_path)
                    converted += 1
                else:
                    dst_path = os.path.join(target_dir, filename)
                    with open(src_path, "rb") as fsrc, open(dst_path, "wb") as fdst:
                        fdst.write(fsrc.read())
                    copied += 1
            except Exception as e:
                errors += 1
                print(f"[ERROR] {src_path}: {e}")
                time.sleep(1)
    return total, converted, copied, errors


# ---------------------- ส่วนเมนู / UI ----------------------

def show_summary(total: int, converted: int, copied: int, errors: int, dest_dir: str) -> None:
    clear_screen()
    print(CREDIT_LINE)
    print("-" * 40)
    print(f"ไฟล์ทั้งหมด      : {total}")
    print(f"แปลงสำเร็จ       : {converted}")
    print(f"คัดลอกตรง        : {copied}")
    print(f"ผิดพลาด          : {errors}")
    print(f"ผลลัพธ์อยู่ที่     : {os.path.abspath(dest_dir)}")
    print("-" * 40)
    input("กด Enter เพื่อกลับไปเมนูหลัก...")


def show_menu() -> None:
    clear_screen()
    print("=" * 40)
    print("   JKBNMZX Bytes/Verstring Converter")
    print("=" * 40)
    print("[A1] : convert bytes      -> verstring")
    print("[B2] : convert verstring  -> bytes")
    print("[0 ] : ออกจากโปรแกรม")
    print("-" * 40)


def ask_path(prompt_text: str, default_path: str) -> str:
    user_input = input(f"{prompt_text} (ค่าเริ่มต้น: {default_path}) : ").strip()
    return user_input if user_input else default_path


def main() -> None:
    while True:
        show_menu()
        choice = input("เลือกโหมด (A1 / B2 / 0) : ").strip().upper()

        if choice in ("0", "X", "Q", "EXIT"):
            clear_screen()
            print("ออกจากโปรแกรมแล้ว ขอบคุณที่ใช้งาน")
            break

        elif choice in ("A1", "A"):
            source_dir = ask_path("ระบุโฟลเดอร์ต้นทาง (bytes)", SOURCE_BYTES_DIR)
            dest_dir = ask_path("ระบุโฟลเดอร์ปลายทาง (verstring)", DEST_VERSTRING_DIR)
            if not os.path.isdir(source_dir):
                clear_screen()
                print(f"ไม่พบโฟลเดอร์: {source_dir}")
                input("กด Enter เพื่อกลับไปเมนูหลัก...")
                continue
            total, converted, copied, errors = mode_bytes_to_verstring(source_dir, dest_dir)
            show_summary(total, converted, copied, errors, dest_dir)

        elif choice in ("B2", "B"):
            source_dir = ask_path("ระบุโฟลเดอร์ต้นทาง (verstring)", SOURCE_VERSTRING_DIR)
            dest_dir = ask_path("ระบุโฟลเดอร์ปลายทาง (bytes)", DEST_BYTES_DIR)
            if not os.path.isdir(source_dir):
                clear_screen()
                print(f"ไม่พบโฟลเดอร์: {source_dir}")
                input("กด Enter เพื่อกลับไปเมนูหลัก...")
                continue
            total, converted, copied, errors = mode_verstring_to_bytes(source_dir, dest_dir)
            show_summary(total, converted, copied, errors, dest_dir)

        else:
            clear_screen()
            print("ตัวเลือกไม่ถูกต้อง กรุณาเลือกใหม่")
            time.sleep(1.5)


if __name__ == "__main__":
    main()
