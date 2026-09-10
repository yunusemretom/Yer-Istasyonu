# Third-Party Notices

This repository is **mixed-license**. The MIT license in `LICENSE` covers the
ground station application written for this project. The files listed below are
third-party and keep their original licenses.

## QFlightInstruments (`qflightinstruments/`, `qfi/`)

Qt flight instrument widgets: attitude indicator, HSI, airspeed, altimeter,
vertical speed, turn coordinator.

- Copyright (c) 2013 Marek M. Cel
- Dual licensed under the MIT License and GPL-3.0
- The widgets used by the application (`qfi/`) are used under the **MIT License**
  (`qflightinstruments/LICENSE_MIT.txt`)

## GPL-3.0 components (not used by the application)

These files are **GPL-3.0 only** and are not imported by `main.py`:

| File | Origin |
|---|---|
| `threadGUI.py` | JDE Developers Team (JdeRobot) |
| `qflightinstruments/python/threadGUI.py` | JDE Developers Team (JdeRobot) |
| `qflightinstruments/src/example/` | Marek M. Cel, GPL-3.0 demo application |
| `example.py` | demo derived from the JdeRobot/QFlightInstruments examples |

`example.py` and `threadGUI.py` are standalone demos kept for reference. Because
they are GPL-3.0, they are **not** covered by this repository's MIT license.
Anything that imports them inherits GPL-3.0 obligations.
