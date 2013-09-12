#!/usr/bin/env python3

"""
NAME
    extract_feature_dlm_baseline.py -- generate sample file for VW with
    simplest possible features: source cept and target surface form

SYNOPSIS
    extract_feature_dlm_baseline.py [--no-oov] SOURCE TARGET WORDS CEPT_TABLE

DESCRIPTION
    For each target word (in WORDS file) script outputs a group, that consists
    of:

    - Source cept (as string);
    - List of possible target hypothesis words (also as strings);
    - Hypothesis costs; cost is 0 if hypothesis word equals actual target word,
      and 1 otherwise.
    
    For example:
    
        shared |s p^action///action///NN
        1:1 |t p^nějaké///nějaký///PZYP4----------
        2:1 |t p^opatření///opatření_^(*3it)///NNNP4-----A----
        3:0 |t p^něčem///něco///PZ--6----------    <=== correct word!
        4:1 |t p^žaloby///žaloba///NNFP4-----A----    | cost (number after ":") 
        5:1 |t p^akčního///akční///AAIS2----1A----    | is equal to 0
        6:1 |t p^akcí///akce///NNFS7-----A----
        <...>
        321:1 |t p^__OOV__///__OOV__///------------- 

    Note the OOV token at the end: it somtimes is a correct option if actual 
    target word is not among the hypotheses. If --no-oov option is given,
    then OOV token is not printed, and samples, where actual target word is 
    not in hypotheses list, are just not included into output.

PARAMETERS
    SOURCE
        file with tokenized source language sentences, one per line
    
    TARGET
        file with tokenized target language sentences, one per line

    WORDS
        file with extracted cepts and target words; can be generated by
        extract_words_dlm.py script

    CEPT_TABLE
        Phrase table (cept to target word), which is used to generate list
        of possible target words given source cept. Should look like this:

            source cept ||| target_word ||| <anything>
    
        Compatible phrase table is generated by make_index_dlm.py script

    --no-oov
        don't include OOV token; if actual target word is not among hypotheses,
        just drop the sample.
"""

import collections
import fileinput
import itertools
import optparse
import sys

def phrase_table_parser(path):
    """
    Return frequencies-ignoring iterator through phrase table at given path.
    Iterator will yield (source_cept, target_word) pairs.
    """
    for line in fileinput.input(path):
        cept, target = map(str.strip, line.strip().split("|||")[:2])
        yield cept, target

def load_phrase_table(path):
    """
    Load phrase table into memory, ignoring frequencies (using just first two 
    fields).

    Returns dict, whose key is source cept, and corresponding value is a set of 
    all target words.
    """
    RESULT = collections.defaultdict()
    phrases = phrase_table_parser(path)
    get_cept = lambda entry: entry[0]
    get_target = lambda entry: entry[1]

    for cept, group in itertools.groupby(phrases, key=get_cept):
        group = list(group)
        RESULT[cept] = set(get_target(entry) for entry in group)

    fileinput.close()

    return RESULT

def parse_words_line(line):
    """
    Parse a line, generated by extract_words_dlm.py (hence, "words line"),
    and return source cept and target word
    """
    return line.strip().split("\t")[-2:]

OOV_TOKEN_TEXT = "__OOV__|__OOV__|-------------"

def escape(feature):
    """
    Escape a string so it can be safely used as name for single feature in 
    Vowpal Wabbit.

    Following chars are escaped:

        - "|" (namespace separator in VW, replaced with "///")
        - " " (feature separator, replaced with "___")
        - ":" (separates feature name and feature value, replaced with ";;;")

    """
    return feature.replace("|", "///") \
                  .replace(" ", "___") \
                  .replace(":", ";;;")

def extract_features(words_path, phrase_table, no_oov=False):
    for line in fileinput.input(words_path):
        # Read source cept and target word
        line_index = 0
        cept, target = parse_words_line(line)
        
        # Check data consistency (source cept shouldn't be OOV)
        try:
            candidates = phrase_table[cept]
        except KeyError:
            msg = ("Cept '%s' is not found in cept table. This could only " + 
                   "happen if data is inconsistent: cept table should be "  + 
                   "built using same corpora of parallel sentences, that "  +
                   "was used to 1) train alignments 2) which were used to " + 
                   "generate WORDS file 3) that is now an input to this "   + 
                   "script") % cept
            raise KeyError(msg)

        # Check if target word is OOV
        is_oov = target not in candidates
        if is_oov and no_oov:
            continue # Don't output this sample

        # Write 'source' line
        print("shared |s p^%s" % escape(cept))

        # Write 'target' lines
        for candidate in candidates:
            cost = 0 if candidate == target else 1
            feature = escape(candidate)
            line_index += 1
            print("%i:%i |t p^%s" % (line_index, cost, feature))

        # Write OOV line
        if not no_oov:
            cost = 0 if is_oov else 1
            feature = escape(OOV_TOKEN_TEXT)
            line_index += 1
            print("%i:%i |t p^%s " % (line_index, cost, feature))

        # Empty line at the end
        print()

# ---------------------------------------------------------------------- Main --

def parse_args():
    parser = optparse.OptionParser()
    parser.add_option("--no-oov", action="store_true")
    return parser.parse_args()

def main():
    args, pos_args = parse_args()
        
    source_path       = pos_args[0]
    target_path       = pos_args[1]
    words_path        = pos_args[2]
    phrase_table_path = pos_args[3]

    phrase_table = load_phrase_table(phrase_table_path) 
    extract_features(words_path, phrase_table, no_oov=args.no_oov)

if __name__ == "__main__":
    main() 