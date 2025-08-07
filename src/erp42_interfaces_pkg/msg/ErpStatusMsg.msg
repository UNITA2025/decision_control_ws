int8   control_mode  # 수동(0), 자동(1) 등
bool   e_stop        #긴급 정지 신호
uint8  gear          # 0: 중립, 1: 전진, 2: 후진
uint8  speed         # 0 ~ 200
int32  steer         # ±2000 (조향 각도)
uint8  brake         # 0 ~ 33
int32  encoder       # 바퀴 회전 수 등
uint8  alive         # 수신 감시용 카운터
