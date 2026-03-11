#!/usr/bin/env python3
"""
Универсальный читатель PDF файлов
Поддерживает: PyPDF2, pdfplumber, pdfminer
"""

import os
import sys
import json
from typing import Dict, List, Any
import warnings
warnings.filterwarnings('ignore')

class PDFReader:
    def __init__(self):
        self.results = {}
        
    def read_with_pypdf2(self, file_path: str) -> Dict[str, Any]:
        """Чтение PDF через PyPDF2"""
        try:
            from PyPDF2 import PdfReader
            
            with open(file_path, 'rb') as file:
                pdf = PdfReader(file)
                text = ""
                for page_num, page in enumerate(pdf.pages):
                    text += f"\n--- Страница {page_num + 1} ---\n"
                    text += page.extract_text()
                
                return {
                    "success": True,
                    "method": "PyPDF2",
                    "pages": len(pdf.pages),
                    "text": text,
                    "metadata": pdf.metadata
                }
        except Exception as e:
            return {"success": False, "method": "PyPDF2", "error": str(e)}
    
    def read_with_pdfplumber(self, file_path: str) -> Dict[str, Any]:
        """Чтение PDF через pdfplumber (лучше для таблиц)"""
        try:
            import pdfplumber
            
            with pdfplumber.open(file_path) as pdf:
                text = ""
                tables_data = []
                
                for page_num, page in enumerate(pdf.pages):
                    text += f"\n--- Страница {page_num + 1} ---\n"
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text
                    else:
                        text += "[Текст не найден или изображение]"
                    
                    # Пытаемся извлечь таблицы
                    tables = page.extract_tables()
                    if tables:
                        for table_num, table in enumerate(tables):
                            tables_data.append({
                                "page": page_num + 1,
                                "table": table_num + 1,
                                "data": table
                            })
                
                return {
                    "success": True,
                    "method": "pdfplumber",
                    "pages": len(pdf.pages),
                    "text": text,
                    "tables": tables_data,
                    "has_images": any(page.images for page in pdf.pages)
                }
        except Exception as e:
            return {"success": False, "method": "pdfplumber", "error": str(e)}
    
    def read_with_pdfminer(self, file_path: str) -> Dict[str, Any]:
        """Чтение PDF через pdfminer (самый мощный)"""
        try:
            from pdfminer.high_level import extract_text
            
            text = extract_text(file_path)
            
            return {
                "success": True,
                "method": "pdfminer",
                "text": text,
                "length": len(text)
            }
        except Exception as e:
            return {"success": False, "method": "pdfminer", "error": str(e)}
    
    def analyze_pdf_structure(self, file_path: str) -> Dict[str, Any]:
        """Анализ структуры PDF файла"""
        try:
            from PyPDF2 import PdfReader
            
            with open(file_path, 'rb') as file:
                pdf = PdfReader(file)
                
                structure = {
                    "pages": len(pdf.pages),
                    "metadata": dict(pdf.metadata) if pdf.metadata else {},
                    "encrypted": pdf.is_encrypted,
                    "file_size": os.path.getsize(file_path),
                    "file_path": file_path
                }
                
                # Анализ первой страницы
                if pdf.pages:
                    first_page = pdf.pages[0]
                    structure["first_page_size"] = {
                        "width": float(first_page.mediabox.width),
                        "height": float(first_page.mediabox.height)
                    }
                
                return {"success": True, "structure": structure}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def read_all_methods(self, file_path: str) -> Dict[str, Any]:
        """Пробуем все методы чтения"""
        if not os.path.exists(file_path):
            return {"success": False, "error": f"Файл не найден: {file_path}"}
        
        print(f"📄 Анализируем файл: {file_path}")
        print(f"📊 Размер файла: {os.path.getsize(file_path) / 1024:.2f} KB")
        
        results = {
            "file": file_path,
            "size_kb": os.path.getsize(file_path) / 1024,
            "methods": {}
        }
        
        # 1. Анализ структуры
        print("\n🔍 Анализ структуры PDF...")
        structure = self.analyze_pdf_structure(file_path)
        results["structure"] = structure
        
        # 2. Пробуем все методы чтения
        methods = [
            ("PyPDF2", self.read_with_pypdf2),
            ("pdfplumber", self.read_with_pdfplumber),
            ("pdfminer", self.read_with_pdfminer)
        ]
        
        best_result = None
        for method_name, method_func in methods:
            print(f"\n🔄 Пробуем {method_name}...")
            result = method_func(file_path)
            results["methods"][method_name] = result
            
            if result.get("success") and "text" in result:
                text_length = len(result["text"])
                print(f"   ✅ Успешно! Извлечено символов: {text_length}")
                
                if not best_result or text_length > len(best_result.get("text", "")):
                    best_result = result
                    best_result["method"] = method_name
            else:
                print(f"   ❌ Ошибка: {result.get('error', 'Неизвестная ошибка')}")
        
        # 3. Сохраняем лучший результат
        if best_result:
            results["best_method"] = best_result["method"]
            results["extracted_text"] = best_result.get("text", "")
            results["pages"] = best_result.get("pages", 0)
            results["success"] = True
            
            # Сохраняем текст в файл
            output_file = file_path.replace(".pdf", "_extracted.txt")
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(results["extracted_text"])
            print(f"\n💾 Текст сохранён в: {output_file}")
            
        else:
            results["success"] = False
            results["error"] = "Не удалось извлечь текст ни одним методом"
        
        return results
    
    def print_summary(self, results: Dict[str, Any]):
        """Красивый вывод результатов"""
        print("\n" + "="*60)
        print("📊 РЕЗУЛЬТАТЫ ИЗВЛЕЧЕНИЯ ТЕКСТА ИЗ PDF")
        print("="*60)
        
        if not results.get("success"):
            print(f"❌ ОШИБКА: {results.get('error', 'Неизвестная ошибка')}")
            return
        
        structure = results.get("structure", {}).get("structure", {})
        
        print(f"📄 Файл: {results['file']}")
        print(f"📏 Размер: {results['size_kb']:.2f} KB")
        print(f"📑 Страниц: {structure.get('pages', 'неизвестно')}")
        print(f"🔒 Зашифрован: {'Да' if structure.get('encrypted') else 'Нет'}")
        print(f"🏆 Лучший метод: {results.get('best_method', 'не определён')}")
        
        if "extracted_text" in results:
            text = results["extracted_text"]
            print(f"\n📝 Извлечённый текст ({len(text)} символов):")
            print("-"*40)
            
            # Показываем первые 1000 символов
            preview = text[:1000]
            if len(text) > 1000:
                preview += "\n[... текст продолжается ...]"
            print(preview)
            
            # Сохраняем полный текст в файл
            output_file = results['file'].replace('.pdf', '_full.txt')
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(text)
            print(f"\n💾 Полный текст сохранён в: {output_file}")
        
        # Показываем таблицы если есть
        pdfplumber_result = results["methods"].get("pdfplumber", {})
        if pdfplumber_result.get("success") and pdfplumber_result.get("tables"):
            print(f"\n📊 Найдено таблиц: {len(pdfplumber_result['tables'])}")
            for table_info in pdfplumber_result["tables"]:
                print(f"  • Страница {table_info['page']}, таблица {table_info['table']}: "
                      f"{len(table_info['data'])} строк")
        
        print("\n" + "="*60)

def main():
    if len(sys.argv) < 2:
        print("Использование: python3 pdf_reader.py <путь_к_pdf_файлу>")
        print("Пример: python3 pdf_reader.py документ.pdf")
        sys.exit(1)
    
    pdf_file = sys.argv[1]
    
    if not os.path.exists(pdf_file):
        print(f"❌ Файл не найден: {pdf_file}")
        sys.exit(1)
    
    reader = PDFReader()
    results = reader.read_all_methods(pdf_file)
    reader.print_summary(results)
    
    # Сохраняем результаты в JSON
    json_file = pdf_file.replace('.pdf', '_results.json')
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)
    print(f"📁 JSON результаты сохранены в: {json_file}")

if __name__ == "__main__":
    main()