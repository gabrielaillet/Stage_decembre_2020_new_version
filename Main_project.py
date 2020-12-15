from automata.fa.nfa import NFA
from copy import copy
from random import randint
from time import time
import sys
import numpy as np

sys.setrecursionlimit(11000)


def depth_first_search(automaton, initial_state_of_transition, already_visited=None):
    """
    This function aim to find all the states accessible from the initial_state_of_transition in an transducer_to_use
    Used in : states_set_of_accessible_from_initial_state_nfa , states_set_of_trim_nfa
    :param automaton: is a class nfa object. Type - nfa
    :param initial_state_of_transition: is the starting state from which the function start running. Type - str
    :param already_visited: is a set of all the states reachable from initial_state_of_transition.By default is None
                            . Type - set of str
    :return: already_visited: is a set of all the states reachable from initial_state_of_transition. Type - set of str
    """

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


def ascend_edges(automaton, state_to_backtrack, already_visited=None):
    """
    This function aim to find all the states co-accessible from the state_to_backtrack in an transducer_to_use
    Used in : states_set_of_co_accessible_nfa
    :param automaton: is a class nfa object. Type - nfa
    :param state_to_backtrack: is the starting state from which the function start running. Type - str
    :param already_visited: is a set of all the states reachable from initial_state_of_transition.By default is None
                            . Type - set of str
    :return: already_visited: is a set of all the states reachable from initial_state_of_transition. Type - set of str
    """
    if already_visited is None:
        already_visited = set()
    already_visited.add(state_to_backtrack)
    for initial_state_of_transition in automaton.transitions:
        for character_of_transition in automaton.transitions[initial_state_of_transition]:
            for final_state_of_transition1 in automaton.transitions[initial_state_of_transition][
                character_of_transition]:
                if final_state_of_transition1 == state_to_backtrack:
                    if initial_state_of_transition not in already_visited:
                        already_visited.add(initial_state_of_transition)
                        already_visited = ascend_edges(automaton, initial_state_of_transition, already_visited)
    return already_visited


def states_set_of_accessible_from_initial_state_nfa(automaton):
    """
    This function aim to find all the accessible state of an transducer_to_use. Meaning all states accessible from the initial
    state of the transducer_to_use.
    :param automaton: an nfa object. Type - nfa
    :return: set_states_from_initial_ones: all the states accessible in the transducer_to_use . Type - set of str
    """
    set_of_states_from_initial_ones = depth_first_search(automaton, automaton.initial_states)
    return set_of_states_from_initial_ones


def states_set_of_co_accessible_nfa(automaton, set_of_states):
    """
    This function aim to find all the co-accessible state of an transducer_to_use. Meaning all states co-accessible from the
    finals states of the transducer_to_use.
    :param automaton: an nfa object. Type - nfa
    :param set_of_states:
    :return: set_states_from_final_ones: all the states accessible in the transducer_to_use . Type - set of str
    """
    set_of_states_from_final_ones = set()
    for state in set_of_states:
        current_set = ascend_edges(automaton, state)
        set_of_states_from_final_ones = set_of_states_from_final_ones.union(current_set)
    return set_of_states_from_final_ones


def states_set_of_trim_nfa(automaton):
    """
    Find all the states that are either accessible from the initial state or co-accessible from the finals one.
    :param automaton: an nfa object. Type - nfa
    :return: set_of_trim_states. Type - set of str
    """
    set_of_states_from_initial_ones = depth_first_search(automaton, automaton.initial_states)
    set_of_states_from_final_ones = states_set_of_co_accessible_nfa(automaton, automaton.final_states)
    set_of_trim_states = set_of_states_from_final_ones.intersection(set_of_states_from_initial_ones)
    return set_of_trim_states


def sub_automaton(automaton, set_of_state):
    """
    Considering an transducer_to_use A and a set of state return the sub transducer_to_use SA . Considering two state u,v
     u -- > v is in SA if and only if u and v is in set_of_state and u --> v is in A.
    :param automaton: an nfa object. Type - nfa
    :param set_of_state:  Type - set of str
    :return: sub_automaton_to_return . Type - nfa
    """
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
    sub_automaton_to_return = nfa_with_multiple_initial_states(
        transitions=transition2,
        states=set_of_state,
        final_states=final_states,
        initial_states=initial_states,
        input_symbols=input_symboles,
    )
    return sub_automaton_to_return


def square_transducer_product(first_transducer, other_transducer):
    """
    Considering two transducer_to_use, make the product of them and return a new transducer_to_use.
    :param first_transducer: Type - transducer_to_use
    :param other_transducer: Type - transducer_to_use
    :return: final_transducer: Type - transducer_to_use
    """
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
    final_transducer = transducer(
        final_states=final_states,
        transitions=transitions,
        initial_states=initial_states,
        input_symbols=input_symbols,
        output_symbols=output_symbols,
        states=states,
    )
    return final_transducer


def creat_transitions_for_sub_automaton(transducer_to_use):
    """
    Find all the transition that fit the definition in from_transducer_to_multiple_nfa.
    :param transducer_to_use: Type - transducer
    :return: A dictionary of transition.
    """
    new_transitions = dict()
    for state in transducer_to_use.transitions:
        if state not in new_transitions:
         new_transitions[state] = dict()
        for char in transducer_to_use.transitions[state]:
            if char not in new_transitions[state]:
                new_transitions[state][char] = set()
            for char_to_change in transducer_to_use.transitions[state][char]:
                for element in transducer_to_use.transitions[state][char][char_to_change]:
                    new_transitions[state][char].add(element)
    return new_transitions


def from_transducer_to_multiple_initial_nfa(transducer_to_use):
    """
    Given a transducer T return the transd A induced. Given u,v two states of T, u --(char1)-- > v is in A if
    and only if there is a transition  u --(char1,char2) -- > v in T.
    :param transducer_to_use: Type - transducer
    :return: Type - nfa
    """
    new_transitions = creat_transitions_for_sub_automaton(transducer_to_use)
    return nfa_with_multiple_initial_states(states=transducer_to_use.states,
                                            input_symbols=transducer_to_use.input_symbols,
                                            transitions=new_transitions,
                                            initial_states=transducer_to_use.initial_states,
                                            final_states=transducer_to_use.final_states)


def find_marked_states_for_dag(auto, list_of_state_already_visited=None):
    if list_of_state_already_visited is None:
        list_of_state_already_visited = []
    n = len(auto.states)
    list_of_states_dag = []
    list_of_state_visited = []
    for state in auto.states:
        list_of_state_already_visited += \
            depth_first_search_with_marked_states(auto, state, copy(list_of_state_already_visited))[1]
        if len(list_of_state_already_visited) == n:
            break
    list_of_state_already_visited.reverse()
    new_auto = inverse(auto)

    i = 0
    while i < len(list_of_state_already_visited):
        new_set = \
            depth_first_search_with_marked_states(new_auto, list_of_state_already_visited[i],
                                                  copy(list_of_state_visited), [])[1]
        if len(new_set) == 0:
            list_of_states_dag += [((list_of_state_already_visited[i]), None)]
            i += 1
            continue
        elif len(new_set) == 1:
            list_of_states_dag += [((new_set[0]), None)]
        else:
            list_of_states_dag += [tuple(new_set)]
        list_of_state_visited += new_set
        i += len(new_set)

    return list_of_states_dag


def depth_first_search_with_marked_states(automate, initial_state_of_transition, already_visited, list_marked=None):
    """
    Make a depth first search without considering the transition possible to the states presents in List_market  .
    :param automate:
    :param initial_state_of_transition:
    :param already_visited:
    :param list_marked: set of states presents in automate.states
    :return:
    """
    if list_marked is None:
        list_marked = []
    if initial_state_of_transition in already_visited:
        return already_visited, list_marked
    already_visited += [initial_state_of_transition]
    if initial_state_of_transition not in automate.transitions:
        if initial_state_of_transition not in list_marked:
            list_marked += [initial_state_of_transition]
        return already_visited, list_marked
    else:
        for character_of_transition in automate.transitions[initial_state_of_transition]:
            for final_state_of_transition in automate.transitions[initial_state_of_transition][character_of_transition]:
                if final_state_of_transition not in already_visited:
                    if final_state_of_transition not in list_marked:
                        already_visited, list_marked = depth_first_search_with_marked_states(automate,
                                                                                             final_state_of_transition,
                                                                                             already_visited,
                                                                                             list_marked)
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


def create_dag_of_strongly_connected_component(automaton, list_of_set_of_state):
    """
    This function aim to creates a directed graph from an graph, where each states are a strongly connected component
    of the original automaton.
    :param automaton: The original automaton
    :param list_of_set_of_state: The set of tuple, where each tuple represents all the states of a strongly connected
    component
    :return: an automaton
    """
    only1 = False
    only2 = False
    new_initial_state = None
    new_final_state = set()
    new_transition = dict()
    list_of_state = set()
    for set1 in list_of_set_of_state:
        if set1[1] is None:
            list_of_state.add(set1[0])
        elif len(list_of_set_of_state) == 1:
            list_of_state.add((list_of_set_of_state[0]))
            break
        else:
            list_of_state.add(set1)

    for set_of_state in list_of_set_of_state:
        if automaton.initial_states in set_of_state:
            new_initial_state = set_of_state[0]
    for set_of_state in list_of_set_of_state:
        if set_of_state[1] == None:
            if set_of_state in automaton.final_states:
                new_final_state.add(set_of_state[0])
        for state in set_of_state:
            if state in automaton.final_states:
                new_final_state.add(set_of_state)
                break
    for set_of_state in list_of_set_of_state:
        if set_of_state[1] == None:
            only1 = True
        for other_set_of_state in list_of_set_of_state:
            if other_set_of_state[1] == None:
                only2 = True
            if not only1:
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
                                    if only2:
                                        new_transition[set_of_state][character_of_transition].add(other_set_of_state[0])
                                        only2 = False


                                    else:
                                        new_transition[set_of_state][character_of_transition].add(
                                            other_set_of_state)

                only1 = False
            else:

                initial_state_of_transition = set_of_state[0]
                if initial_state_of_transition in automaton.transitions:

                    for character_of_transition in automaton.transitions[initial_state_of_transition]:

                        for final_state_of_transition in \
                                automaton.transitions[initial_state_of_transition][character_of_transition]:

                            if only2:

                                if final_state_of_transition == other_set_of_state[0]:
                                    if initial_state_of_transition not in new_transition:
                                        new_transition[initial_state_of_transition] = dict()
                                    if character_of_transition not in new_transition[initial_state_of_transition]:
                                        new_transition[initial_state_of_transition][character_of_transition] = set()
                                    new_transition[initial_state_of_transition][character_of_transition].add(
                                        other_set_of_state[0])
                                    only2 = False
                            else:
                                if final_state_of_transition in other_set_of_state:
                                    if initial_state_of_transition not in new_transition:
                                        new_transition[initial_state_of_transition] = dict()
                                    if character_of_transition not in new_transition[initial_state_of_transition]:
                                        new_transition[initial_state_of_transition][character_of_transition] = set()
                                    new_transition[initial_state_of_transition][character_of_transition].add(
                                        other_set_of_state)

        only1 = False
    return nfa_with_multiple_initial_states(initial_states=new_initial_state,
                                            final_states=new_final_state,
                                            transitions=new_transition,
                                            input_symbols=automaton.input_symbols,
                                            states=list_of_state
                                            )

def find_born_of_number(states,output_alphabet):
    max_distance = 0
    for i in output_alphabet:
        for j in output_alphabet:
            b =  abs(len(i) - len(j))
            if b > max_distance:
                max_distance = b
    return 2 * len(states)  * max_distance

def T1_criteria(square_transducer, dag_state):
    born = find_born_of_number(square_transducer.states,square_transducer.output_symbols)
    if len(dag_state) == 1:
        list_to_update1 = set()
        list_to_explore1 = set()
        tuple_to_use = dag_state.pop()
        dag_state.add(tuple_to_use)
        first_element = tuple_to_use[0]
        list_to_update1.add((first_element, 0))
        if first_element in square_transducer.transitions:
            for character_to_change in square_transducer.transitions[first_element]:
                for character_changed in square_transducer.transitions[first_element][character_to_change]:
                    if (character_changed[0] != '') and (character_changed[1] != ''):
                        for final_state_of_transition in square_transducer.transitions[first_element][character_to_change][
                            character_changed]:
                            new_element = (final_state_of_transition, len(character_changed[0]) - len(character_changed[1]))
                            if new_element[0] == first_element:
                                if new_element[1] != 0:
                                    return False
                            if abs(new_element[1]) <= born:
                                list_to_explore1.add(new_element)
                            else:
                                return False
        list_to_update2 = copy(list_to_update1)
        list_to_explore2 = copy(list_to_explore1)
        list_to_explore1, list_to_update1 = add_to_list(square_transducer,first_element, born, list_to_explore1, list_to_update1)
        if list_to_explore1 == False:
            return False
        while list_to_update1 != list_to_update2:
            list_to_explore1, list_to_update1 = add_to_list(square_transducer,first_element, born, list_to_explore1, list_to_update1)
            if list_to_explore1 == False:
                return False
            list_to_explore2, list_to_update2 = add_to_list(square_transducer,first_element, born, list_to_explore2, list_to_update2)
        return True
    else:
        for element in dag_state:
            list_to_update1 = set()
            list_to_explore1 = set()
            first_element = element[0]
            list_to_update1.add((first_element, 0))
            if first_element in square_transducer.transitions:
                for character_to_change in square_transducer.transitions[first_element]:
                    for character_changed in square_transducer.transitions[first_element][character_to_change]:

                        if (character_changed[0] != '') and (character_changed[1] != ''):

                            for final_state_of_transition in \
                                    square_transducer.transitions[first_element][character_to_change][
                                        character_changed]:
                                new_element = (
                                    final_state_of_transition, len(character_changed[0]) - len(character_changed[1]))
                                if new_element[0] == first_element:
                                    if new_element[1] != 0:
                                        return False
                                if abs(new_element[1]) <= born:
                                    list_to_explore1.add(new_element)
                                else:
                                    return False

            list_to_update2 = copy(list_to_update1)
            list_to_explore2 = copy(list_to_explore1)
            list_to_explore1, list_to_update1 = add_to_list(square_transducer,first_element, born,list_to_explore1, list_to_update1)
            if list_to_explore1 == False:
                return False
            while list_to_update1 != list_to_update2:
                list_to_explore1, list_to_update1 = add_to_list(square_transducer,first_element, born, list_to_explore1, list_to_update1)
                if list_to_explore1 == False:
                    return False
                list_to_explore2, list_to_update2 = add_to_list(square_transducer,first_element, born, list_to_explore2, list_to_update2)
        return True


def add_to_list(square_transducer, elem,born,list_to_explore, list_to_update):
    new_list_to_explore = set()
    for element_to_explore in list_to_explore:
        if element_to_explore[0] in square_transducer.transitions:
            for character_to_changed in square_transducer.transitions[element_to_explore[0]]:
                    for character_changed in square_transducer.transitions[element_to_explore[0]][character_to_changed]:
                        if (character_changed[0] != '') and (character_changed[1] != ''):
                            for final_state_of_transition in \
                                    square_transducer.transitions[element_to_explore[0]][character_to_changed][
                                        character_changed]:
                                new_element = (final_state_of_transition,
                                               element_to_explore[1] + len(character_changed[0]) - len(character_changed[1]))
                                if new_element[0] == elem:
                                    if new_element[1] != 0:
                                        return False,False
                                if abs(new_element[1]) <= born:
                                    new_list_to_explore.add(new_element)
                                    list_to_update.add(element_to_explore)
                                else:
                                    return False,False

    return new_list_to_explore, list_to_update


def mark_state(square_transducer):
    """
    Give all the states that are mark for the use of the first algorithm of subsequentiallity
    :param square_transducer:
    :return:
    """
    automaton = from_transducer_to_multiple_initial_nfa(square_transducer)
    dag = create_dag_of_strongly_connected_component(automaton, find_marked_states_for_dag(automaton))
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
                                        marked_state = marked_state.union(set(state))
                                        already_marked.add(state)
                                        set_of_co_accessible = ascend_edges(dag, state)
                                        for state_co_accessible in set_of_co_accessible:
                                            marked_state = marked_state.union(set(state_co_accessible))
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


def creat_random_transducer2(number_of_state_max, density_transition, number_of_final_state, input_symbols,
                             output_symbols, want_epsilon_transition):
    """
    Given a number of state maximum NM, a density of transition,a number of final state,
    an alphabet of input and output.
    Return a transducer that have at most NM states. The function calcul the number of transition of the complets NM
    states transducer and takes randomly density_transition * NM transitions from it to creat the random transducer.
    between 0 and 1 and if that number is lower than the density of transition the given transition is saved for the
    transducer created.
    :param number_of_state_max: Type - int
    :param density_transition: Number between 0 and 1 the precision of the roll is 0.01.Type - float
    :param number_of_final_state: number of final states.
    :param input_symbols: Type - set of char
    :param output_symbols: Type - set of char
    :param want_epsilon_transition: Determine wether or not there is a u ---(char1,'')--> v transition in the transducer
                                    created.  Type-bool
    :return: Type - transducer
    """
    out = copy(output_symbols)
    if want_epsilon_transition == True:
        out.add('')
    number_of_transition = int(
        number_of_state_max * number_of_state_max * len(input_symbols) * len(out) * density_transition)
    list_of_all_transition = []
    for i in range(number_of_state_max):
        for d in input_symbols:
            for f in out:
                for g in range(number_of_state_max):
                    list_of_all_transition += [(i, d, f, g)]
    states = set()
    transition = dict()
    final_states = set()
    for i in range(number_of_transition):
        rand = randint(0, len(list_of_all_transition) - 1)
        current_item = list_of_all_transition[rand]
        list_of_all_transition.remove(current_item)
        if ('q' + str(current_item[0])) not in transition:
            transition['q' + str(current_item[0])] = dict()
        if current_item[1] not in transition['q' + str(current_item[0])]:
            transition['q' + str(current_item[0])][current_item[1]] = dict()
        if current_item[2] not in transition['q' + str(current_item[0])][current_item[1]]:
            transition['q' + str(current_item[0])][current_item[1]][current_item[2]] = set()
        transition['q' + str(current_item[0])][current_item[1]][current_item[2]].add('q' + str(current_item[3]))
        states.add('q' + str(current_item[0]))
        states.add('q' + str(current_item[3]))
        c = len(final_states)
        if c < number_of_final_state:

            rand_final_state = randint(0, 1)
            if rand_final_state == 0:
                final_states.add('q' + str(current_item[0]))

        if c < number_of_final_state:

            rand_final_state = randint(0, 1)
            if rand_final_state == 0:
                final_states.add('q' + str(current_item[3]))
    if number_of_final_state < len(states):
        while len(final_states) <= number_of_final_state:
            fs = states.pop()
            final_states.add(fs)
        states = states.union(final_states)
    else:
        final_states = copy(states)

    initial_state = states.pop()
    states.add(initial_state)
    if want_epsilon_transition:
        out.remove('')
    return transducer(initial_states=initial_state,
                      final_states=final_states,
                      input_symbols=input_symbols,
                      transitions=transition,
                      output_symbols=out,
                      states=states)


def Phi(string_element_1, string_element_2):
    len_str1 = len(string_element_1)
    len_str2 = len(string_element_2)
    if len_str1 <= len_str2:
        if string_element_1 == string_element_2[:len_str1]:
            return '', string_element_2[len_str1:]
        else:
            return 0
    else:
        if string_element_2 == string_element_1[:len_str2]:
            return string_element_1[len_str2:], ''
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
                        for final_state_of_transition in \
                                transitions[initial_state_of_transition][character_of_transition]:
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
                        if character_changed not in \
                                new_transition_of_initial_state[new_state][character_of_transition].keys():
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
                                        if character_changed2 in \
                                                nfa_multiple.transitions[initial_state_of_transition1][
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
        """
        Modify the current transducer to give the trim part of himself
        """
        nfa_from_transducer = from_transducer_to_multiple_initial_nfa(self)
        nfa_from_transducer = sub_automaton(nfa_from_transducer, states_set_of_trim_nfa(nfa_from_transducer))
        self.compare_nfa_and_transducer(nfa_from_transducer)

    def is_sequential(self, step_by_step_print=False):
        """
        Find if there exist an equivalent transducer that is deterministic.
        :return:Type - bool
        """

        self.trim()
        max_value = 2  * len(self.states) **4 *len(self.input_symbols) * len(self.output_symbols)
        current_value = 0
        square_transducer = square_transducer_product(self, self)
        if step_by_step_print:
            print("square transducer done")
        automaton = from_transducer_to_multiple_initial_nfa(square_transducer)
        set_of_marked_state = mark_state(square_transducer)
        set_of_marked_state = set_of_marked_state.union(square_transducer.final_states)
        set_of_co_accessible_state_from_circle = states_set_of_co_accessible_nfa(automaton, set_of_marked_state)
        automaton = sub_automaton(automaton, set_of_co_accessible_state_from_circle)
        if step_by_step_print:
            print("finding all cycle done")
        if automaton.transitions == {}:

            if automaton.initial_states in automaton.final_states:
                return True
            else:
                return False
        square_transducer.compare_nfa_and_transducer(automaton)
        if square_transducer.final_states == set():
            return True

        T1 = dict()
        for states in square_transducer.states:
            T1[states] = ''
        passed = set()
        value_W_prime = {(square_transducer.initial_states, ('', ''))}
        T2 = copy(T1)
        while value_W_prime != set():
            if step_by_step_print:
                current_value += 1
                print("current_percentage of progresse",100*(current_value/max_value))
            state_h_prime = value_W_prime.pop()
            if state_h_prime[0] in square_transducer.transitions:
                for character_of_transition in square_transducer.transitions[state_h_prime[0]]:
                    for character_changed in square_transducer.transitions[state_h_prime[0]][
                        character_of_transition]:
                        for final_state_of_transition in \
                                square_transducer.transitions[state_h_prime[0]][character_of_transition][
                                    character_changed]:
                            h_prime = wB(state_h_prime[1], character_changed)
                            if (final_state_of_transition, h_prime) not in passed:
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
                                for e in value_W_prime:
                                    for e2 in value_W_prime:
                                        if e != e2:
                                            if e[0] == e2[0]:
                                                if e[1][0] == e2[1][0]:
                                                    if e[1][1] != e2[1][1]:
                                                        return False
                                                elif e[1][1] == e2[1][1]:
                                                    if e[1][0] != e2[1][0]:
                                                        return False

            passed.add(state_h_prime)
        return True

    #################### Work in progress #####################
    def is_sequentiel_webber(self):
        self.trim()
        square_transducer = square_transducer_product(self, self)

    ###########################################################
    def is_function(self, as_been_visited=None):
        """
        Find if the transducer is sequential or not.
        :param as_been_visited: Set to None.
        :return: Type - bool
        """
        if as_been_visited is None:
            as_been_visited = set()
        square_transducer = square_transducer_product(self, self)
        automaton = from_transducer_to_multiple_initial_nfa(square_transducer)
        automaton = sub_automaton(automaton, states_set_of_trim_nfa(automaton))
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
                                    for final_state in square_transducer.final_states:
                                        if final_state in dictionary_of_value:
                                            if dictionary_of_value[final_state] != ('', ''):
                                                return False
                                elif final_state_of_transition in as_been_visited:
                                    if dictionary_of_value[final_state_of_transition] != wB(
                                            dictionary_of_value[initial_state_of_transition], character_changed):
                                        return False
                                    for final_state in square_transducer.final_states:
                                        if final_state in dictionary_of_value:
                                            if dictionary_of_value[final_state] != ('', ''):
                                                return False
        return True

"""
transduce = transducer(
    states={'q2', 'q3', 'q0'},
    input_symbols={'c'},
    initial_states='q2',
    output_symbols={'aa','b'},
    final_states={'q0'},
    transitions={'q2': {'c': {'aa': {'q3'}}}, 'q3': {'c': {'aa': {'q2', 'q0'}, 'b': {'q2', 'q0'}}}}
)
a = square_transducer_product(transduce, transduce)
a.trim()
d = from_transducer_to_multiple_initial_nfa(a)
o = transduce.is_sequential()
p = find_marked_states_for_dag(d)
b = create_dag_of_strongly_connected_component(d, p)
g = b.states
l = T1_criteria(a,g)




TT = 0
TF = 0
count_error = 0
for d in range(12,13):
    c = d/100
    for i in range(10000):
        print(i)
        transduce = creat_random_transducer2(8,0.3,1,{'c'},{'aa','b'},want_epsilon_transition=False)
        transduce.trim()
        a = square_transducer_product(transduce,transduce)
        d = from_transducer_to_multiple_initial_nfa(a)
        o = transduce.is_sequential()
        p = find_marked_states_for_dag(d)
        b = create_dag_of_strongly_connected_component(d,p)
        g = b.states
        if not T1_criteria(a,g):
            if o:
                count_error += 1
                print(transduce.states)
                print(transduce.final_states)
                print(transduce.transitions)
                print(a.transitions)
                print(transduce.initial_states)
            TF += 1
        else:
            TT += 1

"""