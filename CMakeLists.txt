cmake_minimum_required(VERSION 3.13)
cmake_policy(SET CMP0003 NEW)
project(picoquic_ns C CXX)
find_package (Threads REQUIRED)
FIND_PACKAGE(PkgConfig REQUIRED)

set(CMAKE_C_STANDARD 11)

set(CMAKE_C_FLAGS "-std=c99 -Wall -Werror -O2 -g ${CC_WARNING_FLAGS} ${CMAKE_C_FLAGS}")

if(DISABLE_DEBUG_PRINTF)
    set(CMAKE_C_FLAGS "-DDISABLE_DEBUG_PRINTF ${CMAKE_C_FLAGS}")
endif()

set(CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/cmake")

OPTION(PICOQUIC_NS_FETCH_PICOQUIC "Fetch PicoQUIC during configuration" OFF)
if(PICOQUIC_NS_FETCH_PICOQUIC)
    # fetch picoquic from GitHub
    include(FetchContent)
    FetchContent_Declare(
            picoquic
            GIT_REPOSITORY  https://github.com/private-octopus/picoquic.git
            GIT_TAG         master
    )
    set(PICOQUIC_FETCH_PTLS ON)
    set(picoquic_BUILD_TESTS ON)
    FetchContent_MakeAvailable(picoquic)
endif ()

find_package(Picoquic REQUIRED)
message(STATUS "Picoquic/include: ${Picoquic_INCLUDE_DIRS}" )
message(STATUS "Picoquic library: ${Picoquic_LIBRARIES}" )

find_package(PTLS REQUIRED)
message(STATUS "picotls/include: ${PTLS_INCLUDE_DIRS}" )
message(STATUS "picotls libraries: ${PTLS_LIBRARIES}" )

find_package(OpenSSL REQUIRED)
message(STATUS "root: ${OPENSSL_ROOT_DIR}")
message(STATUS "OpenSSL_VERSION: ${OPENSSL_VERSION}")
message(STATUS "OpenSSL_INCLUDE_DIR: ${OPENSSL_INCLUDE_DIR}")
message(STATUS "OpenSSL_LIBRARIES: ${OPENSSL_LIBRARIES}")

include_directories(include lib tests 
    ${Picoquic_INCLUDE_DIRS} ${PTLS_INCLUDE_DIRS} ${OPENSSL_INCLUDE_DIR})

add_executable(pico_sim
    src/pico_sim.c
)

target_link_libraries(pico_sim
    ${Picoquic_LIBRARIES}
    ${PTLS_LIBRARIES}
    ${OPENSSL_LIBRARIES}
    ${CMAKE_DL_LIBS}
    ${CMAKE_THREAD_LIBS_INIT}
)

if (NOT PICOQUIC_NS_FETCH_PICOQUIC)
    # get all project files for formatting
    file(GLOB_RECURSE CLANG_FORMAT_SOURCE_FILES *.c *.h)

    # Adds clangformat as target that formats all source files
    add_custom_target(
        clangformat
        COMMAND clang-format
        -style=Webkit
        -i
        ${CLANG_FORMAT_SOURCE_FILES}
    )
endif (NOT PICOQUIC_NS_FETCH_PICOQUIC)