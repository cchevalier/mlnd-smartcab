import random
import math
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator


class LearningAgent(Agent):
    """ An agent that learns to drive in the Smartcab world.
        This is the object you will be modifying. """ 

    def __init__(self, env, learning=False, epsilon=1.0, alpha=0.5):
        super(LearningAgent, self).__init__(env)     # Set the agent in the environment
        self.planner = RoutePlanner(self.env, self)  # Create a route planner
        self.valid_actions = self.env.valid_actions  # The set of valid actions

        # Set parameters of the learning agent
        self.learning = learning # Whether the agent is expected to learn
        self.Q = dict()          # Create a Q-table which will be a dictionary of tuples
        self.epsilon = epsilon   # Random exploration factor
        self.alpha = alpha       # Learning factor

        ###########
        ## TO DO ##
        ###########
        # Set any additional class parameters as needed
        self.t = 0

    def reset(self, destination=None, testing=False):
        """ The reset function is called at the beginning of each trial.
            'testing' is set to True if testing trials are being used
            once training trials have completed. """

        # Select the destination as the new location to route to
        self.planner.route_to(destination)
        
        ########### 
        ## TO DO ##
        ###########
        # Update epsilon using a decay function of your choice
        # Update additional class parameters as needed
        # If 'testing' is True, set epsilon and alpha to 0

        if testing:
            self.epsilon = 0.
            self.alpha = 0.

        else:

            # Increment time
            self.t += 1

            # ------------------------------------------------------
            # Default decay
            # ------------------------------------------------------

            # self.epsilon -= 0.05
            # F, D

            # ------------------------------------------------------
            # Optimized decay functions
            # ------------------------------------------------------

            #
            # Linear decay functions
            # ----------------------

            # self.epsilon -= 0.01
            # F, A, 90 tr.

            # self.epsilon -= 0.005
            # A, A, 198 tr.

            # self.epsilon -= 0.001
            # A+, A, 990 tr

            # self.epsilon -= 0.0005
            # A+, A+, 1981 tr, seed(42)
            # A+, A, 1981 tr, no seed
            #
            # Decay pow function
            # ------------------
            # a = 0.995
            # self.epsilon = a ** self.t
            # A+, A, 919 tr

            #
            # Cos decay functions
            # -------------------

            # self.epsilon = math.cos(0.5 * math.pi * self.t / 500)
            # A+, A, approx 500 tr

            # self.epsilon = math.cos(0.5 * math.pi * self.t / 1000)
            # A+, A, approx 1000 tr, seed 42

            # self.epsilon = math.cos(0.5 * math.pi * self.t / 2000)
            # A+, A, approx 2000 tr, seed 42

            # self.epsilon = math.cos(0.5 * math.pi * self.t / 5000)
            # # A+, A, approx 5000 tr

            self.epsilon = math.cos(0.5 * math.pi * self.t / 10000)
            # ?, ?, approx 10000 tr, seed 42

            #
            # Too rapid decaying functions
            # ----------------------------

            # self.epsilon = 1.0 / (self.t ** 2)

            # a = 0.99
            # self.epsilon = math.exp(-a * self.t)

        return None

    def build_state(self):
        """ The build_state function is called when the agent requests data from the 
            environment. The next waypoint, the intersection inputs, and the deadline 
            are all features available to the agent. """

        # Collect data about the environment
        waypoint = self.planner.next_waypoint()     # The next waypoint
        inputs = self.env.sense(self)               # Visual input - intersection light and traffic
        deadline = self.env.get_deadline(self)      # Remaining deadline

        ########### 
        ## TO DO ##
        ###########
        
        # NOTE : you are not allowed to engineer features outside of the inputs available.
        # Because the aim of this project is to teach Reinforcement Learning, we have placed 
        # constraints in order for you to learn how to adjust epsilon and alpha, and thus
        # learn about the balance between exploration and exploitation.
        # With the hand-engineered features, this learning process gets entirely negated.
        
        # Set 'state' as a tuple of relevant data for the agent        
        state = (waypoint, inputs['light'], inputs['oncoming'], inputs['left'])

        return state

    def get_maxQ(self, state):
        """ The get_max_Q function is called when the agent is asked to find the
            maximum Q-value of all actions based on the 'state' the smartcab is in. """

        ########### 
        ## TO DO ##
        ###########
        # Calculate the maximum Q-value of all actions for a given state

        maxQ = max(self.Q[state].values())

        return maxQ 

    def createQ(self, state):
        """ The createQ function is called when a state is generated by the agent. """

        ########### 
        ## TO DO ##
        ###########
        # When learning, check if the 'state' is not in the Q-table
        # If it is not, create a new dictionary for that state
        #   Then, for each action available, set the initial Q-value to 0.0

        if self.learning:
            if not(state in self.Q):
                self.Q[state] = {None: 0., 'forward': 0., 'left': 0., 'right': 0.}

        return

    def choose_action(self, state):
        """ The choose_action function is called when the agent is asked to choose
            which action to take, based on the 'state' the smartcab is in. """

        # Set the agent state and default action
        self.state = state
        self.next_waypoint = self.planner.next_waypoint()
        action = random.choice(self.valid_actions)

        ########### 
        ## TO DO ##
        ###########
        # When not learning, choose a random action
        if not self.learning:
            return action

        # When learning, choose a random action with 'epsilon' probability
        # Otherwise, choose an action with the highest Q-value for the current state
        # Be sure that when choosing an action with highest Q-value that you randomly
        # select between actions that "tie".

        if self.epsilon > random.random():
            return action
        else:
            maxQ = self.get_maxQ(state)
            possible_actions = []
            for action in self.Q[state]:
                if self.Q[state][action] == maxQ:
                    possible_actions.append(action)
            action = random.choice(possible_actions)

        return action


    def learn(self, state, action, reward):
        """ The learn function is called after the agent completes an action and
            receives a reward. This function does not consider future rewards 
            when conducting learning. """

        ########### 
        ## TO DO ##
        ###########
        # When learning, implement the value iteration update rule
        #   Use only the learning rate 'alpha' (do not use the discount factor 'gamma')
        if self.learning:
            self.Q[state][action] = (1 - self.alpha) * self.Q[state][action] + (self.alpha * reward)

        return


    def update(self):
        """ The update function is called when a time step is completed in the 
            environment for a given trial. This function will build the agent
            state, choose an action, receive a reward, and learn if enabled. """

        state = self.build_state()          # Get current state
        self.createQ(state)                 # Create 'state' in Q-table
        action = self.choose_action(state)  # Choose an action
        reward = self.env.act(self, action) # Receive a reward
        self.learn(state, action, reward)   # Q-learn

        return
        

def run():
    """ Driving function for running the simulation. 
        Press ESC to close the simulation, or [SPACE] to pause the simulation. """

    random.seed(42)  # Added this so as to get reproducible results


    ##############
    # Create the environment
    # Flags:
    #   verbose     - set to True to display additional output from the simulation (def: False)
    #   num_dummies - discrete number of dummy agents in the environment, default is 100
    #   grid_size   - discrete number of intersections (columns, rows), default is (8, 6)
    env = Environment(verbose=False)
    
    ##############
    # Create the driving agent
    # Flags:
    #   learning   - set to True to force the driving agent to use Q-learning (def: False)
    #    * epsilon - continuous value for the exploration factor, default is 1
    #    * alpha   - continuous value for the learning rate, default is 0.5
    agent = env.create_agent(LearningAgent, learning=True, epsilon=1.0, alpha=0.5)
    
    ##############
    # Follow the driving agent
    # Flags:
    #   enforce_deadline - set to True to enforce a deadline metric (def: False)
    env.set_primary_agent(agent, enforce_deadline=True)

    ##############
    # Create the simulation
    # Flags:
    #   update_delay - continuous time (in seconds) between actions, default is 2.0 seconds
    #   display      - set to False to disable the GUI if PyGame is enabled (def: True)
    #   log_metrics  - set to True to log trial and simulation results to /logs (def: False)
    #   optimized    - set to True to change the default log file name (def: False)
    sim = Simulator(env, update_delay=.01, display=False, log_metrics=True, optimized=False)
    
    ##############
    # Run the simulator
    # Flags:
    #   tolerance  - epsilon tolerance before beginning testing, default is 0.05 
    #   n_test     - discrete number of testing trials to perform, default is 0
    sim.run(tolerance=0.005, n_test=100)


if __name__ == '__main__':
    run()
