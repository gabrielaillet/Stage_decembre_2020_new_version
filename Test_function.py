import unittest

from Main_project import transducer,creat_random_transducer2

class Test_is_function(unittest.TestCase):
    def setUp(self) -> None:
        self.empty = transducer(states= {'q1'},
                                input_symbols= set(),
                                output_symbols= set(),
                                final_states= set(),
                                initial_states='q1',
                                transitions = dict()
        )
        self.trivial = transducer(
                states={'q1','q2','q3'},
                input_symbols={'a','b'},
                output_symbols={'c','b'},
                final_states={'q3'},
                initial_states='q1',
                transitions= {'q0': {'b': {'b': {'q1'}}},
                              'q1': {'a':{'c': {'q3'}}}})



    def testEmpty_transducer(self):
        test = self.empty
        bool_expected = True
        bool_get = test.is_function()
        self.assertTrue(bool_expected == bool_get)


    def testTrivial_transducer(self):
        test = self.trivial
        bool_expected = True
        bool_get = test.is_function()
        self.assertTrue(bool_get == bool_expected)


    def testLot_of_non_functional(self):
        for i in range(100):
            print('Lot_of_non_functional',i)
            test = creat_random_transducer2(5,0.9,5,{'a','b'},{'a','b'},want_epsilon_transition=True)
            bool_expected = False
            bool_get = test.is_function()
            self.assertTrue(bool_expected == bool_get)
    def testwork_on_medium_transducer(self):
        test = creat_random_transducer2(10,0.5,2,{'a'},{'b','c'},want_epsilon_transition=True)
        print('creating_random_medium_transducer_is_done')
        test.is_sequential(True)
        self.assertTrue(1 == 1)
