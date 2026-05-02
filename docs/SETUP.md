# Airport Board Setup Guide

Display live flight information near a configurable airport.

## Overview

The Airport Board plugin queries the OpenSky Network's public REST API for aircraft currently flying in the airspace around a given airport's coordinates. It shows the nearest tracked flight's callsign, altitude, and origin country. No API key is required for the anonymous tier (rate-limited to 400 requests/day).

- API reference: https://opensky-network.org/apidoc/rest.html

### Prerequisites

No API key required for the anonymous tier. Keep refresh interval >= 300s to stay within the 400 req/day limit.

## Quick Setup

1. **Enable** — Go to **Integrations** in your FiestaBoard settings and enable **Airport Board**.
2. **Configure** — Fill in the plugin settings (see Configuration Reference below).
3. **Template** — Add a page using the `airport_board` plugin variables:
   ```
   {{{ airport_board.status }}}
   ```
4. **View** — Navigate to your board page to see the live display.

## Template Variables

| Variable | Description | Example |
|---|---|---|
| `airport_board.airport` | Configured airport display name | `SFO` |
| `airport_board.flight_count` | Number of flights detected in the search area | `12` |
| `airport_board.callsign` | Callsign of the nearest tracked flight | `UAL123` |
| `airport_board.altitude_ft` | Geometric altitude of the nearest flight in feet | `8500` |
| `airport_board.origin_country` | Origin country of the nearest flight | `United States` |

## Configuration Reference

| Setting | Name | Description | Default |
|---|---|---|---|
| `enabled` | Enabled |  | `False` |
| `latitude` | Airport Latitude | Latitude of the airport (decimal degrees). | `37.6213` |
| `longitude` | Airport Longitude | Longitude of the airport (decimal degrees). | `-122.379` |
| `radius_deg` | Search Radius (degrees) | Search radius in degrees (≈1° = 111 km). Default 1.0. | `1.0` |
| `airport_name` | Airport Name | Display name shown on the board (e.g. SFO). | `SFO` |
| `refresh_seconds` | Refresh Interval (seconds) | How often to poll. Anonymous tier: keep ≥300s to stay under 400 req/day. | `300` |

## Troubleshooting

- **No flights** — verify coordinates are correct and the radius covers the airport.
- **Rate limited** — the anonymous tier allows 400 req/day (~1 per 216 seconds); keep refresh >= 300s.

