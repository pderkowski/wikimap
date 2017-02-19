CXX = g++
CXXFLAGS = -O3 -std=c++11 -fopenmp

.DEFAULT_GOAL := lib
.PHONY: test lib clean

TESTBIN = testarray
EDGEARRAYLIB = edgearrayext.so

PYTHONINCLUDE = ../../../env/include/python2.7

lib: CXXFLAGS += -fPIC -I$(PYTHONINCLUDE)

%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c -o $@ $^

lib: edgearrayext.cpp
	$(CXX) $(CXXFLAGS) -o $(EDGEARRAYLIB) $^ -shared -lboost_python

test: lib $(TESTBIN)

$(TESTBIN): testarray.cpp
	$(CXX) $(CXXFLAGS) -o $(TESTBIN) $^
	./$(TESTBIN)
	./TestEdgeArray.py

clean:
	rm -f $(TESTBIN) $(EDGEARRAYLIB) *.pyc