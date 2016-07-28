PROGDIR = ../src/zoom
PROGSOURCES = $(PROGDIR)/bounds.cpp $(PROGDIR)/node.cpp $(PROGDIR)/partitiontree.cpp $(PROGDIR)/zoom.cpp
TESTSOURCES = $(wildcard *.cpp)
SOURCES = $(PROGSOURCES) $(TESTSOURCES)
OBJECTS = $(patsubst %.cpp, %.o, $(SOURCES))
CXX = g++
CXXFLAGS  = -I$(PROGDIR) -std=c++11

EXE = ../bin/run_tests

build: $(OBJECTS)
	$(CXX) $(CXXFLAGS) -o $(EXE) $^

test: build
	./$(EXE)

clean:
	rm -f $(OBJECTS) $(EXE)