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
        # for sourceWord in sourceVocabulary:
        #     for targetWord in targetVocabulary:
        #         # TODO What's the form of this tuple supposed to be?
        #         self.setProbability(sourceWord, targetWord, uniformProbability)
        #         if len(self._parameters) % 10000 == 0:
        #             print("Done " + str(len(self._parameters)) + " parameters")

    def setProbability(self, source, target, prob):
        self._changedParameters[(source, target)] = prob

    def getProbability(self, source, target):
        if (source, target) in self._changedParameters:
            return self._changedParameters[(source, target)]
        else:
            return self._uniformProbability


class AlignmentParameters:
    def __init__(self, sourceSentenceList, targetSentenceList):
        self.alignmentParameters = {}
        visitedKeys = set()
        for (currentSourceSentence, currentTargetSentence) in zip(sourceSentenceList, targetSentenceList):
            l = len(currentSourceSentence)
            m = len(currentTargetSentence)

            if (l, m) in visitedKeys:
                continue

            for k in xrange(0, m):
                for j in xrange(0, l):
                    self.alignmentParameters[(j, k, l, m)] = 1 / float(l)
            visitedKeys.add((l, m))

    def __getitem__(self, item):
        return self.alignmentParameters[item]

    def __setitem__(self, item, val):
        self.alignmentParameters[item] = val

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


# this class trains the alignment parameters using EM.
def trainParameters(englishSentenceList, frenchSentenceList, frenchVocabSize, emissionParameters, alignmentParameters, numIterations, modelNo):
    for iterations in xrange(0, numIterations):
        emissionCounts = {}
        alignmentCounts = {}
        modifiedEmissionKeys = []
        modifiedAlignmentKeys = []

        for (currentEnglishExampleWordList, currentFrenchExampleWordList) in zip(englishSentenceList, frenchSentenceList):
            l = len(currentEnglishExampleWordList)
            m = len(currentFrenchExampleWordList)

            for i in xrange(0, len(currentFrenchExampleWordList)):
                frenchWord = currentFrenchExampleWordList[i]
                denominator = 0

                if modelNo == 1:
                    for w in currentEnglishExampleWordList:
                        denominator += emissionParameters.getProbability(w, frenchWord)

                elif modelNo == 2:
                    for count in xrange(0, l):
                        try:
                            denominator = denominator + (alignmentParameters[(count, i, l, m)] *
                                    emissionParameters.getProbability(currentEnglishExampleWordList[count], frenchWord))
                        except KeyError:
                            alignmentParameters[(count,i,l,m)] = 1 / float(l)
                            denominator = denominator + (alignmentParameters[(count, i, l, m)] *
                                    emissionParameters[(currentEnglishExampleWordList[count], frenchWord)])

                for j in xrange(0, len(currentEnglishExampleWordList)):
                    englishWord = currentEnglishExampleWordList[j]
                    modifiedEmissionKeys.append((englishWord, frenchWord))
                    modifiedAlignmentKeys.append((j, i, l, m))

                    # calculate the delta parameter
                    delta = emissionParameters.getProbability(englishWord, frenchWord)

                    if modelNo == 2:
                        delta = delta * alignmentParameters[(j, i, l, m)]

                    delta = float(delta) / float(denominator)

                    # update the counts
                    try:
                        emissionCounts[(englishWord, frenchWord)] += delta
                    except KeyError:
                        emissionCounts[(englishWord, frenchWord)] = delta
                    try:
                        emissionCounts[englishWord] += delta
                    except KeyError:
                        emissionCounts[englishWord] = delta
                    try:
                        alignmentCounts[(j, i, l, m)] += delta
                    except KeyError:
                        alignmentCounts[(j, i, l, m)] = delta
                    try:
                        alignmentCounts[(i, l, m)] += delta
                    except KeyError:
                        alignmentCounts[(i, l, m)] = delta

        # update the parameters
        for key in modifiedEmissionKeys:
            emissionParameters.setProbability(key[0], key[1], float(emissionCounts[key]) / float(emissionCounts[key[0]]))

        if modelNo == 2:
            for key in modifiedAlignmentKeys:
                alignmentParameters[key] = float(alignmentCounts[key]) / float(alignmentCounts[(key[1], key[2], key[3])])


# this class predicts the alignments and prints them to standard out.
def makeAndPrintPredictions(englishSentenceList, frenchSentenceList,
                            emissionParameters, alignmentParameters,
                            distanceParameter):
    for currentIndex in xrange(0, 1000):
        currentEnglishExampleWordList = englishSentenceList[currentIndex]
        currentFrenchExampleWordList = frenchSentenceList[currentIndex]
        l = len(currentEnglishExampleWordList)
        m = len(currentFrenchExampleWordList)
        alignmentString = ''
        for i in xrange(0, len(currentFrenchExampleWordList)):
            frenchWord = currentFrenchExampleWordList[i]
            alignmentString = alignmentString + str(i)
            currentMaximumIndex = 0
            currentMaximum = 0.0
            for j in xrange(0, len(currentEnglishExampleWordList)):
                englishWord = currentEnglishExampleWordList[j]
                if currentMaximum < emissionParameters.getProbability(englishWord, frenchWord) * alignmentParameters[j, i, l, m] * pow(distanceParameter, abs(i - j)):
                    currentMaximum = emissionParameters.getProbability(englishWord, frenchWord) * alignmentParameters[j, i, l, m] * pow(distanceParameter, abs(i - j))
                    currentMaximumIndex = j
            alignmentString = alignmentString + '-' + str(currentMaximumIndex) + ' '

        alignmentString = alignmentString[0:len(alignmentString)-1]
        print(alignmentString)


def main():
    # read the files
    englishSentenceList = readSentenceFile('data/hansards.e', 9999)
    frenchSentenceList = readSentenceFile('data/hansards.f', 9999)
    developmentAlignmentsList = readFile('data/hansards.a', 37)

    # get the french vocab
    englishVocabulary = populateVocabulary(englishSentenceList)
    frenchVocabulary = populateVocabulary(frenchSentenceList)

    # get the initial parameters
    distanceParameter = initializeDistanceParameters(developmentAlignmentsList)

    # create the parameters for training
    emissionParameters = EmissionParameters(englishVocabulary, frenchVocabulary)
    alignmentParameters = AlignmentParameters(englishSentenceList, frenchSentenceList)
    frenchVocabSize = len(frenchVocabulary)

    # train the EM parameters for model 1
    trainParameters(englishSentenceList, frenchSentenceList, frenchVocabSize,
                    emissionParameters, alignmentParameters, 10, 1)

    # train the EM parameters for model 2
    trainParameters(englishSentenceList, frenchSentenceList, frenchVocabSize,
                    emissionParameters, alignmentParameters, 10, 2)

    # write the predictions to file
    makeAndPrintPredictions(englishSentenceList, frenchSentenceList,
                            emissionParameters, alignmentParameters,
                            distanceParameter)

main()
