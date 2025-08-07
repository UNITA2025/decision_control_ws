cmake_minimum_required(VERSION 3.8)
project(erp42_interfaces_pkg)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)

# Generate ROS 2 message interfaces
rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/ErpCmdMsg.msg"
  "msg/ErpStatusMsg.msg"
)

# Export runtime dependencies so other packages can use these interfaces
ament_export_dependencies(rosidl_default_runtime)

ament_package()