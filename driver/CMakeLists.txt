cmake_minimum_required(VERSION 3.10)
project(VNAKitExample LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# =============== НАСТРОЙКИ PYBIND11 ===============
# Найти pybind11 (установленный через pip или системно)
set(pybind11_DIR "/usr/lib/python3/dist-packages/pybind11/share/cmake/pybind11")
find_package(pybind11 REQUIRED)

# =============== ИМПОРТ БИБЛИОТЕКИ VNAKit ===============
# Указываем, что libVNAKit.so — импортированная разделяемая библиотека
add_library(VNAKit SHARED IMPORTED)
set_target_properties(VNAKit PROPERTIES
        IMPORTED_LOCATION "${CMAKE_CURRENT_SOURCE_DIR}/libVNAKit.so"
        INTERFACE_INCLUDE_DIRECTORIES "${CMAKE_CURRENT_SOURCE_DIR}"
)

# =============== СОЗДАНИЕ PYTHON-МОДУЛЯ ===============
# Создаём модуль для Python (вместо исполняемого файла)
pybind11_add_module(vnakit_py
        bindings.cpp      # Ваш файл с биндингами
        VNAKitDevice.cpp  # Реализация вашего класса
)

# Линковка с VNAKit и настройка include-директорий
target_link_libraries(vnakit_py PRIVATE
        VNAKit
)

target_include_directories(vnakit_py PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}  # Для заголовков VNAKitDevice.h и VNAKit.h
)

# =============== НАСТРОЙКА RPATH ===============
# Гарантируем, что модуль найдёт libVNAKit.so при импорте в Python
set_target_properties(vnakit_py PROPERTIES
        INSTALL_RPATH "$ORIGIN"
        BUILD_RPATH "$ORIGIN"
)

# =============== КОПИРОВАНИЕ libVNAKit.so В ДИРЕКТОРИЮ СБОРКИ ===============
# Это критично для запуска из Python!
add_custom_command(TARGET vnakit_py POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy_if_different
        ${CMAKE_CURRENT_SOURCE_DIR}/libVNAKit.so
        $<TARGET_FILE_DIR:vnakit_py>/
        COMMENT "Copying libVNAKit.so to output directory"
)

# =============== ОПЦИОНАЛЬНО: УДАЛЕНИЕ СИМВОЛОВ ДЛЯ ПРОИЗВОДИТЕЛЬНОСТИ ===============
if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
    target_compile_options(vnakit_py PRIVATE -fvisibility=hidden)
endif()