"""
Sopel Emote Finder Module

Description:
    This module searches for emotes in messages from multiple sources (7TV, BetterTTV, FrankerFaceZ). 
    It searches for emotes in the format `:emote_name:` and looks them up from the available 
    emote sources based on a configurable priority list. The emote size is also configurable.
    
Features:
    - Configurable emote sources and search priority (7TV, BTTV, FFZ) via Sopel config.
    - Configurable emote size (small, medium, large) via Sopel config.
    - Handles multiple emotes in a single message with rate limiting delays.
"""

import requests
import sopel
import re
import time

# API base URLs
SEVTV_API_URL = "https://7tv.io/v3/emotes"
BTTV_API_URL = "https://api.betterttv.net/3/emotes/shared/search"
FFZ_API_URL = "https://api.frankerfacez.com/v1/emotes"

# Size map for 7TV, BetterTTV, and FFZ URLs
SIZE_MAP = {
    'small': '1x',
    'medium': '2x',
    'large': '3x'
}

FFZ_SIZE_MAP = {
    'small': '1',
    'medium': '2',
    'large': '4'
}

REQUEST_DELAY = 1.0  # Delay between requests in seconds to avoid rate limiting

def get_size_suffix(size):
    """Get the appropriate size suffix based on the config setting."""
    return SIZE_MAP.get(size, '3x'), FFZ_SIZE_MAP.get(size, '4')

def search_7tv_emote(emote_name, size):
    """Search for an emote in the 7TV database."""
    params = {'query': emote_name}
    response = requests.get(SEVTV_API_URL, params=params)
    
    if response.status_code == 200:
        emotes = response.json()
        if emotes and len(emotes) > 0:
            emote = emotes[0]
            size_suffix, _ = get_size_suffix(size)
            return f"{emote['name']} -> https://cdn.7tv.app/emote/{emote['id']}/{size_suffix}"
    return None

def search_bttv_emote(emote_name, size):
    """Search for an emote in the BetterTTV database."""
    params = {'query': emote_name, 'limit': 1}
    response = requests.get(BTTV_API_URL, params=params)
    
    if response.status_code == 200:
        emotes = response.json()
        if emotes:
            emote = emotes[0]
            size_suffix, _ = get_size_suffix(size)
            return f"{emote['code']} -> https://cdn.betterttv.net/emote/{emote['id']}/{size_suffix}"
    return None

def search_ffz_emote(emote_name, size):
    """Search for an emote in the FrankerFaceZ database."""
    params = {'q': emote_name, 'page': 1, 'per_page': 1}
    response = requests.get(FFZ_API_URL, params=params)
    
    if response.status_code == 200:
        emotes = response.json()
        if 'emoticons' in emotes and emotes['emoticons']:
            emote = emotes['emoticons'][0]
            _, ffz_size_suffix = get_size_suffix(size)
            return f"{emote['name']} -> https://cdn.frankerfacez.com/emoticon/{emote['id']}/{ffz_size_suffix}"
    return None

# Mapping of sources to their corresponding search functions
SEARCH_FUNCTIONS = {
    '7tv': search_7tv_emote,
    'bttv': search_bttv_emote,
    'ffz': search_ffz_emote
}

def configure(config):
    """Configure the emote finder settings."""
    config.define_section('emotes', EmoteConfig)
    config.emotes.configure_setting('sources', 'List of emote sources (default: bttv, ffz)')
    config.emotes.configure_setting('size', 'Emote size (small, medium, large) (default: large)')

class EmoteConfigSection(sopel.config.types.StaticSection):
    sources = sopel.config.types.ListAttribute('sources', default=['bttv', 'ffz'])
    size = sopel.config.types.ChoiceAttribute('size', default='large', choices=['small', 'medium', 'large'])

def setup(bot):
    bot.config.define_section('emotes', EmoteConfigSection)

@sopel.module.rule('.*')
def find_emotes(bot, trigger):
    """Search for emotes in configurable sources based on priority."""
    message = trigger.group(0)
    emote_matches = re.findall(r':(\w+):', message)
    
    sources = bot.config.emotes.sources
    size = bot.config.emotes.size
    
    for idx, emote_name in enumerate(emote_matches):
        matched_emote = None
        
        # Search for the emote across the available sources based on priority
        for source in sources:
            search_func = SEARCH_FUNCTIONS.get(source)
            if search_func:
                matched_emote = search_func(emote_name, size)
                if matched_emote:
                    break  # Stop searching if an emote is found
        
        # Respond if an emote is found
        if matched_emote:
            bot.say(matched_emote)
        
        # Add a delay between requests if there are more than one emote
        if idx < len(emote_matches) - 1:
            time.sleep(REQUEST_DELAY)