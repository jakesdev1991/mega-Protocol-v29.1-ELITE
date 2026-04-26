cmake_minimum_required(VERSION 3.10)
project(OmegaProtocol VERSION 26.0 LANGUAGES C)

# Set standard C11 for modern features, optimizing for the target Gentoo architecture
set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)

# Optimization flags for Peladn HO5 (AMD Ryzen / NPU context)
# -march=native ensures the compiler leverages the specific AMD instructions available
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -O3 -march=native -Wall -Wextra -fPIC")

# The unified interface headers
include_directories(include)

# ---------------------------------------------------------
# High Energy Physics (HEP) CLI Tool Integration
# Automatically configuring FastJet and ROOT if available
# ---------------------------------------------------------

# FastJet Integration
find_program(FASTJET_CONFIG fastjet-config)
if(FASTJET_CONFIG)
    message(STATUS "Found fastjet-config: ${FASTJET_CONFIG}")
    execute_process(COMMAND ${FASTJET_CONFIG} --cxxflags OUTPUT_VARIABLE FASTJET_CXXFLAGS OUTPUT_STRIP_TRAILING_WHITESPACE)
    execute_process(COMMAND ${FASTJET_CONFIG} --libs OUTPUT_VARIABLE FASTJET_LIBS OUTPUT_STRIP_TRAILING_WHITESPACE)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${FASTJET_CXXFLAGS}")
    # Note: FastJet is C++, so you would need to add a CXX wrapper to link these libs.
endif()

# ROOT Integration
find_program(ROOT_CONFIG root-config)
if(ROOT_CONFIG)
    message(STATUS "Found root-config: ${ROOT_CONFIG}")
    execute_process(COMMAND ${ROOT_CONFIG} --cflags OUTPUT_VARIABLE ROOT_CXXFLAGS OUTPUT_STRIP_TRAILING_WHITESPACE)
    execute_process(COMMAND ${ROOT_CONFIG} --libs OUTPUT_VARIABLE ROOT_LIBS OUTPUT_STRIP_TRAILING_WHITESPACE)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${ROOT_CXXFLAGS}")
endif()

# ---------------------------------------------------------

# Find math library for sqrt, log, pow algorithms
find_library(MATH_LIB m)

# Source files
set(SOURCES
    src/core_protocol/omega_core.c
    src/hardware/hsa_mapper.c
    src/utils/monitor.c
    src/domains/tokamak.c
    src/domains/biology_co_evolution.c
)

# Create the language-agnostic shared library
add_library(omega SHARED ${SOURCES})

# Link math operations
if(MATH_LIB)
    target_link_libraries(omega ${MATH_LIB})
endif()

# Output the library to the build directory explicitly
set_target_properties(omega PROPERTIES
    LIBRARY_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}"
)
