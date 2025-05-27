from flask import Blueprint, request, jsonify, abort, make_response
import secrets
import datetime
import requests
from utils.token_generator import generate_token
from utils.config import Config

pstn_bp = Blueprint('pstn', __name__)

# Removed unused validate_jwt function

def is_allowed_origin():
    """Check if the request origin is allowed"""
    from urllib.parse import urlparse
    import os
    
    # For debugging - print environment variables
    print(f"ALLOWED_ORIGINS from env: {os.environ.get('ALLOWED_ORIGINS')}")
    print(f"ALLOWED_ORIGINS from Config: {Config.ALLOWED_ORIGINS}")
    
    origin = request.headers.get('Origin')
    print(f"Request origin: {origin}")
    
    if not origin:
        print("No origin in request")
        return True  # Allow requests with no origin for now
        
    # Parse origin to get domain part
    parsed = urlparse(origin)
    parsed_origin = f"{parsed.hostname}{':' + str(parsed.port) if parsed.port else ''}"
    print(f"Parsed origin: {parsed_origin}")

    # Always allow the Vercel domain
    if "vercel.app" in parsed_origin:
        print(f"Allowing Vercel domain: {parsed_origin}")
        return True
        
    # Always allow localhost
    if parsed_origin in ['localhost:5000', '127.0.0.1:5000', 'localhost', '127.0.0.1']:
        print(f"Allowing localhost: {parsed_origin}")
        return True

    allowed_origins = [o.strip() for o in Config.ALLOWED_ORIGINS.split(',')]
    print(f"Allowed origins list: {allowed_origins}")
    
    # Check for exact match or wildcard match
    for allowed in allowed_origins:
        # Handle wildcard domains
        if allowed.startswith('*'):
            domain_part = allowed[1:].lstrip('.')
            match = parsed_origin.endswith(domain_part)
            print(f"Checking wildcard {allowed} => {domain_part} against {parsed_origin}: {match}")
            if match:
                return True
        else:
            # Check for exact match
            full_match = origin == allowed
            domain_match = parsed_origin == allowed
            hostname_match = parsed_origin == urlparse(allowed).hostname
            print(f"Checking {allowed} => full: {full_match}, domain: {domain_match}, hostname: {hostname_match}")
            if full_match or domain_match or hostname_match:
                return True
    
    print(f"Origin validation failed for: {origin}")
    return False

# Removed unused functions and endpoints

@pstn_bp.route('/pstn', methods=['POST'])
def pstn():
    """PSTN endpoint"""
    try:
        # Check origin
        if not is_allowed_origin():
            abort(403, description="Access denied. Origin validation failed")

        # Get region from request
        data = request.json
        
        # Map region selection to Agora codes
        region_mapping = {
            "North America": "AREA_CODE_NA",
            "Europe": "AREA_CODE_EU", 
            "Asia, excluding Mainland China": "AREA_CODE_AS",
            "Japan": "AREA_CODE_JP",
            "India": "AREA_CODE_IN",
            "Mainland China": "AREA_CODE_CN"
        }
        
        if not data:
            return jsonify({"error": "No JSON data in request"}), 400
            
        if not data.get('region'):
            return jsonify({"error": "Region is required"}), 400
            
        region_code = region_mapping.get(data.get('region'), 'AREA_CODE_NA')

        # Generate token for PSTN call
        # Generate region-prefixed channel name
        random_channel = f"{region_code}_pstn_{secrets.token_hex(4)}"
        
        # Generate token
        try:
            pstn_token = generate_token(random_channel, Config.DEFAULT_UID)
        except Exception as token_error:
            return jsonify({"error": f"Token generation failed: {str(token_error)}"}), 500

        # Prepare request to Agora PSTN service
        headers = {
            'Authorization': f'Basic {Config.PSTN_AUTH}',
            'Content-Type': 'application/json'
        }
        
        pstn_data = {
            "action": "inbound",
            "appid": Config.APP_ID,
            "region": region_code,
            "uid": Config.DEFAULT_UID,
            "channel": random_channel,
            "token": pstn_token
        }

        # Make request to Agora PSTN service
        try:
            response = requests.post(
                Config.AGORA_PSTN_ENDPOINT,
                headers=headers,
                json=pstn_data
            )
            
            # Check for specific error messages
            if response.status_code != 200:
                try:
                    error_data = response.json()
                    if "error" in error_data:
                        return jsonify({
                            "error": "PSTN service error",
                            "details": error_data["error"]
                        }), 400
                except:
                    return jsonify({
                        "error": "PSTN service error",
                        "details": "Unknown error occurred"
                    }), 400
            
            # Return the response from Agora
            return response.json(), response.status_code
        except requests.RequestException as req_error:
            return jsonify({"error": f"PSTN service request failed: {str(req_error)}"}), 500
        except ValueError as json_error:
            return jsonify({"error": "Invalid response from PSTN service", "response_text": response.text}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500
