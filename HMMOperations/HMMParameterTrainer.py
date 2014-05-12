#! /usr/bin/env python2

class HMMParameterTrainer:
    def __init__(self):
        self.transitionCountDict = {}
        self.singleTransitionCountDict = {}
        self.singleEmissionCountDict = {}
        self.emissionCountDict = {}

    def ExpectationStep(self, hiddenStatesList, observationsList,
                    emissionProbabilityDict, transitionProbabilityDict,
                    forwardProbabilityDict, backwardProbabilityDict, dataLikelihood):
        for timeStep in xrange(-1, len(observationsList) - 1):
            for forwardStateEntry in forwardProbabilityDict[timeStep]:
                currentState = forwardStateEntry[0]
                currentStateForwardProbability = forwardStateEntry[1]
                for backwardStateEntry in backwardProbabilityDict[timeStep + 1]:
                    nextState = backwardStateEntry[0]
                    nextStateBackwardProbability = backwardStateEntry[1]
                    try:
                        self.transitionCountDict[(nextState, currentState)] = self.transitionCountDict[(nextState, currentState)] + (
                            currentStateForwardProbability * nextStateBackwardProbability *
                            transitionProbabilityDict[(nextState, currentState)] * emissionProbabilityDict[(observationsList[timeStep + 1], nextState)])
                    except KeyError:
                        self.transitionCountDict[(nextState, currentState)] = (
                        currentStateForwardProbability * nextStateBackwardProbability *
                        transitionProbabilityDict[(nextState, currentState)] * emissionProbabilityDict[(observationsList[timeStep + 1], nextState)])
                    try:
                        self.singleTransitionCountDict[(currentState,)] = self.singleTransitionCountDict[(currentState,)] + (
                            currentStateForwardProbability * nextStateBackwardProbability *
                            transitionProbabilityDict[(nextState,currentState)] * emissionProbabilityDict[(observationsList[timeStep + 1], nextState)])
                    except KeyError:
                        self.singleTransitionCountDict[(currentState,)] = (
                        currentStateForwardProbability * nextStateBackwardProbability *
                        transitionProbabilityDict[(nextState,currentState)] * emissionProbabilityDict[(observationsList[timeStep + 1],nextState)])

            for index in xrange(0, len(hiddenStatesList)):
                currentState = hiddenStatesList[index]
                try:
                    self.emissionCountDict[(observationsList[timeStep+1], currentState)] = \
                        self.emissionCountDict[(observationsList[timeStep+1], currentState)] + (
                            forwardProbabilityDict[timeStep+1][index][1] * backwardProbabilityDict[timeStep + 1][index][1]
                    )
                except KeyError:
                    self.emissionCountDict[(observationsList[timeStep+1], currentState)] = (
                            forwardProbabilityDict[timeStep+1][index][1] * backwardProbabilityDict[timeStep + 1][index][1]
                    )
                try:
                    self.singleEmissionCountDict[(currentState,)] = \
                        self.singleEmissionCountDict[(currentState,)] + (
                            forwardProbabilityDict[timeStep + 1][index][1] * backwardProbabilityDict[timeStep + 1][index][1]
                    )
                except KeyError:
                    self.singleEmissionCountDict[(currentState,)] = (
                            forwardProbabilityDict[timeStep + 1][index][1] * backwardProbabilityDict[timeStep + 1][index][1]
                    )


    def MaximizationStep(self,transitionProbabilityDict, emissionProbabilityDict):
        for (nextState, currentState) in self.transitionCountDict.keys():
            transitionProbabilityDict[(nextState, currentState)] = float(self.transitionCountDict[(nextState, currentState)]) / float(self.singleTransitionCountDict[(currentState,)])

        for (observation, currentState) in self.emissionCountDict.keys():
            emissionProbabilityDict[(observation, currentState)] = float(self.emissionCountDict[(observation, currentState)]) / float(self.singleEmissionCountDict[(currentState,)])
