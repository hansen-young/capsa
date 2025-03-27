cmake_minimum_required(VERSION 3.10.0)
project(Capsa VERSION 0.1.0 LANGUAGES C CXX)

# Find python and pybind11
find_package(Python REQUIRED COMPONENTS Interpreter Development)
find_package(pybind11 REQUIRED)

# Find all .cpp files from cpp-code/
file(GLOB GAME_SRC "cpp-code/src/*.cpp")

# Create a shared library from the cpp files
add_library(cpp_code ${GAME_SRC})

# Include the headers from cpp-code/
target_include_directories(cpp_code PUBLIC cpp-code/include)
target_include_directories(cpp_code PUBLIC ${PYTHON_INCLUDE})
target_include_directories(cpp_code PUBLIC ${PYBIND11_INCLUDE})

# Create a python module from cpp_code
pybind11_add_module(c_utils cpp-code/src/bindings.cpp)
set_target_properties(cpp_code PROPERTIES POSITION_INDEPENDENT_CODE ON)
set_target_properties(c_utils PROPERTIES LIBRARY_OUTPUT_DIRECTORY ${PYTHON_MODULE_PATH})

# Link the shared library to the python module
target_link_libraries(c_utils PRIVATE cpp_code)


include(CTest)
enable_testing()

