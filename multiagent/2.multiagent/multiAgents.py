# multiAgents.py
# --------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from util import manhattanDistance
from game import Directions
import random, util

from game import Agent

class ReflexAgent(Agent):
    """
    A reflex agent chooses an action at each choice point by examining
    its alternatives via a state evaluation function.

    The code below is provided as a guide.  You are welcome to change
    it in any way you see fit, so long as you don't touch our method
    headers.
    """


    def getAction(self, gameState):
        """
        You do not need to change this method, but you're welcome to.

        getAction chooses among the best options according to the evaluation function.

        Just like in the previous project, getAction takes a GameState and returns
        some Directions.X for some X in the set {NORTH, SOUTH, WEST, EAST, STOP}
        """
        # Collect legal moves and successor states
        legalMoves = gameState.getLegalActions()

        # Choose one of the best actions
        scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
        bestScore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        chosenIndex = random.choice(bestIndices) # Pick randomly among the best

        "Add more of your code here if you want to"

        return legalMoves[chosenIndex]

    def evaluationFunction(self, currentGameState, action):
        """
        Design a better evaluation function here.

        The evaluation function takes in the current and proposed successor
        GameStates (pacman.py) and returns a number, where higher numbers are better.

        The code below extracts some useful information from the state, like the
        remaining food (newFood) and Pacman position after moving (newPos).
        newScaredTimes holds the number of moves that each ghost will remain
        scared because of Pacman having eaten a power pellet.

        Print out these variables to see what you're getting, then combine them
        to create a masterful evaluation function.
        """
        # Useful information you can extract from a GameState (pacman.py)
        successorGameState = currentGameState.generatePacmanSuccessor(action)
        newPos = successorGameState.getPacmanPosition()
        newFood = successorGameState.getFood()
        newGhostStates = successorGameState.getGhostStates()
        newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]

        "*** YOUR CODE HERE ***"
        # Return a very high score if successor state is a win position
        if successorGameState.isWin():
            return 99999

        score = 0
        # Find the closest food pellet, and reduce the score by that distance
        # State with the closest food pellet will have the highest score
        min_food_dist = min([manhattanDistance(newPos, food_pos) for food_pos in newFood.asList()])
        score -= min_food_dist

        # Find the distances to the ghosts in the current state
        cur_ghost_dists = []
        for ghost_pos in successorGameState.getGhostPositions():
            man_distance = manhattanDistance(newPos, ghost_pos)
            cur_ghost_dists.append(man_distance)

        # Find the distances to the ghosts in the successor state
        next_ghost_dists = []
        for ghost_pos in successorGameState.getGhostPositions():
            man_distance = manhattanDistance(newPos, ghost_pos)
            next_ghost_dists.append(man_distance)

        # Find the food count in the current and successor states
        cur_food_count = currentGameState.getFood().count()
        next_food_count = newFood.count()

        # Increase score if pacman has eaten the power pellet
        if newPos in currentGameState.getCapsules():
            score += 75

        # Penalize for stopping
        if action == Directions.STOP:
            score -= 5

        # Increase the score if pacman eats a pellet while moving to the successor state
        if next_food_count < cur_food_count:
            score += 100

        # Decrease score for each remaining food pellet
        score -= 5 * next_food_count

        total_scared_time = sum(newScaredTimes)
        # It is better if pacman is closer to the ghosts when they are scared, and farther otherwise
        if total_scared_time > 0:
            if min(cur_ghost_dists) < min(next_ghost_dists):
                score += 100
            else:
                score -= 50
        else:
            if min(cur_ghost_dists) < min(next_ghost_dists):
                score -= 50
            else:
                score += 100

        return successorGameState.getScore() + score - min_food_dist

def scoreEvaluationFunction(currentGameState):
    """
    This default evaluation function just returns the score of the state.
    The score is the same one displayed in the Pacman GUI.

    This evaluation function is meant for use with adversarial search agents
    (not reflex agents).
    """
    return currentGameState.getScore()

class MultiAgentSearchAgent(Agent):
    """
    This class provides some common elements to all of your
    multi-agent searchers.  Any methods defined here will be available
    to the MinimaxPacmanAgent, AlphaBetaPacmanAgent & ExpectimaxPacmanAgent.

    You *do not* need to make any changes here, but you can if you want to
    add functionality to all your adversarial search agents.  Please do not
    remove anything, however.

    Note: this is an abstract class: one that should not be instantiated.  It's
    only partially specified, and designed to be extended.  Agent (game.py)
    is another abstract class.
    """

    def __init__(self, evalFn = 'scoreEvaluationFunction', depth = '2'):
        self.index = 0 # Pacman is always agent index 0
        self.evaluationFunction = util.lookup(evalFn, globals())
        self.depth = int(depth)

class MinimaxAgent(MultiAgentSearchAgent):
    """
    Your minimax agent (question 2)
    """

    def getAction(self, gameState):
        """
        Returns the minimax action from the current gameState using self.depth
        and self.evaluationFunction.

        Here are some method calls that might be useful when implementing minimax.

        gameState.getLegalActions(agentIndex):
        Returns a list of legal actions for an agent
        agentIndex=0 means Pacman, ghosts are >= 1

        gameState.generateSuccessor(agentIndex, action):
        Returns the successor game state after an agent takes an action

        gameState.getNumAgents():
        Returns the total number of agents in the game

        gameState.isWin():
        Returns whether or not the game state is a winning state

        gameState.isLose():
        Returns whether or not the game state is a losing state
        """
        "*** YOUR CODE HERE ***"
        num_of_agents = gameState.getNumAgents()

        def value(game_state, agent, depth):
            # If current state is a terminal state: return the utility and no action
            if game_state.isWin() or game_state.isLose() or depth == self.depth:
                return self.evaluationFunction(game_state), None

            # If it is the turn of Pacman: find the max value
            if agent == self.index:
                return max_value(game_state, depth)
            # Else, it is the turn of the ghosts: find the min value
            else:
                return min_value(game_state, depth, agent)

        def max_value(game_state, depth):
            utility = float('-inf')
            action = None

            # for every possible action: find the maximum utility
            for cur_action in game_state.getLegalActions(self.index):
                # max agent will choose after min agent has minimized the utility
                min_val = value(game_state.generateSuccessor(self.index, cur_action), 1, depth)[0]
                if min_val > utility:
                    utility, action = min_val, cur_action

            return utility, action

        def min_value(game_state, depth, ghost_index):
            utility = float('inf')
            action = None

            # for every possible action: find the minimum utility
            for cur_action in game_state.getLegalActions(ghost_index):
                next_state = game_state.generateSuccessor(ghost_index, cur_action)
                # If the ghost_index is the last agent: next agent will be Pacman
                # Min agent will try to minimize the maximum utility for the max agent
                if ghost_index == num_of_agents - 1:
                    max_val = value(next_state, self.index, depth + 1)[0]
                else:
                    max_val = value(next_state, ghost_index + 1, depth)[0]
                if max_val < utility:
                    utility, action = max_val, cur_action

            return utility, action

        return value(gameState, self.index, 0)[1]

class AlphaBetaAgent(MultiAgentSearchAgent):
    """
    Your minimax agent with alpha-beta pruning (question 3)
    """

    def getAction(self, gameState):
        """
        Returns the minimax action using self.depth and self.evaluationFunction
        """
        "*** YOUR CODE HERE ***"
        num_of_agents = gameState.getNumAgents()
        alpha_global = float('-inf')
        beta_global = float('inf')

        def value(game_state, agent, depth, alpha, beta):
            # If current state is a terminal state: return the utility and no action
            if game_state.isWin() or game_state.isLose() or depth == self.depth:
                return self.evaluationFunction(game_state), None

            # If it is the turn of Pacman: find the max value
            if agent == self.index:
                return max_value(game_state, depth, alpha, beta)
            # Else, it is the turn of the ghosts: find the min value
            else:
                return min_value(game_state, depth, agent, alpha, beta)

        def max_value(game_state, depth, alpha, beta):
            utility = float('-inf')
            action = None

            # for every possible action: find the maximum utility
            for cur_action in game_state.getLegalActions(self.index):
                next_state = game_state.generateSuccessor(self.index, cur_action)
                # max agent will choose after min agent has minimized the utility
                min_val = value(next_state, 1, depth, alpha, beta)[0]
                if min_val > utility:
                    utility, action = min_val, cur_action
                # If utility is more than beta: min agent will ignore this path
                if utility > beta:
                    return utility, action
                alpha = max(utility, alpha)

            return utility, action

        def min_value(game_state, depth, ghost_index, alpha, beta):
            utility = float('inf')
            action = None

            # for every possible action: find the minimum utility
            for cur_action in game_state.getLegalActions(ghost_index):
                next_state = game_state.generateSuccessor(ghost_index, cur_action)
                # If the ghost_index is the last agent: next agent will be Pacman
                # Min agent will try to minimize the maximum utility for the max agent
                if ghost_index == num_of_agents - 1:
                    max_val = value(next_state, self.index, depth + 1, alpha, beta)[0]
                else:
                    max_val = value(next_state, ghost_index + 1, depth, alpha, beta)[0]
                if max_val < utility:
                    utility, action = max_val, cur_action
                # If utility is less than alpha: max agent will ignore this path
                if utility < alpha:
                    return utility, action
                beta = min(utility, beta)

            return utility, action

        return value(gameState, self.index, 0, alpha_global, beta_global)[1]

class ExpectimaxAgent(MultiAgentSearchAgent):
    """
      Your expectimax agent (question 4)
    """

    def getAction(self, gameState):
        """
        Returns the expectimax action using self.depth and self.evaluationFunction

        All ghosts should be modeled as choosing uniformly at random from their
        legal moves.
        """
        "*** YOUR CODE HERE ***"
        num_of_agents = gameState.getNumAgents()

        def value(game_state, agent, depth):
            # If current state is a terminal state: return the expected value and no action
            if game_state.isWin() or game_state.isLose() or depth == self.depth:
                return self.evaluationFunction(game_state), None

            # If it is the turn of Pacman: find the max expected value
            if agent == self.index:
                return max_value(game_state, depth)
            # Else, it is the turn of the ghosts: find the total expected value
            else:
                return exp_value(game_state, depth, agent)

        def max_value(game_state, depth):
            utility = float('-inf')
            action = None

            # for every possible action: find the maximum expected value
            for cur_action in game_state.getLegalActions(self.index):
                # max agent will choose after chance agent has calculated the expected value
                min_val = value(game_state.generateSuccessor(self.index, cur_action), 1, depth)[0]
                if min_val > utility:
                    utility, action = min_val, cur_action

            return utility, action

        def exp_value(game_state, depth, ghost_index):
            exp_val = 0
            action = None

            actions_list = game_state.getLegalActions(ghost_index)
            num_of_actions = len(actions_list)
            # for every possible action: find the total expected value of all the paths
            for cur_action in actions_list:
                next_state = game_state.generateSuccessor(ghost_index, cur_action)
                # If the ghost_index is the last agent: next agent will be Pacman
                # Min agent will try to minimize the expected value for the max agent
                if ghost_index == num_of_agents - 1:
                    max_val = value(next_state, self.index, depth + 1)[0]
                else:
                    max_val = value(next_state, ghost_index + 1, depth)[0]
                exp_val += (max_val / num_of_actions)

            return exp_val, action

        return value(gameState, self.index, 0)[1]

