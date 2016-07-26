PROGDIR = ../src/quadtree
PROGSOURCES = $(PROGDIR)/bounds.cpp $(PROGDIR)/node.cpp $(PROGDIR)/quadtree.cpp
TESTSOURCES = $(wildcard *.cpp)
SOURCES = $(PROGSOURCES) $(TESTSOURCES)
OBJECTS = $(patsubst %.cpp, %.o, $(SOURCES))
CXX = g++
CXXFLAGS  = -I../src/quadtree -std=c++11

EXE = ../bin/run_tests

build: $(OBJECTS)
	$(CXX) $(CXXFLAGS) -o $(EXE) $^

test: build
	./$(EXE)

clean:
	rm -f $(OBJECTS) $(EXE)