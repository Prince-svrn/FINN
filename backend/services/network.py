"""Bounded HTTP reads. Arbitrary private-network fetches and redirects are rejected."""
import ipaddress
import socket
from urllib.parse import urlsplit, urljoin
import httpx

USER_AGENT = 'Mozilla/5.0 (compatible; FINN research prototype; public disclosure reader)'
MAX_BYTES = 20*1024*1024

def validate_public_url(url):
    p = urlsplit(url)
    if p.scheme != 'https' or not p.hostname or p.username or p.password or p.port not in (None,443):
        raise ValueError('Only public HTTPS document URLs are accepted.')
    if p.hostname.lower() in {'localhost', 'metadata.google.internal'}:
        raise ValueError('Private address rejected.')
    try:
        addresses = socket.getaddrinfo(p.hostname,443,type=socket.SOCK_STREAM)
    except socket.gaierror:
        # Managed HTTPS/SOCKS proxies may resolve DNS remotely. Only fixed public
        # providers are accepted in that environment, never a user-chosen host.
        trusted={'www.screener.in','www.nseindia.com','nsearchives.nseindia.com',
                 'archives.nseindia.com','www.bseindia.com','api.bseindia.com',
                 'www.kpit.com','www.tcs.com','www.infosys.com'}
        if p.hostname.lower() in trusted:return url
        raise ValueError('Cannot verify document host with local DNS.')
    if any(not ipaddress.ip_address(a[4][0]).is_global for a in addresses):
        raise ValueError('Private address rejected.')
    return url

async def fetch(url, client=None, max_bytes=MAX_BYTES):
    own = client is None
    client = client or httpx.AsyncClient(timeout=22,headers={'User-Agent': USER_AGENT})
    try:
        for _ in range(4):
            validate_public_url(url)
            async with client.stream('GET', url, follow_redirects=False) as r:
                if r.status_code in (301,302,303,307,308):
                    url = urljoin(url,r.headers['location']); continue
                r.raise_for_status()
                data = bytearray()
                async for block in r.aiter_bytes():
                    data.extend(block)
                    if len(data) > max_bytes: raise ValueError('Source exceeds 20 MB download limit.')
                return bytes(data), url
        raise ValueError('Too many redirects.')
    finally:
        if own: await client.aclose()
