import uuid

import logging


class State:
    def __init__(self, name, before_exit=None, after_entry=None):
        '''
        Creates a State object which will be part of the FSM
        :param name: (string)   Unique name to denote this state
        :param before_exit: (function)  function to execute before exiting this state
        :param after_entry: (function)  function to execute after entering this state
                                        NOTE: function should support all Keyword arguments as **kwargs.
                                        Reference: https://docs.python.org/2.7/tutorial/controlflow.html#keyword-arguments
        '''
        self._name = name
        self._before_exit = before_exit
        self._after_entry = after_entry

    @property
    def name(self):
        '''
        Getter for state name
        :return: (string)
        '''
        return self._name

    def exit_state(self, **kwargs):
        '''
        Executes the before_exit function with the keyword arguments
        :param kwargs: (optional) Input keyword arguments
        :return: None
        '''
        if self._before_exit:
            self._before_exit(**kwargs)

    def enter_state(self, **kwargs):
        '''
        Executes the after_entry function with the keyword arguments
        :param kwargs: (optional) Input keyword arguments
        :return: None
        '''
        if self._after_entry:
            self._after_entry(**kwargs)


class Transition:
    def __init__(self, name, source_name, destination_name, on_transition=None):
        '''
        Creates a Transition object denoting the transition between states
        :param name: (string)               Unique name to denote this transition from a source state.
                                            Transition names can be same for multiple transitions if their source state is different.
        :param source_name: (string)        Source state name
        :param destination_name: (string)   Destination state name
        :param on_transition: (function)    function to execute during this transition
                                            NOTE: function should support Keyword arguments as **kwargs.
                                            Reference: https://docs.python.org/2.7/tutorial/controlflow.html#keyword-arguments
        '''
        self._name = name
        self._source_name = source_name
        self._destination_name = destination_name
        self._on_transition = on_transition

    @property
    def name(self):
        '''
        Getter for transition name
        :return: (string)
        '''
        return self._name

    @property
    def source_name(self):
        '''
        Getter for Transition source name
        :return: (string)
        '''
        return self._source_name

    @property
    def destination_name(self):
        '''
        Getter for Transition destination name
        :return: (string)
        '''
        return self._destination_name

    def execute(self, **kwargs):
        '''
        Executes the on_transition function with the keyword arguments
        :param kwargs: (optional) Input keyword arguments
        :return: None
        '''
        if self._on_transition:
            self._on_transition(**kwargs)


class FSM:
    def __init__(self, initial_state_name, state_list, transition_list):
        '''
        Validates and initializes the FSM class at the given initial_state_name
        :param initial_state_name: (string):    State name for the initial state of FSM
        :param state_list: (list):              List of State objects which builds the FSM
        :param transition_list: (list):         List of Transition objects for navigating between the states
        '''

        # Initializes the fsm data structure
        self._initialize_fsm_data_struture()

        # Validate and add states
        for state in state_list:
            self._validate_and_add_state(state)

        # Validate and add transitions after adding states
        for transition in transition_list:
            self._validate_and_add_transition(transition)

        # Validate and set the initial state name after adding states
        self._validate_and_set_initial_state(initial_state_name)

    @property
    def state(self):
        '''
        Getter for the current state name of FSM
        :return: (string)
        '''
        return self._state

    def execute_transition(self, transition_name, **kwargs):
        '''
        Validates and executes the given transition name from the current state
        :param transition_name: (string)   - Name of the transition to execute
        :param kwargs: (optional)
        :return:
        '''
        transition = self._state_transition_map.get(self.state).get('transitions').get(transition_name)
        if not transition:
            raise FSMException('Invalid transition:{} from source:{}'.format(transition_name, self.state))

        self._execute(self._state_transition_map.get(self.state).get('state'),
                      self._state_transition_map.get(transition.destination_name).get('state'),
                      transition,
                      **kwargs)

    def execute_transition_to(self, destination_name, **kwargs):
        '''
        Validates and executes the transition to the destination state from the current state
        :param destination_name: (string)   - Name of the destination state
        :param kwargs: (optional)  Input keyword arguments for passing on to the State and Transition functions
        :return: None
        '''
        if not self._is_valid_state(destination_name):
            raise FSMException('Cannot execute transition. Invalid state:{}'.format(destination_name))

        transition = self._state_transition_map.get(self.state).get('destination_states').get(destination_name)
        if not transition:
            raise FSMException('Invalid transition between source:{} and destination:{}'.format(self.state, destination_name))

        self._execute(self._state_transition_map.get(self.state).get('state'),
                      self._state_transition_map.get(destination_name).get('state'),
                      transition,
                      **kwargs)

    def _execute(self, source_state, destination_state, transition, **kwargs):
        '''
        Executes the source state exit function, transition function and destination state entry function in this order.
        :param source_state: (State)
        :param destination_state: (State)
        :param transition: (Transition)
        :param kwargs: (optional) Input keyword arguments for passing on to the State and Transition functions
        :return: None
        '''
        logging.debug('Executing Transition:{} - Source:{} Destination:{}'.format(transition.name, source_state.name, destination_state.name))
        source_state.exit_state(**kwargs)
        transition.execute(**kwargs)
        destination_state.enter_state(**kwargs)
        self._state = destination_state.name

    def _is_valid_state(self, state_name):
        '''
        Returns boolean value after validating the input state name
        :param state_name: (string) State name to validate
        :return: (boolean)
        '''
        return self._state_transition_map.get(state_name) is not None

    def _validate_and_add_state(self, state):
        '''
        Validates whether the state name already exits and adds to FSM.
        Raises FSMException if validation fails.
        :param state:   State object to validate and add
        :return: None
        '''
        if self._state_transition_map.get(state.name):
            raise FSMException('State name must be unique, cannot add duplicate.')
        self._state_transition_map[state.name] = {'state': state,
                                                  'transitions': {}, 'destination_states': {}}

    def _validate_and_add_transition(self, transition):
        '''
        Validates the new transition for the following
         1. Valid source name and destination name
         2. Duplicate transition name from the same source state
         3. Duplicate transition between the same source and destination states
        Raises FSMException if validation fails.
        NOTE: All the states must be added before adding transition objects as they are required for validation
        :param transition:  Transition object to validate and add to the FSM
        :return: None
        '''
        if not self._is_valid_state(transition.source_name):
            raise FSMException('Invalid source state:{} in transition:{}'.format(transition.source_name, transition.name))
        if not self._is_valid_state(transition.destination_name):
            raise FSMException('Invalid destination state:{} in transition:{}'.format(transition.destination_name, transition.name))
        if self._state_transition_map.get(transition.source_name).get('destination_states').get(transition.destination_name):
            raise FSMException('Transition between source:{} and destination:{} already exists.'.format(transition.source_name, transition.destination_name))
        if self._state_transition_map.get(transition.source_name).get('transitions').get(transition.name):
            raise FSMException('Duplication transition:{} from source:{}'.format(transition.name, transition.source_name))

        # Set transition data in the _state_transition_map
        self._state_transition_map[transition.source_name]['transitions'][transition.name] = transition
        self._state_transition_map[transition.source_name]['destination_states'][transition.destination_name] = transition

    def _validate_and_set_initial_state(self, initial_state_name):
        '''
        Validates and sets the initial state name.
        Raises FSMException if validation fails.
        NOTE: All the states must be added before setting initial state name as it is required for validation
        :param initial_state_name:  Initial state name to validate
        :return: None
        '''
        if not initial_state_name or not self._state_transition_map.get(initial_state_name):
            raise FSMException('Incorrect initial state. Set a valid initial state name.')
        self._state = initial_state_name

    def _initialize_fsm_data_struture(self):
        # Initializes the data structure for managing FSM states and transitions
        # Example with sample data:
        #
        # self._state_transition_map = {
        #     'state1': {
        #         'state': State(),
        #         'transitions': {
        #             'transition1': Transition(),
        #             'transition2': Transition()
        #         },
        #         'destination_states': {
        #             'state2': Transition(),
        #             'state3': Transition()
        #         }
        #     },
        #     'state3': {
        #         'state': State(),
        #         'transitions': {
        #             'transition3': Transition(),
        #             'transition4': Transition()
        #         },
        #         'destination_states': {
        #             'state4': Transition(),
        #             'state1': Transition()
        #         }
        #     }
        # }
        self._state_transition_map = {}

class FSMBuilder:
    '''
    Follows Builder pattern. Class for building the FSM object.
    '''
    def __init__(self):
        self._states = []
        self._transitions = []
        self._initial_state_name = None

    def add_state(self, before_exit=None, after_entry=None):
        '''
        Creates a State object with a unique random name
        :param before_exit: (function)  function to execute before exiting this state
        :param after_entry: (function)  function to execute after entering this state
        :return: (State)                Returns the State object
        '''
        state_name = self._generate_random_name('state')
        return self.add_named_state(state_name, before_exit=before_exit, after_entry=after_entry)

    def add_named_state(self, name, before_exit=None, after_entry=None):
        '''
        Creates a State object with the given name. Name must be unique
        :param name: (string)           Unique name to identify the state
        :param before_exit: (function)  function to execute before exiting this state
        :param after_entry: (function)  function to execute after entering this state
        :return: (State)
        '''
        state = State(name, before_exit=before_exit, after_entry=after_entry)
        self._states.append(state)
        return state

    def add_transition(self, source_name, destination_name, on_transition=None):
        '''
        Creates a Transition object with a unique random name, denoting the transition between states.
        :param source_name: (string)        Source state name
        :param destination_name: (string)   Destination state name
        :param on_transition: (function)    function to execute during this transition
        :return: (Transition)
        '''
        transition_name = self._generate_random_name('transition')
        return self.add_named_transition(transition_name, source_name, destination_name, on_transition=on_transition)

    def add_named_transition(self, transition_name, source_name, destination_name, on_transition=None):
        '''
        Creates a Transition object with the given name, denoting the transition between states.
        Transition names can be same for multiple transitions if their source state is different.
        :param transition_name: (string)    Unique name to identify the transition from the source state
        :param source_name: (string)        Source state name
        :param destination_name: (string)   Destination state name
        :param on_transition: (function)    function to execute during this transition
        :return: (Transition)
        '''
        transition = Transition(transition_name, source_name, destination_name, on_transition=on_transition)
        self._transitions.append(transition)
        return transition

    def set_initial_state(self, state_name):
        '''
        Sets the initial state name of the FSM.
        NOTE: Initial state must be set compulsorily
        :param state_name: (string) Name of the initial state of FSM
        :return: None
        '''
        self._initial_state_name = state_name

    def build(self):
        '''
        Builds and validates the FSM object
        :return: (FSM)
        '''
        return FSM(self._initial_state_name, self._states, self._transitions)

    def _generate_random_name(self, prefix=''):
        return '{}_{}'.format(prefix, str(uuid.uuid4())[:8])


class FSMException(Exception):
    '''
    Customer exception class for raising FSM exceptions
    '''
    def __init__(self, message):
        '''
        :param message: (string) Input error message
        '''
        self._message = message
