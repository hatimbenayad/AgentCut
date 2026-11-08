"""
AgentCut Intelligence: Disfluency, Filler-Word & Repetition Detector
Spec reference: docs/specs/video-intelligence/spec.md
"""

import re
from typing import List, Dict, Any
from agentcut.intelligence.transcribe import SentenceSegment, WordToken

class DisfluencyDetector:
    """Detects spoken filler words and immediate repetitions in English and Spanish."""

    EN_FILLERS = {
        "um", "uh", "uh-huh", "like", "you know", "sort of", "kind of",
        "basically", "literally", "i mean", "right", "actually"
    }

    ES_FILLERS = {
        "este", "bueno", "o sea", "eh", "em", "sabes", "entonces", "tipo",
        "digamos", "vale"
    }

    def __init__(self, language: str = "en"):
        self.language = language
        self.active_fillers = self.EN_FILLERS | (self.ES_FILLERS if language == "es" else set())

    def analyze(self, sentences: List[SentenceSegment]) -> List[Dict[str, Any]]:
        disfluencies: List[Dict[str, Any]] = []

        for sent in sentences:
            # 1. Flag individual filler words
            for idx, word_tok in enumerate(sent.words):
                norm = re.sub(r"[^\w\s]", "", word_tok.word.lower())
                if norm in self.active_fillers:
                    word_tok.is_filler = True
                    disfluencies.append({
                        "type": "filler_word",
                        "text": word_tok.word,
                        "start": word_tok.start,
                        "end": word_tok.end,
                        "duration": round(word_tok.end - word_tok.start, 3),
                        "sentence_id": sent.sentence_id,
                        "recommended_action": "review_cut"
                    })

            # 2. Flag immediate repeated words (e.g. "the the", "we we")
            for i in range(len(sent.words) - 1):
                w1 = re.sub(r"[^\w]", "", sent.words[i].word.lower())
                w2 = re.sub(r"[^\w]", "", sent.words[i+1].word.lower())
                if w1 and w1 == w2 and (sent.words[i+1].start - sent.words[i].end < 0.8):
                    disfluencies.append({
                        "type": "repetition",
                        "text": f"{sent.words[i].word} {sent.words[i+1].word}",
                        "start": sent.words[i].start,
                        "end": sent.words[i+1].end,
                        "duplicate_word_start": sent.words[i].start,
                        "duplicate_word_end": sent.words[i].end,
                        "sentence_id": sent.sentence_id,
                        "recommended_action": "cut_first_token"
                    })

        return disfluencies

