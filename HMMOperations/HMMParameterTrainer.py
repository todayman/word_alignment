__author__ = 'tejasvamsingh'


def TrainParameters(hiddenStatesList,observationsList,
                    emissionProbabilityDict,transitionProbabilityDict,
                    forwardProbabilityDict,backwardProbabilityDict, dataLikelihood):

    for iterations in xrange(0,20):

        transitionCountDict={}
        singleTransitionCountDict={}
        emissionCountDict={}
        singleEmissionCountDict={}

        for timeStep in xrange(-1,len(observationsList)-1):
            for forwardStateEntry in forwardProbabilityDict[timeStep]:
                currentState = forwardStateEntry[0]
                currentStateForwardProbability = forwardStateEntry[1]
                for backwardStateEntry in backwardProbabilityDict[timeStep+1]:
                    nextState = backwardStateEntry[0]
                    nextStateBackwardProbability = backwardStateEntry[1]
                    try:
                        transitionCountDict[(nextState,currentState)] = transitionCountDict[(nextState,currentState)] + (
                            currentStateForwardProbability*nextStateBackwardProbability*
                            transitionProbabilityDict[(nextState,currentState)]*emissionProbabilityDict[(observationsList[timeStep+1],nextState)])
                    except KeyError:
                        transitionCountDict[(nextState,currentState)] = (
                        currentStateForwardProbability*nextStateBackwardProbability*
                        transitionProbabilityDict[(nextState,currentState)]*emissionProbabilityDict[(observationsList[timeStep+1],nextState)])
                    try:
                        singleTransitionCountDict[(currentState,)] = singleTransitionCountDict[(currentState,)] + (
                            currentStateForwardProbability*nextStateBackwardProbability*
                            transitionProbabilityDict[(nextState,currentState)]*emissionProbabilityDict[(observationsList[timeStep+1],nextState)])
                    except KeyError:
                        singleTransitionCountDict[(currentState,)] = (
                        currentStateForwardProbability*nextStateBackwardProbability*
                        transitionProbabilityDict[(nextState,currentState)]*emissionProbabilityDict[(observationsList[timeStep+1],nextState)])



        for timeStep in xrange(0,len(observationsList)):
            for index in xrange(0,len(hiddenStatesList)):
                currentState = hiddenStatesList[index]
                try:
                    emissionCountDict[(observationsList[timeStep],currentState)] = \
                        emissionCountDict[(observationsList[timeStep],currentState)] +(
                            forwardProbabilityDict[timeStep][index][1] * backwardProbabilityDict[timeStep][index][1]
                    )
                except KeyError:
                    emissionCountDict[(observationsList[timeStep],currentState)] = (
                            forwardProbabilityDict[timeStep][index][1] * backwardProbabilityDict[timeStep][index][1]
                    )
                try:
                    singleEmissionCountDict[(currentState,)] = \
                        singleEmissionCountDict[(currentState,)] +(
                            forwardProbabilityDict[timeStep][index][1] * backwardProbabilityDict[timeStep][index][1]
                    )
                except KeyError:
                    singleEmissionCountDict[(currentState,)] = (
                            forwardProbabilityDict[timeStep][index][1] * backwardProbabilityDict[timeStep][index][1]
                    )


        for (nextState,currentState) in transitionCountDict.keys():
            transitionProbabilityDict[(nextState,currentState)] = float(transitionCountDict[(nextState,currentState)])/float(singleTransitionCountDict[(currentState,)])

        for (observation, currentState) in emissionCountDict.keys():
            emissionProbabilityDict[(observation,currentState)] = float(emissionCountDict[(observation,currentState)])/float(singleEmissionCountDict[(currentState,)])


    return (emissionProbabilityDict,transitionProbabilityDict)
