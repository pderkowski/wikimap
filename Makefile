PAGERANKDIR = wikimap/Pagerank
PAGERANKCOMMONSOURCES = $(PAGERANKDIR)/pagerank.cpp
PAGERANKCOMMONOBJECTS = $(patsubst %.cpp, %.o, $(PAGERANKCOMMONSOURCES))

PAGERANKBINSOURCES = $(PAGERANKDIR)/run_pagerank.cpp
PAGERANKBINOBJECTS = $(patsubst %.cpp, %.o, $(PAGERANKBINSOURCES))

PAGERANKTESTDIR = $(PAGERANKDIR)/test
PAGERANKTESTSOURCES = $(wildcard $(PAGERANKTESTDIR)/*.cpp)
PAGERANKTESTOBJECTS = $(patsubst %.cpp, %.o, $(PAGERANKTESTSOURCES))

SQLTOOLSDIR = wikimap/Tools
SQLTOOLSSOURCES = $(SQLTOOLSDIR)/sqltools.cpp $(SQLTOOLSDIR)/records.cpp $(SQLTOOLSDIR)/parser.cpp
SQLTOOLSOBJECTS = $(patsubst %.cpp, %.o, $(SQLTOOLSSOURCES))

TSNEDIR = external/bhtsne
TSNEBIN = $(TSNEDIR)/bh_tsne

PAGERANKTESTBIN = $(PAGERANKTESTDIR)/run_tests
PAGERANKBIN = $(PAGERANKDIR)/pagerank
SQLTOOLSLIB = $(SQLTOOLSDIR)/libsqltools.so

PYTHONINCLUDE = env/include/python2.7

$(PAGERANKTESTOBJECTS) : CXXFLAGS += -I$(PAGERANKDIR)
$(SQLTOOLSOBJECTS) : CXXFLAGS += -fPIC -I$(PYTHONINCLUDE)

CXX = g++
CXXFLAGS = -std=c++11 -O2

.DEFAULT_GOAL := build

.PHONY: test clean build

%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c -o $@ $^

build: $(PAGERANKBIN) $(SQLTOOLSLIB) $(TSNEBIN)

$(PAGERANKTESTBIN): $(PAGERANKCOMMONOBJECTS) $(PAGERANKTESTOBJECTS)
	@mkdir -p $(@D)
	$(CXX) $(CXXFLAGS) -o $(PAGERANKTESTBIN) $^

$(PAGERANKBIN): $(PAGERANKCOMMONOBJECTS) $(PAGERANKBINSOURCES)
	$(CXX) $(CXXFLAGS) -o $(PAGERANKBIN) $^

$(SQLTOOLSLIB): $(SQLTOOLSOBJECTS)
	$(CXX) $(CXXFLAGS) -o $(SQLTOOLSLIB) $^ -shared -lboost_python

$(TSNEBIN):
	g++ $(TSNEDIR)/sptree.cpp $(TSNEDIR)/tsne.cpp -o $(TSNEBIN) -O2

test: build $(PAGERANKTESTBIN)
	./$(PAGERANKTESTBIN)
	python -m unittest discover -s wikimap/ -v

clean:
	rm -f $(PAGERANKCOMMONOBJECTS) $(PAGERANKTESTBIN) $(PAGERANKBIN) $(SQLTOOLSLIB) $(SQLTOOLSOBJECTS) $(PAGERANKTESTOBJECTS) $(PAGERANKBINOBJECTS)
