# Mobile Architecture — German Voice LLM Tutor (Flutter)

This document describes a recommended mobile architecture for the German Voice LLM Tutor using Flutter (Dart).

Goals

- Low-latency voice interactions (record → send → receive TTS)
- Clean separation: UI, audio pipeline, network layer, local storage
- Prepare for offline-first features (cached prompts, local audio) and async background uploads

High-level choices

- Framework: Flutter (single codebase for iOS & Android)
- State management: Riverpod (recommended) or Provider
- Network: Dio or http (Dio recommended for interceptors, retries)
- Audio: `flutter_sound` or `just_audio` for playback and `flutter_sound` or `audio_streamer` for recording
- File storage: `path_provider` + `hive` or `sqflite` for conversation history

Project structure (suggested)

lib/
├─ main.dart
├─ app.dart
├─ modules/
│  ├─ auth/ (if needed)
│  ├─ recording/ (audio recorder provider, formats)
│  ├─ tutor/ (conversation state, prompts, history)
│  └─ api/ (client, endpoints)
├─ ui/
│  ├─ screens/
│  │  ├─ home_screen.dart
│  │  ├─ practice_screen.dart
│  │  └─ history_screen.dart
│  └─ widgets/

Screens

- Home
  - Choose topic, difficulty, voice prefs
- Practice
  - Main recording UI: record button, live transcript (if streaming STT), recommended corrections, role selector (coach/team-mate)
  - Replay last reply (TTS) and show corrected line + short explanation
- History
  - Conversation logs, saved phrases to review

API / Backend contract

- POST /api/v1/voice/chat
  - Body: multipart/form-data { audio: file (wav/m4a), topic: string }
  - Response: { user_text: string, reply_text: string, tts_url?: string }

- GET /api/v1/history
  - Response: list of conversation items

Audio pipeline

- Record as 16kHz mono WAV/M4A to reduce size and be Whisper-friendly
- Upload with progress indicator
- Receive TTS as URL or raw audio bytes; prefer streaming playback

Offline & caching

- Cache recent prompts and model responses for quick replay
- Allow recording offline and queue uploads (background sync)

Authentication & Security

- Use standard OAuth2 or token-based auth if multi-user / cloud backend
- Securely store tokens with Flutter Secure Storage
- Use HTTPS for all network calls

Performance & Battery

- Batch uploads to reduce wake locks
- Use native recording plugins for efficiency

CI/CD and testing

- Unit tests (Dart) for business logic
- Widget tests for key UI interactions
- GitHub Actions pipeline: analyze, test, build (apk/ipa via codemagic or fastlane)

Privacy & Permissions

- Ask microphone permission at runtime and explain why
- Optional: store transcripts locally and allow user to clear history

Next steps for mobile implementation

1) Build a small prototype with a single Practice screen that records audio, uploads to backend, and plays returned TTS.
2) Add Riverpod providers for audio state and API client.
3) Add offline queue and simple history view.

If you want, I can now:
- Generate a Flutter starter scaffold (lib folder + main.dart + example practice screen)
- Draft the FastAPI endpoints and example request/response handlers
- Create GitHub Actions config for building Flutter app

Tell me which of those you'd like me to produce next.