SOURCES = $(wildcard *.cpp *.hpp)
LIB = graph.so

.PHONY: clean all

all: $(LIB)

$(LIB): CXXFLAGS += -fopenmp -shared -fPIC `python-config --cflags --ldflags`
$(LIB): INCLUDES += -I $(EXTERNAL)/pybind11/include
$(LIB): $(SOURCES)
	$(CXX) $(CXXFLAGS) $(INCLUDES) -o $(LIB) py_graph.cpp

clean:
	rm -f $(OBJECTS) $(LIB)
	rm -f *.pyc
	rm -f *.o
