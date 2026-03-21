#Set this to @ to keep the makefile quiet
SILENCE = @

#---- Outputs ----#
COMPONENT_NAME = stm32cube_analog_dma

#--- Inputs ----#
ifeq "$(STUDENT_USERNAME)" ""
$(error The environment variable STUDENT_USERNAME is not set. \
Set it to the student's GitHub username)
endif
PROJECT_HOME_DIR = ../../../../stm32cube/workspace/$(STUDENT_USERNAME)/analog-dma
ifeq "$(CPPUTEST_HOME)" ""
$(error The environment variable CPPUTEST_HOME is not set. \
Set it to where cpputest is installed)
endif

# --- SRC_FILES and SRC_DIRS ---
# Production code files are compiled and put into
# a library to link with the test runner.
#
# Test code of the same name overrides
# production code at link time.
#
# SRC_FILES specifies individual production code files
SRC_FILES += $(PROJECT_HOME_DIR)/Core/Src/app.c

#
# SRC_DIRS specifies directories containing
# production code C and CPP files.
#
# SRC_DIRS +=

# --- TEST_SRC_FILES and TEST_SRC_DIRS ---
# TEST_SRC_FILES specifies individual test files to build.
#
# TEST_SRC_FILES +=

# TEST_SRC_DIRS specifies directories containing
# test source C and CPP files
TEST_SRC_DIRS += .
TEST_SRC_DIRS += ../mocks/stm32cube

# --- MOCKS_SRC_DIRS ---
# MOCKS_SRC_DIRS specifies directories containing mock source files
MOCKS_SRC_DIRS += ../mocks/stm32cube

# --- INCLUDE_DIRS ---
# mocks/stm32cube must come first so the mock main.h shadows the real one
INCLUDE_DIRS += ../mocks/stm32cube
INCLUDE_DIRS += .
INCLUDE_DIRS += $(CPPUTEST_HOME)/include

# --- CPPUTEST_OBJS_DIR ---
# CHEAT
# This is where the .o files from the unit tests are placed
CPPUTEST_OBJS_DIR = .

# --- CPPUTEST_LIB_DIR ---
# CHEAT
# This is where the cpputest libraries are located
CPPUTEST_LIB_DIR = $(CPPUTEST_HOME)/lib

#--- LIBRARIES ---
LD_LIBRARIES += -L$(CPPUTEST_LIB_DIR)
LD_LIBRARIES += -lCppUTest
LD_LIBRARIES += -lCppUTestExt

# Turn on CppUMock
CPPUTEST_USE_EXTENSIONS = Y

# Some flags to quiet clang
ifeq ($(shell $(CC) -v 2>&1 | grep -c "clang"), 1)
CPPUTEST_WARNINGFLAGS += -Wno-unknown-warning-option
CPPUTEST_WARNINGFLAGS += -Wno-covered-switch-default
CPPUTEST_WARNINGFLAGS += -Wno-reserved-id-macro
CPPUTEST_WARNINGFLAGS += -Wno-keyword-macro
CPPUTEST_WARNINGFLAGS += -Wno-documentation
CPPUTEST_WARNINGFLAGS += -Wno-missing-noreturn
endif

CPPUTEST_WARNINGFLAGS += -Wall
CPPUTEST_WARNINGFLAGS += -Werror
CPPUTEST_WARNINGFLAGS += -Wfatal-errors
CPPUTEST_WARNINGFLAGS += -Wswitch-default
CPPUTEST_WARNINGFLAGS += -Wno-format-nonliteral
CPPUTEST_WARNINGFLAGS += -Wno-sign-conversion
CPPUTEST_WARNINGFLAGS += -Wno-pedantic
CPPUTEST_WARNINGFLAGS += -Wno-shadow
CPPUTEST_WARNINGFLAGS += -Wno-missing-field-initializers
CPPUTEST_WARNINGFLAGS += -Wno-unused-parameter
CPPUTEST_CFLAGS += -pedantic
CPPUTEST_CFLAGS += -Wno-missing-prototypes
CPPUTEST_CFLAGS += -Wno-strict-prototypes
CPPUTEST_CXXFLAGS += -Wno-c++14-compat
CPPUTEST_CXXFLAGS += --std=c++11
CPPUTEST_CXXFLAGS += -Wno-c++98-compat-pedantic
CPPUTEST_CXXFLAGS += -Wno-c++98-compat
CPPUTEST_CFLAGS += -g

CPPUTEST_CFLAGS += -DLFS_NO_ERROR

# Colorize output
CPPUTEST_EXE_FLAGS += -c
CPPUTEST_EXE_FLAGS += -v

LD_LIBRARIES += -lm

# Code coverage
CPPUTEST_USE_GCOV=Y
GCOV_ARGS += -b
GCOV_ARGS += -c

include $(CPPUTEST_HOME)/build/MakefileWorker.mk
