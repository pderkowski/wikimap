SOURCES = sqltools.cpp records.cpp parser.cpp

# PYTHONINCLUDE = ../../../env/include/python2.7

LIB = sqltools.so

.PHONY: all clean

all: $(LIB)

# lib: CXXFLAGS += -fPIC -I$(PYTHONINCLUDE)

$(LIB): CXXFLAGS += -shared -fPIC `python-config --cflags --ldflags`
$(LIB): INCLUDES += -I $(EXTERNAL)/pybind11/include
$(LIB): $(SOURCES)
	$(CXX) $(CXXFLAGS) $(INCLUDES) -o $(LIB) $(SOURCES)

%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c -o $@ $^

clean:
	rm -f $(LIB)
	rm -f *.pyc
	rm -f *.o
