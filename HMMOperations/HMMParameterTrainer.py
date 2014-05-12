#! /usr/bin/env python2


class HMMParameterTrainer:
    def __init__(self):
        self.transitionCountDict = {}
        self.singleTransitionCountDict = {}
        self.singleEmissionCountDict = {}
        self.emissionCountDict = {}

    def ExpectationStep(self, hiddenStatesList, observationsList,
                        emissionProbabilityDict, transitionProbabilityDict,
                        forwardProbabilityDict, backwardProbabilityDict):
        observationLength = len(hiddenStatesList)

        if observationLength not in self.transitionCountDict:
            self.transitionCountDict[observationLength] = {}
        if observationLength not in self.singleTransitionCountDict:
            self.singleTransitionCountDict[observationLength] = {}

        for timeStep in xrange(-1, len(observationsList) - 1):
            for forwardStateEntry in forwardProbabilityDict[timeStep]:
                currentState = forwardStateEntry[0]
                currentStateForwardProbability = forwardStateEntry[1]
                for backwardStateEntry in backwardProbabilityDict[timeStep + 1]:
                    nextState = backwardStateEntry[0]
                    nextStateBackwardProbability = backwardStateEntry[1]
                    try:
                        self.transitionCountDict[observationLength][(nextState, currentState)] = self.transitionCountDict[observationLength][(nextState, currentState)] + (
                            currentStateForwardProbability * nextStateBackwardProbability *
                            transitionProbabilityDict[observationLength][(nextState, currentState)] * emissionProbabilityDict[(observationsList[timeStep + 1],nextState)])
                    except KeyError:
                        self.transitionCountDict[observationLength][(nextState, currentState)] = (
                            currentStateForwardProbability * nextStateBackwardProbability *
                            transitionProbabilityDict[observationLength][(nextState, currentState)] * emissionProbabilityDict[(observationsList[timeStep + 1], nextState)])
                    try:
                        self.singleTransitionCountDict[observationLength][(currentState,)] = self.singleTransitionCountDict[observationLength][(currentState,)] + (
                            currentStateForwardProbability * nextStateBackwardProbability *
                            transitionProbabilityDict[observationLength][(nextState, currentState)] * emissionProbabilityDict[(observationsList[timeStep + 1], nextState)])
                    except KeyError:
                        self.singleTransitionCountDict[observationLength][(currentState,)] = (
                            currentStateForwardProbability * nextStateBackwardProbability *
                            transitionProbabilityDict[observationLength][(nextState, currentState)] * emissionProbabilityDict[(observationsList[timeStep + 1], nextState)])

            for index in xrange(0,len(hiddenStatesList)):
                currentState = hiddenStatesList[index]
                self.emissionCountDict[(observationsList[timeStep + 1], currentState)] = \
                    self.emissionCountDict.get((observationsList[timeStep + 1], currentState), 0) + (
                        forwardProbabilityDict[timeStep + 1][index][1] * backwardProbabilityDict[timeStep + 1][index][1]
                )
                self.singleEmissionCountDict[(currentState,)] = \
                    self.singleEmissionCountDict.get((currentState,), 0) + (
                        forwardProbabilityDict[timeStep + 1][index][1] * backwardProbabilityDict[timeStep + 1][index][1]
                )

        nextStateBackwardProbability = backwardProbabilityDict[len(observationsList)][0][1]
        nextState = "</s>"
        for currentStateEntry in forwardProbabilityDict[len(observationsList) - 1]:
            currentState = currentStateEntry[0]
            currentStateForwardProbability = currentStateEntry[1]
            try:
                self.transitionCountDict[observationLength][(nextState, currentState)] = self.transitionCountDict[observationLength][(nextState, currentState)] + (
                    currentStateForwardProbability * nextStateBackwardProbability *
                    transitionProbabilityDict[observationLength][(nextState, currentState)])
            except KeyError:
                self.transitionCountDict[observationLength][(nextState, currentState)] = (
                    currentStateForwardProbability * nextStateBackwardProbability *
                    transitionProbabilityDict[observationLength][(nextState, currentState)])
            try:
                self.singleTransitionCountDict[observationLength][(currentState,)] = self.singleTransitionCountDict[observationLength][(currentState,)] + (
                    currentStateForwardProbability * nextStateBackwardProbability *
                    transitionProbabilityDict[observationLength][(nextState, currentState)])
            except KeyError:
                self.singleTransitionCountDict[observationLength][(currentState,)] = (
                    currentStateForwardProbability * nextStateBackwardProbability *
                    transitionProbabilityDict[observationLength][(nextState, currentState)])


    def MaximizationStep(self, transitionProbabilityDict, emissionProbabilityDict):
        for observationLength in self.transitionCountDict.keys():
            for (nextState, currentState) in self.transitionCountDict[observationLength].keys():
                try:
                    transitionProbabilityDict[observationLength][(nextState, currentState)] = float(self.transitionCountDict[observationLength][(nextState, currentState)]) / float(self.singleTransitionCountDict[observationLength][(currentState,)])
                except :
                    transitionProbabilityDict[observationLength][(nextState, currentState)] = 0.0

        for (observation, currentState) in self.emissionCountDict.keys():
            try:
                emissionProbabilityDict[(observation, currentState)] = float(self.emissionCountDict[(observation, currentState)]) / float(self.singleEmissionCountDict[(currentState,)])
            except:
                emissionProbabilityDict[(observation, currentState)] = 0.0
