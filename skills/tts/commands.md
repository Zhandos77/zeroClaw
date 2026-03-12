# TTS команды

## `/tts <текст>`

Шаги:
1. `OUTFILE="/tmp/tts_$(cat /proc/sys/kernel/random/uuid | tr -d '-').mp3"`
2. `edge-tts --voice ru-RU-SvetlanaNeural --text "<текст>" --write-media "$OUTFILE"`
3. Проверить: `ls "$OUTFILE"`
4. Ответить: `[AUDIO:$OUTFILE]`

Имя файла — только ASCII (UUID без дефисов).
