"""
Unit Tests: Video Intelligence Subsystems
"""

import pytest
from agentcut.intelligence.vad import VoiceActivityDetector
from agentcut.intelligence.disfluency import DisfluencyDetector
from agentcut.intelligence.transcribe import SentenceSegment, WordToken
from agentcut.intelligence.ocr import OCREngine

def test_pause_classification():
    vad = VoiceActivityDetector()
    assert vad._classify_pause(0.2) == ("micro_pause", "preserve")
    assert vad._classify_pause(0.5) == ("conversational_pause", "preserve")
    assert vad._classify_pause(1.1) == ("dramatic_pause", "preserve")
    assert vad._classify_pause(2.2) == ("dead_silence", "cut")

def test_disfluency_detection():
    detector = DisfluencyDetector(language="en")
    sentences = [
        SentenceSegment(
            sentence_id="s1",
            text="Um today we we will discuss editing.",
            start=0.0,
            end=4.0,
            words=[
                WordToken("Um", 0.0, 0.4, 0.98),
                WordToken("today", 0.5, 1.0, 0.99),
                WordToken("we", 1.2, 1.5, 0.97),
                WordToken("we", 1.6, 1.9, 0.96),
                WordToken("will", 2.0, 2.3, 0.99),
                WordToken("discuss", 2.4, 2.8, 0.98),
                WordToken("editing", 2.9, 3.4, 0.99),
            ]
        )
    ]

    disfluencies = detector.analyze(sentences)
    types = [d["type"] for d in disfluencies]
    assert "filler_word" in types
    assert "repetition" in types

def test_ocr_temporal_tracking():
    engine = OCREngine()
    # Simulate same text detected on consecutive frames 2.0s apart
    raw_events = [
        {"timestamp": 1.0, "text": "AGENTCUT DEMO", "confidence": 0.95, "box": [100, 200, 300, 250]},
        {"timestamp": 3.0, "text": "AGENTCUT DEMO", "confidence": 0.93, "box": [102, 201, 305, 252]},
    ]
    tracked = engine._temporal_track(raw_events)
    # Must be merged into 1 continuous event from 1.0s to 3.0s
    assert len(tracked) == 1
    assert tracked[0].text == "AGENTCUT DEMO"
    assert tracked[0].start == 1.0
    assert tracked[0].end == 3.0

