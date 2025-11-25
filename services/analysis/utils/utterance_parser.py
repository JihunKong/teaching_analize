"""
Utterance Parser Utility
Converts Module 1 transcript segments into utterance format for analysis
"""

import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


def segments_to_utterances(segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Convert Module 1 segments to utterance format for analysis

    Args:
        segments: List of segments from Module 1
            [
                {'timestamp': 125, 'text': 'utterance text'},
                {'timestamp': 150, 'text': 'next utterance'},
                ...
            ]

    Returns:
        List of utterances in analysis format
            [
                {'id': 'utt_0001', 'text': '...', 'timestamp': '00:02:05'},
                {'id': 'utt_0002', 'text': '...', 'timestamp': '00:02:30'},
                ...
            ]
    """
    if not segments:
        logger.warning("No segments provided to convert")
        return []

    utterances = []

    for i, segment in enumerate(segments):
        # Extract text
        text = segment.get('text', '').strip()
        if not text:
            continue  # Skip empty segments

        # Extract and convert timestamp
        timestamp_seconds = segment.get('timestamp')
        if timestamp_seconds is not None:
            # Convert seconds (int) to HH:MM:SS format (string)
            timestamp_str = seconds_to_hms(timestamp_seconds)
        else:
            # If no timestamp, use sequential fake timestamp
            timestamp_str = f"00:{i//60:02d}:{i%60:02d}"
            logger.debug(f"Segment {i} has no timestamp, using fake: {timestamp_str}")

        # Create utterance
        utterance = {
            "id": f"utt_{i+1:04d}",  # utt_0001, utt_0002, ...
            "text": text,
            "timestamp": timestamp_str
        }

        utterances.append(utterance)

    logger.info(f"Converted {len(segments)} segments into {len(utterances)} utterances")
    return utterances


def seconds_to_hms(seconds: int) -> str:
    """
    Convert seconds (integer) to HH:MM:SS format (string)

    Args:
        seconds: Total seconds (e.g., 125)

    Returns:
        Formatted timestamp string (e.g., "00:02:05")
    """
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60

    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def hms_to_seconds(timestamp: str) -> int:
    """
    Convert HH:MM:SS format (string) to seconds (integer)

    Args:
        timestamp: Formatted timestamp string (e.g., "00:02:05")

    Returns:
        Total seconds (e.g., 125)
    """
    try:
        parts = timestamp.split(':')
        if len(parts) == 3:
            hours, minutes, seconds = map(int, parts)
            return hours * 3600 + minutes * 60 + seconds
        elif len(parts) == 2:
            minutes, seconds = map(int, parts)
            return minutes * 60 + seconds
        else:
            logger.warning(f"Invalid timestamp format: {timestamp}")
            return 0
    except ValueError:
        logger.error(f"Failed to parse timestamp: {timestamp}")
        return 0


# Testing
if __name__ == "__main__":
    # Test data
    test_segments = [
        {'timestamp': 0, 'text': '안녕하세요. 오늘은 피타고라스 정리에 대해 배워보겠습니다.'},
        {'timestamp': 125, 'text': '피타고라스 정리는 직각삼각형에서 성립하는 법칙입니다.'},
        {'timestamp': 250, 'text': 'a²+b²=c²라는 공식으로 표현됩니다.'},
        {'timestamp': None, 'text': '이해가 되나요?'},  # No timestamp
        {'timestamp': 400, 'text': ''},  # Empty text
    ]

    print("Input segments:")
    for seg in test_segments:
        print(f"  {seg}")

    print("\nConverted utterances:")
    utterances = segments_to_utterances(test_segments)
    for utt in utterances:
        print(f"  {utt}")

    print("\nTimestamp conversion tests:")
    print(f"  125 seconds -> {seconds_to_hms(125)}")
    print(f"  3661 seconds -> {seconds_to_hms(3661)}")
    print(f"  00:02:05 -> {hms_to_seconds('00:02:05')} seconds")
    print(f"  01:01:01 -> {hms_to_seconds('01:01:01')} seconds")
