#! /usr/bin/env python2


class HMMLikelihoodEstimator:

    def __init__(self, uniformEmissionProbability, uniformTransitionProbability):
        self.uniformEmissionProbability = uniformEmissionProbability
        self.uniformTransitionProbability = uniformTransitionProbability

    def ForwardProbabilityComputer(self, hiddenStatesList, observationsList,
                                   emissionProbabilityDict, transitionProbabilityDict):
        forwardProbabilityDict = {}
        forwardProbabilityDict[-1] = [("<s>", 1.0)]

        observationLength = len(hiddenStatesList)

        if observationLength not in transitionProbabilityDict:
            transitionProbabilityDict[observationLength] = {}

        for timeStep in xrange(0,len(observationsList)):
            forwardProbabilityDict[timeStep] = []
            forwardProbList = []
            scaleFactor = 0
            for hiddenState in hiddenStatesList:
                forwardProb = 0.0
                for previousStateEntry in forwardProbabilityDict[timeStep - 1]:
                    previousState = previousStateEntry[0]
                    previousStateForwardProbability = float(previousStateEntry[1])
                    forwardProb += previousStateForwardProbability * transitionProbabilityDict[observationLength].get((hiddenState,previousState), 1.0 / float(observationLength))
                forwardProb *= emissionProbabilityDict.get((observationsList[timeStep], hiddenState), self.uniformEmissionProbability)

                forwardProbList.append((hiddenState, forwardProb))
                scaleFactor += forwardProb

            for hiddenState, forwardProb in forwardProbList:
                forwardProbabilityDict[timeStep].append((hiddenState, float(forwardProb) / float(scaleFactor)))

        # transition to the end state </s>

        forwardProb = 0.0
        for previousStateEntry in forwardProbabilityDict[len(observationsList) - 1]:
            previousState = previousStateEntry[0]
            previousStateForwardProbability = float(previousStateEntry[1])
            forwardProb += previousStateForwardProbability * transitionProbabilityDict[observationLength].get(("</s>", previousState), 1.0 / float(observationLength))

        forwardProbabilityDict[len(observationsList)] = [("</s>", forwardProb)]

        return forwardProbabilityDict

    def BackWardProbabilityComputer(self, hiddenStatesList, observationsList,
                                    emissionProbabilityDict, transitionProbabilityDict):
        BackwardProbabilityDict = {}
        observationLength = len(hiddenStatesList)

        BackwardProbabilityDict[len(observationsList)] = [("</s>", 1.0)]
        BackwardProbabilityDict[len(observationsList)-1] = []
        scaleFactor = 0.0

        backProbList = []
        for hiddenState in hiddenStatesList:
            backProbList.append((hiddenState, transitionProbabilityDict[observationLength][("</s>", hiddenState)]))
            scaleFactor += transitionProbabilityDict[observationLength][("</s>", hiddenState)]

        for hiddenState, backwardProb in backProbList:
            BackwardProbabilityDict[len(observationsList) - 1].append((hiddenState, float(backwardProb) / float(scaleFactor)))

        for timeStep in xrange(len(observationsList) - 2, -1, -1):
            BackwardProbabilityDict[timeStep] = []
            scaleFactor = 0.0
            backProbList = []
            for hiddenState in hiddenStatesList:
               backwardProb = 0.0
               for nextStateEntry in BackwardProbabilityDict[timeStep+1]:
                   nextState=nextStateEntry[0]
                   nextStateBackwardProbability = float(nextStateEntry[1])

                   backwardProb = backwardProb + (nextStateBackwardProbability*
                                                  transitionProbabilityDict[observationLength][(nextState,hiddenState)]*
                                                  emissionProbabilityDict[(observationsList[timeStep+1],nextState)])

               backProbList.append((hiddenState,backwardProb))
               scaleFactor = scaleFactor + backwardProb


            for hiddenState,prob in backProbList:
                BackwardProbabilityDict[timeStep].append((hiddenState, float(prob) / float(scaleFactor)))

        BackwardProbabilityDict[-1] = []
        backwardProb = 0.0
        for nextStateEntry in BackwardProbabilityDict[0]:
            nextState = nextStateEntry[0]
            nextStateBackwardProbability = float(nextStateEntry[1])
            backwardProb = backwardProb + (nextStateBackwardProbability *
                                           transitionProbabilityDict[observationLength][(nextState, "<s>")] *
                                           emissionProbabilityDict[(observationsList[0], nextState)])

        BackwardProbabilityDict[-1].append(("<s>", backwardProb))

        return BackwardProbabilityDict

    def ComputeDataLikelihood(self, hiddenStatesList, observationsList, emissionProbabilityDict, transitionProbabilityDict):

        forwardProbabilityDict = self.ForwardProbabilityComputer(hiddenStatesList, observationsList, emissionProbabilityDict, transitionProbabilityDict)
        backwardProababilityDict = self.BackWardProbabilityComputer(hiddenStatesList, observationsList, emissionProbabilityDict, transitionProbabilityDict)

        return (forwardProbabilityDict, backwardProababilityDict)
