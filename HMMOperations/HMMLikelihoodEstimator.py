__author__ = 'tejasvamsingh'


def ForwardProbabilityComputer(hiddenStatesList, observationsList,
                               emissionProbabilityDict,transitionProbabilityDict):

    forwardProbabilityDict={}
    forwardProbabilityDict[-1] = [("<s>",1.0)]


    for timeStep in xrange(0,len(observationsList)):
        forwardProbabilityDict[timeStep]=[]
        for hiddenState in hiddenStatesList:
            forwardProb =0.0
            for previousStateEntry in forwardProbabilityDict[timeStep-1]:
                previousState = previousStateEntry[0]
                previousStateForwardProbability = previousStateEntry[1]
                forwardProb=forwardProb + (previousStateForwardProbability*transitionProbabilityDict[(hiddenState,previousState)])
            forwardProb=forwardProb * emissionProbabilityDict[(observationsList[timeStep],hiddenState)]
            forwardProbabilityDict[timeStep].append((hiddenState,forwardProb))

    # transition to the end state </s>

    forwardProb =0.0
    for previousStateEntry in forwardProbabilityDict[len(observationsList)-1]:
        previousState = previousStateEntry[0]
        previousStateForwardProbability = previousStateEntry[1]
        forwardProb=forwardProb + (previousStateForwardProbability*transitionProbabilityDict[("</s>",previousState)])

    forwardProbabilityDict[len(observationsList)] = [("</s>",forwardProb)]

    return forwardProbabilityDict

def BackWardProbabilityComputer(hiddenStatesList,observationsList,
                                emissionProbabilityDict, transitionProbabilityDict):


    BackwardProbabilityDict={}

    BackwardProbabilityDict[len(observationsList)]=[("</s>",1.0)]

    BackwardProbabilityDict[len(observationsList)-1] = []

    for hiddenState in hiddenStatesList:
        BackwardProbabilityDict[len(observationsList)-1].append((hiddenState,transitionProbabilityDict[("</s>",hiddenState)]))

    for timeStep in xrange(len(observationsList)-2,-1,-1):
        BackwardProbabilityDict[timeStep]=[]
        for hiddenState in hiddenStatesList:
           backwardProb = 0.0
           for nextStateEntry in BackwardProbabilityDict[timeStep+1]:
               nextState=nextStateEntry[0]
               nextStateBackwardProbability = nextStateEntry[1]
               backwardProb = backwardProb + (nextStateBackwardProbability*
                                              transitionProbabilityDict[(nextState,hiddenState)]*
                                              emissionProbabilityDict[(observationsList[timeStep+1],nextState)])
           BackwardProbabilityDict[timeStep].append((hiddenState,backwardProb))

    BackwardProbabilityDict[-1]=[]
    backwardProb=0.0
    for nextStateEntry in BackwardProbabilityDict[0]:
        nextState=nextStateEntry[0]
        nextStateBackwardProbability = nextStateEntry[1]
        backwardProb = backwardProb + (nextStateBackwardProbability*
                                              transitionProbabilityDict[(nextState,"<s>")]*
                                              emissionProbabilityDict[(observationsList[0],nextState)])

    BackwardProbabilityDict[-1].append(("<s>",backwardProb))

    return BackwardProbabilityDict;

def ComputeDataLikelihood(hiddenStatesList, observationsList, emissionProbabilityDict, transitionProbabilityDict):

    forwardProbabilityDict = ForwardProbabilityComputer(hiddenStatesList,observationsList,emissionProbabilityDict,transitionProbabilityDict)
    backwardProababilityDict = BackWardProbabilityComputer(hiddenStatesList,observationsList,emissionProbabilityDict,transitionProbabilityDict)

    dataLikelihood = forwardProbabilityDict[len(observationsList)][0][1]

    return (forwardProbabilityDict,backwardProababilityDict,dataLikelihood)
