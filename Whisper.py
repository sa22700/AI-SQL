import os
import queue
import threading
import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel

MODEL_DIR = os.path.join(os.path.dirname(__file__), "faster-whisper-small.en")
SR = 16000
BEAM = 5

_model = None
_model_lock = threading.Lock()

def _get_model() -> WhisperModel:
    global _model
    if _model is None:
        with _model_lock:
            if _model is None:
                _model = WhisperModel(MODEL_DIR, device="cpu", compute_type="int8")
    return _model

def record_audio(samplerate: int = SR) -> np.ndarray:
    q: queue.Queue[np.ndarray] = queue.Queue()
    stop = threading.Event()

    def callback(indata, frames, time_info, status):
        q.put(indata.copy())

    def waiter():
        input("Recording... press Enter to stop: ")
        stop.set()

    threading.Thread(target=waiter, daemon=True).start()
    with sd.InputStream(samplerate=samplerate, channels=1, dtype="float32", callback=callback):
        while not stop.is_set():
            sd.sleep(50)
    chunks = []
    while not q.empty():
        chunks.append(q.get())
    if not chunks:
        return np.zeros((0,), dtype=np.float32)
    return np.concatenate(chunks, axis=0).reshape(-1).astype(np.float32)

def speech_to_text(language: str = "en") -> str:
    model = _get_model()
    audio = record_audio(SR)
    if audio.size == 0:
        return ""
    segments, info = model.transcribe(
        audio,
        language=language,
        task="transcribe",
        beam_size=BEAM,
        vad_filter=True,
    )
    return " ".join(
        (s.text or "").strip() for s in segments if (s.text or "").strip()
    ).strip()
