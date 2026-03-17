# LRT Live TV Server

> **WARNING: This project was entirely created with AI (Claude). Review all code before using in production.**

Flask-based HDHomeRun-compatible live TV tuner server for [LRT](https://www.lrt.lt) (Lithuanian National Broadcaster). Designed to integrate with Jellyfin as a live TV source.

## Supported Channels

| # | Channel |
|---|---------|
| 1 | LTV1 |
| 2 | LTV2 |
| 3 | WORLD |
| 4 | LR |
| 5 | Klasika |
| 6 | Opus |
| 7 | LRT100 |

## How It Works

The server emulates an HDHomeRun network tuner. When Jellyfin requests a channel, it:

1. Fetches a signed stream URL from the LRT API
2. Uses FFmpeg to remux the HLS stream into a continuous MPEG-TS stream
3. Pipes the MPEG-TS data back to Jellyfin

## Setup

### Docker (recommended)

```bash
docker build -t lrt-live .
docker run -d -p 5000:5000 --name lrt-live lrt-live
```

### Local

```bash
pip install -r requirements.txt
cp .env.example .env
python app.py
```

## Jellyfin Configuration

1. Go to **Dashboard > Live TV > Tuner Devices**
2. Add tuner, select **HD Homerun**
3. Enter the server address (e.g. `http://192.168.1.1:5000`)
4. Save

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `BASE_URL` | `http://localhost:5000` | Public URL of the server |
| `FLASK_DEBUG` | `false` | Enable Flask debug mode |

## API Endpoints

- `GET /discover.json` — Device discovery
- `GET /lineup.json` — Channel lineup
- `GET /lineup_status.json` — Tuner status
- `GET /auto/v<n>` — Stream channel (MPEG-TS)

## Running Tests

```bash
pytest
```
