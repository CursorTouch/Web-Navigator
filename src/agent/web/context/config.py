from dataclasses import dataclass,field
from typing import Optional,Any

@dataclass
class ContextConfig:
    credentials:dict[str,Any]=field(default_factory=dict)
    minimum_wait_page_load_time:float=0.5
    wait_for_network_idle_page_load_time:float=1
    maximum_wait_page_load_time:float=5
    disable_security:bool=True
    user_agent:str="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"


RELEVANT_RESOURCE_TYPES = [
	'document',
	'stylesheet',
	'image',
	'font',
	'script',
	'iframe',
]

RELEVANT_CONTENT_TYPES = [
	'text/html',
	'text/css',
	'application/javascript',
	'image/',
	'font/',
	'application/json',
]

IGNORED_URL_PATTERNS = [
	# Analytics and tracking
	'analytics',
	'tracking',
	'telemetry',
    'googletagmanager'
	'beacon',
	'metrics',
	# Ad-related
	'doubleclick',
	'adsystem',
	'adserver',
	'advertising',
    'cdn.optimizely',
	# Social media widgets
	'facebook.com/plugins',
	'platform.twitter',
	'linkedin.com/embed',
	# Live chat and support
	'livechat',
	'zendesk',
	'intercom',
	'crisp.chat',
	'hotjar',
	# Push notifications
	'push-notifications',
	'onesignal',
	'pushwoosh',
	# Background sync/heartbeat
	'heartbeat',
	'ping',
	'alive',
	# WebRTC and streaming
	'webrtc',
	'rtmp://',
	'wss://',
	# Common CDNs for dynamic content
	'cloudfront.net',
	'fastly.net'
]