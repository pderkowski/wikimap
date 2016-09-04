PAGERANKDIR = wikimap/Pagerank
PAGERANKSOURCES = $(PAGERANKDIR)/pagerank.cpp
PAGERANKOBJECTS = $(patsubst %.cpp, %.o, $(PAGERANKSOURCES))

PYTHONINCLUDE = env/include/python2.7

CXX = g++
CXXFLAGS = -std=c++11 -O2 -fPIC -I$(PYTHONINCLUDE)

PAGERANKLIB = $(PAGERANKDIR)/libpagerank.so

.DEFAULT_GOAL := $(PAGERANKLIB)

.PHONY: test clean

%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c -o $@ $^

$(PAGERANKLIB): $(PAGERANKOBJECTS)
	$(CXX) $(CXXFLAGS) $^ -shared -lboost_python -o $(PAGERANKLIB)

test:
	python -m unittest discover -s wikimap/ -v

clean:
	rm -f $(PAGERANKOBJECTS) $(PAGERANKLIB)