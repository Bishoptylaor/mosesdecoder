// $Id$

#include "moses/TranslationModel/PhraseDictionaryTreeAdaptor.h"
#include <sys/stat.h>
#include <algorithm>
#include "moses/TranslationModel/PhraseDictionaryTree.h"
#include "moses/Phrase.h"
#include "moses/FactorCollection.h"
#include "moses/InputFileStream.h"
#include "moses/InputType.h"
#include "moses/ConfusionNet.h"
#include "moses/Sentence.h"
#include "moses/StaticData.h"
#include "moses/UniqueObject.h"
#include "moses/PDTAimp.h"
#include "moses/UserMessage.h"

namespace Moses
{
/*************************************************************
	function definitions of the interface class
	virtually everything is forwarded to the implementation class
*************************************************************/

PhraseDictionaryTreeAdaptor::
PhraseDictionaryTreeAdaptor(const std::string &line)
  : PhraseDictionary("PhraseDictionaryTreeAdaptor", line)
{
  imp = new PDTAimp(this,m_numInputScores);
}

PhraseDictionaryTreeAdaptor::~PhraseDictionaryTreeAdaptor()
{
  imp->CleanUp();
  delete imp;
}


bool PhraseDictionaryTreeAdaptor::Load(const std::vector<FactorType> &input
                                       , const std::vector<FactorType> &output
                                       , const std::string &filePath
                                       , const std::vector<float> &weight
                                       , size_t tableLimit
                                       , const LMList &languageModels
                                       , float weightWP)
{
  if(m_numScoreComponents!=weight.size()) {
    std::stringstream strme;
    strme << "ERROR: mismatch of number of scaling factors: "<<weight.size()
          <<" "<<m_numScoreComponents<<"\n";
    UserMessage::Add(strme.str());
    return false;
  }


  // set PhraseDictionary members
  m_tableLimit=tableLimit;

  imp->Create(input,output,filePath,weight,languageModels);
  return true;
}

void PhraseDictionaryTreeAdaptor::InitializeForInput(InputType const& source)
{
  imp->CleanUp();
  // caching only required for confusion net
  if(ConfusionNet const* cn=dynamic_cast<ConfusionNet const*>(&source))
    imp->CacheSource(*cn);
}

TargetPhraseCollection const*
PhraseDictionaryTreeAdaptor::GetTargetPhraseCollection(Phrase const &src) const
{
  return imp->GetTargetPhraseCollection(src);
}

TargetPhraseCollection const*
PhraseDictionaryTreeAdaptor::GetTargetPhraseCollection(InputType const& src,WordsRange const &range) const
{
  if(imp->m_rangeCache.empty()) {
    return imp->GetTargetPhraseCollection(src.GetSubString(range));
  } else {
    return imp->m_rangeCache[range.GetStartPos()][range.GetEndPos()];
  }
}

void PhraseDictionaryTreeAdaptor::EnableCache()
{
  imp->useCache=1;
}
void PhraseDictionaryTreeAdaptor::DisableCache()
{
  imp->useCache=0;
}

}
