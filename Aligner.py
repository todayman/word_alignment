__author__ = 'tejasvamsingh'



# There are as many hidden states as there are words in the english sentence.
# There are j time steps where j is the number of words in the french sentence.
# The words of the french sentence are observed.
# At each time step, a hidden state ( that is a a word at some position 'i' in the english sentence) emits
# a french word j. a_j = i.

# Now... what are the initial parameters ... trained from Model 1 , 2  ?



import itertools
import time
import cProfile

from HMMOperations.HMMAlignmentHandler import HMMAlignmentHander

from PostProcessor import printAl
from align import fetchTranslationParameters


start = time.time()
frenchFileHandle =  open("/Users/tejasvamsingh/Working/Projects/ML/Code/MLAligner/data/hansards.f")
englishFileHandle = open("/Users/tejasvamsingh/Working/Projects/ML/Code/MLAligner/data/hansards.e")

hiddenStatesLists  = []
observationsLists = []

numTrainingLines = 10000

for line in itertools.islice(frenchFileHandle,numTrainingLines):
    englishSentence = englishFileHandle.readline().rstrip()
    frenchSentence = line.rstrip()
    englishSentenceWordList = englishSentence.split()
    frenchSentenceWordList = frenchSentence.split()
    hiddenStatesLists.append(englishSentenceWordList)
    observationsLists.append(frenchSentenceWordList)


totalHiddenStatesList = list(set([item for sublist in hiddenStatesLists for item in sublist]))
totalObservationsList = list(set([item for sublist in observationsLists for item in sublist]))

emissionParameters,distanceParameter = fetchTranslationParameters()

hmmAlignmentHandlerObject = HMMAlignmentHander(totalHiddenStatesList,totalObservationsList,emissionParameters)
hmmAlignmentHandlerObject.TrainAligner(hiddenStatesLists,observationsLists)
alignmentsList=hmmAlignmentHandlerObject.ComputeAlignments(hiddenStatesLists,observationsLists,distanceParameter)

for alignment in alignmentsList:
	print(alignment)


end = time.time()

print("time :",end-start)
















