import re
import unicodedata


def slugify(value: str) -> str:
    value = unicodedata.normalize('NFKD', value)
    value = value.encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value).strip().lower()
    value = re.sub(r'[-\s]+', '-', value)
    return value


def get_client_ip(request) -> str:
    forwarded = request.headers.get('X-Forwarded-For')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.remote_addr or '0.0.0.0'


def category_icon(category: str) -> str:
    icons = {
        'web':    '🌐',
        'crypto': '🔐',
        'pwn':    '💥',
        'rev':    '🔄',
        'forensics': '🔍',
        'misc':   '🐉',
        'osint':  '👁',
        'network':'📡',
    }
    return icons.get(category.lower(), '🎯')
