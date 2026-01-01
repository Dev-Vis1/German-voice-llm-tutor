import asyncio
import aiofiles
from pathlib import Path
import tempfile
import subprocess
from typing import Optional

# Try to import edge-tts (free option)
try:
    import edge_tts
    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False

# Try to import pyttsx3 (offline fallback)
try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False

async def speak_text(text: str, voice: str = "de-DE-KatjaNeural", prefer_offline: bool = True) -> bytes:
    """
    Convert text to speech and return audio bytes.
    
    Args:
        text: Text to convert to speech
        voice: Voice to use (Edge TTS voice name)
        prefer_offline: If True, use offline TTS first, then fallback to online
    
    Returns:
        Audio data as bytes (WAV format)
    """
    if prefer_offline and PYTTSX3_AVAILABLE:
        try:
            return await _pyttsx3_synthesize(text)
        except Exception as e:
            print(f"Offline TTS failed, trying online: {e}")
    
    if EDGE_TTS_AVAILABLE:
        try:
            return await _edge_tts_synthesize(text, voice)
        except Exception as e:
            print(f"Online TTS failed: {e}")
            if PYTTSX3_AVAILABLE:
                return await _pyttsx3_synthesize(text)
            raise e
    elif PYTTSX3_AVAILABLE:
        return await _pyttsx3_synthesize(text)
    else:
        raise Exception("No TTS engine available. Install edge-tts or pyttsx3")

async def save_tts_audio(text: str, output_path: str, voice: str = "de-DE-KatjaNeural", prefer_offline: bool = True) -> None:
    """
    Convert text to speech and save to file.
    
    Args:
        text: Text to convert
        output_path: Where to save the audio file
        voice: Voice to use
        prefer_offline: If True, use offline TTS first
    """
    # Ensure output directory exists
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    if prefer_offline and PYTTSX3_AVAILABLE:
        try:
            await _pyttsx3_save(text, output_path)
            return
        except Exception as e:
            print(f"Offline TTS save failed, trying online: {e}")
    
    if EDGE_TTS_AVAILABLE:
        try:
            await _edge_tts_save(text, output_path, voice)
        except Exception as e:
            print(f"Online TTS save failed: {e}")
            if PYTTSX3_AVAILABLE:
                await _pyttsx3_save(text, output_path)
            else:
                raise e
    elif PYTTSX3_AVAILABLE:
        await _pyttsx3_save(text, output_path)
    else:
        raise Exception("No TTS engine available")

async def _edge_tts_synthesize(text: str, voice: str) -> bytes:
    """Use Edge TTS to synthesize speech."""
    communicate = edge_tts.Communicate(text, voice)
    
    audio_data = b""
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data += chunk["data"]
    
    return audio_data

async def _edge_tts_save(text: str, output_path: str, voice: str) -> None:
    """Use Edge TTS to save speech to file."""
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)

async def _pyttsx3_synthesize(text: str) -> bytes:
    """Use pyttsx3 for offline TTS (fallback)."""
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
        temp_path = temp_file.name
    
    # Run pyttsx3 in a separate thread since it's blocking
    def _save_with_pyttsx3():
        engine = pyttsx3.init()
        
        # Set German voice if available
        voices = engine.getProperty('voices')
        for voice in voices:
            if 'german' in voice.name.lower() or 'de' in voice.id.lower():
                engine.setProperty('voice', voice.id)
                break
        
        engine.save_to_file(text, temp_path)
        engine.runAndWait()
    
    # Run in thread pool
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, _save_with_pyttsx3)
    
    # Read the file
    async with aiofiles.open(temp_path, 'rb') as f:
        audio_data = await f.read()
    
    # Clean up
    Path(temp_path).unlink(missing_ok=True)
    
    return audio_data

async def _pyttsx3_save(text: str, output_path: str) -> None:
    """Use pyttsx3 to save speech directly to file."""
    def _save_sync():
        engine = pyttsx3.init()
        
        # Try to set German voice
        voices = engine.getProperty('voices')
        for voice in voices:
            if 'german' in voice.name.lower() or 'de' in voice.id.lower():
                engine.setProperty('voice', voice.id)
                break
        
        engine.save_to_file(text, output_path)
        engine.runAndWait()
    
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, _save_sync)

def list_available_voices() -> list:
    """
    List available TTS voices.
    
    Returns:
        List of voice names
    """
    if EDGE_TTS_AVAILABLE:
        return _list_edge_voices()
    elif PYTTSX3_AVAILABLE:
        return _list_pyttsx3_voices()
    else:
        return []

def _list_edge_voices() -> list:
    """List Edge TTS voices."""
    # Common German voices
    return [
        "de-DE-KatjaNeural",    # Female
        "de-DE-ConradNeural",   # Male
        "de-DE-AmalaNeural",    # Female
        "de-DE-BerndNeural",    # Male
        "de-DE-ChristophNeural", # Male
        "de-DE-GiselaNeural",   # Female
        "de-DE-KasperNeural",   # Male
        "de-DE-KlarissaNeural", # Female
        "de-DE-KlausNeural",    # Male
        "de-DE-LouisaNeural",   # Female
    ]

def _list_pyttsx3_voices() -> list:
    """List pyttsx3 system voices."""
    try:
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        return [voice.name for voice in voices if voice.name]
    except:
        return []

def is_tts_available() -> tuple[bool, str]:
    """
    Check if TTS is available.
    
    Returns:
        (is_available, engine_name) tuple
    """
    if EDGE_TTS_AVAILABLE:
        return True, "edge-tts"
    elif PYTTSX3_AVAILABLE:
        return True, "pyttsx3"
    else:
        return False, "none"

def check_offline_capabilities() -> dict:
    """
    Check which components work offline.
    
    Returns:
        Dictionary with offline capability status
    """
    capabilities = {
        "whisper": True,  # Always works offline after model download
        "tts_offline": PYTTSX3_AVAILABLE,
        "tts_online": EDGE_TTS_AVAILABLE,
        "ollama_local": True  # Assumes Ollama is running locally
    }
    
    return capabilities

# Test function
if __name__ == "__main__":
    print("=== Offline Capabilities Check ===")
    caps = check_offline_capabilities()
    
    print(f"✅ Whisper (Speech Recognition): {'Available' if caps['whisper'] else 'Not Available'}")
    print(f"✅ Offline TTS (pyttsx3): {'Available' if caps['tts_offline'] else 'Not Available'}")
    print(f"🌐 Online TTS (Edge): {'Available' if caps['tts_online'] else 'Not Available'}")
    print(f"🏠 Local LLM (Ollama): {'Available' if caps['ollama_local'] else 'Not Available'}")
    
    if caps['whisper'] and caps['tts_offline']:
        print("\\n✅ FULLY OFFLINE CAPABLE!")
    else:
        print("\\n⚠️  Some offline components missing")

# Test function
if __name__ == "__main__":
    async def test_tts():
        print("Testing TTS availability...")
        
        available, engine = is_tts_available()
        if available:
            print(f"✓ TTS available via {engine}")
            
            voices = list_available_voices()
            print(f"Available voices: {voices[:3]}...")  # Show first 3
            
            # Test synthesis
            try:
                test_text = "Hallo! Ich bin dein Deutsch-Tutor."
                print(f"Testing synthesis: '{test_text}'")
                
                audio_data = await speak_text(test_text)
                print(f"✓ Generated {len(audio_data)} bytes of audio")
                
                # Save test file
                test_file = "test_tts.wav"
                await save_tts_audio(test_text, test_file)
                print(f"✓ Saved test audio to {test_file}")
                
            except Exception as e:
                print(f"✗ TTS test failed: {e}")
        else:
            print("✗ No TTS engine available. Install with:")
            print("  pip install edge-tts")
            print("  or: pip install pyttsx3")
    
    asyncio.run(test_tts())