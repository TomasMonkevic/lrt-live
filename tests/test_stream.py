import pytest
from unittest.mock import patch, MagicMock
import requests

from services.lrt_api import LrtApiError

_FETCH_PATCH = "routes.stream.fetch_stream_url"
_POPEN_PATCH = "routes.stream.subprocess.Popen"

MOCK_STREAM_URL = "https://cdn.lrt.lt/master.m3u8"
FAKE_TS_DATA = b"\x47" * 188


def _mock_popen(cmd, **kwargs):
    mock_proc = MagicMock()
    mock_proc.stdout.read = MagicMock(side_effect=[FAKE_TS_DATA, b""])
    mock_proc.stderr.read = MagicMock(return_value=b"")
    mock_proc.kill = MagicMock()
    mock_proc.wait = MagicMock()
    return mock_proc


class TestStreamChannel:
    def test_valid_channel_returns_200(self, client):
        with patch(_FETCH_PATCH, return_value=MOCK_STREAM_URL):
            with patch(_POPEN_PATCH, side_effect=_mock_popen):
                response = client.get("/auto/v1")
                data = response.data
        assert response.status_code == 200

    def test_returns_mpegts_content_type(self, client):
        with patch(_FETCH_PATCH, return_value=MOCK_STREAM_URL):
            with patch(_POPEN_PATCH, side_effect=_mock_popen):
                response = client.get("/auto/v1")
                _ = response.data
        assert "video/mp2t" in response.content_type

    def test_response_contains_ts_data(self, client):
        with patch(_FETCH_PATCH, return_value=MOCK_STREAM_URL):
            with patch(_POPEN_PATCH, side_effect=_mock_popen):
                response = client.get("/auto/v1")
                data = response.data
        assert len(data) == len(FAKE_TS_DATA)
        assert data[:1] == b"\x47"

    def test_unknown_channel_returns_404(self, client):
        response = client.get("/auto/v99")
        assert response.status_code == 404

    def test_lrt_api_failure_returns_502(self, client):
        with patch(_FETCH_PATCH, side_effect=LrtApiError("upstream down")):
            response = client.get("/auto/v1")
        assert response.status_code == 502

    def test_channel_1_calls_correct_param(self, client):
        with patch(_FETCH_PATCH, return_value=MOCK_STREAM_URL) as mock_fetch:
            with patch(_POPEN_PATCH, side_effect=_mock_popen):
                response = client.get("/auto/v1")
                _ = response.data
        mock_fetch.assert_called_once_with("LTV1")

    def test_ffmpeg_receives_stream_url(self, client):
        with patch(_FETCH_PATCH, return_value=MOCK_STREAM_URL):
            with patch(_POPEN_PATCH, side_effect=_mock_popen) as mock_popen:
                response = client.get("/auto/v1")
                _ = response.data
        cmd = mock_popen.call_args[0][0]
        assert MOCK_STREAM_URL in cmd
        assert "ffmpeg" in cmd[0]
        assert "-f" in cmd
        assert "mpegts" in cmd

    @pytest.mark.parametrize("guide_number", ["1", "2", "3", "4", "5", "6", "7"])
    def test_all_channels_return_200(self, client, guide_number):
        with patch(_FETCH_PATCH, return_value=MOCK_STREAM_URL):
            with patch(_POPEN_PATCH, side_effect=_mock_popen):
                response = client.get(f"/auto/v{guide_number}")
                _ = response.data
        assert response.status_code == 200


class TestFetchStreamUrl:
    def _make_lrt_response(self, content: str) -> dict:
        return {"response": {"data": {"content": content}}}

    def test_returns_content_field(self, app):
        mock_resp = MagicMock()
        mock_resp.json.return_value = self._make_lrt_response(MOCK_STREAM_URL)
        mock_resp.raise_for_status = MagicMock()
        with app.app_context():
            with patch("requests.get", return_value=mock_resp):
                from services.lrt_api import fetch_stream_url
                result = fetch_stream_url("LTV1")
        assert result == MOCK_STREAM_URL

    def test_raises_on_network_error(self, app):
        with app.app_context():
            with patch("requests.get", side_effect=requests.ConnectionError()):
                from services.lrt_api import fetch_stream_url
                with pytest.raises(LrtApiError):
                    fetch_stream_url("LTV1")

    def test_raises_on_bad_json_shape(self, app):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"unexpected": "shape"}
        mock_resp.raise_for_status = MagicMock()
        with app.app_context():
            with patch("requests.get", return_value=mock_resp):
                from services.lrt_api import fetch_stream_url
                with pytest.raises(LrtApiError):
                    fetch_stream_url("LTV1")

    def test_raises_on_empty_content(self, app):
        mock_resp = MagicMock()
        mock_resp.json.return_value = self._make_lrt_response("")
        mock_resp.raise_for_status = MagicMock()
        with app.app_context():
            with patch("requests.get", return_value=mock_resp):
                from services.lrt_api import fetch_stream_url
                with pytest.raises(LrtApiError):
                    fetch_stream_url("LTV1")

    def test_raises_on_http_error(self, app):
        mock_resp = MagicMock()
        mock_resp.raise_for_status.side_effect = requests.HTTPError("500")
        with app.app_context():
            with patch("requests.get", return_value=mock_resp):
                from services.lrt_api import fetch_stream_url
                with pytest.raises(LrtApiError):
                    fetch_stream_url("LTV1")
