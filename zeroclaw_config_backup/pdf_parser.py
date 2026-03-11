import PyPDF2
import re
from datetime import datetime

def read_pdf_with_pypdf2(pdf_path):
    """Чтение PDF с использованием PyPDF2"""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            print(f"📄 Файл: {pdf_path}")
            print(f"📊 Страниц: {len(pdf_reader.pages)}")
            
            full_text = ""
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                page_text = page.extract_text()
                
                if page_text:
                    print(f"\n=== Страница {page_num + 1} ===")
                    print(page_text[:500])  # Первые 500 символов каждой страницы
                    full_text += page_text + "\n\n"
            
            return full_text
            
    except Exception as e:
        return f"❌ Ошибка при чтении PDF: {str(e)}"

if __name__ == "__main__":
    # Тестируем на твоём файле
    pdf_path = "/root/.zeroclaw/workspace/telegram_files/Документ_23022026.pdf"
    result = read_pdf_with_pypdf2(pdf_path)
    
    if isinstance(result, str) and not result.startswith("❌"):
        print(f"\n✅ Успешно прочитано. Общий размер текста: {len(result)} символов")
        
        # Анализ структуры
        lines = result.split('\n')
        print(f"\n📈 Строк в документе: {len(lines)}")
        
        # Поиск ключевых слов
        keywords = ['договор', 'соглашение', 'акт', 'счет', 'паспорт', 'заявление']
        for keyword in keywords:
            matches = [line for line in lines if keyword.lower() in line.lower()]
            if matches:
                print(f"\n🔍 Найдено '{keyword}':")
                for match in matches[:3]:
                    print(f"   - {match[:100]}...")
    else:
        print(result)