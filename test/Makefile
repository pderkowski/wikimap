PROGDIR = ../src/zoom
PROGSOURCES = $(PROGDIR)/bounds.cpp $(PROGDIR)/node.cpp $(PROGDIR)/partitiontree.cpp $(PROGDIR)/zoom.cpp
WRAPSOURCES = $(PROGDIR)/zoomwrapper.cpp
TESTSOURCES = $(wildcard *.cpp)
TESTOBJECTS = $(patsubst %.cpp, %.o, $(TESTSOURCES))
PROGOBJECTS = $(patsubst %.cpp, %.o, $(PROGSOURCES))
WRAPOBJECTS = $(patsubst %.cpp, %.o, $(WRAPSOURCES))
CXX = g++
CXXFLAGS  = -I$(PROGDIR) -std=c++11 -fPIC

PYTHON = /usr/include/python2.7

EXE = ../bin/run_tests
LIB = ../lib/python/libzoompy.so

export PYTHONPATH := $(realpath ../lib/python):$(realpath ../src):$(PYTHONPATH)

$(WRAPOBJECTS): CXXFLAGS += -I$(PYTHON)

%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c -o $@ $^

build_test: $(PROGOBJECTS) $(TESTOBJECTS)
	$(CXX) $(CXXFLAGS) -o $(EXE) $^

build_bindings: $(PROGOBJECTS) $(WRAPOBJECTS)
	$(CXX) $^ -shared -lboost_python -o $(LIB)

test: build_test build_bindings
	./$(EXE)
	./test_python_bindings.py

clean:
	rm -f $(TESTOBJECTS) $(PROGOBJECTS) $(WRAPOBJECTS) $(EXE) $(LIB)