#ifndef RAND_WALK_H
#define RAND_WALK_H

#include "Snap.h"

///Simulates one walk and writes it into Walk vector
void SimulateWalk(const PNGraph& InGraph, int64 StartNId, int WalkLen, double BacktrackProb, TIntV& Walk);

#endif //RAND_WALK_H
