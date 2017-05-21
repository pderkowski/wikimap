export EXTERNAL = $(realpath external)
export PAGERANKDIR = $(realpath wikimap/Pagerank)
export TSNEDIR = $(realpath external/bhtsne)
export SNAPDIR = $(realpath external/snap)
export GRAPHDIR = $(realpath wikimap/Graph)
export NODE2VECDIR = $(realpath wikimap/Embeddings/Node2Vec)
export WORD2VECDIR = $(realpath wikimap/Embeddings/)
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

.PHONY: test clean build tsne edgearray tableimporter node2vec pagerank word2vec

%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c -o $@ $^

build: pagerank $(AGGREGATEBIN) tsne edgearray word2vec node2vec tableimporter

word2vec:
	cd $(WORD2VECDIR) && $(MAKE)

node2vec:
	cd $(NODE2VECDIR) && $(MAKE)

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
	cd $(NODE2VECDIR) && $(MAKE) clean
	cd $(SNAPDIR) && $(MAKE) clean
	cd $(EDGEARRAYDIR) && $(MAKE) clean
	cd $(TSNEDIR) && $(MAKE) clean
	cd $(TABLEIMPORTERDIR) && $(MAKE) clean
	cd $(WORD2VECDIR) && $(MAKE) clean