PROGDIR = ../src/quadtree
PROGSOURCES = $(PROGDIR)/bounds.cpp
TESTSOURCES = $(wildcard *.cpp)
SOURCES = $(PROGSOURCES) $(TESTSOURCES)
OBJECTS = $(patsubst %.cpp, %.o, $(SOURCES))
CXX = g++
CXXFLAGS  = -I../src/quadtree -std=c++11

EXE = run_tests

build: $(OBJECTS)
	$(CXX) -o $(EXE) $^

test: build
	./$(EXE)

clean:
	rm -f $(OBJECTS) $(EXE)