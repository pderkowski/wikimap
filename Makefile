export EXTERNAL = $(realpath external)
export TSNEDIR = $(realpath wikimap/TSNE)
export GRAPHDIR = $(realpath wikimap/Graph)
export EMBEDDINGS = $(realpath wikimap/Embeddings/)
export EDGEARRAYDIR = $(realpath wikimap/Tables/EdgeArray)
export TABLEIMPORTERDIR = $(realpath wikimap/Tables/TableImporter)

export CXX = g++
export CXXFLAGS = -std=c++11 -march=native -O3 -Wall

.DEFAULT_GOAL := build

.PHONY: test clean build embeddings edgearray tsne tableimporter graph

%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c -o $@ $^

build: embeddings edgearray tsne tableimporter graph

embeddings:
	cd $(EMBEDDINGS) && $(MAKE)

edgearray:
	cd $(EDGEARRAYDIR) && $(MAKE)

tsne:
	cd $(TSNEDIR) && $(MAKE)

tableimporter:
	cd $(TABLEIMPORTERDIR) && $(MAKE)

graph:
	cd $(GRAPHDIR) && $(MAKE)

test: build
	python -m unittest discover -s wikimap/ -v

clean:
	find . -name '*.pyc' -delete
	cd $(EMBEDDINGS) && $(MAKE) clean
	cd $(EDGEARRAYDIR) && $(MAKE) clean
	cd $(TSNEDIR) && $(MAKE) clean
	cd $(TABLEIMPORTERDIR) && $(MAKE) clean
	cd $(GRAPHDIR) && $(MAKE) clean