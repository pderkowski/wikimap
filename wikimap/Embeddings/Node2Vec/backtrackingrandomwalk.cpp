#include "stdafx.h"
#include "Snap.h"
#include "backtrackingrandomwalk.h"
#include "random.h"

int getOutDeg(const PNGraph& graph, int64 nodeId) {
  return graph->GetNI(nodeId).GetOutDeg();
}

bool hasNeighbor(const PNGraph& graph, int64 nodeId) {
  return getOutDeg(graph, nodeId) > 0;
}

int64 getRandomNeighborId(const PNGraph& graph, int64 nodeId) {
  const int outDeg = getOutDeg(graph, nodeId);
  return graph->GetNI(nodeId).GetNbrNId(ThreadRandom::get().GetUniDevInt(outDeg));
}

int64 getNextNodeId(const PNGraph& graph, int64 last, int64 prev, double BacktrackProb) {
  if (!hasNeighbor(graph, last)) {
    return getRandomNeighborId(graph, prev);
  } else if (!hasNeighbor(graph, prev)) {
    return getRandomNeighborId(graph, last);
  } else {
    double draw = ThreadRandom::get().GetUniDev();
    if (draw >= BacktrackProb) {
      return getRandomNeighborId(graph, last);
    } else {
      return getRandomNeighborId(graph, prev);
    }
  }
}

//Simulates a random walk
void SimulateWalk(const PNGraph& InGraph, int64 StartNId, int WalkLen, double BacktrackProb, TIntV& WalkV) {
  WalkV.Add(StartNId);
  if (WalkLen == 1) { return; }
  if (!hasNeighbor(InGraph, StartNId)) { return; }
  WalkV.Add(getRandomNeighborId(InGraph, StartNId));
  while (WalkV.Len() < WalkLen) {
    int64 last = WalkV.Last();
    int64 prev = WalkV.LastLast();
    if (!hasNeighbor(InGraph, last) && !hasNeighbor(InGraph, prev)) { return; }
    WalkV.Add(getNextNodeId(InGraph, last, prev, BacktrackProb));
  }
}
