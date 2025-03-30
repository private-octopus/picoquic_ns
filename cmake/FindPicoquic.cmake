# - Try to find Picoquic

if (PICOQUIC_NS_FETCH_PICOQUIC)
    set(Picoquic_INCLUDE_DIR ${picoquic_SOURCE_DIR}/picoquic)
    set(Picoquic_TEST_DIR ${picoquic_SOURCE_DIR}/picoquictest)
    set(Picoquic_LOG_DIR ${picoquic_SOURCE_DIR}/loglib)

    set(Picoquic_CORE_LIBRARY picoquic-core)
    set(Picoquic_LOG_LIBRARY picoquic-log)
    set(Picoquic_TEST_LIBRARY picoquic-test)
    set(Picoquic_HTTP_LIBRARY picohttp-core)
else(PICOQUIC_NS_FETCH_PICOQUIC)
    find_path(Picoquic_INCLUDE_DIR
        NAMES picoquic.h
        HINTS ${CMAKE_SOURCE_DIR}/../picoquic/picoquic
              ${CMAKE_BINARY_DIR}/../picoquic/picoquic
              ../picoquic/picoquic/ )

    find_path(Picoquic_TEST_DIR
        NAMES picoquic_ns.h
        HINTS ${CMAKE_SOURCE_DIR}/../picoquic/picoquictest
              ${CMAKE_BINARY_DIR}/../picoquic/picoquictest
              ../picoquic/picoquictest/ )

    find_path(Picoquic_LOG_DIR
        NAMES autoqlog.h
        HINTS ${CMAKE_SOURCE_DIR}/../picoquic/loglib
              ${CMAKE_BINARY_DIR}/../picoquic/loglib
              ../picotls/picoquic/ )

    set(Picoquic_HINTS
        ${CMAKE_BINARY_DIR}/../picoquic
        ${CMAKE_BINARY_DIR}/../picoquic/build
        ../picoquic
        ../picoquic/build)

    find_library(Picoquic_CORE_LIBRARY picoquic-core HINTS ${Picoquic_HINTS})
    find_library(Picoquic_LOG_LIBRARY picoquic-log HINTS ${Picoquic_HINTS})
    find_library(Picoquic_TEST_LIBRARY picoquic-test HINTS ${Picoquic_HINTS})
    find_library(Picoquic_HTTP_LIBRARY picohttp-core HINTS ${Picoquic_HINTS})
endif(PICOQUIC_NS_FETCH_PICOQUIC)

include(FindPackageHandleStandardArgs)
# handle the QUIETLY and REQUIRED arguments and set Picoquic_FOUND to TRUE
# if all listed variables are TRUE
find_package_handle_standard_args(Picoquic REQUIRED_VARS
        Picoquic_CORE_LIBRARY
        Picoquic_TEST_LIBRARY
        Picoquic_LOG_LIBRARY
        Picoquic_HTTP_LIBRARY
        Picoquic_INCLUDE_DIR
        Picoquic_LOG_DIR
        Picoquic_TEST_DIR )

if(Picoquic_FOUND)
    set(Picoquic_LIBRARIES
            ${Picoquic_TEST_LIBRARY}
            ${Picoquic_HTTP_LIBRARY}
            ${Picoquic_LOG_LIBRARY}
            ${Picoquic_CORE_LIBRARY}
    )
    set(Picoquic_INCLUDE_DIRS
            ${Picoquic_INCLUDE_DIR}
            ${Picoquic_TEST_DIR}
            ${Picoquic_LOG_DIR})
endif()

mark_as_advanced(Picoquic_LIBRARIES Picoquic_INCLUDE_DIRS)
