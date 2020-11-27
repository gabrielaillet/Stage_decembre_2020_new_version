from automata.fa.nfa import NFA
from copy import deepcopy


class nfa_with_multiple_initial_states:
    def __init__(self, nfa_object, set_of_initial_states):
        self.all_nfa = dict()
        for initial_state in set_of_initial_states:
            self.all_nfa[initial_state] = NFA(states=nfa_object.states, input_symbols=nfa_object.input_symbols,
                                              transitions=nfa_object.transitions,
                                              initial_state=initial_state,
                                              final_states=nfa_object.final_states
                                              )

        self.states = nfa_object.states
        self.input_symbols = nfa_object.input_symbols
        self.initial_states = set_of_initial_states
        self.final_states = nfa_object.final_states
        self.transitions = nfa_object.transitions

    def parcourt_profondeur(self, initial_state, already_visited=None):
        if already_visited is None:
            already_visited = set()
        already_visited.add(initial_state)
        if initial_state not in self.transitions:
            return already_visited
        if initial_state in self.transitions:
            for transitions in self.transitions[initial_state]:
                for neightbors in self.transitions[initial_state][transitions]:
                    if neightbors not in already_visited:
                        already_visited.add(neightbors)
                        already_visited = self.parcourt_profondeur(neightbors, already_visited)
        return already_visited

    def remonter_lien(self, state_to_bactrack, already_visited=None):
        if already_visited is None:
            already_visited = set()
        already_visited.add(state_to_bactrack)
        for state in self.transitions:
            for char in self.transitions[state]:
                for state1 in self.transitions[state][char]:
                    if state1 == state_to_bactrack:
                        if state not in already_visited:
                            already_visited.add(state)
                            already_visited = self.remonter_lien(state, already_visited)
        return already_visited

    def Find_cycle(self, state_to_bactrack, already_visited=None, circle = []):
        if already_visited is None:
            already_visited = []
        for state in self.transitions:
            for char in self.transitions[state]:
                for state1 in self.transitions[state][char]:
                    if state1 in state_to_bactrack:
                        if state not in already_visited:
                            already_visited += [state]
                            circle = self.Find_cycle(already_visited, already_visited,circle)
                        else:
                            print('non')
                            ind = already_visited.index(state)
                            circle += [already_visited[ind:]]
        return circle

    def states_set_of_trim_nfa(self):
        states_set_of_from_initial = set()
        states_set_of_from_final = set()
        for states in self.initial_states:
            current_set = self.parcourt_profondeur(states)
            states_set_of_from_initial = states_set_of_from_initial.union(current_set)
        for states in self.final_states:
            current_set = self.remonter_lien(states)
            states_set_of_from_final = states_set_of_from_final.union(current_set)
        return states_set_of_from_final.intersection(states_set_of_from_initial)

    def trim_for_all(self):
        set_of_state = self.states_set_of_trim_nfa()

        transition = self.transitions
        transition2 = dict()
        initial_states = set()
        final_states = set()
        input_symboles = set()

        for key in transition:
            if key in set_of_state:
                transition2[key] = dict()
                for key_of_key in transition[key]:
                    transition2[key][key_of_key] = set()
                    for element in transition[key][key_of_key]:
                        if element in set_of_state:
                            transition2[key][key_of_key].add(element)

                    if transition2[key][key_of_key] == set():
                        del transition2[key][key_of_key]
                if transition2[key] == dict():
                    del transition2[key]

        for initial_state in self.initial_states:
            if initial_state in set_of_state:
                initial_states.add(initial_state)
        for final_state in self.final_states:
            if final_state in set_of_state:
                final_states.add(final_state)

        for key in transition:
            for char in transition[key]:
                input_symboles.add(char)

        if initial_states != set():
            self.transitions = transition2
            self.states = set_of_state
            self.final_states = final_states
            self.initial_states = initial_states
            self.input_symbols = input_symboles

    def trim(self):
        self.trim_for_all()
        first = self.initial_states.pop()
        nfa = NFA(states=self.states,
                  input_symbols=self.input_symbols,
                  transitions=self.transitions,
                  final_states=self.final_states,
                  initial_state=first
                  )

        self.initial_states.add(first)
        nfa = nfa_with_multiple_initial_states(nfa, self.initial_states)
        self.all_nfa = nfa.all_nfa


class square_automaton(nfa_with_multiple_initial_states):

    def __init__(self, nfa1_with_multiple_initial_states, nfa2_with_multiple_initial_states):
        self.all_nfa = [nfa1_with_multiple_initial_states.all_nfa, nfa2_with_multiple_initial_states.all_nfa]
        self.input_symbols = nfa1_with_multiple_initial_states.input_symbols.intersection(
            nfa2_with_multiple_initial_states.input_symbols)
        self.transitions = dict()
        self.states = set()

        for departure1 in nfa1_with_multiple_initial_states.transitions:
            for departure2 in nfa2_with_multiple_initial_states.transitions:
                for transition1 in nfa1_with_multiple_initial_states.transitions[departure1]:
                    for transition2 in nfa2_with_multiple_initial_states.transitions[departure2]:
                        if transition1 == transition2:
                            self.transitions[(departure1, departure2)] = dict()
                            self.states.add((departure1, departure2))
                            self.transitions[(departure1, departure2)][transition1] = set()

                            for arrival1 in nfa1_with_multiple_initial_states.transitions[departure1][transition1]:
                                for arrival2 in nfa2_with_multiple_initial_states.transitions[departure2][transition2]:
                                    self.transitions[(departure1, departure2)][transition1].add((arrival1, arrival2))
                                    self.states.add((arrival1, arrival2))
        initial_states = set()

        for states1 in nfa1_with_multiple_initial_states.initial_states:
            for states2 in nfa2_with_multiple_initial_states.initial_states:
                initial_states.add((states1, states2))
                initial_states.add((states2, states1))
                self.states.add((states1, states2))
                self.states.add((states2, states1))
        self.initial_states = initial_states
        final_states = set()

        for states1 in nfa1_with_multiple_initial_states.final_states:
            for states2 in nfa2_with_multiple_initial_states.final_states:
                final_states.add((states1, states2))
                final_states.add((states2, states1))
                self.states.add((states1, states2))
                self.states.add((states2, states1))
        self.final_states = final_states


class transducer:
    def __init__(self, states, input_symbols, initial_states, final_states, transitions):
        self.states = states
        self.input_symbols = input_symbols
        self.initial_states = initial_states
        self.final_states = final_states
        self.transitions = transitions

    def new_transition(self):
        new_transitions = dict()
        for state in self.transitions:
            new_transitions[state] = dict()
            for char in self.transitions[state]:
                new_transitions[state][char] = set()
                for char_to_change in self.transitions[state][char]:
                    for element in self.transitions[state][char][char_to_change]:
                        new_transitions[state][char].add(element)
        return new_transitions

    def from_transducer_too_multiple_initial_nfa(self):
        new_transitions = self.new_transition()
        initial = self.initial_states.pop()
        new_nfa = NFA(states=self.states,
                      input_symbols=self.input_symbols,
                      initial_state=initial,
                      final_states=self.final_states,
                      transitions=new_transitions)
        self.initial_states.add(initial)
        return nfa_with_multiple_initial_states(new_nfa, self.initial_states)

    def compare_nfa_transducer(self, nfa_multiple):
        self.states = nfa_multiple.states
        self.input_symbols = nfa_multiple.input_symbols
        self.initial_states = nfa_multiple.initial_states
        self.final_states = nfa_multiple.final_states

        new_transition = dict()
        for departure1 in nfa_multiple.transitions:
            for departure2 in self.transitions:
                if departure1 == departure2:
                    new_transition[departure1] = dict()
                    for value1 in nfa_multiple.transitions[departure1]:
                        for value2 in self.transitions[departure2]:
                            if value1 == value2:
                                new_transition[departure1][value1] = dict()
                                for value_to_change in self.transitions[departure1][value1]:
                                    new_transition[departure1][value1][value_to_change] = set()
                                    for element2 in self.transitions[departure1][value1][value_to_change]:
                                        if element2 in nfa_multiple.transitions[departure1][value1]:
                                            new_transition[departure1][value1][value_to_change].add(element2)
                                    if new_transition[departure1][value1][value_to_change] == set():
                                        del new_transition[departure1][value1][value_to_change]
                                if new_transition[departure1][value1] == dict():
                                    del new_transition[departure1][value1]
                    if new_transition[departure1] == dict():
                        del new_transition[departure1]
        self.transitions = new_transition

    def trim(self):
        a = deepcopy(self)
        a = a.from_transducer_too_multiple_initial_nfa()
        a.trim()
        self.compare_nfa_transducer(a)


class square_transducer(transducer):

    def __init__(self, nfa1_with_multiple_initial_states, nfa2_with_multiple_initial_states):
        self.input_symbols = nfa1_with_multiple_initial_states.input_symbols.intersection(
            nfa2_with_multiple_initial_states.input_symbols)

        self.transitions = dict()
        self.states = set()
        for departure1 in nfa1_with_multiple_initial_states.transitions:
            for departure2 in nfa2_with_multiple_initial_states.transitions:
                for transition1 in nfa1_with_multiple_initial_states.transitions[departure1]:
                    for transition2 in nfa2_with_multiple_initial_states.transitions[departure2]:
                        if transition1 == transition2:
                            self.transitions[(departure1, departure2)] = dict()
                            self.states.add((departure1, departure2))
                            self.transitions[(departure1, departure2)][transition1] = dict()
                            for arrival1_key in nfa1_with_multiple_initial_states.transitions[departure1][transition1]:
                                for arrival2_key in \
                                        nfa2_with_multiple_initial_states.transitions[departure2][transition2]:
                                    self.transitions[(departure1, departure2)][transition1][
                                        (arrival1_key, arrival2_key)] = set()
                                    for arrival1 in \
                                            nfa1_with_multiple_initial_states.transitions[departure1][transition1][
                                                arrival1_key]:
                                        for arrival2 in \
                                                nfa2_with_multiple_initial_states.transitions[departure2][transition2][
                                                    arrival2_key]:
                                            self.transitions[(departure1, departure2)][transition1][
                                                (arrival1_key, arrival2_key)].add((arrival1, arrival2))
                                            self.states.add((arrival1, arrival2))
        initial_states = set()

        for states1 in nfa1_with_multiple_initial_states.initial_states:
            for states2 in nfa2_with_multiple_initial_states.initial_states:
                initial_states.add((states1, states2))
                initial_states.add((states2, states1))
                self.states.add((states1, states2))
                self.states.add((states2, states1))
        self.initial_states = initial_states
        final_states = set()

        for states1 in nfa1_with_multiple_initial_states.final_states:
            for states2 in nfa2_with_multiple_initial_states.final_states:
                final_states.add((states1, states2))
                final_states.add((states2, states1))
                self.states.add((states1, states2))
                self.states.add((states2, states1))
        self.final_states = final_states

    def square_transductor_too_automaton(self):
        nfa = NFA(initial_state='q0',
                  final_states={'q0'},
                  input_symbols={'a'},
                  transitions={'q0': {'a': {'q0'}}},
                  states={'q0'})
        nfa = nfa_with_multiple_initial_states(nfa, {'q0'})
        nfa = square_automaton(nfa, nfa)
        new_transition = self.new_transition()
        nfa.transitions = new_transition
        nfa.states = self.states
        nfa.final_states = self.final_states
        nfa.initial_states = self.initial_states
        nfa.input_symbols = self.input_symbols
        return nfa

    def trim(self):
        a = deepcopy(self)
        a = a.square_transductor_too_automaton()
        a.trim_for_all()
        self.compare_nfa_transducer(a)


transducer = transducer(
    states={'q0', 'q1', 'q2', 'q3', 'q4'},
    input_symbols={'a', 'b'},
    initial_states={'q0'},
    final_states={'q1'},
    transitions={
        'q0': {'a': {'b': {'q1'}, 'a': {'q3', 'q1'}}},
        # Use '' as the key name for empty string (lambda/epsilon) transitions
        'q1': {'b': {'b': {'q0'}}},
        'q3': {'b': {'a': {'q0','q1'}}}}
)


def reverse(str):
    str2 = ''
    for i in range(len(str) - 1, -1, -1):
        str2 += str[i]
    return str2


def remove(str1, str2):
    len_str1 = len(str1)
    len_str2 = len(str2)
    len_str = min(len_str1, len_str2)
    for i in range(len_str):
        if str1[len_str1 - i - 1] != str2[i]:
            new_str = str1[:len_str1 - i] + str2[i:]
            return new_str
    if len_str == len_str1:
        new_str = str2[len_str1:]
        return new_str
    else:
        new_str = str1[:len_str1 - len_str2]
        return new_str


def Phi(str1, str2):
    len_str1 = len(str1)
    len_str2 = len(str2)
    if str1 == str2[:len_str1]:
        return '', remove(reverse(str1), str2)
    if str2 == str1[:len_str2]:
        return remove(reverse(str2), str1), ''
    else:
        return 0


def wB(tuple1, tuple2):
    if tuple1 == 0:
        return 0
    else:
        return Phi(tuple1[0] + tuple2[0], tuple1[1] + tuple2[1])


def is_function(transducer, as_been_visited=None):
    square_transducer_to_use = square_transducer(transducer, transducer)
    square_transducer_to_use.trim()
    if as_been_visited is None:
        as_been_visited = set()
    value = dict()
    for states in square_transducer_to_use.initial_states:
        value[states] = ('', '')
        as_been_visited.add(states)
    while len(as_been_visited) != len(square_transducer_to_use.states):
        for transition in square_transducer_to_use.transitions:
            for values in square_transducer_to_use.transitions[transition]:
                for value_to_change in square_transducer_to_use.transitions[transition][values]:
                    for next_state in square_transducer_to_use.transitions[transition][values][value_to_change]:
                        if transition in as_been_visited:
                            if (next_state not in as_been_visited) and (transition in as_been_visited):
                                value[next_state] = wB(value[transition], value_to_change)
                                as_been_visited.add(next_state)
                            elif next_state in as_been_visited:
                                if value[next_state] != wB(value[transition], value_to_change):
                                    return False

    for final_state in square_transducer_to_use.final_states:
        if value[final_state] != ('', ''):
            return False
    return True


def distance_between_word(str1,str2):
    if str1 == str2[:len(str1)]:
        return len(str2) - len(str1)
    if str2 == str1[:len(str2)]:
        return len(str1) - len(str2)
    else:
        len_prefix = 0
        for i in range(min(len(str2),len(str1))):
            if str1[i] == str2[i]:
                len_prefix += 1
            else:
                return len(str1) + len(str2) - 2 * len_prefix

a = transducer.from_transducer_too_multiple_initial_nfa()
print(a.Find_cycle([a.final_states.pop()]))

