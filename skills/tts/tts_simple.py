#!/usr/bin/env python3
"""
Простая реализация TTS (Text-to-Speech) навыка.
Использует gTTS для онлайн-озвучивания текста.
"""

import os
import tempfile
from typing import Optional, Dict, List
import subprocess
import sys

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False


class TTSEngine:
    """Движок для преобразования текста в речь."""
    
    def __init__(self):
        self.supported_languages = {
            'ru': 'русский',
            'en': 'английский',
            'kk': 'казахский',
            'fr': 'французский',
            'de': 'немецкий',
            'es': 'испанский',
            'it': 'итальянский',
            'ja': 'японский',
            'ko': 'корейский',
            'zh-cn': 'китайский (упрощенный)',
            'zh-tw': 'китайский (традиционный)',
        }
        
        self.default_voice = 'default'
        self.default_speed = 1.0
        
    def speak(self, text: str, language: str = 'ru', 
              voice: str = 'default', speed: float = 1.0) -> bool:
        """
        Озвучить текст.
        
        Args:
            text: Текст для озвучивания
            language: Код языка (ru, en, kk и т.д.)
            voice: Голос (пока не используется, зарезервировано)
            speed: Скорость речи (пока не используется, зарезервировано)
            
        Returns:
            bool: Успешно ли выполнено озвучивание
        """
        if not GTTS_AVAILABLE:
            print("Ошибка: gTTS не установлен. Установите: pip install gtts")
            return False
            
        if not text or not text.strip():
            print("Ошибка: Пустой текст")
            return False
            
        if language not in self.supported_languages:
            print(f"Ошибка: Язык '{language}' не поддерживается. "
                  f"Доступные: {', '.join(self.supported_languages.keys())}")
            return False
            
        try:
            # Создаем временный файл
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp_file:
                temp_path = tmp_file.name
            
            # Создаем TTS объект и сохраняем в файл
            tts = gTTS(text=text, lang=language, slow=False)
            tts.save(temp_path)
            
            # Пытаемся воспроизвести файл
            if self._play_audio(temp_path):
                print(f"✅ Текст озвучен ({self.supported_languages[language]})")
                success = True
            else:
                print("⚠️  Файл создан, но воспроизвести не удалось")
                success = True  # Файл создан успешно
                
            # Удаляем временный файл
            try:
                os.unlink(temp_path)
            except:
                pass
                
            return success
            
        except Exception as e:
            print(f"❌ Ошибка при озвучивании: {e}")
            return False
    
    def save(self, text: str, filename: str, 
             language: str = 'ru', format: str = 'mp3') -> Optional[str]:
        """
        Сохранить озвученный текст в файл.
        
        Args:
            text: Текст для озвучивания
            filename: Имя выходного файла
            language: Код языка
            format: Формат аудио (mp3, wav, ogg) - пока только mp3
            
        Returns:
            str: Путь к сохраненному файлу или None при ошибке
        """
        if not GTTS_AVAILABLE:
            print("Ошибка: gTTS не установлен. Установите: pip install gtts")
            return None
            
        if not text or not text.strip():
            print("Ошибка: Пустой текст")
            return None
            
        if language not in self.supported_languages:
            print(f"Ошибка: Язык '{language}' не поддерживается. "
                  f"Доступные: {', '.join(self.supported_languages.keys())}")
            return None
            
        # Проверяем расширение файла
        if not filename.lower().endswith('.mp3'):
            filename = filename + '.mp3'
            
        try:
            # Создаем TTS объект и сохраняем в файл
            tts = gTTS(text=text, lang=language, slow=False)
            tts.save(filename)
            
            # Проверяем, что файл создан
            if os.path.exists(filename):
                file_size = os.path.getsize(filename)
                print(f"✅ Аудиофайл сохранен: {filename} ({file_size} байт)")
                return os.path.abspath(filename)
            else:
                print("❌ Файл не создан")
                return None
                
        except Exception as e:
            print(f"❌ Ошибка при сохранении: {e}")
            return None
    
    def get_voices(self) -> Dict[str, List[str]]:
        """
        Получить список доступных голосов и языков.
        
        Returns:
            Dict с информацией о доступных голосах
        """
        return {
            'supported_languages': self.supported_languages,
            'default_voice': self.default_voice,
            'default_speed': self.default_speed,
            'engine': 'gTTS (Google Text-to-Speech)',
            'online': True,
            'max_text_length': 5000,
        }
    
    def _play_audio(self, filepath: str) -> bool:
        """
        Воспроизвести аудиофайл.
        
        Args:
            filepath: Путь к аудиофайлу
            
        Returns:
            bool: Успешно ли воспроизведено
        """
        # Пытаемся использовать различные плееры
        players = [
            ['mpg321', filepath],  # MP3 плеер
            ['mpg123', filepath],  # Альтернативный MP3 плеер
            ['play', filepath],    # SoX плеер
            ['aplay', filepath],   # ALSA плеер
            ['ffplay', '-nodisp', '-autoexit', filepath],  # FFmpeg плеер
        ]
        
        for player_cmd in players:
            try:
                player = player_cmd[0]
                if self._check_command_exists(player):
                    subprocess.run(player_cmd, check=False, 
                                 stdout=subprocess.DEVNULL, 
                                 stderr=subprocess.DEVNULL)
                    return True
            except:
                continue
                
        print("⚠️  Не найден подходящий аудиоплеер. Установите один из: "
              "mpg321, mpg123, play (sox), aplay, ffplay")
        return False
    
    def _check_command_exists(self, command: str) -> bool:
        """Проверить, существует ли команда в системе."""
        try:
            subprocess.run(['which', command], check=True, 
                         stdout=subprocess.DEVNULL, 
                         stderr=subprocess.DEVNULL)
            return True
        except:
            return False


# Функции для использования из других модулей
def tts_speak(text: str, language: str = 'ru', 
              voice: str = 'default', speed: float = 1.0) -> bool:
    """Озвучить текст."""
    engine = TTSEngine()
    return engine.speak(text, language, voice, speed)


def tts_save(text: str, filename: str, 
             language: str = 'ru', format: str = 'mp3') -> Optional[str]:
    """Сохранить озвученный текст в файл."""
    engine = TTSEngine()
    return engine.save(text, filename, language, format)


def tts_voices() -> Dict:
    """Получить список доступных голосов и языков."""
    engine = TTSEngine()
    return engine.get_voices()


def test_tts():
    """Тестовая функция для проверки TTS."""
    print("🧪 Тестирование TTS навыка...")
    
    engine = TTSEngine()
    
    # Проверяем доступность gTTS
    if not GTTS_AVAILABLE:
        print("❌ gTTS не установлен. Установите: pip install gtts")
        return False
    
    # Тест 1: Получение информации о голосах
    voices_info = engine.get_voices()
    print(f"✅ Поддерживаемые языки: {len(voices_info['supported_languages'])}")
    
    # Тест 2: Озвучивание короткого текста
    print("🔊 Тест озвучивания...")
    success = engine.speak("Привет, это тест TTS", language='ru')
    
    # Тест 3: Сохранение в файл
    print("💾 Тест сохранения файла...")
    saved_file = engine.save("Тестовое сообщение для сохранения", 
                           "test_tts_output.mp3", language='ru')
    
    if saved_file:
        print(f"✅ Файл сохранен: {saved_file}")
        
    return success and saved_file is not None


if __name__ == "__main__":
    # Если запущен напрямую, запускаем тест
    if len(sys.argv) > 1:
        if sys.argv[1] == "test":
            test_tts()
        elif sys.argv[1] == "speak" and len(sys.argv) > 2:
            text = " ".join(sys.argv[2:])
            tts_speak(text)
        elif sys.argv[1] == "save" and len(sys.argv) > 3:
            text = sys.argv[2]
            filename = sys.argv[3]
            language = sys.argv[4] if len(sys.argv) > 4 else 'ru'
            tts_save(text, filename, language)
        elif sys.argv[1] == "voices":
            print(tts_voices())
        else:
            print("Использование:")
            print("  python tts_simple.py test           - запустить тест")
            print("  python tts_simple.py speak <текст>  - озвучить текст")
            print("  python tts_simple.py save <текст> <файл> [язык] - сохранить в файл")
            print("  python tts_simple.py voices         - показать доступные голоса")
    else:
        test_tts()