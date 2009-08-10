__author__ = 'Tom Schaul, tom@idsia.ch'

from scipy import power

from pybrain.utilities import abstractMethod
from task import Task
from pybrain.rl.agents.agent import Agent
from pybrain.structure.modules.module import Module
from pybrain.rl.experiments.episodic import EpisodicExperiment
from pybrain.rl.environments.fitnessevaluator import FitnessEvaluator


class EpisodicTask(Task, FitnessEvaluator):
    """ A task that consists of independent episodes. """

    # tracking cumulative reward
    cumreward = 0
    
    # tracking the number of samples
    samples = 0
    
    # the discount factor 
    discount = None
    
    # a task can have an intrinsic batchsize, reward being always averaged over a number of episodes.
    batchSize = 1
    
    
    
    def reset(self):
        """ reinitialize the environment """
        # Note: if a task needs to be reset at the start, the subclass constructor 
        # should take care of that.
        self.env.reset()
        self.cumreward = 0
        self.samples = 0        
        
    def isFinished(self): 
        """ is the current episode over? """
        abstractMethod()
        
    def performAction(self, action):
        Task.performAction(self, action)
        self.addReward()
        self.samples += 1
    
    def addReward(self):
        """ a filtered mapping towards performAction of the underlying environment. """                
        # by default, the cumulative reward is just the sum over the episode    
        if self.discount:
            self.cumreward += power(self.discount, self.samples) * self.getReward()
        else:
            self.cumreward += self.getReward()
    
    def getTotalReward(self):
        """ the accumulated reward since the start of the episode """
        return self.cumreward
        
    def f(self, x):
        """ An episodic task can be used as an evaluation function of a module that produces actions 
        from observations, or as an evaluator of an agent. """
        r = 0.
        for _ in range(self.batchSize):
            if isinstance(x, Module):
                x.reset()
                self.reset()
                while not self.isFinished():
                    self.performAction(x.activate(self.getObservation()))                
            elif isinstance(x, Agent):
                EpisodicExperiment(self, x).doEpisodes()
            else:
                raise ValueError(self.__class__.__name__+' cannot evaluate the fitness of '+str(type(x)))
            r += self.getTotalReward()
        return r / float(self.batchSize)
        