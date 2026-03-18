import pytest


class TestDiscoverJson:
    def test_returns_200(self, client):
        response = client.get("/discover.json")
        assert response.status_code == 200

    def test_content_type_is_json(self, client):
        response = client.get("/discover.json")
        assert response.content_type == "application/json"

    def test_contains_required_fields(self, client):
        data = client.get("/discover.json").get_json()
        for field in ("DeviceID", "FriendlyName", "ModelNumber", "FirmwareVersion",
                      "TunerCount", "BaseURL", "LineupURL"):
            assert field in data, f"Missing field: {field}"

    def test_lineup_url_ends_with_lineup_json(self, client):
        data = client.get("/discover.json").get_json()
        assert data["LineupURL"].endswith("/lineup.json")

    def test_tuner_count_is_seven(self, client):
        data = client.get("/discover.json").get_json()
        assert data["TunerCount"] == 7

    def test_base_url_matches_test_server(self, client):
        data = client.get("/discover.json").get_json()
        assert data["BaseURL"] == "http://localhost:5000"


class TestDeviceXml:
    def test_returns_200(self, client):
        response = client.get("/device.xml")
        assert response.status_code == 200

    def test_content_type_is_xml(self, client):
        response = client.get("/device.xml")
        assert "application/xml" in response.content_type

    def test_contains_silicondust_manufacturer(self, client):
        response = client.get("/device.xml")
        assert b"<manufacturer>Silicondust</manufacturer>" in response.data

    def test_contains_friendly_name(self, client):
        response = client.get("/device.xml")
        assert b"LRT Live HDHomeRun" in response.data

    def test_contains_model_number(self, client):
        response = client.get("/device.xml")
        assert b"HDHR5-4K" in response.data


class TestLineupStatus:
    def test_returns_200(self, client):
        response = client.get("/lineup_status.json")
        assert response.status_code == 200

    def test_scan_not_in_progress(self, client):
        data = client.get("/lineup_status.json").get_json()
        assert data["ScanInProgress"] == 0

    def test_has_source_list(self, client):
        data = client.get("/lineup_status.json").get_json()
        assert isinstance(data["SourceList"], list)
        assert len(data["SourceList"]) > 0

    def test_source_is_cable(self, client):
        data = client.get("/lineup_status.json").get_json()
        assert data["Source"] == "Cable"


class TestLineupJson:
    def test_returns_200(self, client):
        response = client.get("/lineup.json")
        assert response.status_code == 200

    def test_has_seven_channels(self, client):
        data = client.get("/lineup.json").get_json()
        assert len(data) == 7

    def test_each_channel_has_required_fields(self, client):
        data = client.get("/lineup.json").get_json()
        for channel in data:
            assert "GuideNumber" in channel
            assert "GuideName" in channel
            assert "URL" in channel

    def test_channel_urls_point_to_auto_endpoint(self, client):
        data = client.get("/lineup.json").get_json()
        for channel in data:
            assert "/auto/v" in channel["URL"]
            assert channel["URL"].startswith("http://localhost:5000")

    def test_guide_numbers_are_unique(self, client):
        data = client.get("/lineup.json").get_json()
        numbers = [ch["GuideNumber"] for ch in data]
        assert len(numbers) == len(set(numbers))

    def test_channel_1_is_lrt_televizija(self, client):
        data = client.get("/lineup.json").get_json()
        ch1 = next(ch for ch in data if ch["GuideNumber"] == "1")
        assert ch1["GuideName"] == "LRT TV"

    def test_all_expected_channels_present(self, client):
        data = client.get("/lineup.json").get_json()
        names = {ch["GuideName"] for ch in data}
        for expected in ("LRT TV", "LRT Plius", "LRT Lituanica",
                         "LRT Radijas", "LRT Klasika", "LRT Opus", "LRT 100"):
            assert expected in names

