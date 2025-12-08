cmake_minimum_required(VERSION 3.10)
project(vna_calibration_python)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

# ---- Найти Python ----
find_package(Python3 COMPONENTS Interpreter Development REQUIRED)

# =============== НАСТРОЙКИ PYBIND11 ===============
# Найти pybind11
set(pybind11_DIR "/usr/lib/python3/dist-packages/pybind11/share/cmake/pybind11")
find_package(pybind11 REQUIRED)

# ---- Создание Python модуля ----
pybind11_add_module(vnakit_calibration
        ../bindingsCalibration.cpp
        ../VNACalibration.cpp
)

# Если нужны include директории
target_include_directories(vnakit_calibration PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/..)

# ---- Установка RPATH ----
set_target_properties(vnakit_calibration PROPERTIES
    INSTALL_RPATH "$ORIGIN"
    BUILD_RPATH "$ORIGIN"
)

# ---- Копирование дополнительных файлов (при необходимости) ----
# Здесь можно указать команды для копирования, если это необходимо
# add_custom_command(TARGET vna_cal POST_BUILD ...)
