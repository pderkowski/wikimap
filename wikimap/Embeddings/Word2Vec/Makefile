SOURCES = $(wildcard *.hpp *.cpp)
# SOURCES = word2vec.cpp
# OBJECTS = $(patsubst %.cpp, %.o, $(SOURCES))

CXXFLAGS += -std=c++11 -fopenmp
BIN = word2vec

.PHONY: clean all

all: $(BIN)

# %.o: %.cpp
# 	$(CXX) $(CXXFLAGS) -c -o $@ $^

$(BIN): $(SOURCES)
	$(CXX) $(CXXFLAGS) -o $@ word2vec.cpp

clean:
	rm -f $(BIN)
