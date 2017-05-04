#include "stdafx.h"
#include "n2v.h"

TVec<TRnd> makeRnds(int num, int seed) {
  TVec<TRnd> Rnds;
  for (int i = 0; i < num; ++i) {
    Rnds.Add(TRnd(seed + i));
  }
  return Rnds;
}

void node2vec(const PNGraph& InGraph, double BacktrackProb, int Dimensions,
 int WalkLen, int NumWalks, int WinSize, int Iter, bool Verbose,
 TIntFltVH& EmbeddingsHV) {
  TIntV NIdsV;
  for (TNGraph::TNodeI NI = InGraph->BegNI(); NI < InGraph->EndNI(); NI++) {
    NIdsV.Add(NI.GetId());
  }

  //Generate random walks
  int64 AllWalks = (int64)NumWalks * NIdsV.Len();
  TVVec<TInt, int64> WalksVV(AllWalks,WalkLen);
  TIntV WalkLens(AllWalks);
  TVec<TRnd> Rnds = makeRnds(omp_get_max_threads(), time(NULL));
  int64 WalksDone = 0;
  const int64 MaxChunkSize = 1000;

  if (Verbose) {
    printf("Walking Progress: 0.00%%");fflush(stdout);
  }

  for (int64 i = 0; i < NumWalks; i++) {
    NIdsV.Shuffle(Rnds[0]);
#pragma omp parallel for schedule(dynamic, 1)
    for (int64 j = 0; j < NIdsV.Len(); j += MaxChunkSize) {
      TRnd& ThreadRnd = Rnds[omp_get_thread_num()];
      const int64 ChunkSize = (NIdsV.Len() - j < MaxChunkSize)? (NIdsV.Len() - j) : MaxChunkSize;
      for (int64 k = j; k < j + ChunkSize; ++k) {
        TIntV WalkV;
        SimulateWalk(InGraph, NIdsV[k], WalkLen, BacktrackProb, ThreadRnd, WalkV);
        for (int64 l = 0; l < WalkV.Len(); l++) {
          WalksVV.PutXY(i*NIdsV.Len()+k, l, WalkV[l]);
        }
        WalkLens[k] = WalkV.Len();
      }
#pragma omp atomic
      WalksDone += ChunkSize;

      if (Verbose && omp_get_thread_num() == 0) { // only master reports progress
        int64 LocalWalksDone;
#pragma omp atomic read
        LocalWalksDone = WalksDone;
        printf("\rWalking Progress: %.2lf%%",(double)LocalWalksDone*100/(double)AllWalks);fflush(stdout);
      }
    }
  }

  if (Verbose) {
    printf("\rWalking Progress: 100.00%%\n");fflush(stdout);
  }
  //Learning embeddings
  LearnEmbeddings(WalksVV, WalkLens, Dimensions, WinSize, Iter, Verbose, Rnds, EmbeddingsHV);
}
