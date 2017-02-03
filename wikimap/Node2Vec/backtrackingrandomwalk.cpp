#include "stdafx.h"
#include "Snap.h"
#include "backtrackingrandomwalk.h"

int getOutDeg(const PNGraph& graph, int64 nodeId) {
  return graph->GetNI(nodeId).GetOutDeg();
}

bool hasNeighbor(const PNGraph& graph, int64 nodeId) {
  return getOutDeg(graph, nodeId) > 0;
}

int64 getRandomNeighborId(const PNGraph& graph, int64 nodeId, TRnd& Rnd) {
  const int outDeg = getOutDeg(graph, nodeId);
  return graph->GetNI(nodeId).GetNbrNId(Rnd.GetUniDevInt(outDeg));
}

int64 getNextNodeId(const PNGraph& graph, int64 last, int64 prev, double BacktrackProb, TRnd& Rnd) {
  if (!hasNeighbor(graph, last)) {
    return getRandomNeighborId(graph, prev, Rnd);
  } else if (!hasNeighbor(graph, prev)) {
    return getRandomNeighborId(graph, last, Rnd);
  } else {
    double draw = Rnd.GetUniDev();
    if (draw >= BacktrackProb) {
      return getRandomNeighborId(graph, last, Rnd);
    } else {
      return getRandomNeighborId(graph, prev, Rnd);
    }
  }
}

//Simulates a random walk
void SimulateWalk(const PNGraph& InGraph, int64 StartNId, int WalkLen, double BacktrackProb, TRnd& Rnd, TIntV& WalkV) {
  WalkV.Add(StartNId);
  if (WalkLen == 1) { return; }
  if (!hasNeighbor(InGraph, StartNId)) { return; }
  WalkV.Add(getRandomNeighborId(InGraph, StartNId, Rnd));
  while (WalkV.Len() < WalkLen) {
    int64 last = WalkV.Last();
    int64 prev = WalkV.LastLast();
    if (!hasNeighbor(InGraph, last) && !hasNeighbor(InGraph, prev)) { return; }
    WalkV.Add(getNextNodeId(InGraph, last, prev, BacktrackProb, Rnd));
  }
}
