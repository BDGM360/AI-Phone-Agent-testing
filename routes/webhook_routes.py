from flask import Blueprint, request, jsonify, render_template
from datetime import datetime
import pytz
import requests
import os
import json
import base64
from utils.config import Config
from utils.token_generator import generate_token

webhook_bp = Blueprint('webhook', __name__)

# Validate configuration on module load
Config.validate_config()

# Store notifications in memory (will be cleared on server restart)
notifications = []
processed_notice_ids = set()  # For deduplication
convo_ai_active = False  # Track ConvoAI state
current_agent_id = None  # Store the current agent ID

def is_valid_pstn_event(data):
    """Check if the event is for the PSTN channel with correct parameters"""
    try:
        channel_name = data.get('payload', {}).get('channelName', '')
        return (
            'pstn' in channel_name.lower() and
            data.get('payload', {}).get('uid') == 111 and
            data.get('productId') == 1
        )
    except:
        return False

def handle_convo_ai(action, channel_name=None):
    """Handle ConvoAI start/stop actions"""
    global current_agent_id
    
    if action == "start" and channel_name:
        try:
            url = f"{Config.AGORA_AI_ENDPOINT}/projects/{Config.APP_ID}/join"
            
            payload = {
                "name": "pstnai",
                "properties": {
                    "channel": channel_name,
                    "token": generate_token(channel_name, "222"),  # Generate token for agent with fixed uid 222
                    "agent_rtc_uid": Config.AGENT_UID,
                    "remote_rtc_uids": [Config.DEFAULT_UID],
                    "idle_timeout": 120,
                    "advanced_features": {
                        "enable_bhvs": True,
                        "enable_aivad": True
                    },
                    "llm": {
                        "style": "openai",
                        "url": "https://api.openai.com/v1/chat/completions",
                        "api_key": Config.OPENAI_API_KEY,
                        "system_messages": [
                            {
                                "role": "system",
                                "content": """You are Jack, a friendly and experienced Agora support agent. You have a warm, empathetic personality and genuinely enjoy helping customers solve their problems. Your goal is to make customers feel heard and supported while efficiently addressing their needs.

When handling general inquiries:
- Start with a friendly greeting and show genuine interest in helping
- Use a conversational tone while maintaining professionalism
- Share your knowledge about Agora's products in an engaging way
- Naturally weave in documentation links when relevant, saying something like "I can share a helpful guide about that"

When handling technical issues:
- Express empathy about the problem they're experiencing
- Gather the following information naturally through conversation:
  * Their company name and CID (from Agora Console)
  * The project they're working on
  * What's happening (let them explain in their own words)
  * The channel name if relevant
  * When this started happening (in UTC time)
  * How urgent this is for them (guide them to choose P1, P2, or P3)

After collecting information:
- Acknowledge their situation with empathy
- Summarize what you understand in a conversational way
- Guide them to email support@agora.io, explaining how this will help resolve their issue faster

Your personality traits:
- Warm and approachable
- Patient and understanding
- Knowledgeable but not condescending
- Natural in conversation while being efficient
- Proactive in anticipating needs

Remember to:
- Use conversational transitions between topics
- Show you're actively listening by referencing details they've shared
- Be encouraging and supportive
- Make the interaction feel like a helpful conversation rather than a rigid process"""
                            }
                        ],
                        "max_history": 10,
                        "greeting_message": "This is Jack from Agora Support Call center. I am glad to assist you here. Please feel free to ask any questions about Agora or you can report an issue on this call. Please let me know how I can assist you?",
                        "failure_message": "Please hold on a second.",
                        "silence_message": "Are you still there?",
                        "input_modalities": ["text"],
                        "output_modalities": ["text"],
                        "params": {
                            "model": "gpt-4o-mini",
                            "max_tokens": 1024
                        }
                    },
                    "tts": {
                        "vendor": "elevenlabs",
                        "params": {
                            "key": Config.ELEVENLABS_API_KEY,
                            "model_id": "eleven_flash_v2_5",
                            "voice_id": Config.ELEVENLABS_VOICE_ID
                        }
                    },
                    "asr": {
                        "language": "en-US"
                    },
                    "vad": {
                        "silence_duration_ms": 480
                    },
                    "parameters": {
                        "enable_dump": True,
                        "enable_error_message": True,
                        "enable_delay": True
                    }
                }
            }
            
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f"Basic {base64.b64encode(f'{Config.AGORA_API_KEY}:{Config.AGORA_API_SECRET}'.encode('utf-8')).decode('utf-8')}"
            }

            response = requests.post(url, headers=headers, json=payload)
            response_data = response.json()
            
            if response.status_code == 200 and response_data.get('status') == 'RUNNING':
                current_agent_id = response_data.get('agent_id')
                return True
            return False
            
        except Exception as e:
            return False
    else:  # stop
        if not current_agent_id:
            return False
            
        try:
            url = f"{Config.AGORA_AI_ENDPOINT}/projects/{Config.APP_ID}/agents/{current_agent_id}/leave"
            
            headers = {
                'Authorization': f"Basic {base64.b64encode(f'{Config.AGORA_API_KEY}:{Config.AGORA_API_SECRET}'.encode('utf-8')).decode('utf-8')}"
            }

            response = requests.post(url, headers=headers, data="")
            if response.status_code == 200:
                current_agent_id = None
                return True
            return False
            
        except Exception as e:
            return False

# Removed unused notifications endpoint

@webhook_bp.route('/webhook', methods=['POST'])
def webhook():
    """Webhook endpoint for notifications"""
    try:
        global convo_ai_active
        data = request.json
        notice_id = data.get('noticeId')
        
        # Deduplication check
        if notice_id in processed_notice_ids:
            return jsonify({
                "status": "skipped",
                "message": "Duplicate notification"
            }), 200
        
        # Add to processed IDs
        processed_notice_ids.add(notice_id)
        
        # Keep processed IDs set manageable
        if len(processed_notice_ids) > 1000:
            processed_notice_ids.clear()  # Reset if too many IDs stored
        
        # Create notification entry
        notification = {
            'timestamp': datetime.now(pytz.UTC).strftime('%Y-%m-%d %H:%M:%S UTC'),
            'data': data,
            'processed': False
        }
        
        # Handle specific event types
        event_type = data.get('eventType')
        if event_type in [103, 104] and is_valid_pstn_event(data):
            channel_name = data.get('payload', {}).get('channelName', '')
            if event_type == 103 and not convo_ai_active and channel_name:
                # Start ConvoAI only if it's not already active
                if handle_convo_ai("start", channel_name):
                    convo_ai_active = True
                    notification['data']['convo_ai_action'] = "started"
                    notification['processed'] = True
            elif event_type == 104 and convo_ai_active:
                # Stop ConvoAI if it's active
                if handle_convo_ai("stop"):
                    convo_ai_active = False
                    notification['data']['convo_ai_action'] = "stopped"
                    notification['processed'] = True
        
        # Only store unprocessed notifications
        if not notification['processed']:
            notifications.insert(0, notification)
            # Keep only the last 50 unprocessed notifications
            if len(notifications) > 50:
                notifications.pop()
        
        return jsonify({
            "status": "received",
            "message": "Webhook processed successfully"
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500
