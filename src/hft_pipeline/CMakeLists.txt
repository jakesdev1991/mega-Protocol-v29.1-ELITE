cmake_minimum_required(VERSION 3.20)
project(omega_hft_pipeline LANGUAGES CXX)

add_library(omega_hft_pipeline STATIC
    src/avx_evaluator.cpp
    src/npu_scorer.cpp
    src/prediction.cpp
    src/yellowstone_ingestor.cpp
)

target_include_directories(omega_hft_pipeline PUBLIC include)
target_compile_features(omega_hft_pipeline PUBLIC cxx_std_20)
target_compile_options(omega_hft_pipeline PRIVATE -Wall -Wextra -Wpedantic -O3)

include(CheckCXXCompilerFlag)
check_cxx_compiler_flag("-mavx512f" OMEGA_HAS_AVX512F_FLAG)
if(OMEGA_HAS_AVX512F_FLAG)
    target_compile_options(omega_hft_pipeline PRIVATE -mavx512f)
endif()

add_executable(omega_hft_pipeline_demo src/main.cpp)
target_link_libraries(omega_hft_pipeline_demo PRIVATE omega_hft_pipeline)
