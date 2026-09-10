# Yer İstasyonu

A desktop ground control station shell for UAV and rocket operations: flight
instruments, an interactive map with waypoint editing, a live camera feed and
serial link selection, in one PyQt5 application.

Status: the interface, map and camera pipeline work. The telemetry link is not
finished, so instruments are not yet driven by a real vehicle.

![demo](docs/demo.gif)

## Tech stack

![Python](https://img.shields.io/badge/Python-3.7+-3776AB?logo=python&logoColor=white)
![PyQt5](https://img.shields.io/badge/PyQt5-5.15-41CD52?logo=qt&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-4.8-5C3EE8?logo=opencv&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-1.24-013243?logo=numpy&logoColor=white)
![pySerial](https://img.shields.io/badge/pySerial-Telemetry-lightgrey)
![License](https://img.shields.io/badge/License-MIT-blue)

## Quick start

```bash
# 1. Clone
git clone https://github.com/yunusemretom/Yer-Istasyonu.git
cd Yer-Istasyonu

# 2. Virtual environment and dependencies
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3. Run
python main.py
```

On Linux, PyQt5 also needs the system Qt platform plugins:

```bash
sudo apt install libxcb-xinerama0 libxcb-cursor0
```

To build a standalone executable:

```bash
python build_executable.py     # PyInstaller, uses main.spec
```

## How it works

The application is a Qt widget tree with three data sources feeding it: a serial
telemetry link, a camera, and operator input from the map.

```
main.py            main window, layout, command buttons
sidebar.py         connection panel, port and baud rate selection
hud.py             heads-up display overlay
map_widget.py      QGraphicsView map, markers, waypoints
qfi/               flight instrument widgets (third party)
resource_rc.py     compiled Qt resources from resource.qrc
```

Flight instruments come from QFlightInstruments rather than being drawn from
scratch: attitude indicator, HSI, airspeed, altimeter, vertical speed and turn
coordinator. Reimplementing calibrated instrument faces would have been weeks of
work for a worse result than an established MIT-licensed library.

### The Qt plugin conflict that cost a day

The first thing `main.py` does, before importing PyQt5, is this:

```python
for env_key in ("QT_QPA_PLATFORM_PLUGIN_PATH", "QT_PLUGIN_PATH"):
    env_value = os.environ.get(env_key, "")
    if "cv2" in env_value:
        os.environ.pop(env_key, None)
```

`opencv-python` ships its own copy of Qt and sets these variables on import. On
Linux the application would then load OpenCV's Qt plugins into a PyQt5 process
and abort with a platform plugin error that names neither library. The symptom
looked like a broken PyQt install; the cause was two Qt runtimes in one process.
Order matters here: the variables have to be cleared before PyQt5 is imported,
which is why this sits above the import block rather than in a setup function.

### Drawing the map instead of embedding a browser

The obvious way to get a map into Qt is to embed a web view and run Leaflet or
Folium in it. I started there and moved away from it. A web view adds a browser
engine to the dependency tree, makes the PyInstaller build much larger and more
fragile, and puts a process boundary between a click on the map and the
application state that has to react to it.

`map_widget.py` instead draws into a `QGraphicsView` directly and exposes what
the application needs as Qt signals:

```python
coordinate_clicked = pyqtSignal(float, float)   # lat, lon
command_executed   = pyqtSignal(str)
```

Waypoint editing then becomes ordinary Qt signal wiring rather than JavaScript
interop. The tradeoff is real and deliberate: there are no satellite basemap
tiles, so this is a geometry and waypoint view, not a substitute for a mapping
stack.

### Keeping the interface responsive

Camera capture blocks, so it cannot live on the GUI thread. `VideoThread` is a
`QThread` that owns the `cv2.VideoCapture` loop and pushes frames out as a
signal:

```python
class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)
```

The widget receives frames in a slot on the GUI thread. This matters more in
PyQt5 than it looks: touching a widget from a non-Qt thread is undefined
behavior, not merely bad style, and it fails as an intermittent crash rather
than an error. The vendored `threadGUI.py` demo shows the pattern I moved away
from, calling `gui.update()` straight from a plain Python thread. It is kept for
reference and is not imported by the application.

The same treatment is what the serial link still needs, and is the reason it is
listed as unfinished below rather than shipped.

## Known limitations

- **The telemetry link is incomplete.** The interface enumerates serial ports and
  offers baud rates, but there is no read loop or packet parser yet, so the
  instruments are not driven by vehicle data. This is the next piece of work.
- No satellite or street basemap tiles, by the design tradeoff above.
- No MAVLink implementation, so this is not a QGroundControl replacement and
  cannot do parameter or mission protocol exchange.
- The camera path and the map are the parts that have actually been exercised.
- The Windows PyInstaller build is the one that gets used; the Linux build is
  less tested.
- No unit tests. Verification has been manual.
- The repository is mixed-license. See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

## Roadmap

- Finish the telemetry link: a `QThread` serial reader feeding the instruments
  through signals, mirroring how `VideoThread` already works.
- Speak MAVLink rather than a custom format, so any ArduPilot or PX4 vehicle
  works unmodified.
- Offline raster tile support so the map has a real basemap without a web view.
- Automated tests around the packet parser once it exists, since that is the
  part most likely to break silently.

## License

MIT for the application code. See [LICENSE](LICENSE) and
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for the vendored components.

Turkish documentation is preserved in [README.tr.md](README.tr.md), alongside
[KULLANIM_KILAVUZU.md](KULLANIM_KILAVUZU.md).
