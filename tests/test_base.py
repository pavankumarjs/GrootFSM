from unittest import TestCase

import logging

import sys

from mock import Mock

from fsm.base import FSMBuilder, FSMException


def setUpModule():
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

def tearDownModule():
    pass

class TestFSM(TestCase):

    def setUp(self):
        self.builder = FSMBuilder()

    def tearDown(self):
        pass

    def test_fsm_builder_with_random_names(self):
        before_exit1, after_entry1 = Mock(), Mock()
        state1 = self.builder.add_state( before_exit=before_exit1, after_entry=after_entry1)
        before_exit2, after_entry2 = Mock(), Mock()
        state2 = self.builder.add_state(before_exit=before_exit2, after_entry=after_entry2)
        before_exit3, after_entry3 = Mock(), Mock()
        state3 = self.builder.add_state(before_exit=before_exit3, after_entry=after_entry3)

        on_transition11, on_transition12, on_transition23, on_transition31 = Mock(), Mock(), Mock(), Mock()
        transition11 = self.builder.add_transition(state1.name, state1.name, on_transition=on_transition11)
        transition12 = self.builder.add_transition(state1.name, state2.name, on_transition=on_transition12)
        transition23 = self.builder.add_transition(state2.name, state3.name, on_transition=on_transition23)
        transition31 = self.builder.add_transition(state3.name, state1.name, on_transition=on_transition31)
        self.builder.set_initial_state(state1.name)

        fsm = self.builder.build()

        self.assertEqual(before_exit1.call_count, 0)
        self.assertEqual(after_entry1.call_count, 0)
        self.assertEqual(on_transition11.call_count, 0)
        fsm.execute_transition_to(state1.name, test_arg=111)
        self.assertEqual(fsm.state, state1.name)
        self.assertEqual(before_exit1.call_count, 1)
        before_exit1.assert_called_with(test_arg=111)
        self.assertEqual(after_entry1.call_count, 1)
        after_entry1.assert_called_with(test_arg=111)
        self.assertEqual(on_transition11.call_count, 1)
        on_transition11.assert_called_with(test_arg=111)

        self.assertRaises(FSMException, fsm.execute_transition_to, state3.name)

        self.assertEqual(after_entry2.call_count, 0)
        self.assertEqual(on_transition12.call_count, 0)
        fsm.execute_transition_to(state2.name)
        self.assertEqual(fsm.state, state2.name)
        self.assertEqual(before_exit1.call_count, 2)
        self.assertEqual(after_entry2.call_count, 1)
        self.assertEqual(on_transition12.call_count, 1)

        self.assertRaises(FSMException, fsm.execute_transition, transition31.name, **{'test_arg':111})
        before_exit2.assert_not_called()
        on_transition31.assert_not_called()

        self.assertEqual(before_exit2.call_count, 0)
        self.assertEqual(after_entry3.call_count, 0)
        self.assertEqual(on_transition23.call_count, 0)
        fsm.execute_transition(transition23.name)
        self.assertEqual(fsm.state, state3.name)
        self.assertEqual(before_exit2.call_count, 1)
        self.assertEqual(after_entry3.call_count, 1)
        self.assertEqual(on_transition23.call_count, 1)

    def test_fsm_builder_with_names(self):
        before_exit1, after_entry1 = Mock(), Mock()
        state1 = self.builder.add_named_state('state1', before_exit=before_exit1, after_entry=after_entry1)
        before_exit2, after_entry2 = Mock(), Mock()
        state2 = self.builder.add_named_state('state2', before_exit=before_exit2, after_entry=after_entry2)
        before_exit3, after_entry3 = Mock(), Mock()
        state3 = self.builder.add_named_state('state3', before_exit=before_exit3, after_entry=after_entry3)

        on_transition11, on_transition12, on_transition23, on_transition31 = Mock(), Mock(), Mock(), Mock()
        transition11 = self.builder.add_named_transition('transition11', state1.name, state1.name, on_transition=on_transition11)
        transition12 = self.builder.add_named_transition('transition12', state1.name, state2.name, on_transition=on_transition12)
        transition23 = self.builder.add_named_transition('transition23', state2.name, state3.name, on_transition=on_transition23)
        transition31 = self.builder.add_named_transition('transition31', state3.name, state1.name, on_transition=on_transition31)
        self.builder.set_initial_state(state1.name)

        fsm = self.builder.build()

        self.assertEqual(before_exit1.call_count, 0)
        self.assertEqual(after_entry1.call_count, 0)
        self.assertEqual(on_transition11.call_count, 0)
        fsm.execute_transition_to('state1', test_arg=111)
        self.assertEqual(fsm.state, 'state1')
        self.assertEqual(before_exit1.call_count, 1)
        self.assertEqual(after_entry1.call_count, 1)
        self.assertEqual(on_transition11.call_count, 1)

        self.assertRaises(FSMException, fsm.execute_transition_to, 'state3')

        self.assertEqual(after_entry2.call_count, 0)
        self.assertEqual(on_transition12.call_count, 0)
        fsm.execute_transition_to('state2')
        self.assertEqual(fsm.state, 'state2')
        self.assertEqual(before_exit1.call_count, 2)
        self.assertEqual(after_entry2.call_count, 1)
        self.assertEqual(on_transition12.call_count, 1)

        self.assertRaises(FSMException, fsm.execute_transition, 'transition31', **{'test_arg':111})
        before_exit2.assert_not_called()
        on_transition31.assert_not_called()

        self.assertEqual(before_exit2.call_count, 0)
        self.assertEqual(after_entry3.call_count, 0)
        self.assertEqual(on_transition23.call_count, 0)
        fsm.execute_transition('transition23')
        self.assertEqual(fsm.state, 'state3')
        self.assertEqual(before_exit2.call_count, 1)
        self.assertEqual(after_entry3.call_count, 1)
        self.assertEqual(on_transition23.call_count, 1)

    def test_fsm_builder_error(self):
        before_exit1, after_entry1 = Mock(), Mock()
        state1 = self.builder.add_state(before_exit=before_exit1, after_entry=after_entry1)
        before_exit2, after_entry2 = Mock(), Mock()
        state2 = self.builder.add_state(before_exit=before_exit2, after_entry=after_entry2)

        on_transition12 = Mock()
        transition12 = self.builder.add_transition(state1.name, state2.name, on_transition=on_transition12)

        self.assertRaises(FSMException, self.builder.build)


    def test_fsm_builder_duplicate_transition_error(self):
        before_exit1, after_entry1 = Mock(), Mock()
        state1 = self.builder.add_state(before_exit=before_exit1, after_entry=after_entry1)
        before_exit2, after_entry2 = Mock(), Mock()
        state2 = self.builder.add_state(before_exit=before_exit2, after_entry=after_entry2)

        on_transition11, on_transition12 = Mock(), Mock()
        transition11 = self.builder.add_transition(state1.name, state1.name, on_transition=on_transition11)
        transition11_duplicate = self.builder.add_transition(state1.name, state1.name, on_transition=on_transition11)
        transition12 = self.builder.add_transition(state1.name, state2.name, on_transition=on_transition12)

        self.builder.set_initial_state(state1.name)
        self.assertRaises(FSMException, self.builder.build)

    def test_fsm_builder_duplicate_transition_name_error(self):
        before_exit1, after_entry1 = Mock(), Mock()
        state1 = self.builder.add_state(before_exit=before_exit1, after_entry=after_entry1)
        before_exit2, after_entry2 = Mock(), Mock()
        state2 = self.builder.add_state(before_exit=before_exit2, after_entry=after_entry2)

        on_transition11, on_transition12 = Mock(), Mock()
        transition11 = self.builder.add_named_transition('transition11', state1.name, state1.name, on_transition=on_transition11)
        transition11_duplicate = self.builder.add_named_transition('transition11', state1.name, state1.name, on_transition=on_transition11)
        transition12 = self.builder.add_transition(state1.name, state2.name, on_transition=on_transition12)

        self.builder.set_initial_state(state1.name)
        self.assertRaises(FSMException, self.builder.build)

    def test_fsm_builder_duplicate_state_error(self):
        before_exit1, after_entry1 = Mock(), Mock()
        state1 = self.builder.add_named_state('state1', before_exit=before_exit1, after_entry=after_entry1)
        state1_duplicate = self.builder.add_named_state('state1', before_exit=before_exit1, after_entry=after_entry1)
        before_exit2, after_entry2 = Mock(), Mock()
        state2 = self.builder.add_state(before_exit=before_exit2, after_entry=after_entry2)

        on_transition11, on_transition12 = Mock(), Mock()
        transition11 = self.builder.add_transition(state1.name, state1.name, on_transition=on_transition11)
        transition12 = self.builder.add_transition(state1.name, state2.name, on_transition=on_transition12)

        self.builder.set_initial_state(state1.name)
        self.assertRaises(FSMException, self.builder.build)
