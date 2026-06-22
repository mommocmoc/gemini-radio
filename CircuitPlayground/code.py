"""
NanoBanana Radio — CP Express 쪽 (CircuitPython)
=================================================
NanoBanana Cam에서 검증된 패턴 그대로:
  - 부팅 시 show_bmp()를 1회 실행(깨끗한 메모리에서).
  - 화면 갱신은 auto-reload에 맡긴다: Pi가 CIRCUITPY/state.bmp 를 쓰면
    CircuitPython이 파일 변경을 감지해 code.py를 자동 재시작 → 다시 show_bmp().
  - 그래서 SHOW 신호도, supervisor.reload()도 필요 없다.

버튼:
  A/B 엣지(짧게 눌렀다 뗌) → Pi로 'A\n' / 'B\n' 전송.

필요 라이브러리 (CIRCUITPY/lib, ★ .mpy 번들에서):
  adafruit_gizmo/        (EInk_HD_Gizmo 포함)
  adafruit_ssd1681.mpy   (200x200 HD Gizmo 드라이버 — il0373 아님!)
  displayio, usb_cdc, gc 는 펌웨어 내장.
  ※ NanoBanana Cam에서 쓰던 lib 구성 그대로 복사하면 가장 확실.

주의:
  - E-Ink HD Gizmo(200x200, SSD1681) 사용 → EInk_HD_Gizmo().
    152x152 일반 Gizmo면 EInk_Gizmo() + adafruit_il0373 으로 바꿀 것.
  - show_bmp 시작에 gc.collect()로 메모리 확보(SAMD21 RAM이 작아 중요).
"""

import gc
import time

import board
import digitalio
import displayio
import usb_cdc
from adafruit_gizmo import eink_gizmo

BMP_PATH = "/state.bmp"   # Pi가 CIRCUITPY 루트에 써넣는 파일


def show_bmp(display):
    """state.bmp 를 E-Ink에 1회 표시. 파일이 없거나 메모리 부족이어도 죽지 않게."""
    gc.collect()
    f = None
    try:
        f = open(BMP_PATH, "rb")
        pic = displayio.OnDiskBitmap(f)
        g = displayio.Group()
        g.append(displayio.TileGrid(
            pic,
            pixel_shader=getattr(pic, "pixel_shader", displayio.ColorConverter()),
        ))
        display.root_group = g
        display.refresh()
        print("E-Ink 표시 완료")
    except OSError:
        print("state.bmp 없음 (첫 부팅이면 정상)")
    except MemoryError:
        print("메모리 부족 - 표시 실패")
        gc.collect()
    finally:
        if f:
            f.close()


# === 부팅 직후: 깨끗한 메모리에서 BMP 1회 표시 ===
display = eink_gizmo.EInk_HD_Gizmo()
show_bmp(display)

# === 버튼 준비 ===
btn_a = digitalio.DigitalInOut(board.BUTTON_A)
btn_a.switch_to_input(pull=digitalio.Pull.DOWN)
btn_b = digitalio.DigitalInOut(board.BUTTON_B)
btn_b.switch_to_input(pull=digitalio.Pull.DOWN)

ser = usb_cdc.data if usb_cdc.data else usb_cdc.console
prev_a = False
prev_b = False

print("CP 준비 완료. 버튼 대기 중.")

# === 메인 루프: 버튼 엣지 → Pi로 전송 ===
# 화면 갱신은 auto-reload가 처리하므로 여기서는 버튼만 본다.
while True:
    a, b = btn_a.value, btn_b.value

    if a and not prev_a:
        ser.write(b"A\n")
    if b and not prev_b:
        ser.write(b"B\n")
    prev_a, prev_b = a, b

    # 수신 버퍼는 비워둔다(Pi가 보낸 게 있어도 무시 — 화면은 auto-reload로 갱신)
    if ser.in_waiting:
        ser.read(ser.in_waiting)

    time.sleep(0.02)
