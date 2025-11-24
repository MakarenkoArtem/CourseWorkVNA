cmake_minimum_required(VERSION 3.10)
project(VNAKitExample LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Указываем, что libVNAKit.so — импортированная разделяемая библиотека
add_library(VNAKit SHARED IMPORTED)
set_target_properties(VNAKit PROPERTIES
    IMPORTED_LOCATION "${CMAKE_CURRENT_SOURCE_DIR}/libVNAKit.so"
    INTERFACE_INCLUDE_DIRECTORIES "${CMAKE_CURRENT_SOURCE_DIR}"
)

# Источники
add_executable(vna_example VNAKit.h VNAKitDevice.h main.cpp VNAKitDevice.cpp)

# Линковка с импортированной библиотекой
target_link_libraries(vna_example PRIVATE VNAKit)

# Устанавливаем RPATH, чтобы бинарник искал .so рядом с собой
set_target_properties(vna_example PROPERTIES
    INSTALL_RPATH "$ORIGIN"
    BUILD_RPATH "$ORIGIN"
)

# Опционально: копировать .so в директорию сборки (для удобства запуска)
add_custom_command(TARGET vna_example POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy_if_different
        ${CMAKE_CURRENT_SOURCE_DIR}/libVNAKit.so
        $<TARGET_FILE_DIR:vna_example>/
)
