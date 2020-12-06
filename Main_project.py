from automata.fa.nfa import NFA
from copy import copy
from random import randint
from time import time
import sys

sys.setrecursionlimit(11000)


def depth_first_search(automaton, initial_state_of_transition, already_visited=None):
    if already_visited is None:
        already_visited = set()
    already_visited.add(initial_state_of_transition)
    if initial_state_of_transition not in automaton.transitions:
        return already_visited
    if initial_state_of_transition in automaton.transitions:
        for character_of_transition in automaton.transitions[initial_state_of_transition]:
            for final_state_of_transition in automaton.transitions[initial_state_of_transition][
                character_of_transition]:
                if final_state_of_transition not in already_visited:
                    already_visited.add(final_state_of_transition)
                    already_visited = depth_first_search(automaton, final_state_of_transition, already_visited)
    return already_visited


def ascend_edges(automaton, state_to_bactrack, already_visited=None):
    if already_visited is None:
        already_visited = set()
    already_visited.add(state_to_bactrack)
    for initial_state_of_transition in automaton.transitions:
        for character_of_transition in automaton.transitions[initial_state_of_transition]:
            for final_state_of_transition1 in automaton.transitions[initial_state_of_transition][
                character_of_transition]:
                if final_state_of_transition1 == state_to_bactrack:
                    if initial_state_of_transition not in already_visited:
                        already_visited.add(initial_state_of_transition)
                        already_visited = ascend_edges(automaton, initial_state_of_transition, already_visited)
    return already_visited


def states_set_of_accessible_from_initial_state_nfa(automaton):
    set_of_states_from_initial_ones = depth_first_search(automaton, automaton.initial_states)
    return set_of_states_from_initial_ones


def states_set_of_co_accessible_nfa(automaton, set_of_states):
    set_of_states_from_final_ones = set()
    for state in set_of_states:
        current_set = ascend_edges(automaton, state)
        set_of_states_from_final_ones = set_of_states_from_final_ones.union(current_set)
    return set_of_states_from_final_ones


def states_set_of_trim_nfa(automaton):
    set_of_states_from_initial_ones = depth_first_search(automaton, automaton.initial_states)
    set_of_states_from_final_ones = states_set_of_co_accessible_nfa(automaton, automaton.final_states)
    return set_of_states_from_final_ones.intersection(set_of_states_from_initial_ones)


def sub_automaton(automaton, set_of_state):
    transition = automaton.transitions
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
    if automaton.initial_states in set_of_state:
        initial_states = automaton.initial_states

    for final_state in automaton.final_states:
        if final_state in set_of_state:
            final_states.add(final_state)

    for initial_states_of_transition in transition:
        for char in transition[initial_states_of_transition]:
            input_symboles.add(char)
    return nfa_with_multiple_initial_states(
        transitions=transition2,
        states=set_of_state,
        final_states=final_states,
        initial_states=initial_states,
        input_symbols=input_symboles,
    )


def square_transducer_product(first_transducer, other_transducer):
    input_symbols = first_transducer.input_symbols.intersection(
        other_transducer.input_symbols)
    output_symbols = first_transducer.output_symbols.union(other_transducer.output_symbols)
    transitions = dict()
    states = set()
    final_states = set()
    for initial_state_of_transition1 in first_transducer.transitions:
        for initial_state_of_transition2 in other_transducer.transitions:
            for character_of_transition1 in first_transducer.transitions[initial_state_of_transition1]:
                for character_of_transition2 in other_transducer.transitions[initial_state_of_transition2]:
                    if character_of_transition1 == character_of_transition2:
                        transitions[(initial_state_of_transition1, initial_state_of_transition2)] = dict()
                        states.add((initial_state_of_transition1, initial_state_of_transition2))
                        transitions[(initial_state_of_transition1, initial_state_of_transition2)][
                            character_of_transition1] = dict()
                        for character_changed1 in first_transducer.transitions[initial_state_of_transition1][
                            character_of_transition1]:
                            for character_changed2 in \
                                    other_transducer.transitions[initial_state_of_transition2][
                                        character_of_transition2]:
                                transitions[(initial_state_of_transition1, initial_state_of_transition2)][
                                    character_of_transition1][
                                    (character_changed1, character_changed2)] = set()
                                for final_state_of_transition1 in \
                                        first_transducer.transitions[initial_state_of_transition1][
                                            character_of_transition1][
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
    initial_states = (first_transducer.initial_states, other_transducer.initial_states)
    states.add((first_transducer.initial_states, other_transducer.initial_states))
    states.add((other_transducer.initial_states, first_transducer.initial_states))
    for states1 in first_transducer.final_states:
        for states2 in other_transducer.final_states:
            final_states.add((states1, states2))
            final_states.add((states2, states1))
            states.add((states1, states2))
            states.add((states2, states1))
    return transducer(
        final_states=final_states,
        transitions=transitions,
        initial_states=initial_states,
        input_symbols=input_symbols,
        output_symbols=output_symbols,
        states=states,
    )


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
            new_state = str(len(states))
            new_state = "q" + new_state
            new_transition_of_initial_state = dict()
            new_transition_of_initial_state[new_state] = dict()
            for initial_state_of_transition in transitions:
                if initial_state_of_transition in initial_states:
                    for character_of_transition in transitions[initial_state_of_transition]:
                        new_transition_of_initial_state[new_state][character_of_transition] = set()
                        for final_state_of_transition in transitions[initial_state_of_transition][
                            character_of_transition]:
                            new_transition_of_initial_state[new_state][character_of_transition].add(
                                final_state_of_transition)

            new_transition = transitions
            new_transition[new_state] = new_transition_of_initial_state[new_state]
            new_initial_state = new_state
            new_final_state = copy(final_states)
            new_states = states
            new_states.add(new_state)
            for initial_state in initial_states:
                for final_state in final_states:
                    if initial_state == final_state:
                        new_final_state.add(new_state)

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


class transducer:
    def __init__(self, states, input_symbols, output_symbols, initial_states, final_states, transitions):
        if type(initial_states) is set:
            new_state = str(len(states))
            new_state = "q" + new_state
            new_transition_of_initial_state = dict()
            new_transition_of_initial_state[new_state] = dict()
            for initial_state_of_transition in initial_states:
                for character_of_transition in transitions[initial_state_of_transition]:
                    if character_of_transition not in new_transition_of_initial_state[new_state].keys():
                        new_transition_of_initial_state[new_state][character_of_transition] = dict()
                    for character_changed in transitions[initial_state_of_transition][character_of_transition]:
                        if character_changed not in new_transition_of_initial_state[new_state][
                            character_of_transition].keys():
                            new_transition_of_initial_state[new_state][character_of_transition][
                                character_changed] = set()
                        for final_state_of_transition in \
                                transitions[initial_state_of_transition][character_of_transition][character_changed]:
                            new_transition_of_initial_state[new_state][character_of_transition][character_changed].add(
                                final_state_of_transition)
            new_transition = transitions
            new_transition[new_state] = new_transition_of_initial_state[new_state]
            new_initial_state = new_state
            new_final_state = copy(final_states)
            new_state = states
            new_state.add(new_state)
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
        nfa_from_transducer = from_transducer_too_multiple_initial_nfa(self)
        nfa_from_transducer = sub_automaton(nfa_from_transducer, states_set_of_trim_nfa(nfa_from_transducer))
        self.compare_nfa_and_transducer(nfa_from_transducer)

    def is_sequential(self):
        a = time()
        self.trim()
        square_transducer = square_transducer_product(self, self)
        automaton = from_transducer_too_multiple_initial_nfa(square_transducer)
        print("square ", time() - a)
        set_of_marked_state = mark_state(square_transducer)
        print("mark time ", time() - a)
        set_of_co_accessible_state_from_circle = states_set_of_co_accessible_nfa(automaton,set_of_marked_state)
        automaton = sub_automaton(automaton,set_of_co_accessible_state_from_circle)
        print("final time ", time() - a)
        if automaton.transitions == {}:
            if automaton.initial_states in automaton.final_states:
                return True
            else:
                return False
        square_transducer.compare_nfa_and_transducer(automaton)
        T1 = dict()
        for states in square_transducer.states:
            T1[states] = ''
        passed = set()
        value_W_prime = {(square_transducer.initial_states, ('', ''))}
        T2 = copy(T1)
        while value_W_prime != set():
            state = value_W_prime.pop()
            if state[0] in square_transducer.transitions:
                for character_of_transition in square_transducer.transitions[state[0]]:
                    for character_changed in square_transducer.transitions[state[0]][
                        character_of_transition]:
                        for final_state_of_transition in \
                                square_transducer.transitions[state[0]][character_of_transition][
                                    character_changed]:
                            h_prime = wB(state[1], character_changed)
                            if (final_state_of_transition, h_prime) not in passed:
                                value_W_prime.add((final_state_of_transition, h_prime))
                                if h_prime == 0:
                                    return False
                                else:
                                    case_2 = False
                                    if h_prime[0] != 0:
                                        case_2 = True
                                    if case_2:
                                        if are_comparable(h_prime[0], T1[final_state_of_transition]):
                                            if len(h_prime[0]) > len(T1[final_state_of_transition]):
                                                T1[final_state_of_transition] = h_prime
                                        else:
                                            return False
                                    else:
                                        if are_comparable(h_prime[1], T2[final_state_of_transition]):
                                            if len(h_prime[2]) > len(T2[final_state_of_transition]):
                                                T2[final_state_of_transition] = h_prime
                                        else:
                                            return False
                                value_W_prime.add((final_state_of_transition, h_prime))
                passed.add(state)
        return True

    def is_function(self, as_been_visited=None):
        if as_been_visited is None:
            as_been_visited = set()
        square_transducer = square_transducer_product(self, self)
        automaton = from_transducer_too_multiple_initial_nfa(square_transducer)
        automaton.sub_automaton(automaton.states_set_of_trim_nfa())
        square_transducer.compare_nfa_and_transducer(automaton)
        if automaton.transitions == {}:
            if automaton.initial_states in automaton.final_states:
                return True
            else:
                return False
        dictionary_of_value = dict()
        dictionary_of_value[square_transducer.initial_states] = ('', '')
        as_been_visited.add(square_transducer.initial_states)
        if square_transducer.transitions == {}:
            return True
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


def creat_random_transducer(number_of_state_max, density_transition, input_symbols, output_symbols,
                            want_epsilon_transition=None):
    if want_epsilon_transition is None:
        want_epsilon_transition = True
    if want_epsilon_transition:
        output_symbols.add('')
    state = set()
    transition = dict()
    for index in range(number_of_state_max):
        state.add('q' + str(index))

    initial_state = state.pop()
    state.add(initial_state)
    final_states = set()
    number_of_final_state = randint(1, number_of_state_max)
    true_set_of_state = set()

    for index in range(number_of_final_state):
        final_states.add(state.pop())

    state = state.union(final_states)

    for state_of_initial_transition in state:
        for character_of_transition in input_symbols:
            for character_changed in output_symbols:
                for final_state_of_transition in state:
                    random_number = randint(1, 100) / 100
                    if random_number < density_transition:
                        if state_of_initial_transition not in transition:
                            transition[state_of_initial_transition] = dict()
                        if character_of_transition not in transition[state_of_initial_transition]:
                            transition[state_of_initial_transition][character_of_transition] = dict()
                        if character_changed not in transition[state_of_initial_transition][character_of_transition]:
                            transition[state_of_initial_transition][character_of_transition][character_changed] = set()
                        transition[state_of_initial_transition][character_of_transition][character_changed].add(
                            final_state_of_transition)
                        true_set_of_state.add(state_of_initial_transition)
                        true_set_of_state.add(final_state_of_transition)
    true_set_of_state = true_set_of_state.union(final_states)
    true_set_of_state.add(initial_state)

    return transducer(
        states=true_set_of_state,
        input_symbols=input_symbols,
        output_symbols=output_symbols,
        initial_states=initial_state,
        final_states=final_states,
        transitions=transition,
    )


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


def are_comparable(str1, str2):
    if Phi(str1, str2) != 0:
        return True
    else:
        return False


def add_tuple_string(tuple1, tuple2):
    return tuple1[0] + tuple2[0], tuple1[1] + tuple2[1]


def number_of_transition(tranduceur):
    number = 0
    for i in tranduceur.transitions:
        for t in tranduceur.transitions[i]:
            for n in tranduceur.transitions[i][t]:
                number += 1
    return number


################# work in progress #######################################################
def find_marked_states(auto, list_of_state_already_visited=None):
    if list_of_state_already_visited is None:
        list_of_state_already_visited = []
    n = len(auto.states)
    list_of_states_dag = []
    list_of_state_visited = []
    a = time()
    for state in auto.states:
        list_of_state_already_visited += \
        depth_first_search_with_marked_states(auto, state, copy(list_of_state_already_visited))[1]
        if len(list_of_state_already_visited) == n:
            break
    print("copy", time() - a)
    list_of_state_already_visited.reverse()
    new_auto = inverse(auto)
    i = 0
    while i < len(list_of_state_already_visited):
        new_set = set()
        new_set = \
        depth_first_search_with_marked_states(new_auto, list_of_state_already_visited[i], list_of_state_visited)[0]
        list_of_states_dag += [tuple(new_set)]
        list_of_state_visited += new_set
        i += len(new_set)

    print("co_acce", time() - a)
    return list_of_states_dag


def from_transducer_too_multiple_initial_nfa(transducer):
    new_transitions = transducer.creat_transitions_for_sub_automaton()
    return nfa_with_multiple_initial_states(states=transducer.states, input_symbols=transducer.input_symbols,
                                            transitions=new_transitions, initial_states=transducer.initial_states,
                                            final_states=transducer.final_states)


def depth_first_search_with_marked_states(automate, initial_state_of_transition, already_visited, list_marked=None):
    if list_marked is None:
        list_marked = []
    if initial_state_of_transition in already_visited:
        return already_visited, list_marked
    already_visited += [initial_state_of_transition]
    if initial_state_of_transition not in automate.transitions:
        list_marked += [initial_state_of_transition]
        return already_visited, list_marked
    else:
        for character_of_transition in automate.transitions[initial_state_of_transition]:
            for final_state_of_transition in automate.transitions[initial_state_of_transition][character_of_transition]:
                if final_state_of_transition not in already_visited:
                    already_visited, list_marked = depth_first_search_with_marked_states(automate,
                                                                                         final_state_of_transition,
                                                                                         already_visited, list_marked)
        list_marked += [initial_state_of_transition]
        return already_visited, list_marked


def inverse(automaton):
    new_transition = dict()
    for initial_state_of_transition in automaton.transitions:
        for character_of_transition in automaton.transitions[initial_state_of_transition]:
            for final_state_of_transition in automaton.transitions[initial_state_of_transition][
                character_of_transition]:
                if final_state_of_transition not in new_transition:
                    new_transition[final_state_of_transition] = dict()
                if character_of_transition not in new_transition[final_state_of_transition]:
                    new_transition[final_state_of_transition][character_of_transition] = set()
                new_transition[final_state_of_transition][character_of_transition].add(initial_state_of_transition)
    return nfa_with_multiple_initial_states(transitions=new_transition,
                                            final_states=automaton.final_states,
                                            initial_states=automaton.initial_states,
                                            input_symbols=automaton.input_symbols,
                                            states=automaton.states

                                            )


def co_assessible_search_test(automaton, state_to_bactrack, list_to_acces, already_visited=None):
    if already_visited is None:
        already_visited = set()
    if state_to_bactrack in list_to_acces:
        return already_visited
    already_visited.add(state_to_bactrack)
    for initial_state_of_transition in automaton.transitions:
        for character_of_transition in automaton.transitions[initial_state_of_transition]:
            for final_state_of_transition in automaton.transitions[initial_state_of_transition][
                character_of_transition]:
                if final_state_of_transition == state_to_bactrack:
                    if initial_state_of_transition not in already_visited:
                        if initial_state_of_transition not in list_to_acces:
                            already_visited.add(initial_state_of_transition)
                            already_visited = co_assessible_search_test(automaton, initial_state_of_transition,
                                                                        list_to_acces, already_visited)
    return already_visited


def creat_dag(automaton, list_of_set_of_state):
    new_initial_state = None
    new_final_state = set()
    new_transition = dict()
    for set_of_state in list_of_set_of_state:
        if automaton.initial_states in set_of_state:
            new_initial_state = set_of_state
    for set_of_state in list_of_set_of_state:
        for state in set_of_state:
            if state in automaton.final_states:
                new_final_state.add(set_of_state)
                break
    for set_of_state in list_of_set_of_state:
        for other_set_of_state in list_of_set_of_state:
            if set_of_state != other_set_of_state:
                for initial_state_of_transition in set_of_state:
                    if initial_state_of_transition in automaton.transitions:
                        for character_of_transition in automaton.transitions[initial_state_of_transition]:
                            for final_state_of_transition in automaton.transitions[initial_state_of_transition][
                                character_of_transition]:
                                if final_state_of_transition in other_set_of_state:
                                    if initial_state_of_transition not in new_transition:
                                        new_transition[set_of_state] = dict()
                                    if character_of_transition not in new_transition[set_of_state]:
                                        new_transition[set_of_state][character_of_transition] = set()
                                    new_transition[set_of_state][character_of_transition].add(other_set_of_state)
                                    break

    return nfa_with_multiple_initial_states(initial_states=new_initial_state,
                                            final_states=new_final_state,
                                            transitions=new_transition,
                                            input_symbols=automaton.input_symbols,
                                            states=list_of_set_of_state
                                            )


def mark_state(square_transducer):
    automaton = from_transducer_too_multiple_initial_nfa(square_transducer)
    dag = creat_dag(automaton, find_marked_states(automaton))
    marked_state = set()
    already_marked = set()
    for state in dag.states:
        if state not in already_marked:
            for element in state:
                if element in square_transducer.transitions:
                    for character_of_transition in square_transducer.transitions[element]:
                        for character_changed in square_transducer.transitions[element][character_of_transition]:
                            for element1 in state:
                                if element1 in square_transducer.transitions[element][character_of_transition][
                                    character_changed]:
                                    if character_changed != [('', '')]:
                                        marked_state.union(set(state))
                                        already_marked.add(state)
                                        set_of_co_accessible = ascend_edges(dag,state)
                                        for state_co_accessible in set_of_co_accessible:
                                            marked_state.union(set(state_co_accessible))
                                            already_marked.add(state_co_accessible)

    return marked_state


def square_automaton(first_nfa, other_nfa):
    input_symbols = first_nfa.input_symbols.intersection(
        other_nfa.input_symbols)
    transitions = dict()
    states = set()
    for initial_state_of_transition1 in first_nfa.transitions:
        for initial_state_of_transition2 in other_nfa.transitions:
            for character_of_transition1 in first_nfa.transitions[initial_state_of_transition1]:
                for character_of_transition2 in other_nfa.transitions[initial_state_of_transition2]:
                    if character_of_transition1 == character_of_transition2:
                        transitions[(initial_state_of_transition1, initial_state_of_transition2)] = dict()
                        states.add((initial_state_of_transition1, initial_state_of_transition2))
                        transitions[(initial_state_of_transition1, initial_state_of_transition2)][
                            character_of_transition1] = set()
                        for final_state_of_transition1 in first_nfa.transitions[initial_state_of_transition1][
                            character_of_transition1]:
                            for final_state_of_transition2 in other_nfa.transitions[initial_state_of_transition2][
                                character_of_transition2]:
                                transitions[(initial_state_of_transition1, initial_state_of_transition2)][
                                    character_of_transition1].add(
                                    (final_state_of_transition1, final_state_of_transition2))
                                states.add((final_state_of_transition1, final_state_of_transition2))

    initial_states = set()
    initial_states.add((first_nfa.initial_states, other_nfa.initial_states))
    initial_states.add((other_nfa.initial_states, first_nfa.initial_states))
    states.add((first_nfa.initial_states, other_nfa.initial_states))
    states.add((other_nfa.initial_states, first_nfa.initial_states))
    final_states = set()
    for states1 in first_nfa.final_states:
        for states2 in other_nfa.final_states:
            final_states.add((states1, states2))
            final_states.add((states2, states1))
            states.add((states1, states2))
            states.add((states2, states1))
    return nfa_with_multiple_initial_states(
        final_states=final_states,
        transitions=transitions,
        initial_states=initial_states,
        input_symbols=input_symbols,
        states=states
    )


transduce = transducer(
    states={'q0', 'q1', 'q2', 'q3', 'q4', 'q5', 'q6'},
    input_symbols={'a', 'b'},
    initial_states='q0',
    output_symbols={'', 'b'},
    final_states={'q0', 'q1'},
    transitions={'q0': {'b': {'b': {'q1'}}},
                 'q1': {'b': {'b': {'q0', 'q2'}}},
                 'q2': {'b': {'b': {'q3'}}},
                 'q3': {'b': {'b': {'q4', 'q5'}}},
                 'q4': {'b': {'b': {'q2'}}},
                 'q5': {'b': {'': {'q6'}}},
                 'q6': {'b': {'': {'q5'}}}})
b = from_transducer_too_multiple_initial_nfa(transduce)
b_prim = inverse(b)

for i in range(100):
    a = creat_random_transducer(35, 0.1, {'b'}, {'b'}, want_epsilon_transition=True)
    print(a.transitions)
    print(a.is_sequential())
