"""
Yapay Ufuk Göstergesi (Artificial Horizon / ADI)
================================================
Gereksinim:  pip install PySide6
Çalıştırma:  python artificial_horizon.py
"""

import sys
import math
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QHBoxLayout, QVBoxLayout, QSlider, QLabel, QGroupBox
)
from PySide6.QtCore import Qt, QTimer, QPointF, QRectF
from PySide6.QtGui import (
    QPainter, QColor, QPen, QBrush, QFont,
    QPainterPath, QLinearGradient, QConicalGradient, QPolygonF
)


# ─────────────────────────────────────────────
#  Renk sabitleri
# ─────────────────────────────────────────────
SKY_TOP     = QColor("#1a6fa8")
SKY_BOT     = QColor("#5aafdf")
GND_TOP     = QColor("#7a5c28")
GND_BOT     = QColor("#4a3518")
WHITE       = QColor(255, 255, 255)
RED         = QColor(220,  50,  50)
GREEN_HUD   = QColor( 80, 220, 120)
BLACK_SEMI  = QColor(  0,   0,   0, 180)
YELLOW      = QColor(240, 200,  40)


class ArtificialHorizon(QWidget):
    """
    Yapay ufuk (Attitude Direction Indicator) widget'ı.

    Dışarıdan güncelleme:
        widget.set_attitude(roll_deg, pitch_deg)
        widget.set_heading(heading_deg)
        widget.set_airspeed(knots)
        widget.set_altitude(feet)
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(420, 420)

        # Uçuş verileri
        self._roll    =  0.0   # derece  (-180 … +180)
        self._pitch   =  0.0   # derece  (-90  … +90)
        self._heading =  0.0   # derece  (0    … 360)
        self._airspeed=  0.0   # knot
        self._altitude=  0.0   # feet
        self._vsi     =  0.0   # ft/min (opsiyonel)

    # ── Setter API ──────────────────────────────
    def set_attitude(self, roll: float, pitch: float):
        self._roll  = roll
        self._pitch = pitch
        self.update()

    def set_heading(self, hdg: float):
        self._heading = hdg % 360
        self.update()

    def set_airspeed(self, spd: float):
        self._airspeed = max(0.0, spd)
        self.update()

    def set_altitude(self, alt: float):
        self._altitude = alt
        self.update()

    # ── Paint ───────────────────────────────────
    def paintEvent(self, _event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setRenderHint(QPainter.TextAntialiasing)

        W, H = self.width(), self.height()
        cx, cy = W / 2, H / 2
        R = min(W, H) / 2 - 4          # ufuk dairesi yarıçapı

        # Tüm çizimi daireye kırp
        clip = QPainterPath()
        clip.addEllipse(QPointF(cx, cy), R, R)
        p.setClipPath(clip)

        self._draw_background(p, cx, cy, R)
        self._draw_pitch_lines(p, cx, cy, R)

        p.setClipping(False)

        self._draw_roll_arc(p, cx, cy, R)
        self._draw_aircraft_symbol(p, cx, cy)
        self._draw_compass_strip(p, W, H)
        self._draw_speed_tape(p, cx, cy, R)
        self._draw_altitude_tape(p, cx, cy, R)
        self._draw_status_bar(p, W, H)

    # ── Arka plan: gökyüzü + yer ────────────────
    def _draw_background(self, p: QPainter, cx, cy, R):
        roll_r  = math.radians(-self._roll)
        pitch_px = self._pitch * (R / 45.0)

        p.save()
        p.translate(cx, cy)
        p.rotate(math.degrees(roll_r))           # dikkat: Qt rotate derece ister
        p.rotate(self._roll)                     # sıfırla, rotate(-roll) yerine:
        p.restore()

        # Doğru transform: önce merkeze taşı, döndür, sonra pitch
        p.save()
        p.translate(cx, cy)
        p.rotate(-self._roll)
        p.translate(0, pitch_px)

        half = R * 3

        # Gökyüzü gradyanı
        grad_sky = QLinearGradient(0, -half, 0, 0)
        grad_sky.setColorAt(0, SKY_TOP)
        grad_sky.setColorAt(1, SKY_BOT)
        p.fillRect(int(-half), int(-half), int(half*2), int(half), grad_sky)

        # Yer gradyanı
        grad_gnd = QLinearGradient(0, 0, 0, half)
        grad_gnd.setColorAt(0, GND_TOP)
        grad_gnd.setColorAt(1, GND_BOT)
        p.fillRect(int(-half), 0, int(half*2), int(half), grad_gnd)

        # Ufuk çizgisi
        pen = QPen(WHITE, 2)
        p.setPen(pen)
        p.drawLine(int(-half), 0, int(half), 0)

        p.restore()

    # ── Pitch (eğim) çizgileri ───────────────────
    def _draw_pitch_lines(self, p: QPainter, cx, cy, R):
        p.save()
        p.translate(cx, cy)
        p.rotate(-self._roll)
        pitch_px = self._pitch * (R / 45.0)
        p.translate(0, pitch_px)

        font = QFont("Monospace", 9)
        p.setFont(font)

        for deg in range(-40, 41, 5):
            if deg == 0:
                continue
            y = -deg * (R / 45.0)
            is_ten = (deg % 10 == 0)
            w = 55 if is_ten else 30
            lw = 1.5 if is_ten else 0.8

            pen = QPen(QColor(255, 255, 255, 200), lw)
            p.setPen(pen)
            p.drawLine(int(-w), int(y), int(w), int(y))

            if is_ten:
                p.setPen(QPen(WHITE))
                lbl = str(abs(deg))
                p.drawText(QPointF(w + 6, y + 4), lbl)
                p.drawText(QPointF(-w - 20, y + 4), lbl)

        p.restore()

    # ── Roll yay + tik çizgileri ─────────────────
    def _draw_roll_arc(self, p: QPainter, cx, cy, R):
        p.save()
        p.translate(cx, cy)

        arc_r = R - 10
        pen = QPen(QColor(255, 255, 255, 160), 1)
        p.setPen(pen)

        tick_angles = [-60, -45, -30, -20, -10, 0, 10, 20, 30, 45, 60]
        for a in tick_angles:
            rad = math.radians(a - 90)
            length = 12 if a % 30 == 0 else 7
            x1 = math.cos(rad) * arc_r
            y1 = math.sin(rad) * arc_r
            x2 = math.cos(rad) * (arc_r - length)
            y2 = math.sin(rad) * (arc_r - length)
            p.drawLine(QPointF(x1, y1), QPointF(x2, y2))

        # Roll gösterge üçgeni (sabit, üstte)
        pen_tri = QPen(WHITE, 1.5)
        p.setPen(pen_tri)
        p.setBrush(QBrush(WHITE))
        tri = QPolygonF([
            QPointF(0, -(arc_r - 2)),
            QPointF(-6, -(arc_r - 14)),
            QPointF( 6, -(arc_r - 14)),
        ])
        p.drawPolygon(tri)

        # Roll gösterge oku (dönen)
        p.rotate(-self._roll)
        p.setBrush(QBrush(YELLOW))
        p.setPen(QPen(YELLOW, 1))
        roll_ptr = QPolygonF([
            QPointF(0, -(arc_r - 2)),
            QPointF(-6, -(arc_r - 14)),
            QPointF( 6, -(arc_r - 14)),
        ])
        p.drawPolygon(roll_ptr)

        p.restore()

        # Dış halka
        pen_ring = QPen(QColor(80, 80, 80), 2)
        p.setPen(pen_ring)
        p.setBrush(Qt.NoBrush)
        p.drawEllipse(QPointF(cx, cy), R, R)

    # ── Uçak sembolü (sabit) ─────────────────────
    def _draw_aircraft_symbol(self, p: QPainter, cx, cy):
        p.save()
        p.translate(cx, cy)
        pen = QPen(RED, 3, Qt.SolidLine, Qt.RoundCap)
        p.setPen(pen)
        # Sol kanat
        p.drawLine(QPointF(-65, 0), QPointF(-22, 0))
        p.drawLine(QPointF(-22, 0), QPointF(-14, 9))
        # Sağ kanat
        p.drawLine(QPointF( 65, 0), QPointF( 22, 0))
        p.drawLine(QPointF( 22, 0), QPointF( 14, 9))
        # Merkez nokta
        p.setBrush(QBrush(RED))
        p.setPen(Qt.NoPen)
        p.drawEllipse(QPointF(0, 0), 5, 5)
        p.restore()

    # ── Pusula şeridi (üst) ──────────────────────
    def _draw_compass_strip(self, p: QPainter, W, H):
        bar_h = 30
        p.fillRect(0, 0, W, bar_h, BLACK_SEMI)

        font = QFont("Monospace", 9)
        p.setFont(font)

        dirs = {0:"N", 45:"NE", 90:"E", 135:"SE",
                180:"S", 225:"SW", 270:"W", 315:"NW"}
        px_per_deg = 3.2
        cx = W / 2
        hdg = self._heading

        p.save()
        p.setClipRect(0, 0, W, bar_h)

        for d in range(int(hdg) - 60, int(hdg) + 61):
            norm = d % 360
            x = cx + (d - hdg) * px_per_deg
            is_major = (norm % 45 == 0)
            is_mid   = (norm % 10 == 0)

            pen = QPen(QColor(255, 255, 255, 180 if is_major else 90),
                       1.5 if is_major else 0.8)
            p.setPen(pen)
            y_top = 4 if is_major else (10 if is_mid else 16)
            p.drawLine(QPointF(x, y_top), QPointF(x, bar_h - 2))

            if is_major and norm in dirs:
                p.setPen(QPen(WHITE))
                p.drawText(QPointF(x - 7, 12), dirs[norm])
            elif is_mid and not is_major:
                p.setPen(QPen(QColor(255, 255, 255, 140)))
                p.drawText(QPointF(x - 8, 11), str(norm))

        # Merkez işaret oku
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(RED))
        ptr = QPolygonF([
            QPointF(cx, bar_h),
            QPointF(cx - 5, bar_h - 10),
            QPointF(cx + 5, bar_h - 10),
        ])
        p.drawPolygon(ptr)
        p.restore()

        # Heading kutusu
        p.fillRect(int(cx) - 22, bar_h, 44, 18, BLACK_SEMI)
        p.setPen(QPen(GREEN_HUD))
        p.setFont(QFont("Monospace", 10))
        p.drawText(QRectF(cx - 22, bar_h, 44, 18),
                   Qt.AlignCenter, f"{int(self._heading):03d}°")

    # ── Hız bandı (sol) ─────────────────────────
    def _draw_speed_tape(self, p: QPainter, cx, cy, R):
        x = int(cx - R) + 2
        y = int(cy - 80)
        w, h = 42, 160
        self._draw_tape(p, x, y, w, h,
                        self._airspeed, 0, 120, "AS", right_side=False)

    # ── İrtifa bandı (sağ) ──────────────────────
    def _draw_altitude_tape(self, p: QPainter, cx, cy, R):
        x = int(cx + R) - 44
        y = int(cy - 80)
        w, h = 42, 160
        self._draw_tape(p, x, y, w, h,
                        self._altitude, 0, 500, "ALT", right_side=True)

    def _draw_tape(self, p, x, y, w, h, val, vmin, vmax,
                   label, right_side=True):
        # Arka plan
        p.fillRect(x, y, w, h, BLACK_SEMI)
        pen_border = QPen(QColor(255, 255, 255, 40), 0.5)
        p.setPen(pen_border)
        p.drawRect(x, y, w, h)

        font_sm = QFont("Monospace", 8)
        p.setFont(font_sm)

        steps = 5
        for i in range(steps + 1):
            v = vmin + (vmax - vmin) * i / steps
            yy = y + h - int((v - vmin) / (vmax - vmin) * h)
            p.setPen(QPen(QColor(255, 255, 255, 100), 0.8))
            if right_side:
                p.drawLine(x + 4,  yy, x + 10, yy)
                p.setPen(QPen(QColor(255, 255, 255, 160)))
                p.drawText(QPointF(x + 12, yy + 4), str(int(v)))
            else:
                p.drawLine(x + w - 4, yy, x + w - 10, yy)
                p.setPen(QPen(QColor(255, 255, 255, 160)))
                p.drawText(QPointF(x + 2, yy + 4), str(int(v)))

        # Değer göstergesi
        ratio = (val - vmin) / max(vmax - vmin, 1)
        vy = y + h - int(ratio * h)

        # Ok
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(GREEN_HUD))
        if right_side:
            ptr = QPolygonF([
                QPointF(x,       vy),
                QPointF(x + 14,  vy - 7),
                QPointF(x + 14,  vy + 7),
            ])
        else:
            ptr = QPolygonF([
                QPointF(x + w,       vy),
                QPointF(x + w - 14,  vy - 7),
                QPointF(x + w - 14,  vy + 7),
            ])
        p.drawPolygon(ptr)

        # Değer kutusu
        p.fillRect(x, vy - 10, w, 20, QColor(0, 160, 70, 220))
        p.setPen(QPen(QColor(0, 0, 0)))
        p.setFont(QFont("Monospace", 9))
        p.drawText(QRectF(x, vy - 10, w, 20),
                   Qt.AlignCenter, str(int(val)))

        # Etiket
        p.setPen(QPen(QColor(255, 255, 255, 160)))
        p.setFont(QFont("Sans", 8))
        p.drawText(QRectF(x, y - 16, w, 14), Qt.AlignCenter, label)

    # ── Alt durum çubuğu ────────────────────────
    def _draw_status_bar(self, p: QPainter, W, H):
        bar_h = 28
        p.fillRect(0, H - bar_h, W, bar_h, QColor(0, 0, 0, 200))
        p.setPen(QPen(GREEN_HUD))
        p.setFont(QFont("Monospace", 9))
        p.drawText(QRectF(8, H - bar_h, W - 16, bar_h),
                   Qt.AlignVCenter | Qt.AlignLeft,
                   "Bat 12.59v  EKF  Vibe  GPS:3D Fix")
        p.setPen(QPen(YELLOW))
        p.drawText(QRectF(8, H - bar_h, W - 16, bar_h),
                   Qt.AlignVCenter | Qt.AlignRight,
                   "Guided")


# ─────────────────────────────────────────────
#  Demo penceresi
# ─────────────────────────────────────────────
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Yapay Ufuk Göstergesi – PySide6")
        self.setStyleSheet("background:#1a1a1a; color:white;")

        self.ahi = ArtificialHorizon()

        # ── Slider paneli ──
        def make_slider(label, lo, hi, init, cb):
            grp = QGroupBox(label)
            grp.setStyleSheet(
                "QGroupBox{color:#aaa;font-size:11px;border:1px solid #444;"
                "margin-top:6px;padding:4px}"
                "QGroupBox::title{subcontrol-origin:margin;left:6px}"
            )
            sl = QSlider(Qt.Horizontal)
            sl.setRange(lo, hi)
            sl.setValue(init)
            sl.setStyleSheet(
                "QSlider::groove:horizontal{height:4px;background:#444;border-radius:2px}"
                "QSlider::handle:horizontal{width:14px;height:14px;margin:-5px 0;"
                "background:#5aafdf;border-radius:7px}"
            )
            val_lbl = QLabel(str(init))
            val_lbl.setFixedWidth(36)
            val_lbl.setStyleSheet("color:#fff;font-size:11px")
            sl.valueChanged.connect(lambda v: (val_lbl.setText(str(v)), cb(v)))
            row = QHBoxLayout()
            row.addWidget(sl)
            row.addWidget(val_lbl)
            grp.setLayout(row)
            return grp

        panel = QVBoxLayout()
        panel.setSpacing(4)
        panel.addWidget(make_slider("Roll  (°)", -60, 60,  0,
                                    lambda v: self.ahi.set_attitude(v, self.ahi._pitch)))
        panel.addWidget(make_slider("Pitch (°)", -30, 30,  0,
                                    lambda v: self.ahi.set_attitude(self.ahi._roll, v)))
        panel.addWidget(make_slider("Heading (°)",  0, 359, 0,
                                    self.ahi.set_heading))
        panel.addWidget(make_slider("Airspeed",     0, 120,  0,
                                    self.ahi.set_airspeed))
        panel.addWidget(make_slider("Altitude",     0, 500,  0,
                                    self.ahi.set_altitude))
        panel.addStretch()

        ctrl_widget = QWidget()
        ctrl_widget.setLayout(panel)
        ctrl_widget.setFixedWidth(200)

        root = QHBoxLayout()
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(12)
        root.addWidget(self.ahi, stretch=1)
        root.addWidget(ctrl_widget)

        container = QWidget()
        container.setLayout(root)
        self.setCentralWidget(container)

        # Simülasyon: uçak havada uçuyor gibi
        self._t = 0
        timer = QTimer(self)
        timer.timeout.connect(self._simulate)
        timer.start(50)   # 20 FPS

    def _simulate(self):
        """Slider'ı elle kullanmıyorsan otomatik uçuş simülasyonu."""
        pass   # Slider'lar kontrolü sağlıyor, istersen buraya otonom hareket ekle


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = MainWindow()
    win.resize(700, 460)
    win.show()
    sys.exit(app.exec())