from automata.fa.nfa import NFA
from copy import copy
from random import randint
from time import time
import sys

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
        new_transitions[state] = dict()
        for char in transducer_to_use.transitions[state]:
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

def find_marked_states(auto, list_of_state_already_visited=None):
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
    print(list_of_state_already_visited)
    print(new_auto.transitions)
    set_mark = []
    i = 0
    while i < len(list_of_state_already_visited):
        new_set = \
            depth_first_search_with_marked_states(new_auto, list_of_state_already_visited[i], copy(list_of_state_visited),[])[1]
        print(new_set)
        if len(new_set) == 1 :
            list_of_states_dag += [((new_set[0]),None)]
        else:
            list_of_states_dag += [tuple(new_set)]
        list_of_state_visited += new_set
        print(list_of_states_dag)
        i += len(new_set)
        print(i)

    return list_of_states_dag


def depth_first_search_with_marked_states(automate, initial_state_of_transition, already_visited, list_marked=None):
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
    only1 = False
    only2 = False
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
                if set_of_state[1] == None:
                    only1 = True
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
                                            break

                                        else:
                                            new_transition[set_of_state][character_of_transition].add(
                                                other_set_of_state)
                                            only2 = False
                                            break
                    only1 = False
                else:
                    initial_state_of_transition = set_of_state[0]
                    if initial_state_of_transition in automaton.transitions:
                        for character_of_transition in automaton.transitions[initial_state_of_transition]:
                            for final_state_of_transition in automaton.transitions[initial_state_of_transition][
                                character_of_transition]:
                                if final_state_of_transition in other_set_of_state:
                                    if initial_state_of_transition not in new_transition:
                                        new_transition[initial_state_of_transition] = dict()
                                    if character_of_transition not in new_transition[initial_state_of_transition]:
                                        new_transition[initial_state_of_transition][character_of_transition] = set()
                                    if only2:
                                        new_transition[initial_state_of_transition][character_of_transition].add(other_set_of_state[0])
                                        only2 = False
                                        break
                                    else:
                                        new_transition[initial_state_of_transition][character_of_transition].add(
                                            other_set_of_state)
                                        only2 = False
                    only1 = False

    return nfa_with_multiple_initial_states(initial_states=new_initial_state,
                                            final_states=new_final_state,
                                            transitions=new_transition,
                                            input_symbols=automaton.input_symbols,
                                            states=list_of_set_of_state
                                            )
def depth_first_search2(transd, initial_state_of_transition, g1, g2,transi, set_of_connect, already_visited=None):


    if already_visited is None:
        already_visited = set()
    already_visited.add(initial_state_of_transition)
    if initial_state_of_transition not in transd.transitions:
        return already_visited,g1,g2,transi
    if initial_state_of_transition in transd.transitions:
        for character_of_transition in transd.transitions[initial_state_of_transition]:
            for character_changed in transd.transitions[initial_state_of_transition][character_of_transition]:
                for final_state_of_transition in transd.transitions[initial_state_of_transition][
                    character_of_transition][character_changed]:
                    g1.add((initial_state_of_transition, final_state_of_transition))
                    for i in g2:
                        if (i[1][0] == initial_state_of_transition[0]) and (
                                i[1][1] == initial_state_of_transition[1]):
                            g2.add(((initial_state_of_transition[0], initial_state_of_transition[1], i[1][2]),
                                    (final_state_of_transition[0], final_state_of_transition[1], i[1][2] +
                                     len(character_changed[0]) + len(character_changed[1]))))
                    if final_state_of_transition in set_of_connect:
                        if final_state_of_transition not in already_visited:
                            already_visited.add(final_state_of_transition)
                            already_visited,g1,g2,transi = depth_first_search2(transd, final_state_of_transition,g1,g2,transi,set_of_connect,already_visited)
                    else:
                        transi.add(final_state_of_transition)

    return already_visited,g1,g2,transi

def Truc1(square_transducer):
    g1 = set()
    g2 = set()
    automaton = from_transducer_to_multiple_initial_nfa(square_transducer)
    dag = creat_dag(automaton, find_marked_states(automaton))
    sub_set_to_explore = list(dag.states)
    for char in square_transducer.transitions[square_transducer.initial_states]:
        for truc_changed in square_transducer.transitions[square_transducer.initial_states][char]:
            for state in square_transducer.transitions[square_transducer.initial_states][char][truc_changed]:
                        g1.add((square_transducer.initial_states,state))
                        g2.add(((square_transducer.initial_states[0],square_transducer.initial_states[1],0),
                                (state[0],state[1],len(truc_changed[0]) - len(truc_changed[1]))))

    states = square_transducer.initial_states
    print(dag.transitions)
    set_states = dag.initial_states
    sub_set_to_explore.remove(set_states)
    transi = set()
    already, current_g1, current_g2, transi = depth_first_search2(square_transducer, states, set(), set(), transi,
                                                                  set_states)
    for i in current_g2:
        for d in current_g2:
            if i != d:
                if i[0] == d[0]:
                    if i[1] == d[1]:
                        if i[2] != d[2]:
                            return g1,g2,False

    g2 = g2.union(current_g2)
    g1 = g1.union(current_g1)

    while sub_set_to_explore != []:
        if transi != set():

            states = transi.pop()
        else:
            break
        for e in sub_set_to_explore:
            if states in e:
                set_states = e
                sub_set_to_explore.remove(set_states)
                break

        transi = transi.difference(set_states)

        already, current_g1, current_g2, transi1 = depth_first_search2(square_transducer, states, set(), set(), transi,
                                                                  set_states)
        transi = transi.union(transi1)
        for i in current_g2:
            for d in current_g2:
                if i != d:
                    if i[0] == d[0]:
                        if i[1] == d[1]:
                            if i[2] != d[2]:
                                return g1,g2,False
        g2 = g2.union(current_g2)
        g1 = g1.union(current_g1)
    return g2,True
def mark_state(square_transducer):

    automaton = from_transducer_to_multiple_initial_nfa(square_transducer)
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

def creat_random_transducer(number_of_state_max, density_transition,number_of_final_state, input_symbols, output_symbols,
                            want_epsilon_transition=None):
    """
    Given a number of state maximum NM, a density of transition, an alphabet of input and output return a transducer
    that have at most NM states. For every transition that exist in the complete transducer, we roll a random number
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
    if want_epsilon_transition == True:
        output_symbols.remove('')
    return transducer(
        states=true_set_of_state,
        input_symbols=input_symbols,
        output_symbols=output_symbols,
        initial_states=initial_state,
        final_states=final_states,
        transitions=transition,
    )

def creat_random_transducer2(number_of_state_max, density_transition, number_of_final_state,input_symbols, output_symbols,want_epsilon_transition):
    out = copy(output_symbols)
    if want_epsilon_transition == True:
        out.add('')
    number_of_transition = int(number_of_state_max*number_of_state_max*len(input_symbols)*len(output_symbols)*density_transition)
    list_of_all_transition = []
    for i in range(number_of_state_max):
        for d in input_symbols:
            for f in output_symbols:
                for g in range(number_of_state_max):
                    list_of_all_transition += [(i,d,f,g)]
    states = set()
    transition = dict()
    final_states = set()
    for i in range(number_of_transition):
        rand = randint(0,len(list_of_all_transition)-1)
        current_item = list_of_all_transition[rand]
        list_of_all_transition.remove(current_item)
        if ('q' + str(current_item[0])) not in transition:
            transition['q' + str(current_item[0])] = dict()
        if current_item[1] not in transition['q' + str(current_item[0])]:
            transition['q' + str(current_item[0])][current_item[1]] = dict()
        if current_item[2] not in transition['q' + str(current_item[0])][current_item[1]]:
            transition['q' + str(current_item[0])][current_item[1]][current_item[2]] = set()
        transition['q' + str(current_item[0])][current_item[1]][current_item[2]].add('q' +str(current_item[3]))
        states.add('q' + str(current_item[0]))
        states.add('q' + str(current_item[3]))
        if len(final_states) != number_of_final_state:
            rand_final_state = randint(0,1)
            if rand_final_state == 0:
                final_states.add('q' + str(current_item[0]))
        if len(final_states) != number_of_final_state:
            rand_final_state = randint(0,1)
            if rand_final_state == 0:
                final_states.add('q' + str(current_item[3]))
    while len(final_states) != number_of_final_state:
        fs = states.pop()
        final_states.add(fs)

    states = states.union(final_states)
    initial_state = states.pop()
    states.add(initial_state)
    if want_epsilon_transition == True:
        out.remove('')
    return transducer(initial_states = initial_state,
                       final_states = final_states,
                       input_symbols = input_symbols,
                       transitions = transition,
                       output_symbols = out,
                       states = states)
def reverse(string_element):
    """
    Given a string, return it miror form.
    'ACDB' return 'BDCA'
    :param string_element: Type - str
    :return: Type - str
    """
    str2 = ''
    for i in range(len(string_element) - 1, -1, -1):
        str2 += string_element[i]
    return str2


def remove(string_element_1, string_element_2):
    """
    Given two string S1 and S2 return the concatenate form S1S2 without the identical characters
    S1 = "ABAA"
    S2 = "AACA"
    remobe(S1,S2) = "ABCA"
    :param string_element_1:Type - str
    :param string_element_2:Type - str
    :return:Type - str
    """
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





###############################################
def delay(list_tuple_str1,list_tuple_str2):
    new_list_str = []
    for e in list_tuple_str1:
         new_list_str += [(e[0],e[1] * -1)]
    for e in list_tuple_str2:
        new_list_str += [e]
    new_list = symplify_with_list_tuple(new_list_str)
    while new_list != new_list_str:
        new_list = symplify_with_list_tuple(new_list)
        new_list_str = symplify_with_list_tuple(new_list_str)

    return new_list_str
###############################################
def symplify_with_list_tuple(list_tuple_str):
    new_list = []
    i = 0
    while i <= len(list_tuple_str)-1:
        if i == len(list_tuple_str)-1:
            new_list += [list_tuple_str[i]]
            return new_list
        elif list_tuple_str[i][0] != list_tuple_str[i+1][0]:
            new_list += [list_tuple_str[i]]
            i += 1
        else:
            if list_tuple_str[i][1] == list_tuple_str[i+1][1]:
                new_list += [list_tuple_str[i]]
                i += 1
            else:
                i += 2
    return new_list






def str_element(list_str):
    str_to_use = ''
    for e in list_str:
        str_to_use += e[0]
    return str_to_use



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
        """
        Modify the current transducer to give the trim part of himself
        """
        nfa_from_transducer = from_transducer_to_multiple_initial_nfa(self)
        nfa_from_transducer = sub_automaton(nfa_from_transducer, states_set_of_trim_nfa(nfa_from_transducer))
        self.compare_nfa_and_transducer(nfa_from_transducer)
    def is_sequential(self):
        """
        Find if there exist an equivalent transducer that is deterministic.
        :return:Type - bool
        """
        self.trim()

        square_transducer = square_transducer_product(self, self)
        automaton = from_transducer_to_multiple_initial_nfa(square_transducer)
        a = time()
        set_of_marked_state = mark_state(square_transducer)
        a = time()
        set_of_co_accessible_state_from_circle = states_set_of_co_accessible_nfa(automaton, set_of_marked_state)
        automaton = sub_automaton(automaton, set_of_co_accessible_state_from_circle)

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
    #################### Work in progress #####################
    def is_sequentiel_webber(self):
        self.trim()
        square_transducer = square_transducer_product(self,self)

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
        automaton =  sub_automaton(automaton, states_set_of_trim_nfa(automaton))
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
                                        if dictionary_of_value[final_state] != ('', ''):
                                            return False
                                elif final_state_of_transition in as_been_visited:
                                    if dictionary_of_value[final_state_of_transition] != wB(
                                            dictionary_of_value[initial_state_of_transition], character_changed):
                                        return False
                                    for final_state in square_transducer.final_states:
                                        if dictionary_of_value[final_state] != ('', ''):
                                            return False
        return True








transduce = transducer(
    states={'q0', 'q1'},
    input_symbols={'a'},
    initial_states='q1',
    output_symbols={'', 'b'},
    final_states={'q0'},
    transitions={'q1': {'b': {'': {'q1'},'b':{'q0'}}},
                 'q0': {'b':{'': {'q0'}}},
                 })

a = square_transducer_product(transduce,transduce)
print(a.initial_states)
print(Truc1(a))