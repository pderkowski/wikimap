SOURCES = sqltools.cpp records.cpp parser.cpp
OBJECTS = $(patsubst %.cpp, %.o, $(SOURCES))

PYTHONINCLUDE = ../../../env/include/python2.7

CXX = g++
CXXFLAGS = -O3 -std=c++11

LIB = libsqltools.so

.DEFAULT_GOAL := lib
.PHONY: lib clean

lib: CXXFLAGS += -fPIC -I$(PYTHONINCLUDE)

%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c -o $@ $^

lib: $(SOURCES)
	$(CXX) $(CXXFLAGS) -o $(LIB) $^ -shared -lboost_python

clean:
	rm -f $(LIB) *.pyc $(OBJECTS)