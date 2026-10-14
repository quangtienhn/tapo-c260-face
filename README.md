# Tapo C260 Face Recognition for Home Assistant

🇬🇧 English · [🇻🇳 Tiếng Việt](README.vi.md)

A Home Assistant custom integration that reads the **face-recognition events of a TP-Link Tapo C260** camera over the local network and turns them into entities, events and a management panel ("Face Manager"): who was seen, when, how often, and who is a stranger.

> **Unofficial.** Not affiliated with or endorsed by TP-Link. It uses the camera's local API with your *camera account* (Cloud Password). Use at your own risk.

## Features

- Poll the camera for face events; map camera **Face IDs → names** (the camera itself only knows IDs).
- Strangers are tracked automatically, so you can promote an unknown ID to a named person later.
- **Several faces in one event** are each handled separately (e.g. a known person together with a stranger).
- Per-event de-duplication, with a cooldown for known people.
- **Face Manager** sidebar panel (Vietnamese / English switch):
  - known / unknown people, add / rename / delete;
  - **day history** – who appeared at what time, first and latest sighting of the day;
  - **statistics** – strangers today / 7 / 30 days, chart, top strangers, per-person counts;
  - **integration health** – last successful poll, response time, errors, connection mode, dedup counter;
  - **settings** – polling, dedup, retention limits, sidebar visibility and name.
- Renaming a person applies to **all earlier records** (history stores Face IDs; names are resolved at display time).
- Retention limits: keep statistics/strangers for N days and at most M strangers.
- Works **together with Tapo-Control** by reusing its controller for the same camera, so the two integrations do not fight over the camera session.
- Re-authentication flow when the camera rejects the login.

## Requirements

- Home Assistant **2026.10** or newer (this is the version it was tested on).
- A Tapo **C260** with face recognition enabled in the Tapo app, and a camera account (username + Cloud Password).
- Optional: the [Tapo-Control](https://github.com/JurajNyiri/HomeAssistant-Tapo-Control) integration for the same camera.

## Installation

### HACS (custom repository)

1. HACS → ⋮ → **Custom repositories** → add `https://github.com/quangtienhn/tapo-c260-face`, category **Integration**.
2. Download **Tapo C260 Face Recognition**, then restart Home Assistant.
3. Settings → Devices & services → **Add integration** → *Tapo C260 Face Recognition*.

### Manual

Copy `custom_components/tapo_c260_face` into your Home Assistant `config/custom_components/` folder and restart.

## Setup

Enter the camera IP, the camera account username and the Cloud Password. Then open **Face Manager** (sidebar, or `/tapo_c260_face`), look at the *Unknown* tab after the camera has seen someone, and press **Add person** to give that Face ID a name.

## Entities (per camera)

| Entity | Description |
|---|---|
| `sensor.…_face_name`, `…_face_id` | Latest face (known people preferred inside one event). |
| `sensor.…_last_seen` | Camera time of the latest event. |
| `sensor.…_known_faces`, `…_unknown_faces` | Number of configured / discovered IDs. |
| `sensor.…_unknown_today`, `…_last_unknown_seen` | Strangers today / last stranger. |
| `binary_sensor.…_face_recognized` | Latest face is a known person. |
| `binary_sensor.…_stranger_detected` | On when a **new** stranger event arrives; auto-off after N seconds (default 30). |
| `event.…_face_event` | `face_recognized` / `face_unknown` with `face_id`, `name`, `event_time`, … |
| `binary_sensor.…_camera_connection`, `sensor.…_polling_errors`, `…_connection_mode`, `…_dedup_skipped` | Health (always available, even when polling fails). |
| `…_last_successful_poll`, `…_response_time` | Health, disabled by default (they change on every poll). |

The bus event `tapo_c260_face_detected` is fired for every new face with `face_id`, `name`, `recognized`, `event_time`, `camera`, `event_face_ids`, …

> Note: for a stranger the `Face Name` sensor reports `Stranger` (legacy versions ≤ 0.1.7.0 reported `Người lạ`; update any automations comparing the state).

## Example automations

```yaml
automation:
  - alias: Stranger at the door
    triggers:
      - trigger: state
        entity_id: binary_sensor.CAMERA_stranger_detected
        to: "on"
    actions:
      - action: notify.notify
        data:
          message: "Unknown face detected"

  - alias: Known person arrived
    triggers:
      - trigger: event
        event_type: tapo_c260_face_detected
        event_data:
          recognized: true
    actions:
      - action: notify.notify
        data:
          message: "{{ trigger.event.data.name }} was seen"
```

## Using it with Tapo-Control

If a Tapo-Control entry exists for the same camera IP and its controller is ready, this integration queries `searchDetectionList` **through that controller** and does not log in on its own. While Tapo-Control is still starting it waits; if Tapo-Control is disabled or fails, it falls back to its own session. This relies on Tapo-Control's internal data structures, so it may break when Tapo-Control changes them (tested with Tapo-Control 7.2.7).

## Data and privacy

Everything stays local. Camera credentials are stored in the Home Assistant config entry (like any integration). Face-ID → name mappings are stored in the config entry options; stranger lists and history are stored in `.storage/tapo_c260_face.*`. No faces or images are stored – only the numeric IDs the camera reports.

## Known limitations

- Tested on one camera model (C260) and one firmware.
- Statistics and time history start from the version that introduced them.
- Entity names are English; the Face Manager panel and the config flow are available in English and Vietnamese.

## Acknowledgements

The camera's local secure login (challenge/response with `cnonce`/`nonce`, `digest_passwd`, `lsk`/`ivb` session keys) follows the protocol documented by the open-source [pytapo](https://github.com/JurajNyiri/pytapo) project (MIT, © Juraj Nyíri). This repository contains its own asyncio/aiohttp implementation and bundles no source files from pytapo or Tapo-Control. The optional shared mode talks to the controller object of [Tapo-Control](https://github.com/JurajNyiri/HomeAssistant-Tapo-Control) (Apache-2.0) at runtime. Thanks to those projects.

## License

[MIT](LICENSE)
