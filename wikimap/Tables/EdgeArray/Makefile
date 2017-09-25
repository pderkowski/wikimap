CXXFLAGS += -fopenmp

.DEFAULT_GOAL := all
.PHONY: test lib clean all

TESTBIN = testarray
LIB = edgearrayext.so

all: lib

lib: CXXFLAGS += -shared -fPIC `python-config --cflags --ldflags`
lib: INCLUDES += -I $(EXTERNAL)/pybind11/include
lib: edgearrayext.cpp
	$(CXX) $(CXXFLAGS) $(INCLUDES) -o $(LIB) $^

%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c -o $@ $^

test: $(TESTBIN)

$(TESTBIN): testarray.cpp
	$(CXX) $(CXXFLAGS) -o $(TESTBIN) $^
	./$(TESTBIN)
	./TestEdgeArray.py

clean:
	rm -f $(TESTBIN) $(LIB) *.pyc
