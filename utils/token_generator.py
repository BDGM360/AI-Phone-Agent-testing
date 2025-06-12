from agora_token_builder import RtcTokenBuilder
import time
from utils.config import Config

def generate_token(channel_name, uid):
    """Generate Agora token"""
    if not Config.APP_CERTIFICATE:
        return ""

    expiration_time = Config.TOKEN_EXPIRATION
    current_timestamp = int(time.time())
    privilegeExpiredTs = current_timestamp + expiration_time

    token = RtcTokenBuilder.buildTokenWithUid(
        Config.APP_ID,
        Config.APP_CERTIFICATE,
        channel_name,
        uid,
        1,
        privilegeExpiredTs
    )
    return token
