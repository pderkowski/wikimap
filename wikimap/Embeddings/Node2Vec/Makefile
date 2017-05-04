SOURCES = $(wildcard *.cpp)
OBJECTS = $(patsubst %.cpp, %.o, $(SOURCES))
BIN = node2vec

CXXFLAGS += -fopenmp -lrt -I$(SNAPDIR)/snap-core -I$(SNAPDIR)/glib-core

.PHONY: clean all

all: $(BIN)

$(BIN): $(OBJECTS)
	$(CXX) $(CXXFLAGS) -o $(BIN) $^ $(SNAPDIR)/snap-core/Snap.o

clean:
	rm -f $(OBJECTS) $(BIN)