PAGERANKDIR = wikimap/Pagerank
PAGERANKSOURCES = $(PAGERANKDIR)/pagerank.cpp
PAGERANKOBJECTS = $(patsubst %.cpp, %.o, $(PAGERANKSOURCES))

SQLTOOLSDIR = wikimap/Tools
SQLTOOLSSOURCES = $(SQLTOOLSDIR)/sqltools.cpp
SQLTOOLSOBJECTS = $(patsubst %.cpp, %.o, $(SQLTOOLSSOURCES))

PYTHONINCLUDE = env/include/python2.7

CXX = g++
CXXFLAGS = -std=c++11 -O2 -fPIC -I$(PYTHONINCLUDE)

PAGERANKLIB = $(PAGERANKDIR)/libpagerank.so
SQLTOOLSLIB = $(SQLTOOLSDIR)/libsqltools.so

.DEFAULT_GOAL := build

.PHONY: test clean build

%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c -o $@ $^

build: $(PAGERANKLIB) $(SQLTOOLSLIB)

$(PAGERANKLIB): $(PAGERANKOBJECTS)
	$(CXX) $(CXXFLAGS) $^ -shared -lboost_python -o $(PAGERANKLIB)

$(SQLTOOLSLIB): $(SQLTOOLSOBJECTS)
	$(CXX) $(CXXFLAGS) $^ -shared -lboost_python -o $(SQLTOOLSLIB)

test:
	python -m unittest discover -s wikimap/ -v

clean:
	rm -f $(PAGERANKOBJECTS) $(PAGERANKLIB) $(SQLTOOLSLIB) $(SQLTOOLSOBJECTS)