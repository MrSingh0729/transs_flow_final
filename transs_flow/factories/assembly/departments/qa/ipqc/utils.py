# utils.py
from urllib.parse import urlparse, parse_qs, urlunparse, urlencode

def add_token_to_url(url, platform, access_token):
    """
    Add platform-specific token to URL
    """
    if not access_token:
        return url

    parsed_url = list(urlparse(url))

    if platform == 'lark':
        # Add access_token as query parameter
        query_params = parse_qs(parsed_url[4])
        query_params['access_token'] = [access_token]
        parsed_url[4] = urlencode(query_params, doseq=True)
    elif platform == 'feishu':
        # Add app_access_token as query parameter
        query_params = parse_qs(parsed_url[4])
        query_params['app_access_token'] = [access_token]
        parsed_url[4] = urlencode(query_params, doseq=True)

    return urlunparse(parsed_url)
