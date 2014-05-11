#! /usr/bin/env python2

xrange = range


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


def writeData(fileName, data):
    with open(fileName) as fileObject:
        fileObject.write(data + '\n')


def populateVocabulary(sentenceList):
    vocabulary = set()
    for sentence in sentenceList:
        sentenceParts = sentence.split(' ')
        for word in sentenceParts:
            vocabulary.insert(word)
    return vocabulary


# this class creates initial parameters for EM.
def initalizeEmissionParamters(sourceVocabulary, targetVocabulary):
    uniformProbability = 1 / float(len(targetVocabulary))
    emissionParameters = {}
    for sourceWord in sourceVocabulary:
        for targetWord in targetVocabulary:
            # TODO What's the form of this tuple supposed to be?
            emissionParameters[(sourceWord), targetWord] = uniformProbability
    return emissionParameters


def initalizeAlignmentParameters(self, sourceSentenceList, targetSentenceList):
    alignmentParameters = {}
    visitedKeys = set()
    for i in range(0, len(sourceSentenceList)):
        currentSourceSentence = sourceSentenceList[i]
        currentTargetSentence = targetSentenceList[i]
        l = len(currentSourceSentence.split(' '))
        m = len(currentTargetSentence.split(' '))

        if (l, m) in visitedKeys:
            continue

        for k in xrange(0, m):
            for j in xrange(0, l):
                alignmentParameters[(j, k, l, m)] = 1 / float(l)
        visitedKeys.insert((l, m))

    return alignmentParameters


# Takes in pre-aligned data, measures how far apart the corresponding words
# are from each other.
def initializeDistanceParameters(self, developmentAlignmentsList):
    # Map from aligned (target index, source index) -> ocurrences in the supervised training set
    # alignment count (target index, source index) is the number of times that the word at the target index is
    # aligned to the word at the source index in the supervised set
    alignmentCount = {}

    for alignmentLine in developmentAlignmentsList:
        alignments = alignmentLine.strip().split(' ')
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


# this class creates parameter objects.
class Parameter:
    def __init__(self, emissionParameters, alignmentParameters):
        self.emissionParameters = emissionParameters
        self.alignmentParameters = alignmentParameters

    def getEmissionParameters(self):
        return self.emissionParameters

    def getAlignmentParameters(self):
        return self.alignmentParameters


# this class trains the alignment parameters using EM.
def trainParameters(self, englishSentenceList, frenchSentenceList, frenchVocabSize, emissionParameters, alignmentParameters, numIterations, modelNo):        
    for iterations in xrange(0, numIterations):
        emissionCounts = {}
        alignmentCounts = {}
        modifiedEmissionKeys = []
        modifiedAlignmentKeys = []
        
        for currentTrainingExample in xrange(0, len(englishSentenceList)):
            currentFrenchExampleWordList = frenchSentenceList[currentTrainingExample].split(' ')
            currentEnglishExampleWordList = englishSentenceList[currentTrainingExample].split(' ')
            
            l = len(currentEnglishExampleWordList)
            m = len(currentFrenchExampleWordList)
            
            for i in xrange(0, len(currentFrenchExampleWordList)):
                frenchWord = currentFrenchExampleWordList[i]
                denominator = 0

                if modelNo == 1:                        
                    for w in currentEnglishExampleWordList:
                        try:
                            denominator += emissionParameters[(w, frenchWord)]
                        except KeyError:
                            emissionParameters[(w,frenchWord)] = 1 / float(frenchVocabSize)        
                            denominator += emissionParameters[(w, frenchWord)]

                elif modelNo == 2:
                    #denominator=sum([alignmentParameters[(count,i,l,m)]*emissionParameters[(currentEnglishExampleWordList[count],frenchWord)] for count in xrange(0,l)])                        
                    for count in xrange(0, l):
                        try:
                            denominator = denominator + (alignmentParameters[(count, i, l, m)] *
                                    emissionParameters[(currentEnglishExampleWordList[count], frenchWord)])
                        except KeyError:
                            alignmentParameters[(count,i,l,m)] = 1 / float(l)
                            denominator = denominator + (alignmentParameters[(count, i, l, m)] *
                                    emissionParameters[(currentEnglishExampleWordList[count], frenchWord)])

                for j in xrange(0, len(currentEnglishExampleWordList)):
                    englishWord = currentEnglishExampleWordList[j]
                    modifiedEmissionKeys.append((englishWord, frenchWord))
                    modifiedAlignmentKeys.append((j, i, l, m))

                    # calculate the delta parameter
                    delta = emissionParameters[(englishWord, frenchWord)]

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
            emissionParameters[key] = float(emissionCounts[key]) / float(emissionCounts[key[0]])

        if modelNo == 2:
            for key in modifiedAlignmentKeys:
                alignmentParameters[key] = float(alignmentCounts[key]) / float(alignmentCounts[(key[1], key[2], key[3])])

# this class predicts the alignments and prints them to standard out.
def makeAndPrintPredictions(englishSentenceList, frenchSentenceList,
        emissionParameters, alignmentParameters, distanceParameter):
    for currentIndex in xrange(0, 1000):
        currentEnglishExampleWordList = englishSentenceList[currentIndex].split(' ')
        currentFrenchExampleWordList = frenchSentenceList[currentIndex].split(' ')
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
                if currentMaximum < emissionParameters[(englishWord,frenchWord)] * alignmentParameters[j, i, l, m] * pow(distanceParameter, abs(i - j)):
                    currentMaximum = emissionParameters[(englishWord,frenchWord)] * alignmentParameters[j, i, l, m] * pow(distanceParameter, abs(i - j))
                    currentMaximumIndex = j
            alignmentString = alignmentString+'-' + str(currentMaximumIndex) + ' '
        
        alignmentString = alignmentString[0:len(alignmentString)-1]
        print(alignmentString)


def main():
    # define objects
    ParameterInitializerObject = ParameterInitializer()
    emTrainerObject = EMTrainer()
    predictionWriterObject = PredictionWriter()
    
    #read the files
    englishSentenceList = readFile('data/hansards.e', 9999)
    frenchSentenceList = readFile('data/hansards.f', 9999)
    developmentAlignmentsList = readFile('data/hansards.a', 37)
    
    # get the french vocab                
    frenchVocabulary=vocabularyPopulatorObject.populateFrenchVocabulary(frenchSentenceList)        
    
    # get the initial parameters
    distanceParameter = ParameterInitializerObject.initializeDistanceParameters(developmentAlignmentsList)
    
    #create the parameters for training
    emissionParameters={}
    alignmentParameters={}
    frenchVocabSize=len(frenchVocabulary)
    
    # train the EM parameters for model 1    
    parameterObject1=emTrainerObject.trainParameters(englishSentenceList,frenchSentenceList,frenchVocabSize,emissionParameters,alignmentParameters,10,1)    

    # train the EM parameters for model 2
    parameterObject2=emTrainerObject.trainParameters(englishSentenceList,frenchSentenceList,frenchVocabSize,emissionParameters,alignmentParameters,10,2)

    # write the predictions to file
    predictionWriterObject.makeAndPrintPredictions(englishSentenceList,frenchSentenceList,emissionParameters,alignmentParameters,distanceParameter)
    
    




main()


