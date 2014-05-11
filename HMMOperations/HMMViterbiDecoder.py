__author__ = 'tejasvamsingh'


import sys
from math import log

class HMMViterbiDecoder:

    def __init__(self,transitionProbabilityDict,emissionProbabilityDict):
        self.transitionProbabilityDict = transitionProbabilityDict
        self.emissionProbabilityDict = emissionProbabilityDict

    def Decode(self, hiddenStatesList, observationsList ):
        
        backPointerDict={}
        self.GenerateViterbiLattice(backPointerDict,hiddenStatesList,observationsList)
        return self.ExtractViterbiPath(backPointerDict,hiddenStatesList,observationsList)


    def GenerateViterbiLattice(self,backPointerDict, hiddenStatesList, observationsList):

        viterbiProbabilityDict={}
        viterbiProbabilityDict[-1] = [("<s>",0.0)]
    
    
        for timeStep in xrange(0,len(observationsList)):
            backPointerDict[timeStep]={}
            viterbiProbabilityDict[timeStep]=[]
            for hiddenState in hiddenStatesList:
                viterbiProb = - sys.maxint
                bestState = hiddenState
                for previousStateEntry in viterbiProbabilityDict[timeStep-1]:
                    previousState = previousStateEntry[0]
                    previousStateViterbiProbability = float(previousStateEntry[1])

                    if previousStateViterbiProbability + log(self.transitionProbabilityDict[(hiddenState,previousState)]) > viterbiProb:
                        viterbiProb = previousStateViterbiProbability + log(self.transitionProbabilityDict[(hiddenState,previousState)])
                        bestState = previousState

    
                viterbiProb = viterbiProb + log(self.emissionProbabilityDict[(observationsList[timeStep],hiddenState)])
                viterbiProbabilityDict[timeStep].append((hiddenState,viterbiProb))
                backPointerDict[timeStep][hiddenState] = bestState


    
        # transition to the end state </s>
    
        viterbiProb = - sys.maxint
        bestState = hiddenStatesList[0]
        for previousStateEntry in viterbiProbabilityDict[len(observationsList)-1]:
            previousState = previousStateEntry[0]
            previousStateViterbiProbability = float(previousStateEntry[1])
            if previousStateViterbiProbability + log(self.transitionProbabilityDict[("</s>",previousState)]) > viterbiProb:
                viterbiProb = previousStateViterbiProbability + log(self.transitionProbabilityDict[("</s>",previousState)])
                bestState = previousState

        viterbiProbabilityDict[len(observationsList)] = [("</s>",viterbiProb)]
        backPointerDict[len(observationsList)]={}
        backPointerDict[len(observationsList)]["</s>"] = bestState


    def ExtractViterbiPath(self,backPointerDict, hiddenStatesList, observationsList):

        hiddenStateObservationStateSequence =""
        hiddenState = backPointerDict[len(observationsList)]["</s>"]
        for timeStep in xrange(len(observationsList)-1,-1,-1):
            hiddenStateObservationStateSequence = hiddenStateObservationStateSequence + str(timeStep)+"-"+str(hiddenStatesList.index(hiddenState))+" "
            hiddenState = backPointerDict[timeStep][hiddenState]


        return hiddenStateObservationStateSequence.rstrip()







    
