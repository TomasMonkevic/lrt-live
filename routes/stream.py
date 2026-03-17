import logging
import subprocess

from flask import Blueprint, Response, abort, current_app, stream_with_context

from services.lrt_api import LrtApiError, fetch_stream_url

stream_blueprint = Blueprint("stream", __name__)

logger = logging.getLogger(__name__)

_CHUNK_SIZE = 65536


def _generate_ts_stream(stream_url: str):
    """Remux an HLS stream into a continuous MPEG-TS byte stream using FFmpeg.

    FFmpeg handles all HLS complexity: master playlists, separate audio
    renditions, segment fetching, and proper audio/video muxing into MPEG-TS.
    """
    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel", "error",
        "-i", stream_url,
        "-c", "copy",
        "-f", "mpegts",
        "-",
    ]

    logger.info("Starting FFmpeg: %s", " ".join(cmd))
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    try:
        while True:
            chunk = proc.stdout.read(_CHUNK_SIZE)
            if not chunk:
                break
            yield chunk
    except GeneratorExit:
        pass
    finally:
        proc.kill()
        proc.wait()
        stderr = proc.stderr.read().decode(errors="replace")
        if stderr:
            logger.error("FFmpeg stderr: %s", stderr)


@stream_blueprint.route("/auto/v<channel_number>")
def stream_channel(channel_number: str) -> Response:
    channels = current_app.config["CHANNELS"]
    channel = next(
        (ch for ch in channels if ch["guide_number"] == channel_number),
        None,
    )
    if channel is None:
        abort(404)

    try:
        stream_url = fetch_stream_url(channel["lrt_channel_param"])
    except LrtApiError as exc:
        current_app.logger.error(
            "Failed to fetch stream URL for channel %s: %s", channel_number, exc
        )
        abort(502)

    return Response(
        stream_with_context(_generate_ts_stream(stream_url)),
        mimetype="video/mp2t",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Transfer-Encoding": "chunked",
        },
    )
