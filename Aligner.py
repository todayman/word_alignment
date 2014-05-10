__author__ = 'tejasvamsingh'



# There are as many hidden states as there are words in the english sentence.
# There are j time steps where j is the number of words in the french sentence.
# The words of the french sentence are observed.
# At each time step, a hidden state ( that is a a word at some position 'i' in the english sentence) emits
# a french word j. a_j = i.

# Now... what are the initial parameters ... trained from Model 1 , 2  ?


from HMMOperations.HMMAlignmentHandler import ComputeAlignments


frenchFileHandle =  open("/Users/tejasvamsingh/Working/Projects/ML/Code/MLAligner/data/hansards.f")
englishFileHandle = open("/Users/tejasvamsingh/Working/Projects/ML/Code/MLAligner/data/hansards.e")

for line in frenchFileHandle.readlines():
    englishSentence = englishFileHandle.readline().rstrip()
    frenchSentence = line.rstrip()
    hiddenStatesList = englishSentence.split()
    observationList = frenchSentence.split()
    ComputeAlignments(hiddenStatesList,observationList)

    break







