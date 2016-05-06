#include <boost/foreach.hpp>
#include <boost/functional/hash_fwd.hpp>
#include "ActiveChart.h"
#include "InputPath.h"
#include "Word.h"

using namespace std;

namespace Moses2
{
namespace SCFG
{
SymbolBindElement::SymbolBindElement(
    const Range *range,
    const SCFG::Word *word,
    const Moses2::HypothesisColl *hypos)
:range(range)
,word(word)
,hypos(hypos)
{
  assert( (word->isNonTerminal && hypos) || (!word->isNonTerminal && hypos == NULL));
}

size_t hash_value(const SymbolBindElement &obj)
{
  size_t ret = (size_t) obj.range;
  boost::hash_combine(ret, obj.word);

  return ret;
}

////////////////////////////////////////////////////////////////////////////
void SymbolBind::Add(const Range &range, const SCFG::Word &word, const Moses2::HypothesisColl *hypos)
{
  SymbolBindElement ele(&range, &word, hypos);
  coll.push_back(ele);

  if (word.isNonTerminal) {
    ++numNT;
  }
}

std::vector<const SymbolBindElement*> SymbolBind::GetNTElements() const
{
  std::vector<const SymbolBindElement*> ret;

  for (size_t i = 0; i < coll.size(); ++i) {
    const SymbolBindElement &ele = coll[i];
    //cerr << "ele=" << ele.word->isNonTerminal << " " << ele.hypos << endl;

    if (ele.word->isNonTerminal) {
      ret.push_back(&ele);
    }
  }

  return ret;
}

std::ostream& operator<<(std::ostream &out, const SymbolBind &obj)
{
  BOOST_FOREACH(const SymbolBindElement &ele, obj.coll) {
    out << "("<< *ele.range << *ele.word << ") ";
  }

  return out;
}

}
}

