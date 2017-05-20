SOURCES = $(wildcard *.hpp *.cpp)

CXXFLAGS += -std=c++11 -fopenmp -O3 -funroll-loops -Wall -march=native
BIN = word2vec
LIB = word2vec.so

.PHONY: clean all

all: $(BIN) $(LIB)

$(BIN): $(SOURCES)
	$(CXX) $(CXXFLAGS) -o $@ word2vec.cpp

$(LIB): CXXFLAGS += -shared -fPIC `python-config --cflags --ldflags` -UNDEBUG
$(LIB): INCLUDES += -I $(EXTERNAL)/pybind11/include
$(LIB): $(SOURCES)
	$(CXX) $(CXXFLAGS) $(INCLUDES) -o $(LIB) py_word2vec.cpp

clean:
	rm -f *.o
	rm -f $(LIB)
	rm -f $(BIN)
