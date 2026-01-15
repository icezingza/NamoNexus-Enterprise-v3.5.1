## Input-Validation Features (Day-2)
- Message length capped at 5,000 characters
- User-ID max 255 chars, no control bytes
- Voice/Facial features clamped 0.0-1.0 scale
- File upload: .wav/.mp3 only, <= 5 MB
- Invalid payload -> HTTP 422 with clear field error
