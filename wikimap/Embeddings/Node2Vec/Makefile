SOURCES = $(wildcard *.cpp)
OBJECTS = $(patsubst %.cpp, %.o, $(SOURCES))
COMMONOBJECTS = $(filter-out node2vec.o word2vec.o, $(OBJECTS))
N2VBIN = node2vec
W2VBIN = word2vec

CXXFLAGS += -fopenmp -lrt -I$(SNAPDIR)/snap-core -I$(SNAPDIR)/glib-core

.PHONY: clean all

all: $(N2VBIN) $(W2VBIN)

$(N2VBIN): $(COMMONOBJECTS) node2vec.o
	$(CXX) $(CXXFLAGS) -o $(N2VBIN) $^ $(SNAPDIR)/snap-core/Snap.o

$(W2VBIN): $(COMMONOBJECTS) word2vec.o
	$(CXX) $(CXXFLAGS) -o $(W2VBIN) $^ $(SNAPDIR)/snap-core/Snap.o

clean:
	rm -f $(OBJECTS) $(N2VBIN) $(W2VBIN)