#include "stdafx.h"
#include "Snap.h"
#include "w2v.h"
#include "random.h"

//Code from https://github.com/nicholas-leonard/word2vec/blob/master/word2vec.c
//Customized for SNAP and node2vec

void LearnVocab(const TVec<TIntV>& Sentences, TIntV& Vocab) {
  for( int64 i = 0; i < Vocab.Len(); i++) { Vocab[i] = 0; }
  for( int64 i = 0; i < Sentences.Len(); i++) {
    for(int j = 0; j < Sentences[i].Len(); j++) {
      Vocab[Sentences[i][j]]++;
    }
  }
}

//Precompute unigram table using alias sampling method
void InitUnigramTable(const TIntV& Vocab, TIntV& KTable, TFltV& UTable) {
  double TrainWordsPow = 0;
  double Pwr = 0.75;
  TFltV ProbV(Vocab.Len());
  for (int64 i = 0; i < Vocab.Len(); i++) {
    ProbV[i]=TMath::Power(Vocab[i],Pwr);
    TrainWordsPow += ProbV[i];
    KTable[i]=0;
    UTable[i]=0;
  }
  for (int64 i = 0; i < ProbV.Len(); i++) {
    ProbV[i] /= TrainWordsPow;
  }
  TIntV UnderV;
  TIntV OverV;
  for (int64 i = 0; i < ProbV.Len(); i++) {
    UTable[i] = ProbV[i] * ProbV.Len();
    if ( UTable[i] < 1 ) {
      UnderV.Add(i);
    } else {
      OverV.Add(i);
    }
  }
  while(UnderV.Len() > 0 && OverV.Len() > 0) {
    int64 Small = UnderV.Last();
    int64 Large = OverV.Last();
    UnderV.DelLast();
    OverV.DelLast();
    KTable[Small] = Large;
    UTable[Large] = UTable[Large] + UTable[Small] - 1;
    if (UTable[Large] < 1) {
      UnderV.Add(Large);
    } else {
      OverV.Add(Large);
    }
  }
}

int64 RndUnigramInt(const TIntV& KTable, const TFltV& UTable) {
  TRnd& Rnd = ThreadRandom::get();
  TInt X = KTable[static_cast<int64>(Rnd.GetUniDev()*KTable.Len())];
  double Y = Rnd.GetUniDev();
  return Y < UTable[X] ? X : KTable[X];
}

//Initialize negative embeddings
void InitNegEmb(const TIntV& Vocab, int Dimensions, TVVec<TFlt, int64>& SynNeg) {
  SynNeg = TVVec<TFlt, int64>(Vocab.Len(),Dimensions);
  for (int64 i = 0; i < SynNeg.GetXDim(); i++) {
    for (int j = 0; j < SynNeg.GetYDim(); j++) {
      SynNeg(i,j) = 0;
    }
  }
}

//Initialize positive embeddings
void InitPosEmb(const TIntV& Vocab, int Dimensions, TVVec<TFlt, int64>& SynPos) {
  SynPos = TVVec<TFlt, int64>(Vocab.Len(),Dimensions);
  for (int64 i = 0; i < SynPos.GetXDim(); i++) {
    for (int j = 0; j < SynPos.GetYDim(); j++) {
      SynPos(i,j) =(ThreadRandom::get().GetUniDev()-0.5)/Dimensions;
    }
  }
}

void TrainModel(const TIntV& WalkV, int Dimensions, int WinSize,
    bool DynamicWindow, const TIntV& KTable, const TFltV& UTable,
    const TFltV& ExpTable, double Alpha, TVVec<TFlt, int64>& SynNeg,
    TVVec<TFlt, int64>& SynPos)  {
  TFltV Neu1V(Dimensions);
  TFltV Neu1eV(Dimensions);

  for (int64 WordI=0; WordI<WalkV.Len(); WordI++) {
    int64 Word = WalkV[WordI];
    for (int i = 0; i < Dimensions; i++) {
      Neu1V[i] = 0;
      Neu1eV[i] = 0;
    }
    int Offset;
    if (DynamicWindow) {
      Offset = ThreadRandom::get().GetUniDevInt() % WinSize;
    } else {
      Offset = 0;
    }
    for (int a = Offset; a < WinSize * 2 + 1 - Offset; a++) {
      if (a == WinSize) { continue; }
      int64 CurrWordI = WordI - WinSize + a;
      if (CurrWordI < 0){ continue; }
      if (CurrWordI >= WalkV.Len()){ continue; }
      int64 CurrWord = WalkV[CurrWordI];
      for (int i = 0; i < Dimensions; i++) { Neu1eV[i] = 0; }
      //negative sampling
      for (int j = 0; j < NegSamN+1; j++) {
        int64 Target, Label;
        if (j == 0) {
          Target = Word;
          Label = 1;
        } else {
          Target = RndUnigramInt(KTable, UTable);
          if (Target == Word) { continue; }
          Label = 0;
        }
        double Product = 0;
        for (int i = 0; i < Dimensions; i++) {
          Product += SynPos(CurrWord,i) * SynNeg(Target,i);
        }
        double Grad;                     //Gradient multiplied by learning rate
        if (Product > MaxExp) { Grad = (Label - 1) * Alpha; }
        else if (Product < -MaxExp) { Grad = Label * Alpha; }
        else {
          double Exp = ExpTable[static_cast<int>(Product*ExpTablePrecision)+TableSize/2];
          Grad = (Label - 1 + 1 / (1 + Exp)) * Alpha;
        }
        for (int i = 0; i < Dimensions; i++) {
          Neu1eV[i] += Grad * SynNeg(Target,i);
          SynNeg(Target,i) += Grad * SynPos(CurrWord,i);
        }
      }
      for (int i = 0; i < Dimensions; i++) {
        SynPos(CurrWord,i) += Neu1eV[i];
      }
    }
  }
}

void normalizeEmbeddings(TVVec<TFlt, int64>& SynPos) {
#pragma omp parallel for schedule(static)
  for (int64 i = 0; i < SynPos.GetXDim(); ++i) {
    TFltV CurrV(SynPos.GetYDim());
    for (int j = 0; j < SynPos.GetYDim(); j++) { CurrV[j] = SynPos(i, j); }
    TLinAlg::Normalize(CurrV);
    for (int j = 0; j < SynPos.GetYDim(); j++) { SynPos(i, j) = CurrV[j]; }
  }
}

void LearnEmbeddings(TVec<TIntV> Sentences, int Dimensions, int WinSize,
 int Iter, bool DynamicWindow, bool Verbose, TIntFltVH& EmbeddingsHV) {
  TIntIntH RnmH;
  TIntIntH RnmBackH;
  int64 NNodes = 0;
  //renaming nodes into consecutive numbers
  for (int i = 0; i < Sentences.Len(); i++) {
    for (int64 j = 0; j < Sentences[i].Len(); j++) {
      if ( RnmH.IsKey(Sentences[i][j]) ) {
        Sentences[i][j] = RnmH.GetDat(Sentences[i][j]);
      } else {
        RnmH.AddDat(Sentences[i][j] ,NNodes);
        RnmBackH.AddDat(NNodes, Sentences[i][j]);
        Sentences[i][j] = NNodes++;
      }
    }
  }
  TIntV Vocab(NNodes);
  LearnVocab(Sentences, Vocab);
  TIntV KTable(NNodes);
  TFltV UTable(NNodes);
  TVVec<TFlt, int64> SynNeg;
  TVVec<TFlt, int64> SynPos;
  InitPosEmb(Vocab, Dimensions, SynPos);
  InitNegEmb(Vocab, Dimensions, SynNeg);
  InitUnigramTable(Vocab, KTable, UTable);
  TFltV ExpTable(TableSize);
#pragma omp parallel for schedule(dynamic)
  for (int i = 0; i < TableSize; i++ ) {
    double Value = -MaxExp + static_cast<double>(i) / static_cast<double>(ExpTablePrecision);
    ExpTable[i] = TMath::Power(TMath::E, Value);
  }
  int64 WordCnt = 0;
  int64 AllWords = 0;
  for (int i = 0; i < Sentences.Len(); ++i) {
    AllWords += Sentences[i].Len();
  }

  const int64 MaxChunkSize = 50;

// op RS 2016/09/26, collapse does not compile on Mac OS X
//#pragma omp parallel for schedule(dynamic) collapse(2)
  if (Verbose) { printf("Learning Progress: 0.00%%"); fflush(stdout); }

  for (int j = 0; j < Iter; j++) {
#pragma omp parallel for schedule(dynamic)
    for (int64 i = 0; i < Sentences.Len(); i += MaxChunkSize) {
      int64 LocalWordCnt;
#pragma omp atomic read
      LocalWordCnt = WordCnt;

      if (Verbose && omp_get_thread_num() == 0) { // only master thread reports progress
        printf("\rLearning Progress: %.2lf%% ",(double)LocalWordCnt*100/(double)(Iter*AllWords));
        fflush(stdout);
      }

      // SynNeg and SynPos are intentionally not memory-locked (asynchronous SGD)
      double Alpha = StartAlpha * (1 - LocalWordCnt / static_cast<double>(Iter * AllWords + 1));
      Alpha = (Alpha < StartAlpha * 0.0001)? (StartAlpha * 0.0001) : Alpha;

      int64 ChunkTotalLen = 0;

      const int64 ChunkSize = (Sentences.Len() - i < MaxChunkSize)? (Sentences.Len() - i) : MaxChunkSize;
      for (int64 l = i; l < i + ChunkSize; ++l) {
        TrainModel(Sentences[l], Dimensions, WinSize, DynamicWindow, KTable, UTable,
         ExpTable, Alpha, SynNeg, SynPos);

        ChunkTotalLen += Sentences[l].Len();
      }

#pragma omp atomic
      WordCnt += static_cast<int64>(ChunkTotalLen);
    }
  }
  if (Verbose) { printf("\rLearning Progress: 100.00%% \n"); fflush(stdout); }

  if (Verbose) { printf("Normalizing embeddings\n"); fflush(stdout); }
  normalizeEmbeddings(SynPos);

  for (int64 i = 0; i < SynPos.GetXDim(); i++) {
    TFltV CurrV(SynPos.GetYDim());
    for (int j = 0; j < SynPos.GetYDim(); j++) { CurrV[j] = SynPos(i, j); }
    EmbeddingsHV.AddDat(RnmBackH.GetDat(i), CurrV);
  }
}
