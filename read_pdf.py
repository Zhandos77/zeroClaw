#!/usr/bin/env python3
import PyPDF2

pdf_path = "/root/.zeroclaw/workspace/telegram_files/PDF document.pdf"

try:
    pdf = PyPDF2.PdfReader(pdf_path)
    print(f"Страниц: {len(pdf.pages)}")
    print(f"\n=== СОДЕРЖИМОЕ PDF ===\n")
    
    for i, page in enumerate(pdf.pages):
        text = page.extract_text()
        if text and text.strip():
            print(f"--- Страница {i+1} ---")
            print(text)
            print("\n")
        else:
            print(f"--- Страница {i+1} ---")
            print("[Нет текста или текст в изображениях]")
            print("\n")
            
except Exception as e:
    print(f"Ошибка: {e}")
