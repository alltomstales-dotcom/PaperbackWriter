"""Narrate a chapter file to WAV with Kokoro text-to-speech (runs locally, CPU or GPU).

Optional dependency: pip install "paperbackwriter[audio]" (kokoro, soundfile, numpy,
espeakng-loader). Words the English phonemizer gets wrong can be fixed with a JSON
file of {"word": "IPA"} overrides; see examples/pronunciations/.
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path

SAMPLE_RATE = 24000
NUMBERS = ("Zero One Two Three Four Five Six Seven Eight Nine Ten Eleven Twelve Thirteen Fourteen "
           "Fifteen Sixteen Seventeen Eighteen Nineteen Twenty").split()


def spoken_heading(first_paragraph: str) -> str:
    """'Chapter 3: The Tide' -> 'Chapter Three. The Tide.'"""
    m = re.fullmatch(r"Chapter (\d+): (.+)", first_paragraph.strip())
    if not m:
        return first_paragraph
    n = int(m.group(1))
    return f"Chapter {NUMBERS[n] if n < len(NUMBERS) else n}. {m.group(2).rstrip('.')}."


def prepare(text: str, say: dict[str, str]) -> str:
    """Straighten quotes and mark pronunciation overrides as Kokoro [word](/IPA/)."""
    text = text.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    if not say:
        return text
    word = re.compile(r"(?<![\w\[])(" + "|".join(map(re.escape, sorted(say, key=len, reverse=True))) + r")(?![\w\]])")
    return word.sub(lambda m: f"[{m.group(1)}](/{say[m.group(1)]}/)", text)


def narrate(chapter: Path, out: Path, voice: str = "bm_george", speed: float = 0.95,
            lang: str = "b", pronunciations: Path | None = None, max_paragraphs: int = 0) -> float:
    """Write one chapter to a WAV file. Returns its length in minutes."""
    import numpy as np
    import soundfile as sf
    try:  # espeak-ng bundled as a wheel, so no system package is needed
        import espeakng_loader
        from phonemizer.backend.espeak.wrapper import EspeakWrapper
        EspeakWrapper.set_library(espeakng_loader.get_library_path())
        os.environ.setdefault("ESPEAK_DATA_PATH", espeakng_loader.get_data_path())
    except ImportError:
        pass
    from kokoro import KPipeline

    say = json.loads(Path(pronunciations).read_text(encoding="utf-8")) if pronunciations else {}
    pipe = KPipeline(lang_code=lang)

    def speak(text: str):
        chunks = [np.asarray(r.audio, dtype=np.float32) for r in pipe(prepare(text, say), voice=voice, speed=speed)
                  if getattr(r, "audio", None) is not None]
        return np.concatenate(chunks) if chunks else np.zeros(0, np.float32)

    paras = [p.strip() for p in Path(chapter).read_text(encoding="utf-8").split("\n\n") if p.strip()]
    paras[0] = spoken_heading(paras[0])
    if max_paragraphs:
        paras = paras[:max_paragraphs]
    silence = lambda seconds: np.zeros(int(SAMPLE_RATE * seconds), np.float32)
    parts = [silence(0.5)]
    for i, p in enumerate(paras):
        if p == "* * *":
            parts.append(silence(1.2))
            continue
        parts += [speak(p), silence(1.4 if i == 0 else 0.45)]
    parts.append(silence(1.5))
    audio = np.concatenate(parts)
    sf.write(str(out), audio, SAMPLE_RATE)
    return len(audio) / SAMPLE_RATE / 60
