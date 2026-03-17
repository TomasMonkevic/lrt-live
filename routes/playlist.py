from flask import Blueprint, Response, current_app

from services.lrt_api import LrtApiError, fetch_stream_url

playlist_blueprint = Blueprint("playlist", __name__)


@playlist_blueprint.route("/playlist.m3u")
def playlist() -> Response:
    channels = current_app.config["CHANNELS"]
    lines = ["#EXTM3U"]
    for ch in channels:
        try:
            stream_url = fetch_stream_url(ch["lrt_channel_param"])
        except LrtApiError as exc:
            current_app.logger.error(
                "Skipping channel %s, failed to fetch stream URL: %s",
                ch["guide_name"],
                exc,
            )
            continue
        lines.append(
            f'#EXTINF:-1 tvg-id="{ch["guide_name"]}" tvg-name="{ch["guide_name"]}"'
            f' group-title="LRT",{ch["guide_name"]}'
        )
        lines.append(stream_url)

    content = "\n".join(lines) + "\n"
    return Response(content, mimetype="application/x-mpegurl")
