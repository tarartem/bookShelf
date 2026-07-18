"""
MOD-03: Ukrainian Linguistic Check
-----------------------------------
Verifies that an uploaded EPUB contains genuine Ukrainian-language content.

Strategy (two independent signals, permissive thresholds):
  1. Ukrainian-specific character ratio
     Characters і, є, ї, ґ (and their uppercase equivalents) exist in Ukrainian
     but NOT in Russian (which uses и, е, г instead). A ratio above 0.8% of all
     alphabetic characters is a strong indicator of Ukrainian.

  2. langdetect language classification
     Runs on a 3000-character text sample extracted from the book body.
     Accepts 'uk' (Ukrainian). Rejects only when langdetect is very confident
     the text is a completely different language AND no Ukrainian chars were found.

Decision logic (deliberately permissive to minimise false positives):
  PASS  - Ukrainian char ratio >= 0.8%
  PASS  - langdetect says 'uk'
  FAIL  - Zero Ukrainian chars AND langdetect confidently identifies another language
"""

import re
import logging
import os
from dotenv import load_dotenv
load_dotenv()
import random
import json
import httpx
from huggingface_hub import InferenceClient
from dataclasses import dataclass
from typing import Optional, List

logger = logging.getLogger(__name__)

# Hugging Face Configuration
HF_API_TOKEN = os.getenv("HF_API_TOKEN")
HF_ROUTER_URL = "https://router.huggingface.co/v1/chat/completions"
HF_LLM_MODEL = "meta-llama/Llama-3.1-8B-Instruct"

# Ukrainian-specific letters (absent from Russian)
_UA_SPECIFIC = set("іїєґІЇЄҐ")

# Minimum ratio of Ukrainian-specific chars among all Cyrillic characters
_UA_CHAR_THRESHOLD = 0.008  # 0.8%


@dataclass
class LinguisticCheckResult:
    passed: bool
    reason: str
    detected_language: str
    ukrainian_char_ratio: float


def extract_text_from_epub(epub_path: str, max_chars: int = 6000, return_samples: bool = False):
    """
    Extract a text sample from an EPUB file.
    Takes content from the beginning, middle, and end of the book
    to get a representative cross-section.
    """
    try:
        import warnings
        import ebooklib
        from ebooklib import epub as ebooklib_epub
        from html.parser import HTMLParser

        class _TextExtractor(HTMLParser):
            def __init__(self):
                super().__init__()
                self.chunks = []
                self._skip = False

            def handle_starttag(self, tag, attrs):
                if tag in ("script", "style"):
                    self._skip = True

            def handle_endtag(self, tag):
                if tag in ("script", "style"):
                    self._skip = False

            def handle_data(self, data):
                if not self._skip:
                    stripped = data.strip()
                    if stripped:
                        self.chunks.append(stripped)

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            book = ebooklib_epub.read_epub(epub_path, options={"ignore_ncx": True})

        # Collect all text items
        all_text_chunks = []
        for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
            content = item.get_content()
            if not content:
                continue
            parser = _TextExtractor()
            try:
                parser.feed(content.decode("utf-8", errors="ignore"))
                chunk = " ".join(parser.chunks)
                if chunk.strip():
                    all_text_chunks.append(chunk)
            except Exception:
                continue

        if not all_text_chunks:
            return None

        # Sample from beginning, middle, and end
        total = len(all_text_chunks)
        indices = sorted(set([
            0,
            total // 2,
            max(0, total - 1),
            random.randint(0, max(0, total - 1)),
        ]))

        sample_parts = []
        chars_per_part = max_chars // len(indices)
        for idx in indices:
            sample_parts.append(all_text_chunks[idx][:chars_per_part])

        if return_samples:
            return sample_parts
        return " ".join(sample_parts)

    except Exception as e:
        logger.warning(f"Text extraction failed for {epub_path}: {e}")
        return None


def _count_ukrainian_char_ratio(text: str) -> float:
    """Return ratio of Ukrainian-specific characters to all Cyrillic characters."""
    cyrillic = sum(1 for c in text if "\u0400" <= c <= "\u04FF")
    if cyrillic == 0:
        return 0.0
    ua_specific = sum(1 for c in text if c in _UA_SPECIFIC)
    return ua_specific / cyrillic


def _detect_language(text: str) -> tuple[str, float]:
    """
    Run langdetect on text. Returns (language_code, probability).
    Falls back to ('unknown', 0.0) on any error.
    """
    try:
        from langdetect import detect_langs
        results = detect_langs(text)
        if results:
            top = results[0]
            return top.lang, top.prob
    except Exception as e:
        logger.warning(f"langdetect failed: {e}")
    return "unknown", 0.0


def check_ukrainian_language(epub_path: str) -> LinguisticCheckResult:
    """
    Main MOD-03 entry point. Returns a LinguisticCheckResult.
    Called during book upload before the DB entry is created.
    """
    text = extract_text_from_epub(epub_path)

    if not text or len(text.strip()) < 100:
        # Cannot extract text — don't block, pass to admin review
        logger.warning(f"MOD-03: Could not extract text from {epub_path}, skipping check.")
        return LinguisticCheckResult(
            passed=True,
            reason="Text extraction failed — skipped linguistic check.",
            detected_language="unknown",
            ukrainian_char_ratio=0.0,
        )

    # Signal 1: Ukrainian character ratio
    ua_ratio = _count_ukrainian_char_ratio(text)

    # Signal 2: langdetect
    detected_lang, lang_confidence = _detect_language(text)

    logger.info(
        f"MOD-03: epub={epub_path} | ua_ratio={ua_ratio:.3f} "
        f"| lang={detected_lang} ({lang_confidence:.2f})"
    )

    # --- Decision logic ---

    # PASS: Strong Ukrainian character presence
    if ua_ratio >= _UA_CHAR_THRESHOLD:
        return LinguisticCheckResult(
            passed=True,
            reason=f"Ukrainian character ratio {ua_ratio:.1%} — content confirmed as Ukrainian.",
            detected_language=detected_lang,
            ukrainian_char_ratio=ua_ratio,
        )

    # PASS: langdetect says Ukrainian
    if detected_lang == "uk":
        return LinguisticCheckResult(
            passed=True,
            reason="Language detection confirmed Ukrainian.",
            detected_language=detected_lang,
            ukrainian_char_ratio=ua_ratio,
        )

    # FAIL: No Ukrainian chars AND langdetect is confident it's something else
    if ua_ratio == 0.0 and lang_confidence >= 0.85 and detected_lang != "unknown":
        lang_names = {
            "ru": "Russian", "en": "English", "pl": "Polish",
            "de": "German", "fr": "French", "es": "Spanish",
        }
        lang_display = lang_names.get(detected_lang, detected_lang.upper())
        return LinguisticCheckResult(
            passed=False,
            reason=(
                f"The uploaded text appears to be in {lang_display}, not Ukrainian. "
                f"This library accepts Ukrainian-language books only."
            ),
            detected_language=detected_lang,
            ukrainian_char_ratio=ua_ratio,
        )

    # Borderline: pass with a warning (will still go to admin review)
    return LinguisticCheckResult(
        passed=True,
        reason=f"Borderline result (ua_ratio={ua_ratio:.1%}, lang={detected_lang}). Passed for admin review.",
        detected_language=detected_lang,
        ukrainian_char_ratio=ua_ratio,
    )


# Global Inference Client
hf_client = InferenceClient(api_key=HF_API_TOKEN)


def _get_embedding(text: str) -> Optional[List[float]]:
    """Fetch embedding from Hugging Face Inference API using huggingface_hub client."""
    if not HF_API_TOKEN:
        return None
    
    try:
        # MiniLM expects shorter chunks
        embedding = hf_client.feature_extraction(
            text[:1000],
            model=HF_MODEL
        )
        
        # Convert to list if it's a numpy-like object
        if hasattr(embedding, "tolist"):
            return embedding.tolist()
        return embedding
    except Exception as e:
        logger.error(f"Failed to fetch embedding: {e}")
    return None


def _cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """Calculate cosine similarity between two vectors."""
    import math
    dot_product = sum(a * b for a, b in zip(v1, v2))
    magnitude1 = math.sqrt(sum(a * a for a in v1))
    magnitude2 = math.sqrt(sum(b * b for b in v2))
    if not magnitude1 or not magnitude2:
        return 0.0
    return dot_product / (magnitude1 * magnitude2)


@dataclass
class SemanticCheckResult:
    passed: bool
    reason: str
    similarity_score: float


def check_semantic_alignment(title: str, author: str, epub_path: str) -> SemanticCheckResult:
    """
    MOD-04: Verify that the book content matches the title and isn't gibberish.
    Returns SemanticCheckResult.
    """
    samples = extract_text_from_epub(epub_path, max_chars=1500, return_samples=True)
    if not samples:
        return SemanticCheckResult(passed=True, reason="Could not extract text for semantic check.", similarity_score=0.5)
    
    # Combined text for entropy check
    text_sample = " ".join(samples)

    # 1. Simple Gibberish Heuristic (entropy check) - Does NOT require AI API
    # If the text has too many unique characters relative to its length, it might be junk
    unique_chars = len(set(text_sample))
    if len(text_sample) > 200 and unique_chars / len(text_sample) > 0.4:
         return SemanticCheckResult(
             passed=False, 
             reason="The file content appears to be random or corrupted data (high entropy).", 
             similarity_score=0.0
         )

    if not HF_API_TOKEN:
        return SemanticCheckResult(
            passed=True, 
            reason="HF_API_TOKEN missing — skipped AI semantic match.", 
            similarity_score=1.0
        )

    # 2. LLM-based Semantic Verification (MOD-04)
    try:
        # We use a single representative sample for the LLM to save tokens/time
        # Usually, the second sample (middle of the book) is best.
        sample_to_check = samples[len(samples)//2] if len(samples) > 1 else samples[0]
        
        headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
        payload = {
            "model": HF_LLM_MODEL,
            "messages": [
                {
                    "role": "system", 
                    "content": "You are an AI Librarian. Verify if the book content matches its title and author. "
                               "Ignore page numbers or technical metadata. "
                               "Reply ONLY with '[MATCH]' or '[MISMATCH]' followed by a brief reason in Ukrainian."
                },
                {
                    "role": "user", 
                    "content": f"Title: {title}\nAuthor: {author}\nContent Sample: {sample_to_check[:800]}"
                }
            ],
            "max_tokens": 50,
            "temperature": 0.1
        }
        
        with httpx.Client() as client:
            response = client.post(HF_ROUTER_URL, headers=headers, json=payload, timeout=20.0)
            if response.status_code == 200:
                data = response.json()
                llm_reply = data["choices"][0]["message"]["content"]
                
                if "[MISMATCH]" in llm_reply:
                    logger.warning(f"MOD-04: LLM Mismatch for '{title}': {llm_reply}")
                    return SemanticCheckResult(
                        passed=False,
                        reason=f"Невідповідність змісту: {llm_reply.replace('[MISMATCH]', '').strip()}",
                        similarity_score=0.1
                    )
                else:
                    return SemanticCheckResult(
                        passed=True,
                        reason="Content alignment verified by AI Librarian.",
                        similarity_score=0.9 # High confidence for LLM match
                    )
            else:
                logger.warning(f"HF Router Error: {response.status_code} - {response.text}")
                return SemanticCheckResult(passed=True, reason="AI Librarian is busy — skipped semantic match.", similarity_score=0.5)
                
    except Exception as e:
        logger.error(f"Failed to verify semantic alignment via LLM: {e}")
        return SemanticCheckResult(passed=True, reason="Internal AI error — skipped semantic match.", similarity_score=0.5)
