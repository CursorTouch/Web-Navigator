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


RELEVANT_FILE_EXTENSIONS = set([
	'.pdf','.doc','.docx','.xls',
	'.xlsx','.ppt','.pptx','.txt',
	'.csv','.json','.png','.jpg',
	'.jpeg','.gif','.svg','.zip',
	'.rar','.7z','.tar','.gz',
	'.bz2','.mp3','.mp4','.wav',
	'.ogg','.flac','.webm','.mp4',
	'.avi','.mkv','.mov','.wmv',
	'.mpg','.mpeg','.m4v','.3gp',
])

RELEVANT_CONTEXT_TYPES =set([
    #Document Files
    'application/x-7z-compressed',
	'application/zip',
	'application/x-rar-compressed',
	'application/x-iso9660-image',
	'application/x-tar',
	'application/x-gzip',
	'application/x-bzip2',
	'application/vnd.ms-excel',
	'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
	'application/vnd.ms-powerpoint',
	'application/vnd.openxmlformats-officedocument.presentationml.presentation',
	'application/pdf',
	'application/msword',
	'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
	'application/vnd.oasis.opendocument.text',
    #Audio Files
    'audio/mpeg','audio/wav','audio/mp3','audio/ogg','audio/flac','audio/webm',
	#Video Files
	'video/mp4','video/ogg','video/webm','video/quicktime',
	#Image Files
	'image/jpeg','image/png','image/gif','image/bmp','image/svg+xml'
])

RELEVANT_RESOURCE_TYPES = [
	'document',
	'stylesheet',
	'image',
	'font',
	'script',
	'iframe',
]

IGNORED_URL_PATTERNS = set([
	'analytics',
	'tracking',
	'telemetry',
    'googletagmanager',
	'beacon',
	'metrics',
	'doubleclick',
	'adsystem',
	'adserver',
	'advertising',
    'cdn.optimizely',
	'facebook.com/plugins',
	'platform.twitter',
	'linkedin.com/embed',
	'livechat',
	'zendesk',
	'intercom',
	'crisp.chat',
	'hotjar',
	'push-notifications',
	'onesignal',
	'pushwoosh',
	'heartbeat',
	'ping',
	'alive',
	'webrtc',
	'rtmp://',
	'wss://',
	'cloudfront.net',
	'fastly.net'
])