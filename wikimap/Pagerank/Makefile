SOURCES = $(wildcard *.cpp)
OBJECTS = $(patsubst %.cpp, %.o, $(SOURCES))
BIN = pagerank

CXXFLAGS += -std=c++11

.PHONY: clean all

%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c -o $@ $^

all: $(BIN)

$(BIN):$(OBJECTS)
	$(CXX) $(CXXFLAGS) -o $(BIN) $^

clean:
	rm -f $(OBJECTS) $(BIN)
