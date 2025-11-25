async def get_transcript_with_improved_methods(video_id: str, language: str = "ko", youtube_url: str = None) -> Dict[str, Any]:
    """
    Improved transcription method with multiple fallbacks:
    1. Direct API (youtube-transcript-api) - fastest and most reliable
    2. Innertube API - backup when direct API fails
    3. Browser automation - final fallback for difficult cases
    """
    if not youtube_url:
        youtube_url = f"https://www.youtube.com/watch?v={video_id}"
    
    logger.info(f"Starting improved transcription for video: {video_id}")
    
    try:
        # Use improved transcript extractor
        extractor = ImprovedTranscriptExtractor()
        result = await extractor.extract_transcript(youtube_url, language)
        
        if result["success"]:
            method_used = result.get("method_used", "unknown")
            logger.info(f"SUCCESS: {method_used} transcribed {result['character_count']} characters in {result['processing_time']:.2f}s")
            return result
        else:
            logger.warning(f"Improved methods failed: {result['error']}")
            
            # Final fallback to browser automation
            logger.info("Attempting browser automation as final fallback...")
            
            async with BrowserTranscriber() as browser_transcriber:
                browser_result = await browser_transcriber.transcribe_youtube_video(youtube_url, language)
            
            if browser_result["success"]:
                logger.info(f"SUCCESS: Browser automation transcribed {browser_result['character_count']} characters")
                browser_result["method_used"] = "browser_automation_fallback"
                return browser_result
            else:
                logger.error(f"All methods failed. Final error: {browser_result['error']}")
                return {
                    "success": False,
                    "error": f"All transcription methods failed. Direct API: {result['error']}. Browser: {browser_result['error']}",
                    "video_id": video_id,
                    "methods_tried": ["direct_api", "innertube_api", "browser_automation"]
                }
    
    except Exception as e:
        logger.error(f"Improved transcription failed: {str(e)}")
        return {
            "success": False,
            "error": f"Improved transcription failed: {str(e)}",
            "video_id": video_id
        }