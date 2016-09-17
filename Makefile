PAGERANKDIR = wikimap/Pagerank
PAGERANKSOURCES = $(PAGERANKDIR)/pagerank.cpp
PAGERANKOBJECTS = $(patsubst %.cpp, %.o, $(PAGERANKSOURCES))

SQLTOOLSDIR = wikimap/Tools
SQLTOOLSSOURCES = $(SQLTOOLSDIR)/sqltools.cpp $(SQLTOOLSDIR)/records.cpp $(SQLTOOLSDIR)/parser.cpp
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
	$(CXX) $(CXXFLAGS) -o $(PAGERANKLIB) $^ -shared -lboost_python

$(SQLTOOLSLIB): $(SQLTOOLSOBJECTS)
	$(CXX) $(CXXFLAGS) -o $(SQLTOOLSLIB) $^ -shared -lboost_python

test:
	python -m unittest discover -s wikimap/ -v

clean:
	rm -f $(PAGERANKOBJECTS) $(PAGERANKLIB) $(SQLTOOLSLIB) $(SQLTOOLSOBJECTS)