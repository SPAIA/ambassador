CC := gcc

# Set to TRUE to enable logging functions.
LOG_ENABLE = FALSE

CORE_INCLUDE_PATHS = -I./uld-driver/inc
PLATFORM_INCLUDE_PATHS = -I./platform

BASE_CFLAGS = -Wall -Werror -Wno-missing-braces
CFLAGS_RELEASE = -Os -g0

LIB_CORE_SOURCES = $(wildcard ./uld-driver/src/*.c)
LIB_PLATFORM_SOURCES = $(wildcard ./platform/*.c)

LIB_SOURCES := $(LIB_CORE_SOURCES) $(LIB_PLATFORM_SOURCES)
INCLUDE_PATH = $(CORE_INCLUDE_PATHS) $(PLATFORM_INCLUDE_PATHS)

CFLAGS = $(BASE_CFLAGS) $(CFLAGS_RELEASE) $(INCLUDE_PATH)

all:
	$(CC) $(CFLAGS) -o spaia ./spaia.c $(LIB_SOURCES)

clean:
	rm -f spaia
