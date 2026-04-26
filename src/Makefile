# OMEGA PROTOCOL: NATIVE ANDROID BUILD (CLANG)
CC = clang
CFLAGS = -Wall -O3
LDFLAGS = -lOpenCL

all: sarai_core

sarai_core: sarai_core.c
	$(CC) $(CFLAGS) -o sarai_core sarai_core.c $(LDFLAGS)

clean:
	rm -f sarai_core
