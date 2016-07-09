all: src/pagerank.cpp
	g++ -std=c++11 -o bin/pagerank $^