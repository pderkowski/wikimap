TSNEBIN = bh_tsne
TSNESOURCES = sptree.cpp tsne.cpp
TSNEOBJECTS = $(patsubst %.cpp, %.o, $(TSNESOURCES))

CXX = g++
CXXFLAGS = -O3 -std=c++11 -fopenmp -Wno-unused-result

.PHONY: clean tsne
.DEFAULT_GOAL := tsne

%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c -o $@ $^

$(TSNEBIN): $(TSNEOBJECTS)
	$(CXX) $(CXXFLAGS) -o $(TSNEBIN) $^

tsne: $(TSNEBIN)

clean:
	rm -rf $(TSNEBIN) $(TSNEOBJECTS) *.pyc