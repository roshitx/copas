import ipaddress
import socket
from urllib.parse import urlparse


_BLOCKED_HOSTNAMES = frozenset({
    "localhost",
    "metadata.google.internal",
    "metadata.google.com",
})

_BLOCKED_TLDS = frozenset({".local", ".internal"})

_PRIVATE_NETWORKS = [
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fc00::/7"),
    ipaddress.ip_network("fe80::/10"),
]


def _is_private_ip(ip_str: str) -> bool:
    try:
        addr = ipaddress.ip_address(ip_str)
    except ValueError:
        return True
    return any(addr in network for network in _PRIVATE_NETWORKS)


def validate_public_url(url: str) -> str:
    """Validate that a URL points to a public internet host.

    Returns the validated URL on success.
    Raises ValueError with a descriptive message on failure.
    """
    parsed = urlparse(url)

    if parsed.scheme not in ("http", "https"):
        raise ValueError("URL scheme must be http or https")

    hostname = parsed.hostname
    if not hostname:
        raise ValueError("URL must contain a valid hostname")

    hostname_lower = hostname.lower()

    if hostname_lower in _BLOCKED_HOSTNAMES:
        raise ValueError("URL hostname is not allowed")

    if any(hostname_lower.endswith(tld) for tld in _BLOCKED_TLDS):
        raise ValueError("URL hostname is not allowed")

    try:
        addr_infos = socket.getaddrinfo(hostname, None, socket.AF_UNSPEC, socket.SOCK_STREAM)
    except socket.gaierror:
        raise ValueError("Could not resolve URL hostname")

    if not addr_infos:
        raise ValueError("URL hostname resolved to no addresses")

    for addr_info in addr_infos:
        ip_str = addr_info[4][0]
        if _is_private_ip(ip_str):
            raise ValueError("URL must not point to a private or reserved IP address")

    return url
