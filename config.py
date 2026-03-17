import os
from typing import TypedDict


class ChannelConfig(TypedDict):
    guide_number: str
    guide_name: str
    lrt_channel_param: str


CHANNELS: list[ChannelConfig] = [
    {"guide_number": "1", "guide_name": "LTV1",    "lrt_channel_param": "LTV1"},
    {"guide_number": "2", "guide_name": "LTV2",    "lrt_channel_param": "LTV2"},
    {"guide_number": "3", "guide_name": "WORLD",   "lrt_channel_param": "WORLD"},
    {"guide_number": "4", "guide_name": "LR",      "lrt_channel_param": "LR"},
    {"guide_number": "5", "guide_name": "Klasika", "lrt_channel_param": "Klasika"},
    {"guide_number": "6", "guide_name": "Opus",    "lrt_channel_param": "Opus"},
    {"guide_number": "7", "guide_name": "LRT100",  "lrt_channel_param": "LRT100"},
]


class Config:
    DEVICE_ID: str = os.environ.get("DEVICE_ID", "LRTLIVE1")
    FRIENDLY_NAME: str = os.environ.get("DEVICE_FRIENDLY_NAME", "LRT Live HDHomeRun")
    MODEL_NUMBER: str = "HDHR5-4K"
    FIRMWARE_VERSION: str = "20190621"
    TUNER_COUNT: int = len(CHANNELS)
    BASE_URL: str = os.environ.get("BASE_URL", "http://localhost:5000")
    LRT_API_BASE_URL: str = (
        "https://www.lrt.lt/servisai/stream_url/live/get_live_url.php"
    )
    CHANNELS: list[ChannelConfig] = CHANNELS


class TestingConfig(Config):
    TESTING: bool = True
    BASE_URL: str = "http://localhost:5000"
