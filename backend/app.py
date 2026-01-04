from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
import tempfile
import os
from datetime import datetime
import json
from pathlib import Path
from .whisper_service import transcribe_audio
from .ollama_client import ask_ollama
from .tts_service import save_tts_audio

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "German Voice LLM Tutor Backend is running!"}

@app.post("/api/v1/voice/chat")
async def voice_chat(
    audio: UploadFile = File(...),
    topic: str = Form(default="general conversation")
):
    
    try:
        # Save uploaded audio temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
            content = await audio.read()
            temp_audio.write(content)
            temp_audio_path = temp_audio.name
        
        print(f"Audio uploaded: {audio.filename}, size: {len(content)} bytes")
        print(f"Temp file created: {temp_audio_path}")
        
        # Transcribe with Whisper
        try:
            user_text = transcribe_audio(temp_audio_path)
            print(f"Transcription successful: {user_text[:100]}...")
        except Exception as transcription_error:
            print(f"Transcription failed with error: {transcription_error}")
            # Clean up temp file before raising
            os.unlink(temp_audio_path)
            raise transcription_error
        
        # Clean up temp file
        os.unlink(temp_audio_path)
        
        if not user_text.strip():
            return JSONResponse(
                status_code=400, 
                content={"error": "Could not transcribe audio"}
            )
        
        # Get system prompt
        system_prompt_path = Path("backend/prompts/system_prompt.txt")
        if system_prompt_path.exists():
            with open(system_prompt_path, 'r', encoding='utf-8') as f:
                system_prompt = f.read()
        else:
            system_prompt = "You are a helpful German tutor. Respond in German."
        
        # Build full prompt
        full_prompt = f"{system_prompt}\n\nTopic: {topic}\nUser: {user_text}\nTutor:"
        
        # Get LLM response
        try:
            reply_text = ask_ollama(full_prompt)
            print(f"LLM response successful: {reply_text[:100]}...")
        except Exception as llm_error:
            print(f"LLM request failed: {llm_error}")
            # Fallback response when LLM fails
            reply_text = f"Ich habe verstanden: '{user_text}'. Das ist interessant! (Ollama ist nicht verfügbar)"
        
        # Generate TTS audio  
        try:
            tts_filename = f"reply_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
            tts_path = f"data/audio/{tts_filename}"
            await save_tts_audio(reply_text, tts_path)
            print(f"TTS generation successful: {tts_filename}")
            tts_url = f"/audio/{tts_filename}"
        except Exception as tts_error:
            print(f"TTS generation failed: {tts_error}")
            # Continue without TTS audio
            tts_filename = None
            tts_url = None
        
        # Save conversation history
        try:
            conversation = {
                "timestamp": datetime.now().isoformat(),
                "topic": topic,
                "user_text": user_text,
                "reply_text": reply_text,
                "tts_file": tts_filename
            }
            
            history_file = "data/history/conversations.jsonl"
            with open(history_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(conversation, ensure_ascii=False) + '\n')
            print("Conversation saved to history")
        except Exception as history_error:
            print(f"Failed to save conversation history: {history_error}")
            # Continue anyway - don't fail the entire request for history issues

        print(f"Returning successful response: user_text='{user_text}', reply_text='{reply_text[:50]}...', tts_url='{tts_url}'")
        return {
            "user_text": user_text,
            "reply_text": reply_text,
            "tts_url": tts_url,
            "topic": topic
        }
        
    except Exception as e:
        print(f"Request processing failed with error: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        
        return JSONResponse(
            status_code=500,
            content={"error": f"Processing failed: {str(e)}"}
        )

@app.get("/api/v1/history")
async def get_history(limit: int = 10):
    """Get recent conversation history"""
    try:
        history_file = "data/history/conversations.jsonl"
        if not os.path.exists(history_file):
            return {"conversations": []}
        
        conversations = []
        with open(history_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            # Get last 'limit' conversations
            for line in lines[-limit:]:
                if line.strip():
                    conversations.append(json.loads(line.strip()))
        
        return {"conversations": conversations}
    
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to get history: {str(e)}"}
        )

@app.get("/audio/{filename}")
async def get_audio(filename: str):
    """Serve TTS audio files"""
    from fastapi.responses import FileResponse
    
    audio_path = f"data/audio/{filename}"
    if os.path.exists(audio_path):
        return FileResponse(audio_path, media_type="audio/wav")
    else:
        return JSONResponse(status_code=404, content={"error": "Audio file not found"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")