#! /usr/bin/env python2


# There are as many hidden states as there are words in the english sentence.
# There are j time steps where j is the number of words in the french sentence.
# The words of the french sentence are observed.
# At each time step, a hidden state ( that is a a word at some position 'i' in the english sentence) emits
# a french word j. a_j = i.

# Now... what are the initial parameters ... trained from Model 1 , 2  ?


import argparse
import itertools
import time

from HMMOperations.HMMAlignmentHandler import HMMAlignmentHander
start = time.time()
parser = argparse.ArgumentParser(description="Aligner that uses the HMM")
parser.add_argument('--target_sentence_file', type=argparse.FileType('r'),
                    default="data/hansards.f")
parser.add_argument('--source_sentence_file', type=argparse.FileType('r'),
                    default="data/hansards.e")
parser.add_argument('--sentence_count', type=int, default=10000)

args = parser.parse_args()

hiddenStatesLists = []
observationsLists = []

for line in itertools.islice(args.target_sentence_file, args.sentence_count):
    englishSentence = args.source_sentence_file.readline().rstrip()
    frenchSentence = line.rstrip()
    englishSentenceWordList = englishSentence.split()
    frenchSentenceWordList = frenchSentence.split()
    hiddenStatesLists.append(englishSentenceWordList)
    observationsLists.append(frenchSentenceWordList)


totalHiddenStatesList = list(set([item for sublist in hiddenStatesLists for item in sublist]))
totalObservationsList = list(set([item for sublist in observationsLists for item in sublist]))

hmmAlignmentHandlerObject = HMMAlignmentHander(totalHiddenStatesList, totalObservationsList)
hmmAlignmentHandlerObject.TrainAligner(hiddenStatesLists, observationsLists)
alignmentsList = hmmAlignmentHandlerObject.ComputeAlignments(hiddenStatesLists, observationsLists)

for alignment in alignmentsList:
    print(alignment)

end = time.time()

print("time :", end-start)
