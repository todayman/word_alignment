#! /usr/bin/env python2


# remember parameters keys are (x,y) for p(x|y)

def initializeParameters(hiddenStateList, observationList):
    return initializeUniformDistribution(hiddenStateList, observationList)


def initializeUniformDistribution(hiddenStateList, observationList):
    uniformEmissionProbability = float(1) / float(len(observationList))
    uniformTransitionProbability = float(1) / float(len(hiddenStateList))
    emissionProbabilityDict = {}
    transitionProbabilityDict = {}

    for hiddenState in hiddenStateList:
        for observation in observationList:
            emissionProbabilityDict[(observation, hiddenState)] = uniformEmissionProbability

    for hiddenState in hiddenStateList:
        for otherHiddenState in hiddenStateList:
            transitionProbabilityDict[(otherHiddenState, hiddenState)] = uniformTransitionProbability
        transitionProbabilityDict[(hiddenState, "<s>")] = uniformTransitionProbability # <s> is our initial state
        transitionProbabilityDict[("</s>", hiddenState)] = uniformTransitionProbability # </s> is our final state

    return emissionProbabilityDict,transitionProbabilityDict
