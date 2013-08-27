CC=g++

#VPATH=
OBJDIR=obj
#SRCS=$(wildcard $(foreach EVERY_VPATH,$(VPATH),$(EVERY_VPATH)/*.c $(EVERY_VPATH)/*.cpp $(EVERY_VPATH)/*.cc $(EVERY_VPATH)/*.s))
SRCS=$(wildcard $(foreach EVERY_VPATH,$(VPATH),$(EVERY_VPATH)/*.c $(EVERY_VPATH)/*.cpp $(EVERY_VPATH)/*.cc $(EVERY_VPATH)/*.s))
#echo $(SRCS)

SRCS=$(wildcard *.c) $(wildcard *.cc) $(wildcard *.cpp)

OBJ:=$(patsubst %.cc, %.o, $(SRCS))
#GCOV=-ftest-coverage -fprofile-arcs  
GCOV=
LD=-lpthread  -lodbc
CFLAG=-pg

TARGET=run
INC+=../inc

STATIC_LIB=libats.a
DYNA_LIB=libats.so

LIB_PATH=../lib

all:$(OBJ)
	$(CC) -g -Wall -o $(TARGET) $(OBJ) $(GCOV) $(LD) $(CFLAG)

%.o:%.c
	$(CC) -Wall -g -o $@ -c $< -I$(INC) $(CFLAG)
%.o:%.cc
	$(CC) -Wall -g -o $@ -c $< -I$(INC) $(CFLAG)
%.o:%.cpp
	$(CC) -Wall -g -o $@ -c $< -I$(INC) $(CFLAG)


manual:$(OBJ)
	ar ruv librts.a a.o hello.o product.o consume.o #$(GCOV)
	$(CC) -o $(TARGET) main.o gcov_helper.o -L. -lrts -I../inc $(LD)

lib:$(OBJ)
	ar ruv $(STATIC_LIB) $(OBJ) #$(GCOV)
	$(CC) -shared $(OBJ) -o $(DYNA_LIB) 

single:main.o
	$(CC) -Wall -g -o run main.c -I../inc  

.PHONY:clean
clean:
	-rm -f $(OBJ)
	-rm -f $(TARGET)
	
distclean:
	-rm -f $(OBJ)
	-rm -f $(TARGET)
	-rm -rf $(STATIC_LIB) $(DYNA_LIB)

install:
	install $(STATIC_LIB) $(LIB_PATH)
	install $(DYNA_LIB) $(LIB_PATH)
