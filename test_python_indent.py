#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2013 Bruno Perriot <bperriot@gmail.com>
# This file is released under the terms of the MIT license.

"""Test for python_indent.py using py.test library.
"""

import pytest
from mock import patch, Mock

import python_indent
from python_indent import get_new_line_indent
from python_indent import line_filter
from python_indent import PythonDeindenter


class FakeRegion(object):
    """Mock for sublime.Region."""
    def __init__(self, begin, end):
        self._begin = int(begin)
        self._end = int(end)

    def begin(self):
        return self._begin

    def end(self):
        return self._end

    def empty(self):
        return self._begin == self._end

    def __getitem__(self, i):
        if i is 0:
            return self._begin
        elif i is 1:
            return self._end
        else:
            raise IndexError

    def __str__(self):
        return "FakeRegion(%d,%d)" % (self._begin, self._end)


class FakeView(str):
    """Mock for sublime.View."""
    def __init__(self, string, sel=None, tab_size=4):
        self.tab_size = tab_size
        self.string = string
        self.lines = string.split('\n')
        self.line_marks = [0]
        cursor = 0
        for l in self.lines:
            cursor += len(l) + 1
            self.line_marks.append(cursor)
        if sel:
            self.sel_ = [FakeRegion(s[0], s[1]) for s in sel]
        else:
            self.sel_ = [FakeRegion(len(string), len(string))]

        self.commands = [(None, None, 1)]

    def settings(self):
        return {'tab_size': self.tab_size}

    def line(self, sel):
        if not isinstance(sel, FakeRegion):
            sel = FakeRegion(sel, sel)

        for mark in self.line_marks:
            if sel[0] >= mark:
                line_start = mark
            if sel[1] < mark:
                line_stop = mark
                break
        return FakeRegion(line_start, line_stop)


    def substr(self, line):
        if isinstance(line, FakeRegion):
            return self.string[line.begin():line.end()].strip('\n')
        else:
            return self.string[line[0]:line[1]].strip('\n')

    def sel(self):
        return self.sel_

    def command_history(self, i, b):
        return self.commands

    def begin_edit(self):
        pass

    def end_edit(self, edit):
        pass

    def replace(self, edit, region, new_str):
        pass


def test_deindent_right_indent():
    tests_blocks = [
("""if True:
    a = 3
    else:""", 0),
("""    if True:
        a = 0
        else:""", 4),
("""    if True:
        a = 0
    else:""", 4),
    ]

    for block, indent in tests_blocks:
        view = FakeView(block)
        view.commands = ["insert", {"characters": block[-1]}, 1]

        #deindenter = PythonDeindenter()
        #mock = Mock()
        #deindenter.change_indent = mock
    
        #with patch('__main__.python_indent.change_indent') as mock:
        with patch.object(PythonDeindenter, 'change_indent', return_value=None) as mock:
            deindenter = PythonDeindenter()
            deindenter.on_modified(view)

        mock.assert_called_once_with(block.split('\n')[-1], indent)


def test_deindent_right_align():
    """Test that the new line is aligned to the right start block line."""
    tests_blocks = [
("""    if True:
        a = 8
        else:""", 4),
("""    if True:
        a = 8
    elif True:
        a = 4
        else:""", 4),
("""    if True:
        a = 8
        elif """, 4),
("""    if True:
        a = 8
    elif True:
        a = 4
        elif """, 4),
("""    if True:
        if True:
            a = 8
        else:
            a = 4
            else:""", 4),
("""    if True:
        if True:
            a = 8
        elif:
            a = 4
            else:""", 8),
("""    if True:
        if True:
            a = 8
        elif:
            a = 4
    else:""", 4),

("""    try:
        a = 8
        except:""", 4),
("""    try:
        a = 8
        except """, 4),
("""    try:
        a = 8
    except:
        a = 4
        except:""", 4),
("""    try:
        a = 8
        finally:""", 4),
("""    try:
        a = 8
    except:
        a = 4
        finally:""", 4),
("""    try:
        a = 8
    except:
        a = 4
        else:""", 4),
("""    try:
        a = 8
    except:
        a = 4
    else:
        a = 2
        finally:""", 4),
("""    try:
        a = 8
    except:
        a = 4
    else:
        if True:
            a = 2
        else:
            a = 0
            finally:""", 4),
("""    if True:
        a = 8
        try:
            a = 2
        finally:
            a = 0
            else:""", 4),

    ]


    for block, indent in tests_blocks:
        view = FakeView(block)
        view.commands = ["insert", {"characters": block[-1]}, 1]

        with patch.object(PythonDeindenter, 'change_indent', return_value=None) as mock:
            PythonDeindenter().on_modified(view)

        mock.assert_called_once_with(block.split('\n')[-1], indent)


def test_deindent_start_block_pattern():
    """Line starting like a keyword should not be used for alignement."""
    tests_blocks = [
("""if_true()
    a = 4
    else:""", 4),
("""except_one()
    a = 4
    finally:""", 4),
("""try_this()
    a = 4
    finally:""", 4),
    ]

    for block, indent in tests_blocks:
        view = FakeView(block)
        view.commands = ["insert", {"characters": block[-1]}, 1]

        with patch.object(PythonDeindenter, 'change_indent', return_value=None) as mock:
            PythonDeindenter().on_modified(view)

        assert not mock.called


def test_deindent_wrong_command():
    """Deindent should not trigger on other commands that 'insert'."""
    tests_blocks = [
("""if True:
    a = 4
    else:""", 4)]

    for block, indent in tests_blocks:
        view = FakeView(block)
        view.commands = ["replace", {"characters": block[-1]}, 1]

        with patch.object(PythonDeindenter, 'change_indent', return_value=None) as mock:
            PythonDeindenter().on_modified(view)

        assert not mock.called

def test_deindent_no_matching_block():
    """Deindent should not trigger on other commands that 'insert'."""
    tests_blocks = [
("""    else:""", 4)]

    for block, indent in tests_blocks:
        view = FakeView(block)
        view.commands = ["insert", {"characters": block[-1]}, 1]

        with patch.object(PythonDeindenter, 'change_indent', return_value=None) as mock:
            PythonDeindenter().on_modified(view)

        assert not mock.called


def test_deindent_wrong_param():
    """Deindent should only trigger on ' ' or ':' insert."""
    tests_blocks = [
("""if True:
    a = 4
    else""", 0),
("""if True:
    a = 4
    else """, 0),
("""if True:
    a = 4
    else_do() """, 0),
("""try:
    a = 4
    finally""", 0),
("""try:
    a = 4
    finally """, 0),
("""try:
    a = 4
    finally_done() """, 0),
("""try:
    a = 4
    except""", 0),
("""try:
    a = 4
    except_this() """, 0),
("""if True:
    a = 4
    elif""", 0),
("""if True:
    a = 4
    elifthis() """, 0),
    ]

    for block, indent in tests_blocks:
        view = FakeView(block)
        view.commands = ["insert", {"characters": block[-1]}, 1]

        with patch.object(PythonDeindenter, 'change_indent', return_value=None) as mock:
            PythonDeindenter().on_modified(view)

        assert not mock.called


def test_new_line_indent():

    tests_blocks = [
        # basic indent
        ('    a = 5', 4),

        # new block
        ('def func():', 4),
        ('    def func():', 8),
        ('def f(a,\n      b):', 4),
        ('def f(a,\n      b,\n      c):', 4),
        ('for a in {"a":"a"}:', 4),

        # line continuation within brackets
        ('def func(a,', 9),
        ('def f(a, \n      b,', 6),
        ('alphabet = ("a", "b",', 12),
        ('alphabet = ["a", "b",', 12),
        ('alphabet = {"a":"a", "b":"b",', 12),
        ('for a in {"a":', 10),

        ('func((a,', 6),  # nested brackets
        ('func([a,', 6),
        ('func({a', 6),
        ('func({a:', 6),
        ('def func({a:', 10),
        ('numbers = ((1, "1"), ', 11),
        ('numbers = [[1, "1"], ', 11),
        ('numbers = ((1, "1"), (2,', 22),
        ('numbers = [[1, "1"], [2,', 22),
        ('numbers = [{1: "1"}, ', 11),
        ('numbers = [{1: "1"}, {2:', 22),

        ('func((1,\n      ),(2,', 9),  # () inverted on previous line
        ('func([1,\n      ],[2,', 9),
        ('func({1:1\n      },{2:2', 9),
        ('func({1:1\n      },{2:', 9),

        # line continuation just after a bracket
        ('a = (', 4),
        ('a = [', 4),
        ('a = {', 4),
        ('def func(', 8),
        ('    def func(', 12),
        ('numbers = ((1, "1"), (', 4),

        # closing bracket
        ('numbers = ((1, "1"), (2, "2"))', 0),
        ('numbers = [[1, "1"], [2, "2"]]', 0),
        ('numbers = [{1: "1"}, {2: "2"}]', 0),
        ('    a)', 0),
        ('    a]', 0),
        ('    a}', 0),
        ('    foo,  \n    bar)', 0),
        ('alphabet = ("a", \n            "b")', 0),
        ('alphabet = ["a", \n            "b"]', 0),
        ('alphabet = {"a":"a", \n            "b":"b"}', 0),

        # bracket in string
        ('a = "("', 0),

        # comments
        ('a = 3 # comment', 0),
        ('    a = 3 # comment', 4),
        ('a = 3 # comment (', 0),
        ('    a = 3 # comment (', 4),
        ('    a = 3 # comment )', 4),
        ('    a = 3 # comment ())', 4),

        # end of block
        ('        pass', 4),
        ('        pass eie', 8),
        ('        return', 4),
        ('        return 3', 4),
        ('        return (a,\n                b)', 4),
        ('        continue', 4),
        ('        break', 4),
        ('        raise', 4),
        ('        raise Exception', 4),

        # possible confusion with end of block
        ('        return (', 12),
        ('        return (a,', 16),
        ('        continue ae', 8),
        ('        break ae', 8),

        # blank line
        ('    a = 4\n', 0),
        ('    a = 4\n    ', 4),
        ('    a = 4\n    \n', 0),
        ('    a = 4\n    \n    ', 4),

        # unreasonable indent for line continuation (already too much indented)
        # line continuation by backslash
    ]

    for block, indent in tests_blocks:
        view = FakeView(block)
        cursor = len(block)
        assert get_new_line_indent(view, cursor) == indent


def test_line_filter():
    """Line_filter should remove comments and string."""
    filter_line_test = [
        ('func("a")', 'func("a")'),
        ('func("a"', 'func("a"'),
        ('func("("', 'func("_"'),
        ('func(")"', 'func("_"'),
        ('func("["', 'func("_"'),
        ('func("]"', 'func("_"'),
        ('func("{"', 'func("_"'),
        ('func("}"', 'func("_"'),
        ('func("(a)"', 'func("_a_"'),
        ("func('(a)', ')'", "func('_a_', '_'"),
        ("func('('", "func('_'"),
        ("func('(a)', ')'", "func('_a_', '_'"),
        (""" "('(')" """, """ "_'_'_" """),
        (""" "(")"(" """, """ "_")"_" """),
        (""" "(")'(' """, """ "_")'_' """),
        ("""  "(')",("(",'(a)' """, """  "_'_",("_",'_a_' """),
        (r'"(\")"', r'"_\"_"'),
        (r'"(\\")', r'"_\\")'),
        (r'"(\\\")"', r'"_\\\"_"'),
        (r'"(\\\\")', r'"_\\\\")'),
        (r'"(\\\\\")', r'"_\\\\\")'),  # limit of the escape-escaping
        (r'"\"("', r'"\"_"'),
        (r'"\\"("', r'"\\"("'),
        ("some line  # with comments", "some line  "),
        ("some line  # with # comments", "some line  "),
        ("some line  #", "some line  "),
        ("some line '#' with no comment", "some line '_' with no comment"),
        ("#", ""),
        ("# some comment", "")

        # triple quote
        # mixed quote
    ]
    # test line filter
    for input, output in filter_line_test:
        assert line_filter(input) == output


