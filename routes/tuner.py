from flask import Blueprint, Response, jsonify, current_app

tuner_blueprint = Blueprint("tuner", __name__)


@tuner_blueprint.route("/discover.json")
def discover() -> Response:
    base_url = current_app.config["BASE_URL"]
    return jsonify({
        "DeviceID":        current_app.config["DEVICE_ID"],
        "FriendlyName":    current_app.config["FRIENDLY_NAME"],
        "ModelNumber":     current_app.config["MODEL_NUMBER"],
        "FirmwareVersion": current_app.config["FIRMWARE_VERSION"],
        "TunerCount":      current_app.config["TUNER_COUNT"],
        "BaseURL":         base_url,
        "LineupURL":       f"{base_url}/lineup.json",
    })


@tuner_blueprint.route("/device.xml")
def device_xml() -> Response:
    base_url = current_app.config["BASE_URL"]
    friendly_name = current_app.config["FRIENDLY_NAME"]
    device_id = current_app.config["DEVICE_ID"]
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<root xmlns="urn:schemas-upnp-org:device-1-0">\n'
        "  <specVersion><major>1</major><minor>0</minor></specVersion>\n"
        f"  <URLBase>{base_url}</URLBase>\n"
        "  <device>\n"
        "    <deviceType>urn:schemas-upnp-org:device:MediaServer:1</deviceType>\n"
        f"    <friendlyName>{friendly_name}</friendlyName>\n"
        "    <manufacturer>Silicondust</manufacturer>\n"
        "    <modelNumber>HDHR5-4K</modelNumber>\n"
        "    <modelName>HDHomeRun CONNECT</modelName>\n"
        f"    <UDN>uuid:{device_id}</UDN>\n"
        "  </device>\n"
        "</root>"
    )
    return Response(xml, mimetype="application/xml")


@tuner_blueprint.route("/lineup_status.json")
def lineup_status() -> Response:
    return jsonify({
        "ScanInProgress": 0,
        "ScanPossible":   1,
        "Source":         "Cable",
        "SourceList":     ["Cable"],
    })


@tuner_blueprint.route("/lineup.json")
def lineup() -> Response:
    base_url = current_app.config["BASE_URL"]
    channels = current_app.config["CHANNELS"]
    lineup_data = [
        {
            "GuideNumber": ch["guide_number"],
            "GuideName":   ch["guide_name"],
            "URL":         f"{base_url}/auto/v{ch['guide_number']}",
        }
        for ch in channels
    ]
    return jsonify(lineup_data)
