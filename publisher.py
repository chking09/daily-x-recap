"""
Publisher - X API integration for posting market recap content
Handles authentication and posting to X platform
"""

import base64
import hashlib
import hmac
import logging
import secrets
import string
import time
import urllib.parse
from typing import Dict

import requests

from config import (
    X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_SECRET,
    X_API_BASE_URL, X_TWEETS_ENDPOINT, MAX_TWEET_LENGTH, MAX_RETRIES
)


def _percent_encode(value: str) -> str:
    """
    Percent encode a string according to RFC 3986
    """
    return urllib.parse.quote(str(value), safe='')


def _generate_oauth_signature(
    method: str,
    url: str,
    params: Dict[str, str],
    consumer_secret: str,
    token_secret: str
) -> str:
    """
    Generate OAuth 1.0a signature for X API authentication
    
    Args:
        method: HTTP method (POST)
        url: Full API endpoint URL
        params: OAuth parameters dictionary
        consumer_secret: X API secret key
        token_secret: X access token secret
        
    Returns:
        Base64 encoded signature string
    """
    # Percent encode all parameters
    encoded_params = []
    for key, value in params.items():
        encoded_key = _percent_encode(key)
        encoded_value = _percent_encode(value)
        encoded_params.append((encoded_key, encoded_value))
    
    # Sort parameters
    encoded_params.sort()
    
    # Create parameter string
    param_string = '&'.join([f"{k}={v}" for k, v in encoded_params])
    
    # Create signature base string
    base_string = f"{method}&{_percent_encode(url)}&{_percent_encode(param_string)}"
    
    # Create signing key
    signing_key = f"{_percent_encode(consumer_secret)}&{_percent_encode(token_secret)}"
    
    # Generate signature
    signature = hmac.new(
        signing_key.encode('utf-8'),
        base_string.encode('utf-8'),
        hashlib.sha1
    ).digest()
    
    return base64.b64encode(signature).decode('utf-8')


def _generate_oauth_header() -> str:
    """
    Generate OAuth 1.0a authorization header for X API
    
    Returns:
        OAuth authorization header string
    """
    # Generate random nonce
    nonce = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
    timestamp = str(int(time.time()))
    
    # OAuth parameters (only for header, not including request body)
    oauth_params = {
        'oauth_consumer_key': X_API_KEY,
        'oauth_nonce': nonce,
        'oauth_signature_method': 'HMAC-SHA1',
        'oauth_timestamp': timestamp,
        'oauth_token': X_ACCESS_TOKEN,
        'oauth_version': '1.0'
    }
    
    # Generate signature (OAuth params only, body is separate)
    url = f"{X_API_BASE_URL}{X_TWEETS_ENDPOINT}"
    signature = _generate_oauth_signature('POST', url, oauth_params, X_API_SECRET, X_ACCESS_SECRET)
    oauth_params['oauth_signature'] = signature
    
    # Build authorization header
    auth_header_params = []
    for key, value in oauth_params.items():
        encoded_value = _percent_encode(str(value))
        auth_header_params.append(f'{key}="{encoded_value}"')
    
    return f"OAuth {', '.join(auth_header_params)}"


def _format_content_for_x(content: str) -> str:
    """
    Format content to fit X platform constraints
    
    Args:
        content: Raw content string
        
    Returns:
        Formatted content that fits X character limits
    """
    if len(content) <= MAX_TWEET_LENGTH:
        return content
    
    # If content is too long, truncate with ellipsis
    truncated = content[:MAX_TWEET_LENGTH - 3] + "..."
    logging.warning("Content truncated from %d to %d characters", len(content), len(truncated))
    return truncated


def post_to_x(content: str) -> bool:
    """
    Post market recap content to X platform using API v2
    
    Args:
        content: Formatted content string to post
        
    Returns:
        True if successful, False otherwise
    """
    if not all([X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_SECRET]):
        logging.error("Missing X API credentials")
        return False
    
    # Format content for X platform
    formatted_content = _format_content_for_x(content)
    
    # Prepare API request
    url = f"{X_API_BASE_URL}{X_TWEETS_ENDPOINT}"
    headers = {
        'Authorization': _generate_oauth_header(),
        'Content-Type': 'application/json'
    }
    payload = {
        'text': formatted_content
    }
    
    # Attempt to post with retry logic
    for attempt in range(MAX_RETRIES):
        try:
            logging.info("Attempting to post to X (attempt %d/%d)", attempt + 1, MAX_RETRIES)

            response = requests.post(url, json=payload, headers=headers, timeout=30)

            if response.status_code == 201:
                logging.info("Successfully posted to X platform")
                return True
            if response.status_code == 429:
                logging.warning("Rate limit exceeded, stopping retries")
                return False
            logging.error("X API error: %d - %s", response.status_code, response.text)

        except requests.RequestException as e:
            logging.error("Network error posting to X: %s", e)

        # Wait before retry (exponential backoff)
        if attempt < MAX_RETRIES - 1:
            wait_time = 2 ** attempt
            logging.info("Waiting %d seconds before retry", wait_time)
            time.sleep(wait_time)
    
    logging.error("Failed to post to X after all retry attempts")
    return False