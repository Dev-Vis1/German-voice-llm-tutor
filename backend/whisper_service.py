import subprocess
import tempfile
import os
from pathlib import Path

def transcribe_audio(audio_file_path: str) -> str:
    """
    Ultra-fast transcription optimized for 5-second German audio clips.
    No CLI fallback for maximum speed.
    """
    print(f"Attempting to transcribe: {audio_file_path}")
    
    # Skip CLI - go straight to library for speed
    try:
        result = _transcribe_with_library(audio_file_path, "tiny")
        if result:
            print(f"Library transcription successful: {result[:100]}...")
            return result
    except Exception as lib_error:
        print(f"Library transcription failed: {lib_error}")
        return ""  # Return empty instead of raising exception
    
    return ""

def _transcribe_with_cli(audio_file_path: str, model_size: str) -> str:
    """
    Use Whisper CLI command for transcription.
    """
    # Create temp directory for output
    with tempfile.TemporaryDirectory() as temp_dir:
        cmd = [
            "whisper", 
            audio_file_path,
            "--model", model_size,
            "--language", "de",  # German
            "--output_dir", temp_dir,
            "--output_format", "txt",
            "--verbose", "False"
        ]
        
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True,
            timeout=60  # 60 second timeout
        )
        
        if result.returncode != 0:
            raise Exception(f"Whisper CLI failed: {result.stderr}")
        
        # Find the output text file
        audio_name = Path(audio_file_path).stem
        txt_file = Path(temp_dir) / f"{audio_name}.txt"
        
        if txt_file.exists():
            with open(txt_file, 'r', encoding='utf-8') as f:
                return f.read().strip()
        else:
            raise Exception("Whisper output file not found")

def _transcribe_with_library(audio_file_path: str, model_size: str) -> str:
    """
    Ultra-fast Whisper transcription optimized for 5-second clips.
    """
    try:
        import whisper
        print(f"Whisper library imported successfully")
        
        # Quick file validation
        if not os.path.exists(audio_file_path):
            raise Exception(f"Audio file not found: {audio_file_path}")
        
        file_size = os.path.getsize(audio_file_path)
        print(f"Audio file size: {file_size} bytes")
        
        if file_size == 0:
            raise Exception("Audio file is empty")
        
        # Use tiny model for maximum speed
        print(f"Loading Whisper model: tiny (optimized for speed)")
        model = whisper.load_model("tiny", device="cpu")
        
        print(f"Starting transcription of: {audio_file_path}")
        
        # Ultra-fast transcription settings for German
        result = model.transcribe(
            audio_file_path, 
            language="de",  # Force German
            verbose=False,
            fp16=False,
            word_timestamps=False,
            condition_on_previous_text=False,
            temperature=0.0,
            no_speech_threshold=0.1,  # Lower for short clips
            logprob_threshold=-1.0,   # Less strict
            compression_ratio_threshold=2.4,
            beam_size=1  # Greedy search for speed
        )
        
        transcribed_text = result["text"].strip()
        detected_language = result.get("language", "unknown")
        print(f"Detected language: {detected_language.title()}")
        print(f"Transcription completed. Language: {detected_language}, Text: '{transcribed_text}' (length: {len(transcribed_text)})")
        
        if not transcribed_text:
            return "[Kein Audio erkannt]"
            
        return transcribed_text
        
    except ImportError as e:
        raise Exception(f"Cannot import whisper library: {e}")
    except Exception as e:
        print(f"Library transcription error: {e}")
        raise Exception(f"Library transcription error: {e}")

def is_whisper_available() -> tuple[bool, str]:
    """
    Check if Whisper is available (CLI or library).
    
    Returns:
        (is_available, method) tuple
    """
    # Check CLI
    try:
        result = subprocess.run(
            ["whisper", "--help"], 
            capture_output=True, 
            timeout=5
        )
        if result.returncode == 0:
            return True, "cli"
    except:
        pass
    
    # Check library
    try:
        import whisper
        return True, "library"
    except ImportError:
        pass
    
    return False, "none"

# Test function
if __name__ == "__main__":
    print("Testing Whisper availability...")
    
    available, method = is_whisper_available()
    if available:
        print(f"✓ Whisper is available via {method}")
        
        # If you have a test audio file, you can test transcription here
        # test_audio = "path/to/test.wav"
        # if os.path.exists(test_audio):
        #     try:
        #         text = transcribe_audio(test_audio)
        #         print(f"Test transcription: {text}")
        #     except Exception as e:
        #         print(f"✗ Transcription test failed: {e}")
    else:
        print("✗ Whisper not found. Install with:")
        print("  pip install openai-whisper")
        print("  or: pip install git+https://github.com/openai/whisper.git")