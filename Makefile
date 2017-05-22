export EXTERNAL = $(realpath external)
export PAGERANKDIR = $(realpath wikimap/Pagerank)
export TSNEDIR = $(realpath external/bhtsne)
export SNAPDIR = $(realpath external/snap)
export GRAPHDIR = $(realpath wikimap/Graph)
export EMBEDDINGS = $(realpath wikimap/Embeddings/)
export EDGEARRAYDIR = $(realpath wikimap/Tables/EdgeArray)
export TABLEIMPORTERDIR = $(realpath wikimap/Tables/TableImporter)

AGGREGATESOURCES = $(GRAPHDIR)/categorygraph.cpp $(GRAPHDIR)/aggregate.cpp
AGGREGATEOBJECTS = $(patsubst %.cpp, %.o, $(AGGREGATESOURCES))
AGGREGATEBIN = $(GRAPHDIR)/aggregate

$(AGGREGATEOBJECTS) : CXXFLAGS += -I$(SNAPDIR)/snap-core -I$(SNAPDIR)/glib-core -std=c++11
$(AGGREGATEBIN) : CXXFLAGS +=  -fopenmp -lrt

export CXX = g++
export CXXFLAGS = -O3

.DEFAULT_GOAL := build

.PHONY: test clean build tsne edgearray tableimporter pagerank embeddings

%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c -o $@ $^

build: pagerank $(AGGREGATEBIN) tsne edgearray tableimporter embeddings

embeddings:
	cd $(EMBEDDINGS) && $(MAKE)

edgearray:
	cd $(EDGEARRAYDIR) && $(MAKE)

tsne:
	cd $(TSNEDIR) && $(MAKE)

tableimporter:
	cd $(TABLEIMPORTERDIR) && $(MAKE)

$(SNAPDIR)/snap-core/Snap.o:
	cd $(SNAPDIR) && $(MAKE) -C snap-core

$(AGGREGATEBIN): $(SNAPDIR)/snap-core/Snap.o $(AGGREGATEOBJECTS)
	$(CXX) $(CXXFLAGS) -o $(AGGREGATEBIN) $^

pagerank:
	cd $(PAGERANKDIR) && $(MAKE)

test: build
	python -m unittest discover -s wikimap/ -v

clean:
	find . -name '*.pyc' -delete
	rm -f $(AGGREGATEOBJECTS) $(AGGREGATEBIN)
	cd $(PAGERANKDIR) && $(MAKE) clean
	cd $(SNAPDIR) && $(MAKE) clean
	cd $(EDGEARRAYDIR) && $(MAKE) clean
	cd $(TSNEDIR) && $(MAKE) clean
	cd $(TABLEIMPORTERDIR) && $(MAKE) clean
	cd $(EMBEDDINGS) && $(MAKE) clean