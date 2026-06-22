"""
NanoBanana Radio — CP Express boot.py
======================================
NanoBanana Cam과 동일한 방식:
  - 평소 부팅: storage.remount("/", readonly=True)
      → CP 입장에선 읽기전용 = USB 호스트(Pi)가 CIRCUITPY에 state.bmp 쓰기 가능.
      → Pi의 파일 쓰기가 auto-reload를 트리거해 code.py가 재시작되며 화면 갱신.
  - A 버튼을 누른 채 부팅: 쓰기 권한을 CP가 보유(=Pi 쓰기 불가)
      → Mac/Pi에서 code.py 등을 수정할 때 이 모드로 부팅.

  - console + data 둘 다 활성화(Pi와 버튼 신호 통신용).

주의:
  boot.py 변경은 hard reset(전원 재인가/reset 버튼) 후에만 적용됨.
"""
import board
import digitalio
import storage
import usb_cdc

# A 버튼 상태로 모드 분기
btn_a = digitalio.DigitalInOut(board.BUTTON_A)
btn_a.switch_to_input(pull=digitalio.Pull.DOWN)

if btn_a.value:
    # A 누른 채 부팅: CP가 쓰기 보유(편집 모드). Pi는 이때 쓰기 불가.
    pass
else:
    # 일반 부팅: CP 읽기전용 → Pi(USB 호스트)가 state.bmp 쓰기 가능 + auto-reload 동작
    storage.remount("/", readonly=True)

usb_cdc.enable(console=True, data=True)
