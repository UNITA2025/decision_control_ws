# decision_control_ws
This workspace implements and manages Perception &amp; Decision and Control algorithms for the ERP42 autonomous vehicle platform as ROS 2 packages.

# 간단 사용 방법.
1. 컨트롤 런치파일을 실행시켜서 ERP와의 통신을 시작한다.
>ros2 launch erp42_control_pkg erp42_base.launch.py

2. 실행하고자 하는 동작 모듈을 test_module에 만들고,
> ros2 run test_module_pkg 'ex)motor_only_parking_node'
