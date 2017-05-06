#include "stdafx.h"

#include "n2v.h"

#ifdef USE_OPENMP
#include <omp.h>
#endif

void ParseArgs(int& argc, char* argv[], TStr& InFile, TStr& OutFile,
 int& Dimensions, int& WalkLen, int& NumWalks, int& WinSize, int& Iter,
 bool& DynamicWindow, bool& Verbose, double& BacktrackProb) {
  Env = TEnv(argc, argv, TNotify::StdNotify);
  Env.PrepArgs(TStr::Fmt("\nAn algorithmic framework for representational learning on graphs."));
  InFile = Env.GetIfArgPrefixStr("-i:", "stdin",
   "Input graph path. Default is stdin");
  OutFile = Env.GetIfArgPrefixStr("-o:", "stdout",
   "Output graph path.");
  Dimensions = Env.GetIfArgPrefixInt("-d:", 128,
   "Number of dimensions. Default is 128");
  WalkLen = Env.GetIfArgPrefixInt("-l:", 80,
   "Length of walk per source. Default is 80");
  NumWalks = Env.GetIfArgPrefixInt("-r:", 10,
   "Number of walks per source. Default is 10");
  WinSize = Env.GetIfArgPrefixInt("-k:", 10,
   "Context size for optimization. Default is 10");
  Iter = Env.GetIfArgPrefixInt("-e:", 1,
   "Number of epochs in SGD. Default is 1");
  BacktrackProb = Env.GetIfArgPrefixFlt("-b:", 0.5,
   "Backtracking probability. Default is 0.5");
  DynamicWindow = !Env.IsArgStr("-f", "Fixed window.");
  Verbose = Env.IsArgStr("-v", "Verbose output.");
}

void ReadGraph(const TStr& InFile, bool Verbose, PNGraph& InGraph) {
  PSIn input;
  if (InFile == "stdin") {
    input = TStdIn::New();
  } else {
    input = TFIn::New(InFile);
  }
  int64 LineCnt = 0;
  try {
    TStr Ln;
    while (input->GetNextLn(Ln)) {
      TStr Line, Comment;
      Ln.SplitOnCh(Line,'#',Comment);
      TStrV Tokens;
      Line.SplitOnWs(Tokens);
      if(Tokens.Len()<2){ continue; }
      int64 SrcNId = Tokens[0].GetInt();
      int64 DstNId = Tokens[1].GetInt();
      if (!InGraph->IsNode(SrcNId)){ InGraph->AddNode(SrcNId); }
      if (!InGraph->IsNode(DstNId)){ InGraph->AddNode(DstNId); }
      InGraph->AddEdge(SrcNId,DstNId);
      LineCnt++;
    }
    if (Verbose) { printf("Read %lld lines from %s\n", (long long)LineCnt, InFile.CStr()); }
  } catch (PExcept Except) {
    if (Verbose) {
      printf("Read %lld lines from %s, then %s\n", (long long)LineCnt, InFile.CStr(),
       Except->GetStr().CStr());
    }
  }
}

void WriteOutput(const TStr& OutFile, TIntFltVH& EmbeddingsHV) {
  PSOut output;
  if (OutFile == "stdout") {
    output = TStdOut::New();
  } else {
    output = TFOut::New(OutFile);
  }
  bool First = 1;
  for (int i = EmbeddingsHV.FFirstKeyId(); EmbeddingsHV.FNextKeyId(i);) {
    if (First) {
      output->PutInt(EmbeddingsHV.Len());
      output->PutCh(' ');
      output->PutInt(EmbeddingsHV[i].Len());
      output->PutLn();
      First = 0;
    }
    output->PutInt(EmbeddingsHV.GetKey(i));
    for (int64 j = 0; j < EmbeddingsHV[i].Len(); j++) {
      output->PutCh(' ');
      output->PutFlt(EmbeddingsHV[i][j]);
    }
    output->PutLn();
  }
}

int main(int argc, char* argv[]) {
  TStr InFile,OutFile;
  int Dimensions, WalkLen, NumWalks, WinSize, Iter;
  double BacktrackProb;
  bool DynamicWindow, Verbose;
  ParseArgs(argc, argv, InFile, OutFile, Dimensions, WalkLen, NumWalks, WinSize,
    Iter, DynamicWindow, Verbose, BacktrackProb);
  PNGraph InGraph = PNGraph::New();
  TIntFltVH EmbeddingsHV;
  ReadGraph(InFile, Verbose, InGraph);
  node2vec(InGraph, BacktrackProb, Dimensions, WalkLen, NumWalks, WinSize, Iter,
    DynamicWindow, Verbose, EmbeddingsHV);
  WriteOutput(OutFile, EmbeddingsHV);
  return 0;
}
