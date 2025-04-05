#!/usr/bin/env python3

import sys
import asyncio
from googletrans import Translator, LANGCODES
from rapidfuzz import process

usage = "Usage: glt <dest language> <? -s> <text to translate>\nLangs: glt -l\nHelp: glt -h"

def supported_langs():
    print(f"Languages:")
    print("<lang> --- <code>")
    for lang, code  in LANGCODES.items():
        print(lang + " --- " + code)
            
def main():
    if sys.argv[1] == "-h":
        print(usage)
        sys.exit(1)

    if sys.argv[1] == "-l":
        supported_langs()
        sys.exit(1)

    if len(sys.argv) < 3:
        print(usage)
        sys.exit(1)
    
    speech = False
    if sys.argv[2] == "-s":
        text_start = sys.argv[3:]
        speech = True
    else :
        text_start = sys.argv[2:]

    lang = sys.argv[1]

    langs = LANGCODES.values()
    lang = process.extractOne(lang, langs)[0]
    
    text = f"{' '.join(text_start).strip()}"
    
    result = asyncio.run(translate_text(lang, text))
    result_text = result.text.strip()
    print(f"Lang: {lang}")
    print(f"Text: {result_text}")
    if speech:
        import platform
        system = platform.system()
        match system:
            case 'Linux': # TODO
                from gtts import gTTS
                import tempfile
                from playsound import playsound
                tts = gTTS(text=result_text, lang=lang)
                # Save to a temporary file and play it
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
                    temp_audio.close()
                    tts.save(temp_audio.name)

            case 'Windows':    
                from pathlib import Path
                import os

                import edge_tts
                async def list_voices():
                    return await edge_tts.list_voices()
                    
                async def get_voice(lang):
                    voices = await list_voices()
                    for voice in voices:
                        if lang in voice['Locale'].strip('-'):
                            return voice["ShortName"]

                async def ed_tts(text, filename, lang):
                    voice = await get_voice(lang)
                    tts = edge_tts.Communicate(text, voice=voice)
                    await tts.save(filename)

                path = Path(__file__).parent / "audio"
                path.mkdir(exist_ok=True)  # Ensure 'audio' directory exists

                files = [f for f in os.listdir(path) if f.endswith(".mp3")]
                files_sorted = sorted(files, reverse=True)

                if files_sorted:
                    filename = path / f"{int(files_sorted[0].replace('.mp3', '')) + 1}.mp3"
                else:
                    filename = path / "1.mp3"
                
                asyncio.run(ed_tts(result_text, filename, lang))

        import pygame
        pygame.mixer.init()
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()

        # Keep script running while the audio plays
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

async def translate_text(lang, text):
    async with Translator() as translator:
        return await translator.translate(dest=lang, text=text)


if __name__ == "__main__":
    main()

