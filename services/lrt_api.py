import requests
from flask import current_app


class LrtApiError(Exception):
    """Raised when the LRT API returns an unexpected or failed response."""


def fetch_stream_url(channel_param: str) -> str:
    """Fetch the HLS stream URL for the given LRT channel parameter.

    Returns the ``content`` field from the LRT API response.
    Raises :class:`LrtApiError` on network failure or unexpected response shape.
    """
    api_url = current_app.config["LRT_API_BASE_URL"]
    try:
        response = requests.get(
            api_url,
            params={"channel": channel_param},
            timeout=10,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise LrtApiError(f"LRT API request failed: {exc}") from exc

    try:
        data = response.json()
        stream_url: str = data["response"]["data"]["content"]
    except (KeyError, TypeError, ValueError) as exc:
        raise LrtApiError(f"Unexpected LRT API response shape: {exc}") from exc

    if not stream_url:
        raise LrtApiError("LRT API returned an empty stream URL")

    return stream_url
