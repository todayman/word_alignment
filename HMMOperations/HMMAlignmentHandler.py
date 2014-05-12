#! /usr/bin/env python2
from HMMParameterInitializer import initializeParameters
from HMMLikelihoodEstimator import HMMLikelihoodEstimator
from HMMParameterTrainer import HMMParameterTrainer
from HMMViterbiDecoder import HMMViterbiDecoder


class HMMAlignmentHander:

    def __init__(self, hiddenStatesList, observationsList, emissionParameters):
        self.emissionProbabilityDict = emissionParameters
        self.transitionProbabilityDict = {}
        self.uniformEmissionProbability = float(1) / float(len(observationsList))
        self.uniformTransitionProbability = float(1) / float(len(hiddenStatesList))

    def TrainAligner(self, hiddenStatesLists, observationsLists):
        hmmLikelihoodEstimatorObject = HMMLikelihoodEstimator(self.uniformEmissionProbability, self.uniformTransitionProbability)

        for iterationNumber in xrange(0,3):
            hmmParameterTrainerObject = HMMParameterTrainer()

            for hiddenStatesList,observationsList in zip(hiddenStatesLists,observationsLists):
                forwardProbabilityDict, backwardProbabilityDict = \
                    hmmLikelihoodEstimatorObject.ComputeDataLikelihood(hiddenStatesList,
                                                                       observationsList,
                                                                       self.emissionProbabilityDict,
                                                                       self.transitionProbabilityDict,)
                hmmParameterTrainerObject.ExpectationStep(hiddenStatesList, observationsList,
                                                          self.emissionProbabilityDict, self.transitionProbabilityDict,
                                                          forwardProbabilityDict, backwardProbabilityDict)
            hmmParameterTrainerObject.MaximizationStep(self.transitionProbabilityDict, self.emissionProbabilityDict)

    def ComputeAlignments(self, hiddenStatesLists, observationsLists):
        hmmViterbiDecoderObject = HMMViterbiDecoder(self.transitionProbabilityDict, self.emissionProbabilityDict)
        alignmentList = []
        numSentences = 0
        for hiddenStatesList, observationsList in zip(hiddenStatesLists, observationsLists):
            alignmentList.append(hmmViterbiDecoderObject.Decode(hiddenStatesList, observationsList))
            numSentences = numSentences + 1
            if numSentences == 1000:
                break

        return alignmentList
