export PAGERANKDIR = $(realpath wikimap/Pagerank)
export TSNEDIR = $(realpath external/bhtsne)
export SNAPDIR = $(realpath external/snap)
export GRAPHDIR = $(realpath wikimap/Graph)
export NODE2VECDIR = $(realpath wikimap/Embeddings/Node2Vec)
export EDGEARRAYDIR = $(realpath wikimap/Tables/EdgeArray)

PAGERANKCOMMONSOURCES = $(PAGERANKDIR)/pagerank.cpp
PAGERANKCOMMONOBJECTS = $(patsubst %.cpp, %.o, $(PAGERANKCOMMONSOURCES))
PAGERANKBINSOURCES = $(PAGERANKDIR)/run_pagerank.cpp
PAGERANKBINOBJECTS = $(patsubst %.cpp, %.o, $(PAGERANKBINSOURCES))
PAGERANKBIN = $(PAGERANKDIR)/pagerank

TABLEIMPORTERDIR = wikimap/Tables/TableImporter
AGGREGATESOURCES = $(GRAPHDIR)/categorygraph.cpp $(GRAPHDIR)/aggregate.cpp
AGGREGATEOBJECTS = $(patsubst %.cpp, %.o, $(AGGREGATESOURCES))
AGGREGATEBIN = $(GRAPHDIR)/aggregate

$(PAGERANKBIN): CXXFLAGS += -std=c++11
$(AGGREGATEOBJECTS) : CXXFLAGS += -I$(SNAPDIR)/snap-core -I$(SNAPDIR)/glib-core -std=c++11
$(AGGREGATEBIN) : CXXFLAGS +=  -fopenmp -lrt

export CXX = g++
export CXXFLAGS = -O3

.DEFAULT_GOAL := build

.PHONY: test clean build tsne edgearray tableimporter node2vec

%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c -o $@ $^

build: $(PAGERANKBIN) $(AGGREGATEBIN) tsne edgearray node2vec tableimporter

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

$(PAGERANKBIN): $(PAGERANKCOMMONOBJECTS) $(PAGERANKBINSOURCES)
	$(CXX) $(CXXFLAGS) -o $(PAGERANKBIN) $^

test: build
	python -m unittest discover -s wikimap/ -v

clean:
	rm -f $(PAGERANKCOMMONOBJECTS) $(PAGERANKBIN) $(PAGERANKBINOBJECTS) $(AGGREGATEOBJECTS) $(AGGREGATEBIN)
	cd $(NODE2VECDIR) && $(MAKE) clean
	cd $(SNAPDIR) && $(MAKE) clean
	cd $(EDGEARRAYDIR) && $(MAKE) clean
	cd $(TSNEDIR) && $(MAKE) clean
	cd $(TABLEIMPORTERDIR) && $(MAKE) clean