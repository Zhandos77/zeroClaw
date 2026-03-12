"""
TTS (Text-to-Speech) Skill for ZeroClaw
Provides text-to-speech conversion using Google TTS
"""

from .tts_simple import tts_speak, tts_save, tts_voices

__all__ = ['tts_speak', 'tts_save', 'tts_voices']

__version__ = '1.0.0'