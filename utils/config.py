import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(override=True)

class Config:
    # Agora Credentials
    APP_ID = os.getenv('APP_ID')
    APP_CERTIFICATE = os.getenv('APP_CERTIFICATE')
    AGORA_API_KEY = os.getenv('AGORA_API_KEY')
    AGORA_API_SECRET = os.getenv('AGORA_API_SECRET')

    # OpenAI and ElevenLabs Credentials
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')
    ELEVENLABS_VOICE_ID = os.getenv('ELEVENLABS_VOICE_ID')

    # API Endpoints
    AGORA_PSTN_ENDPOINT = "https://sipcm.agora.io/v1/api/pstn"
    AGORA_AI_ENDPOINT = "https://api.agora.io/api/conversational-ai-agent/v2"

    # Default Values
    DEFAULT_UID = "111"
    AGENT_UID = "222"
    TOKEN_EXPIRATION = 3600  # 1 hour in seconds

    # Security configuration
    PSTN_AUTH = os.getenv('PSTN_AUTH')
    ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', 'http://localhost:5000,http://127.0.0.1:5000')  # Default to localhost if not set

    @classmethod
    def validate_config(cls):
        """Validate that all required environment variables are set"""
        required_vars = [
            'APP_ID', 'APP_CERTIFICATE', 'AGORA_API_KEY', 'AGORA_API_SECRET',
            'PSTN_AUTH', 'OPENAI_API_KEY', 'ELEVENLABS_API_KEY',
            'ELEVENLABS_VOICE_ID'
        ]
        missing_vars = [var for var in required_vars if not getattr(cls, var)]
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
