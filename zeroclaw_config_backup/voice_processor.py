#!/usr/bin/env python3
"""
Обработчик голосовых сообщений для ZeroClaw
Использует Vosk для распознавания речи
"""

import os
import json
import wave
import subprocess
import tempfile
from pathlib import Path

class VoiceProcessor:
    def __init__(self, model_path=None):
        """
        Инициализация процессора голосовых сообщений
        
        Args:
            model_path: Путь к модели Vosk (по умолчанию ищет в workspace)
        """
        self.model_path = model_path or self._find_vosk_model()
        self.model_loaded = False
        self._check_dependencies()
        
        # Загружаем модель при инициализации
        if self.model_path:
            try:
                import vosk
                self.model = vosk.Model(self.model_path)
                self.model_loaded = True
                print(f"✅ Модель Vosk загружена: {self.model_path}")
            except Exception as e:
                print(f"❌ Ошибка загрузки модели Vosk: {e}")
                self.model_loaded = False
        
    def _find_vosk_model(self):
        """Найти модель Vosk в workspace"""
        possible_paths = [
            "/root/.zeroclaw/workspace/model_vosk_ru",
            "/root/.zeroclaw/workspace/vosk-model-small-ru-0.22",
            "./model_vosk_ru"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                print(f"✅ Найдена модель Vosk: {path}")
                return path
        
        print("⚠️ Модель Vosk не найдена. Попробуйте скачать:")
        print("wget https://alphacephei.com/vosk/models/vosk-model-small-ru-0.22.zip")
        print("unzip vosk-model-small-ru-0.22.zip")
        return None
    
    def _check_dependencies(self):
        """Проверить зависимости"""
        try:
            import vosk
            print("✅ Vosk импортируется успешно")
        except ImportError:
            print("❌ Vosk не установлен. Установите: pip3 install vosk")
            
        # Проверим доступные аудио инструменты
        self.audio_tools = {}
        
        # Проверка ffmpeg
        try:
            result = subprocess.run(['which', 'ffmpeg'], capture_output=True, text=True)
            if result.stdout:
                self.audio_tools['ffmpeg'] = result.stdout.strip()
                print(f"✅ ffmpeg найден: {self.audio_tools['ffmpeg']}")
            else:
                print("⚠️ ffmpeg не найден. Будем использовать альтернативные методы")
        except:
            print("⚠️ Не удалось проверить ffmpeg")
    
    def convert_audio(self, input_path, output_path, target_format="wav"):
        """
        Конвертировать аудио файл в нужный формат
        
        Args:
            input_path: Входной файл
            output_path: Выходной файл
            target_format: Целевой формат (wav, mp3 и т.д.)
            
        Returns:
            bool: Успешно ли конвертирование
        """
        input_path = str(input_path)
        output_path = str(output_path)
        
        # Проверка существования файла
        if not os.path.exists(input_path):
            print(f"❌ Файл не существует: {input_path}")
            return False
        
        # Определяем формат по расширению
        input_ext = Path(input_path).suffix.lower()
        
        # Если уже WAV и нужен WAV - просто копируем
        if input_ext == '.wav' and target_format == 'wav':
            import shutil
            shutil.copy2(input_path, output_path)
            print(f"✅ Файл уже в формате WAV, скопирован: {output_path}")
            return True
        
        # Пробуем разные методы конвертации
        methods = [
            self._convert_with_ffmpeg,
            self._convert_with_pydub,
            self._convert_with_sox,
        ]
        
        for method in methods:
            try:
                if method(input_path, output_path, target_format):
                    print(f"✅ Конвертация успешна методом {method.__name__}")
                    return True
            except Exception as e:
                print(f"⚠️ Метод {method.__name__} не сработал: {e}")
                continue
        
        print("❌ Не удалось конвертировать файл ни одним методом")
        return False
    
    def _convert_with_ffmpeg(self, input_path, output_path, target_format):
        """Конвертация через ffmpeg"""
        if 'ffmpeg' not in self.audio_tools:
            return False
        
        cmd = [
            self.audio_tools['ffmpeg'],
            '-i', input_path,
            '-ar', '16000',      # Частота дискретизации 16kHz
            '-ac', '1',          # Моно
            '-acodec', 'pcm_s16le',  # Кодек для WAV
            output_path,
            '-y'                 # Перезаписать если существует
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0
    
    def _convert_with_pydub(self, input_path, output_path, target_format):
        """Конвертация через pydub"""
        try:
            from pydub import AudioSegment
            
            # Загружаем аудио
            audio = AudioSegment.from_file(input_path)
            
            # Конвертируем в моно 16kHz
            audio = audio.set_frame_rate(16000)
            audio = audio.set_channels(1)
            
            # Сохраняем в WAV
            audio.export(output_path, format="wav")
            return True
        except ImportError:
            print("⚠️ pydub не установлен. Установите: pip3 install pydub")
            return False
        except Exception as e:
            print(f"⚠️ Ошибка pydub: {e}")
            return False
    
    def _convert_with_sox(self, input_path, output_path, target_format):
        """Конвертация через sox"""
        try:
            result = subprocess.run(['which', 'sox'], capture_output=True, text=True)
            if not result.stdout:
                return False
            
            cmd = [
                'sox',
                input_path,
                '-r', '16000',      # Частота дискретизации
                '-c', '1',          # Каналы (моно)
                '-b', '16',         # Битность
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False
    
    def recognize_speech(self, audio_path, language="ru"):
        """
        Распознать речь в аудио файле
        
        Args:
            audio_path: Путь к аудио файлу (WAV 16kHz mono)
            language: Язык распознавания
            
        Returns:
            str: Распознанный текст или None при ошибке
        """
        if not self.model_path:
            print("❌ Модель Vosk не загружена")
            return None
        
        try:
            import vosk
            
            # Загружаем модель
            model = vosk.Model(self.model_path)
            
            # Открываем WAV файл
            wf = wave.open(str(audio_path), "rb")
            
            # Проверяем формат
            if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getframerate() != 16000:
                print(f"⚠️ Неверный формат WAV файла:")
                print(f"   Каналы: {wf.getnchannels()} (должно быть 1)")
                print(f"   Размер сэмпла: {wf.getsampwidth()} (должно быть 2)")
                print(f"   Частота: {wf.getframerate()} (должно быть 16000)")
                wf.close()
                return None
            
            # Создаём распознаватель
            rec = vosk.KaldiRecognizer(model, wf.getframerate())
            rec.SetWords(True)
            
            # Читаем и распознаём
            results = []
            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break
                if rec.AcceptWaveform(data):
                    results.append(json.loads(rec.Result()))
            
            # Финальный результат
            results.append(json.loads(rec.FinalResult()))
            
            wf.close()
            
            # Извлекаем текст из результатов
            text = " ".join([result.get("text", "") for result in results if result.get("text")])
            
            return text.strip() if text else "⚠️ Речь не распознана"
            
        except ImportError:
            print("❌ Vosk не установлен. Установите: pip3 install vosk")
            return None
        except Exception as e:
            print(f"❌ Ошибка распознавания: {e}")
            return None
    
    def process_voice_message(self, voice_file_path, output_text_path=None):
        """
        Полная обработка голосового сообщения
        
        Args:
            voice_file_path: Путь к голосовому файлу (OGG, MP3, WAV и т.д.)
            output_text_path: Путь для сохранения текста (опционально)
            
        Returns:
            dict: Результат обработки
        """
        print(f"🎤 Обработка голосового сообщения: {voice_file_path}")
        
        # Создаём временные файлы
        with tempfile.TemporaryDirectory() as tmpdir:
            # Конвертируем в WAV если нужно
            input_path = Path(voice_file_path)
            wav_path = Path(tmpdir) / "converted.wav"
            
            print(f"🔄 Конвертация {input_path.suffix} → WAV...")
            if not self.convert_audio(input_path, wav_path, "wav"):
                return {
                    "success": False,
                    "error": "Не удалось конвертировать аудио",
                    "text": None
                }
            
            # Распознаём речь
            print("🤖 Распознавание речи...")
            text = self.recognize_speech(wav_path)
            
            if not text:
                return {
                    "success": False,
                    "error": "Не удалось распознать речь",
                    "text": None
                }
            
            # Сохраняем текст если нужно
            if output_text_path:
                with open(output_text_path, 'w', encoding='utf-8') as f:
                    f.write(text)
                print(f"💾 Текст сохранён: {output_text_path}")
            
            print(f"✅ Успешно распознано: {len(text)} символов")
            return {
                "success": True,
                "text": text,
                "audio_format": input_path.suffix,
                "model": os.path.basename(self.model_path) if self.model_path else None
            }


def test_voice_processor():
    """Тестирование процессора голосовых"""
    print("🧪 Тестирование VoiceProcessor...")
    
    processor = VoiceProcessor()
    
    if not processor.model_path:
        print("❌ Тест не может быть выполнен: модель Vosk не найдена")
        return
    
    # Создадим тестовый WAV файл (пустой, для проверки)
    import wave
    import struct
    
    test_wav = "/tmp/test_voice.wav"
    
    # Создаём простой WAV файл с тишиной
    with wave.open(test_wav, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(16000)
        
        # 1 секунда тишины
        frames = []
        for i in range(16000):  # 16000 сэмплов для 1 секунды
            frames.append(struct.pack('<h', 0))
        
        wf.writeframes(b''.join(frames))
    
    print(f"📁 Создан тестовый WAV файл: {test_wav}")
    
    # Пробуем распознать
    result = processor.recognize_speech(test_wav)
    
    if result:
        print(f"📝 Результат распознавания: {result}")
    else:
        print("⚠️ Распознавание не удалось (ожидаемо для тишины)")
    
    # Удаляем тестовый файл
    os.remove(test_wav)
    
    print("✅ Тест завершён")


if __name__ == "__main__":
    print("=" * 50)
    print("🎤 Voice Processor for ZeroClaw")
    print("=" * 50)
    
    # Тестирование
    test_voice_processor()
    
    print("\n📋 Инструкция по использованию:")
    print("1. Убедитесь, что установлен Vosk: pip3 install vosk")
    print("2. Скачайте модель: wget https://alphacephei.com/vosk/models/vosk-model-small-ru-0.22.zip")
    print("3. Разархивируйте: unzip vosk-model-small-ru-0.22.zip")
    print("4. Используйте:")
    print("   processor = VoiceProcessor()")
    print("   result = processor.process_voice_message('voice.ogg')")
    print("   print(result['text'])")