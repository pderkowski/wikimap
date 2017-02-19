PAGERANKDIR = wikimap/Pagerank
PAGERANKCOMMONSOURCES = $(PAGERANKDIR)/pagerank.cpp
PAGERANKCOMMONOBJECTS = $(patsubst %.cpp, %.o, $(PAGERANKCOMMONSOURCES))
PAGERANKBINSOURCES = $(PAGERANKDIR)/run_pagerank.cpp
PAGERANKBINOBJECTS = $(patsubst %.cpp, %.o, $(PAGERANKBINSOURCES))
PAGERANKTESTDIR = $(PAGERANKDIR)/test
PAGERANKTESTSOURCES = $(wildcard $(PAGERANKTESTDIR)/*.cpp)
PAGERANKTESTOBJECTS = $(patsubst %.cpp, %.o, $(PAGERANKTESTSOURCES))
PAGERANKTESTBIN = $(PAGERANKTESTDIR)/run_tests
PAGERANKBIN = $(PAGERANKDIR)/pagerank

TABLEIMPORTERDIR = wikimap/Tables/TableImporter

TSNEDIR = external/bhtsne
SNAPDIR = external/snap
GRAPHDIR = wikimap/Graph
AGGREGATESOURCES = $(GRAPHDIR)/categorygraph.cpp $(GRAPHDIR)/aggregate.cpp
AGGREGATEOBJECTS = $(patsubst %.cpp, %.o, $(AGGREGATESOURCES))
AGGREGATEBIN = $(GRAPHDIR)/aggregate

NODE2VECDIR = wikimap/Node2Vec
NODE2VECSOURCES = $(wildcard $(NODE2VECDIR)/*.cpp)
NODE2VECOBJECTS = $(patsubst %.cpp, %.o, $(NODE2VECSOURCES))
NODE2VECBIN = $(NODE2VECDIR)/node2vec

EDGEARRAYDIR = wikimap/Tables/EdgeArray

$(PAGERANKTESTOBJECTS) : CXXFLAGS += -I$(PAGERANKDIR) -std=c++11
$(PAGERANKBIN): CXXFLAGS += -std=c++11
$(AGGREGATEOBJECTS) : CXXFLAGS += -I$(SNAPDIR)/snap-core -I$(SNAPDIR)/glib-core -std=c++11
$(AGGREGATEBIN) : CXXFLAGS +=  -fopenmp -lrt
$(NODE2VECBIN) : CXXFLAGS += -fopenmp -lrt -I$(SNAPDIR)/snap-core -I$(SNAPDIR)/glib-core
CXX = g++
CXXFLAGS = -O3

.DEFAULT_GOAL := build

.PHONY: test clean build node2vec tsne edgearray tableimporter

%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c -o $@ $^

build: $(PAGERANKBIN) $(AGGREGATEBIN) tsne edgearray node2vec tableimporter

node2vec: $(NODE2VECBIN)

edgearray:
	cd $(EDGEARRAYDIR) && make

tsne:
	cd $(TSNEDIR) && make

tableimporter:
	cd $(TABLEIMPORTERDIR) && make

$(SNAPDIR)/snap-core/Snap.o:
	cd $(SNAPDIR) && make -C snap-core

$(AGGREGATEBIN): $(SNAPDIR)/snap-core/Snap.o $(AGGREGATEOBJECTS)
	$(CXX) $(CXXFLAGS) -o $(AGGREGATEBIN) $^

$(NODE2VECBIN): $(SNAPDIR)/snap-core/Snap.o $(NODE2VECOBJECTS)
	$(CXX) $(CXXFLAGS) -o $(NODE2VECBIN) $^

$(PAGERANKTESTBIN): $(PAGERANKCOMMONOBJECTS) $(PAGERANKTESTOBJECTS)
	@mkdir -p $(@D)
	$(CXX) $(CXXFLAGS) -o $(PAGERANKTESTBIN) $^

$(PAGERANKBIN): $(PAGERANKCOMMONOBJECTS) $(PAGERANKBINSOURCES)
	$(CXX) $(CXXFLAGS) -o $(PAGERANKBIN) $^

test: build $(PAGERANKTESTBIN)
	./$(PAGERANKTESTBIN)
	python -m unittest discover -s wikimap/ -v

clean:
	rm -f $(PAGERANKCOMMONOBJECTS) $(PAGERANKTESTBIN) $(PAGERANKBIN) $(PAGERANKTESTOBJECTS) $(PAGERANKBINOBJECTS) $(AGGREGATEOBJECTS) $(AGGREGATEBIN) $(NODE2VECOBJECTS) $(NODE2VECBIN)
	cd $(SNAPDIR) && make clean
	cd $(EDGEARRAYDIR) && make clean
	cd $(TSNEDIR) && make clean
	cd $(TABLEIMPORTERDIR) && make clean