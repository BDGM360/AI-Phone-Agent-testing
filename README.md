# AI Phone Agent

A Flask server providing Agora-related functionalities including PSTN integration, webhook handling, and ConvoAI integration for AI-powered phone calls.

## Features

- PSTN Integration with Agora
- Web UI for PSTN Access
- Webhook Handling for Call Events
- ConvoAI Integration for AI-powered Phone Calls

## Environment Variables

Copy `env.example` to `.env` and configure the following variables:

### Agora Credentials
- `APP_ID`: Your Agora App ID
- `APP_CERTIFICATE`: Your Agora App Certificate
- `AGORA_API_KEY`: Your Agora API key
- `AGORA_API_SECRET`: Your Agora API secret
- `PSTN_AUTH`: Authentication token for Agora PSTN service

### OpenAI Configuration
- `OPENAI_API_KEY`: Your OpenAI API key for LLM integration

### ElevenLabs Configuration
- `ELEVENLABS_API_KEY`: Your ElevenLabs API key for TTS
- `ELEVENLABS_VOICE_ID`: Voice ID for TTS

### Application Settings
- `ALLOWED_ORIGINS`: Comma-separated list of allowed origins for CORS


**Important**: This project must have a public domain to make the AI functionality work correctly. Recommend vercel to test the project.
## Local Development

1. Create and configure `.env` file:
   ```bash
   cp env.example .env
   # Edit .env with your credentials
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Run the development server:
   ```bash
   python app.py
   ```

4. Access the web UI at http://localhost:5000

## Deployment to Vercel

1. Install Vercel CLI:
   ```bash
   npm i -g vercel
   ```

2. Configure environment variables in Vercel:
   - Go to your project settings in Vercel dashboard
   - Add all required environment variables from `env.example`

3. Deploy:
   ```bash
   vercel --prod
   ```

## PSTN Integration

The application provides a web UI for initiating PSTN calls through Agora's service. The PSTN endpoint supports the following regions:

- North America (AREA_CODE_NA)
- Europe (AREA_CODE_EU)
- Asia, excluding Mainland China (AREA_CODE_AS)
- Japan (AREA_CODE_JP)
- India (AREA_CODE_IN)
- Mainland China (AREA_CODE_CN)

When a PSTN call is initiated, the application:
1. Generates a unique channel name with region prefix
2. Creates an Agora token for the channel
3. Makes a request to the Agora PSTN service
4. Returns the phone number and PIN to the user

## Webhook Integration

The webhook endpoint (`/webhook`) handles PSTN events:

- Event 103 (Join Channel): Starts ConvoAI agent if conditions match
- Event 104 (Leave Channel): Stops ConvoAI agent if active

The webhook system:
1. Validates that the event is for a PSTN channel
2. Checks the event type (103 for join, 104 for leave)
3. Manages the ConvoAI agent lifecycle based on these events

### Webhook Configuration

To enable the webhook functionality:

1. Go to the Agora Console
2. Add your webhook URL: `https://yourdomain.com/webhook`
3. Subscribe to RTC channel events 103 (Join Channel) and 104 (Leave Channel)

## ConvoAI Integration

The application integrates with Agora's ConvoAI service to provide AI-powered phone calls. When a user joins a PSTN channel, the ConvoAI agent:

1. Joins the same channel with a different UID
2. Uses OpenAI's GPT model for natural language understanding
3. Uses ElevenLabs for text-to-speech conversion
4. Provides a conversational experience over the phone

The ConvoAI agent is configured with:
- A system prompt for Agora support
- Greeting and failure messages
- Voice settings via ElevenLabs
- ASR (Automatic Speech Recognition) settings

If you need other LLM and TTS vendors, please check the Agora officical document https://docs.agora.io/en/conversational-ai/overview/product-overview and modify the file AI-PHONE-AGENT/routes/webhook_routes.py accordingly.

## Security Notes

- Never commit `.env` file with real credentials
- Keep all API keys and secrets secure
- Use environment variables for sensitive data
- Configure proper CORS settings in production
- Origin validation is implemented for all endpoints

## Troubleshooting

If you encounter issues:
1. Check that all environment variables are correctly set
2. Verify that your Agora account has PSTN capabilities enabled
3. Ensure your OpenAI and ElevenLabs API keys are valid
4. Ensure you have configured the Notification for your project
5. Check the server logs for detailed error messages

### Logging Information

The application logs the following information to assist with troubleshooting:

1. **Webhook Notifications**:
   - `Received webhook notification`: Full JSON payload of incoming webhook
   - `Webhook processing result`: Final processing status

2. **ConvoAI Operations**:
   - `ConvoAI START request`: URL and payload for ConvoAI start request
   - `ConvoAI START response`: Status code and response body
   - `ConvoAI successfully started`: Agent ID and channel name when successful
   - `ConvoAI STOP request`: URL for ConvoAI stop request
   - `ConvoAI STOP response`: Status code and response body

3. **Error Handling**:
   - All errors are logged with stack traces
   - API request failures include status codes and error messages

To view logs in Vercel:
1. Go to your project dashboard
2. Navigate to the "Logs" section
3. Filter by "Function" to see server-side logs
