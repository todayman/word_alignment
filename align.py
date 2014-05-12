#! /usr/bin/env python2


xrange = range


class Sentence:
    def __init__(self, text):
        self.words = text.split()

    def __getitem__(self, index):
        return self.words[index]

    def __iter__(self):
        return self.words.__iter__()

    def __len__(self):
        return len(self.words)


class SentencePair:
    def __init__(self, first, second):
        self.source = first
        self.target = second
        self.alignment = {}
        for k in xrange(0, len(second)):
            for j in xrange(0, len(first)):
                self.alignment[(j, k)] = 1 / float(len(first))


def readFile(fileName, numLines):
    data = []
    i = 0
    with open(fileName) as fileObject:
        for line in fileObject:
            data.append(line)
            i = i + 1
            if i == numLines:
                break

    return data


def readSentenceFile(fileName, numLines):
    return [Sentence(l) for l in readFile(fileName, numLines)]


def writeData(fileName, data):
    with open(fileName) as fileObject:
        fileObject.write(data + '\n')


def populateVocabulary(sentenceList):
    vocabulary = set()
    for sentence in sentenceList:
        for word in sentence:
            vocabulary.add(word)
    return vocabulary


# Tracks the probability that a given source word emits
# a particular target word, regardless of context
class EmissionParameters:
    def __init__(self, sourceVocabulary, targetVocabulary):
        self._changedParameters = {}
        print("initializing " + str(len(sourceVocabulary) * len(targetVocabulary)) + " parameters")
        self._uniformProbability = 1 / float(len(targetVocabulary))

    def setProbability(self, source, target, prob):
        self._changedParameters[(source, target)] = prob

    def getProbability(self, source, target):
        if (source, target) in self._changedParameters:
            return self._changedParameters[(source, target)]
        else:
            return self._uniformProbability


# Takes in pre-aligned data, measures how far apart the corresponding words
# are from each other.
def initializeDistanceParameters(developmentAlignmentsList):
    # Map from aligned (target index, source index) -> ocurrences in the supervised training set
    # alignment count (target index, source index) is the number of times that the word at the target index is
    # aligned to the word at the source index in the supervised set
    alignmentCount = {}

    for alignmentLine in developmentAlignmentsList:
        alignments = alignmentLine.strip().split()
        for alignment in alignments:
            alignmentParts = []
            # '?' means uncertain alignment
            # '-' means certain
            if '?' in alignment:
                alignmentParts = alignment.split('?')
            elif '-' in alignment:
                alignmentParts = alignment.split('-')
            frenchIndex = alignmentParts[0]
            englishIndex = alignmentParts[1]
            if (frenchIndex, englishIndex) not in alignmentCount:
                alignmentCount[(frenchIndex, englishIndex)] = 0
            alignmentCount[(frenchIndex, englishIndex)] += 1

    # now calculate the distance parameter
    # distance parameter is k s.t. k^|i-j| = prob(alignment distance)
    # so we go over the data set and compute k for each distance,
    # then take the weighed average over the alignments
    # This is possibly not the best way to estimate k
    normalizationConstant = sum(alignmentCount.values())
    DistanceParameters = []
    for key in alignmentCount.keys():
        distance = abs(int(key[0]) - int(key[1]))
        if distance == 0:
            distance = 1
        probability = float(alignmentCount[key]) / float(normalizationConstant)
        currentDistanceParameter = pow(probability, float(1) / float(distance))
        DistanceParameters.append(currentDistanceParameter)

    return float(sum(DistanceParameters)) / float(len(DistanceParameters))


def incrementOrInsert(dictionary, key, amount):
    try:
        dictionary[key] += amount
    except KeyError:
        dictionary[key] = amount

# this class trains the alignment parameters using EM.
def trainParameters(sentencePairs, frenchVocabSize, emissionParameters, numIterations, modelNo):
    for iteration in xrange(0, numIterations):
        print('iteration = ' + str(iteration))
        emissionCounts = {}
        alignmentCounts = {}
        modifiedEmissionKeys = []
        modifiedAlignmentKeys = []

        for pair in sentencePairs:
            l = len(pair.source)
            m = len(pair.target)

            for i in xrange(0, len(pair.target)):
                targetWord = pair.target[i]
                denominator = 0

                if modelNo == 1:
                    for w in pair.source:
                        denominator += emissionParameters.getProbability(w, targetWord)

                elif modelNo == 2:
                    for count in xrange(0, len(pair.source)):
                        try:
                            #print('pair.alignment is ' + str(pair.alignment))
                            denominator = denominator + (pair.alignment[(count, i)] *
                                    emissionParameters.getProbability(pair.source[count], targetWord))
                        except KeyError:
                            pair.alignment[(count, i)] = 1 / float(len(pair.source))
                            denominator += (pair.alignment[(count, i)] *
                                    emissionParameters[(pair.source[count], targetWord)])

                for j in xrange(0, len(pair.source)):
                    sourceWord = pair.source[j]
                    modifiedEmissionKeys.append((sourceWord, targetWord))
                    modifiedAlignmentKeys.append((j, i, pair))

                    # calculate the delta parameter
                    delta = emissionParameters.getProbability(sourceWord, targetWord)

                    if modelNo == 2:
                        delta = delta * pair.alignment[(j, i)]

                    delta = float(delta) / float(denominator)

                    # update the counts
                    incrementOrInsert(emissionCounts, (sourceWord, targetWord), delta)
                    incrementOrInsert(emissionCounts, sourceWord, delta)
                    incrementOrInsert(alignmentCounts, (j, i, pair), delta)
                    incrementOrInsert(alignmentCounts, (i, pair), delta)

        # update the parameters
        for key in modifiedEmissionKeys:
            emissionParameters.setProbability(key[0], key[1], float(emissionCounts[key]) / float(emissionCounts[key[0]]))

        if modelNo == 2:
            for key in modifiedAlignmentKeys:
                key[2].alignment[(key[0], key[1])] = float(alignmentCounts[key]) / float(alignmentCounts[(key[1], key[2])])


# this class predicts the alignments and prints them to standard out.
def makeAndPrintPredictions(sentencePairs,
                            emissionParameters,
                            distanceParameter):
    for pair in sentencePairs:
        alignmentString = ''
        for i in xrange(0, len(pair.target)):
            targetWord = pair.target[i]
            alignmentString = alignmentString + str(i)
            currentMaximumIndex = 0
            currentMaximum = 0.0
            for j in xrange(0, len(pair.source)):
                sourceWord = pair.source[j]
                if currentMaximum < emissionParameters.getProbability(sourceWord, targetWord) * pair.alignment[j, i] * pow(distanceParameter, abs(i - j)):
                    currentMaximum = emissionParameters.getProbability(sourceWord, targetWord) * pair.alignment[j, i] * pow(distanceParameter, abs(i - j))
                    currentMaximumIndex = j
            alignmentString = alignmentString + '-' + str(currentMaximumIndex) + ' '

        alignmentString = alignmentString[0:len(alignmentString)-1]
        print(alignmentString)


def main():
    # read the files
    englishSentenceList = readSentenceFile('data/hansards.e', 100)
    frenchSentenceList = readSentenceFile('data/hansards.f', 100)
    developmentAlignmentsList = readFile('data/hansards.a', 37)

    # get the french vocab
    englishVocabulary = populateVocabulary(englishSentenceList)
    frenchVocabulary = populateVocabulary(frenchSentenceList)

    # get the initial parameters
    distanceParameter = initializeDistanceParameters(developmentAlignmentsList)

    # create the parameters for training
    emissionParameters = EmissionParameters(englishVocabulary, frenchVocabulary)
    #alignmentParameters = AlignmentParameters(englishSentenceList, frenchSentenceList)
    sentencePairs = [SentencePair(x, y) for (x, y) in zip(englishSentenceList, frenchSentenceList)]
    frenchVocabSize = len(frenchVocabulary)

    # train the EM parameters for model 1
    trainParameters(sentencePairs, frenchVocabSize,
                    emissionParameters, 10, 1)

    # train the EM parameters for model 2
    trainParameters(sentencePairs, frenchVocabSize,
                    emissionParameters, 10, 2)

    # write the predictions to file
    makeAndPrintPredictions(sentencePairs,
                            emissionParameters,
                            distanceParameter)

main()
