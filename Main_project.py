from automata.fa.nfa import NFA
from copy import deepcopy, copy


class nfa_with_multiple_initial_states(NFA):
    def __init__(self, states, input_symbols, transitions, initial_states, final_states):
        """
        Initial_states can take 2 forms :
            -the first is a set of part of states
            -the second is an only element in states
        In any case it return an nfa with only 1 initial states that is equivalent to the one that have multiple
        initial state
        """

        if type(initial_states) is set:
            new_transition_of_initial_state = dict()
            new_transition_of_initial_state["Qi"] = dict()
            for initial_state_of_transition in transitions:
                if initial_state_of_transition in initial_states:
                    for character_of_transition in transitions[initial_state_of_transition]:
                        new_transition_of_initial_state["Qi"][character_of_transition] = set()
                        for final_state_of_transition in transitions[initial_state_of_transition][
                            character_of_transition]:
                            new_transition_of_initial_state["Qi"][character_of_transition].add(
                                final_state_of_transition)

            new_transition = transitions
            new_transition["Qi"] = new_transition_of_initial_state["Qi"]
            new_initial_state = "Qi"
            new_final_state = copy(final_states)
            new_states = states
            new_states.add("Qi")
            for initial_state in initial_states:
                for final_state in final_states:
                    if initial_state == final_state:
                        new_final_state.add("Qi")

            self.states = new_states
            self.final_states = new_final_state
            self.initial_states = new_initial_state
            self.transitions = new_transition
            self.input_symbols = input_symbols
        else:
            self.states = states
            self.final_states = final_states
            self.initial_states = initial_states
            self.transitions = transitions
            self.input_symbols = input_symbols

    def depth_first_search(self, initial_state_of_transition, already_visited=None):
        if already_visited is None:
            already_visited = set()
        already_visited.add(initial_state_of_transition)
        if initial_state_of_transition not in self.transitions:
            return already_visited
        if initial_state_of_transition in self.transitions:
            for character_of_transition in self.transitions[initial_state_of_transition]:
                for final_state_of_transition in self.transitions[initial_state_of_transition][character_of_transition]:
                    if final_state_of_transition not in already_visited:
                        already_visited.add(final_state_of_transition)
                        already_visited = self.depth_first_search(final_state_of_transition, already_visited)
        return already_visited

    def ascend_edges(self, state_to_bactrack, already_visited=None):
        if already_visited is None:
            already_visited = set()
        already_visited.add(state_to_bactrack)
        for initial_state_of_transition in self.transitions:
            for character_of_transition in self.transitions[initial_state_of_transition]:
                for final_state_of_transition1 in self.transitions[initial_state_of_transition][
                    character_of_transition]:
                    if final_state_of_transition1 == state_to_bactrack:
                        if initial_state_of_transition not in already_visited:
                            already_visited.add(initial_state_of_transition)
                            already_visited = self.ascend_edges(initial_state_of_transition, already_visited)
        return already_visited

    ######################### Work in progress ###################################
    def Find_cycle(self, state_to_bactrack, already_visited=None, circle=None):
        if circle is None:
            circle = []
        if already_visited is None:
            already_visited = []
        for state in self.transitions:
            for char in self.transitions[state]:
                for state1 in self.transitions[state][char]:
                    if state1 in state_to_bactrack:
                        if state not in already_visited:
                            already_visited += [state]
                            circle = self.Find_cycle(already_visited, already_visited, circle)
                        else:
                            ind = already_visited.index(state)
                            circle += [already_visited[ind:]]
        return circle

    ################################################################################
    def states_set_of_trim_nfa(self):
        set_of_states_from_initial_ones = self.depth_first_search(self.initial_states)
        set_of_states_from_final_ones = set()
        for final_state in self.final_states:
            current_set = self.ascend_edges(final_state)
            set_of_states_from_final_ones = set_of_states_from_final_ones.union(current_set)
        return set_of_states_from_final_ones.intersection(set_of_states_from_initial_ones)

    def trim(self):
        set_of_state = self.states_set_of_trim_nfa()
        transition = self.transitions
        transition2 = dict()
        initial_states = set()
        final_states = set()
        input_symboles = set()

        for initial_states_of_transition in transition:
            if initial_states_of_transition in set_of_state:
                transition2[initial_states_of_transition] = dict()
                for character_of_transition in transition[initial_states_of_transition]:
                    transition2[initial_states_of_transition][character_of_transition] = set()
                    for final_states_of_transition in transition[initial_states_of_transition][character_of_transition]:
                        if final_states_of_transition in set_of_state:
                            transition2[initial_states_of_transition][character_of_transition].add(
                                final_states_of_transition)

                    if transition2[initial_states_of_transition][character_of_transition] == set():
                        del transition2[initial_states_of_transition][character_of_transition]
                if transition2[initial_states_of_transition] == dict():
                    del transition2[initial_states_of_transition]

        if self.initial_states in set_of_state:
            initial_states = self.initial_states

        for final_state in self.final_states:
            if final_state in set_of_state:
                final_states.add(final_state)

        for initial_states_of_transition in transition:
            for char in transition[initial_states_of_transition]:
                input_symboles.add(char)
        if initial_states != set():
            self.transitions = transition2
            self.states = set_of_state
            self.final_states = final_states
            self.initial_states = initial_states
            self.input_symbols = input_symboles

    def square_automaton(self, other_nfa):
        input_symbols = self.input_symbols.intersection(
            other_nfa.input_symbols)
        transitions = dict()
        states = set()
        for initial_state_of_transition1 in self.transitions:
            for initial_state_of_transition2 in other_nfa.transitions:
                for character_of_transition1 in self.transitions[initial_state_of_transition1]:
                    for character_of_transition2 in other_nfa.transitions[initial_state_of_transition2]:
                        if character_of_transition1 == character_of_transition2:
                            transitions[(initial_state_of_transition1, initial_state_of_transition2)] = dict()
                            states.add((initial_state_of_transition1, initial_state_of_transition2))
                            transitions[(initial_state_of_transition1, initial_state_of_transition2)][
                                character_of_transition1] = set()
                            for final_state_of_transition1 in self.transitions[initial_state_of_transition1][
                                character_of_transition1]:
                                for final_state_of_transition2 in other_nfa.transitions[initial_state_of_transition2][
                                    character_of_transition2]:
                                    transitions[(initial_state_of_transition1, initial_state_of_transition2)][
                                        character_of_transition1].add(
                                        (final_state_of_transition1, final_state_of_transition2))
                                    states.add((final_state_of_transition1, final_state_of_transition2))

        initial_states = set()
        initial_states.add((self.initial_states, other_nfa.initial_states))
        initial_states.add((other_nfa.initial_states, self.initial_states))
        states.add((self.initial_states, other_nfa.initial_states))
        states.add((other_nfa.initial_states, self.initial_states))
        final_states = set()
        for states1 in self.final_states:
            for states2 in other_nfa.final_states:
                final_states.add((states1, states2))
                final_states.add((states2, states1))
                states.add((states1, states2))
                states.add((states2, states1))

        self.final_states = final_states
        self.transitions = transitions
        self.initial_states = initial_states
        self.input_symbols = input_symbols
        self.states = states


class transducer:
    def __init__(self, states, input_symbols, output_symbols, initial_states, final_states, transitions):
        if type(initial_states) is set:
            new_transition_of_initial_state = dict()
            new_transition_of_initial_state["Qi"] = dict()
            for initial_state_of_transition in initial_states:
                for character_of_transition in transitions[initial_state_of_transition]:
                    if character_of_transition not in new_transition_of_initial_state["Qi"].keys():
                        new_transition_of_initial_state["Qi"][character_of_transition] = dict()
                    for character_changed in transitions[initial_state_of_transition][character_of_transition]:
                        if character_changed not in new_transition_of_initial_state["Qi"][
                            character_of_transition].keys():
                            new_transition_of_initial_state["Qi"][character_of_transition][character_changed] = set()
                        for final_state_of_transition in \
                                transitions[initial_state_of_transition][character_of_transition][character_changed]:
                            new_transition_of_initial_state["Qi"][character_of_transition][character_changed].add(
                                final_state_of_transition)
            new_transition = transitions
            new_transition["Qi"] = new_transition_of_initial_state["Qi"]
            new_initial_state = "Qi"
            new_final_state = copy(final_states)
            new_state = states
            new_state.add("Qi")
            for initial_state in initial_states:
                for final_state in final_states:
                    if initial_state == final_state:
                        new_final_state.add("Qi")

            self.states = new_state
            self.output_symbols = output_symbols
            self.input_symbols = input_symbols
            self.initial_states = new_initial_state
            self.final_states = new_final_state
            self.transitions = new_transition
        else:
            self.states = states
            self.final_states = final_states
            self.initial_states = initial_states
            self.transitions = transitions
            self.input_symbols = input_symbols
            self.output_symbols = output_symbols

    def creat_transitions_for_sub_automaton(self):
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
        new_transitions = self.creat_transitions_for_sub_automaton()
        return nfa_with_multiple_initial_states(states=self.states, input_symbols=self.input_symbols,
                                                transitions=new_transitions, initial_states=self.initial_states,
                                                final_states=self.final_states)

    def compare_nfa_and_transducer(self, nfa_multiple):
        self.states = nfa_multiple.states
        self.input_symbols = nfa_multiple.input_symbols
        self.initial_states = nfa_multiple.initial_states
        self.final_states = nfa_multiple.final_states
        new_transition = dict()
        for initial_state_of_transition1 in nfa_multiple.transitions:
            for initial_state_of_transition2 in self.transitions:
                if initial_state_of_transition1 == initial_state_of_transition2:
                    new_transition[initial_state_of_transition1] = dict()
                    for character_of_transition1 in nfa_multiple.transitions[initial_state_of_transition1]:
                        for character_of_transition2 in self.transitions[initial_state_of_transition2]:
                            if character_of_transition1 == character_of_transition2:
                                new_transition[initial_state_of_transition1][character_of_transition1] = dict()
                                for character_changed1 in self.transitions[initial_state_of_transition1][
                                    character_of_transition1]:
                                    new_transition[initial_state_of_transition1][character_of_transition1][
                                        character_changed1] = set()
                                    for character_changed2 in \
                                            self.transitions[initial_state_of_transition1][character_of_transition1][
                                                character_changed1]:
                                        if character_changed2 in nfa_multiple.transitions[initial_state_of_transition1][
                                            character_of_transition1]:
                                            new_transition[initial_state_of_transition1][character_of_transition1][
                                                character_changed1].add(character_changed2)
                                    if new_transition[initial_state_of_transition1][character_of_transition1][
                                        character_changed1] == set():
                                        del new_transition[initial_state_of_transition1][character_of_transition1][
                                            character_changed1]
                                if new_transition[initial_state_of_transition1][character_of_transition1] == dict():
                                    del new_transition[initial_state_of_transition1][character_of_transition1]
                    if new_transition[initial_state_of_transition1] == dict():
                        del new_transition[initial_state_of_transition1]
        self.transitions = new_transition

    def trim(self):
        a = deepcopy(self)
        a = a.from_transducer_too_multiple_initial_nfa()
        a.trim()
        self.compare_nfa_and_transducer(a)

    def square_transducer(self, other_transducer):

        input_symbols = self.input_symbols.intersection(
            other_transducer.input_symbols)

        transitions = dict()
        states = set()
        final_states = set()

        for initial_state_of_transition1 in self.transitions:
            for initial_state_of_transition2 in other_transducer.transitions:
                for character_of_transition1 in self.transitions[initial_state_of_transition1]:
                    for character_of_transition2 in other_transducer.transitions[initial_state_of_transition2]:
                        if character_of_transition1 == character_of_transition2:
                            transitions[(initial_state_of_transition1, initial_state_of_transition2)] = dict()
                            states.add((initial_state_of_transition1, initial_state_of_transition2))
                            transitions[(initial_state_of_transition1, initial_state_of_transition2)][
                                character_of_transition1] = dict()
                            for character_changed1 in self.transitions[initial_state_of_transition1][
                                character_of_transition1]:
                                for character_changed2 in \
                                        other_transducer.transitions[initial_state_of_transition2][
                                            character_of_transition2]:
                                    transitions[(initial_state_of_transition1, initial_state_of_transition2)][
                                        character_of_transition1][
                                        (character_changed1, character_changed2)] = set()
                                    for final_state_of_transition1 in \
                                            self.transitions[initial_state_of_transition1][character_of_transition1][
                                                character_changed1]:
                                        for final_state_of_transition2 in \
                                                other_transducer.transitions[initial_state_of_transition2][
                                                    character_of_transition2][
                                                    character_changed2]:
                                            transitions[(initial_state_of_transition1, initial_state_of_transition2)][
                                                character_of_transition1][
                                                (character_changed1, character_changed2)].add(
                                                (final_state_of_transition1, final_state_of_transition2))
                                            states.add((final_state_of_transition1, final_state_of_transition2))

        initial_states = (self.initial_states, other_transducer.initial_states)
        states.add((self.initial_states, other_transducer.initial_states))
        states.add((other_transducer.initial_states, self.initial_states))
        for states1 in self.final_states:
            for states2 in other_transducer.final_states:
                final_states.add((states1, states2))
                final_states.add((states2, states1))
                states.add((states1, states2))
                states.add((states2, states1))

        self.final_states = final_states
        self.transitions = transitions
        self.initial_states = initial_states
        self.input_symbols = input_symbols
        self.states = states


def reverse(string_element):
    str2 = ''
    for i in range(len(string_element) - 1, -1, -1):
        str2 += string_element[i]
    return str2


def remove(string_element_1, string_element_2):
    len_str1 = len(string_element_1)
    len_str2 = len(string_element_2)
    len_str = min(len_str1, len_str2)
    for i in range(len_str):
        if string_element_1[len_str1 - i - 1] != string_element_2[i]:
            new_str = string_element_1[:len_str1 - i] + string_element_2[i:]
            return new_str
    if len_str == len_str1:
        new_str = string_element_2[len_str1:]
        return new_str
    else:
        new_str = string_element_1[:len_str1 - len_str2]
        return new_str


def Phi(string_element_1, string_element_2):
    len_str1 = len(string_element_1)
    len_str2 = len(string_element_2)
    if string_element_1 == string_element_2[:len_str1]:
        return '', remove(reverse(string_element_1), string_element_2)
    if string_element_2 == string_element_1[:len_str2]:
        return remove(reverse(string_element_2), string_element_1), ''
    else:
        return 0


def wB(tuple1, tuple2):
    if tuple1 == 0:
        return 0
    else:
        return Phi(tuple1[0] + tuple2[0], tuple1[1] + tuple2[1])


def is_function(transducer_to_use, as_been_visited=None):
    if as_been_visited is None:
        as_been_visited = set()
    square_transducer = deepcopy(transducer_to_use)
    square_transducer.square_transducer(square_transducer)
    square_transducer.trim()
    dictionary_of_value = dict()
    dictionary_of_value[square_transducer.initial_states] = ('', '')
    as_been_visited.add(square_transducer.initial_states)
    while len(as_been_visited) != len(square_transducer.states):
        for initial_state_of_transition in square_transducer.transitions:
            for character_of_transition in square_transducer.transitions[initial_state_of_transition]:
                for character_changed in square_transducer.transitions[initial_state_of_transition][
                    character_of_transition]:
                    for final_state_of_transition in \
                    square_transducer.transitions[initial_state_of_transition][character_of_transition][
                        character_changed]:
                        if initial_state_of_transition in as_been_visited:
                            if (final_state_of_transition not in as_been_visited) and (
                                    initial_state_of_transition in as_been_visited):
                                dictionary_of_value[final_state_of_transition] = wB(
                                    dictionary_of_value[initial_state_of_transition], character_changed)
                                as_been_visited.add(final_state_of_transition)
                            elif final_state_of_transition in as_been_visited:
                                if dictionary_of_value[final_state_of_transition] != wB(
                                        dictionary_of_value[initial_state_of_transition], character_changed):
                                    return False

    for final_state in square_transducer.final_states:
        if dictionary_of_value[final_state] != ('', ''):
            return False
    return True


############# Work in progresse ############

def distance_between_word(str1, str2):
    if str1 == str2[:len(str1)]:
        return len(str2) - len(str1)
    if str2 == str1[:len(str2)]:
        return len(str1) - len(str2)
    else:
        len_prefix = 0
        for i in range(min(len(str2), len(str1))):
            if str1[i] == str2[i]:
                len_prefix += 1
            else:
                return len(str1) + len(str2) - 2 * len_prefix


#############################################

transducer = transducer(
    states={'q0', 'q1'},
    input_symbols={'a'},
    output_symbols={'a', 'b'},
    initial_states='q0',
    final_states={'q1'},
    transitions={
        'q0': {'a': {'a': {'q1'}}},
        'q1': {'a': {'b': {'q1'}}}}
)

print(is_function(transducer))
