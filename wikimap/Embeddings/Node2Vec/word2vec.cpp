#include "stdafx.h"

#include "w2v.h"

#ifdef USE_OPENMP
#include <omp.h>
#endif

void ParseArgs(int& argc, char* argv[], TStr& InFile, TStr& OutFile,
 int& Dimensions, int& WinSize, int& Iter, bool& Verbose) {
  Env = TEnv(argc, argv, TNotify::StdNotify);
  Env.PrepArgs("");
  InFile = Env.GetIfArgPrefixStr("-i:", "stdin",
   "Input file path. Default is stdin");
  OutFile = Env.GetIfArgPrefixStr("-o:", "stdout",
   "Output file path. Default is stdout");
  Dimensions = Env.GetIfArgPrefixInt("-d:", 128,
   "Number of dimensions. Default is 128");
  WinSize = Env.GetIfArgPrefixInt("-k:", 5,
   "Context size for optimization. Default is 5");
  Iter = Env.GetIfArgPrefixInt("-e:", 1,
   "Number of epochs in SGD. Default is 1");
  Verbose = Env.IsArgStr("-v", "Verbose output.");
}

void ReadSentences(const TStr& InFile, bool Verbose, TVec<TIntV>& InSentences) {
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

      TIntV Sentence;
      for (int i = 0; i < Tokens.Len(); ++i) {
        Sentence.Add(Tokens[i].GetInt());
      }
      InSentences.Add(Sentence);

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
  TStr InFile, OutFile;
  int Dimensions, WinSize, Iter;
  bool Verbose;
  ParseArgs(argc, argv, InFile, OutFile, Dimensions, WinSize, Iter, Verbose);
  TVec<TIntV> Sentences;
  ReadSentences(InFile, Verbose, Sentences);
  TIntFltVH EmbeddingsHV;
  LearnEmbeddings(Sentences, Dimensions, WinSize, Iter, Verbose, EmbeddingsHV);
  WriteOutput(OutFile, EmbeddingsHV);
  return 0;
}
