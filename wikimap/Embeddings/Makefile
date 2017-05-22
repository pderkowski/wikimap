SOURCES = $(wildcard *.hpp *.cpp)

CXXFLAGS += -std=c++11 -fopenmp -funroll-loops -Wall -march=native -O3
BIN = word2vec
LIB = embeddings.so

.PHONY: clean all

all: $(BIN) $(LIB)

$(BIN): $(SOURCES)
	$(CXX) $(CXXFLAGS) -o $@ word2vec.cpp

$(LIB): CXXFLAGS += -shared -fPIC `python-config --cflags --ldflags`
$(LIB): INCLUDES += -I $(EXTERNAL)/pybind11/include
$(LIB): $(SOURCES)
	$(CXX) $(CXXFLAGS) $(INCLUDES) -o $(LIB) py_embeddings.cpp

clean:
	rm -f *.o
	rm -f $(LIB)
	rm -f $(BIN)
	rm -f *.pyc