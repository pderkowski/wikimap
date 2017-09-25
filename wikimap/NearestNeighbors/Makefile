SOURCES = $(wildcard *.hpp *.cpp)

CXXFLAGS += -fopenmp
LIB = vptree.so

.PHONY: clean all

all: $(LIB)

$(LIB): CXXFLAGS += -shared -fPIC `python-config --cflags --ldflags`
$(LIB): INCLUDES += -I $(EXTERNAL)/pybind11/include
$(LIB): $(SOURCES)
	$(CXX) $(CXXFLAGS) $(INCLUDES) -o $(LIB) pyvptree.cpp

clean:
	rm -f *.o
	rm -f $(LIB)
	rm -f *.pyc