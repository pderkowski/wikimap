#ifndef N2V_H
#define N2V_H

#include "stdafx.h"

#include "Snap.h"
#include "backtrackingrandomwalk.h"
#include "word2vec.h"

/// Modified node2vec for unweighted directed graphs
/// Based on see http://arxiv.org/pdf/1607.00653v1.pdf
/// Calculates node2vec feature representation for nodes and writes them into EmbeddinsHV
void node2vec(const PNGraph& InGraph, double BacktrackProb, int Dimensions,
    int WalkLen, int NumWalks, int WinSize, int Iter, bool Verbose,
    TIntFltVH& EmbeddingsHV);
#endif //N2V_H
