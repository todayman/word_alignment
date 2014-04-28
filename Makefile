CXX=clang++
CXXFLAGS=-std=c++11 -stdlib=libc++ -g
#CXX=g++
#CXXFLAGS=-std=c++11 -g

#LD=clang++
LD=$(CXX)
LDFLAGS=-stdlib=libc++ -lc++abi

TARGETS=aligner

all: $(TARGETS)

%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c $*.cpp
aligner: align.o
	$(LD) $(LDFLAGS) align.o -o aligner

.PHONY: clean
clean:
	rm -f $(TARGETS) *.o
