"""
Text preprocessing utilities for Korean language
"""

import re
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

# Korean filler words to remove
KOREAN_FILLERS = [
    '어', '음', '그', '저', '뭐', '이제', '그냥', '약간',
    '어떻게', '이런', '저런', '그런', '막', '좀', '되게'
]

def remove_fillers(text: str, fillers: List[str] = None) -> str:
    """
    Remove Korean filler words from text

    Args:
        text: Input text
        fillers: List of filler words (uses default if None)

    Returns:
        Cleaned text
    """
    if fillers is None:
        fillers = KOREAN_FILLERS

    # Remove standalone fillers (with word boundaries)
    for filler in fillers:
        # Match filler as standalone word
        pattern = r'\b' + re.escape(filler) + r'\b'
        text = re.sub(pattern, '', text)

    # Remove repeated characters (e.g., "어어어" -> "어")
    text = re.sub(r'(.)\1{2,}', r'\1', text)

    # Clean up extra spaces
    text = re.sub(r'\s+', ' ', text).strip()

    return text


def normalize_spacing(text: str) -> str:
    """
    Normalize spacing in Korean text

    Args:
        text: Input text

    Returns:
        Text with normalized spacing
    """
    # Remove spaces before punctuation
    text = re.sub(r'\s+([,.!?;:])', r'\1', text)

    # Add space after punctuation if missing
    text = re.sub(r'([,.!?;:])([^\s])', r'\1 \2', text)

    # Remove multiple spaces
    text = re.sub(r'\s+', ' ', text)

    # Remove leading/trailing spaces
    text = text.strip()

    return text


def split_sentences(text: str) -> List[str]:
    """
    Split text into sentences (Korean-aware)

    Args:
        text: Input text

    Returns:
        List of sentences
    """
    # Split on Korean sentence endings
    sentences = re.split(r'([.!?])\s*', text)

    # Combine sentence and its ending punctuation
    result = []
    for i in range(0, len(sentences) - 1, 2):
        if i + 1 < len(sentences):
            sentence = sentences[i] + sentences[i + 1]
            sentence = sentence.strip()
            if sentence:
                result.append(sentence)

    # Add last sentence if exists
    if len(sentences) % 2 == 1 and sentences[-1].strip():
        result.append(sentences[-1].strip())

    return result


def preprocess_utterance(utterance: Dict) -> Dict:
    """
    Preprocess a single utterance

    Args:
        utterance: Utterance dict with 'text' field

    Returns:
        Updated utterance with cleaned text
    """
    original_text = utterance.get('text', '')

    # Store original
    utterance['original_text'] = original_text

    # Clean text
    cleaned = remove_fillers(original_text)
    cleaned = normalize_spacing(cleaned)

    # Update text
    utterance['text'] = cleaned

    # Track what was removed
    removed_fillers = []
    for filler in KOREAN_FILLERS:
        if filler in original_text and filler not in cleaned:
            removed_fillers.append(filler)

    utterance['preprocessing'] = {
        'original_length': len(original_text),
        'cleaned_length': len(cleaned),
        'removed_fillers': removed_fillers
    }

    return utterance


def preprocess_utterances(utterances: List[Dict]) -> List[Dict]:
    """
    Preprocess multiple utterances

    Args:
        utterances: List of utterance dicts

    Returns:
        List of preprocessed utterances
    """
    return [preprocess_utterance(u) for u in utterances]
