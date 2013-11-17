#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2013 Bruno Perriot <bperriot@gmail.com>
# This file is released under the terms of the MIT license.

""" Python PEP8 indent

Sublime text plugin for automatic PEP8-style indent.

"""

import re
import traceback
from itertools import izip

try:
    import sublime
    import sublime_plugin
except ImportError:
    # hack for import outside of sublime_text, for testing purposes

    class FakeSublime(object):
        def Region(self, a, b):
            return tuple((a, b))
    sublime = FakeSublime()
    sublime_plugin = type('sublime_plugin', (), {'EventListener': object})
    sublime_plugin.TextCommand = object


# maximum number of previous lines to lookup
settings = sublime.load_settings('python_indent.sublime-settings')
MAX_LINE_LOOKUP_COUNT = settings.get("max_line_lookup_count", 1000)


## new line indent

reverse_enumerate = lambda l: izip(reversed(xrange(len(l))), reversed(l))


newblock_start_pattern = re.compile(
    r'^\s*(class|def|elif|else|except|finally|for|if|try|with|while)\b.*$')
escape_pattern = r'(?<!(%s\\))'
string_regex = re.compile(r"""(?P<quote>["'])(?P<str>.*?)(%s)(?P=quote)""" % (
    escape_pattern % escape_pattern % escape_pattern % escape_pattern % ''))
comment_regex = re.compile(r"([^#]*)(#(.*))?")
stopexecution_pattern = re.compile(
    r'^\s*(pass\b|return\b.*|continue\b|break\b|raise\b.*|yield\b.*)\s*$')
blankline_pattern = re.compile(r'^\s*$')


def _replace_reserved_char(s):
    """Return the given string with all its brackets and # replaced by _."""
    for c in '()[]{}#':
        s = s.replace(c, '_')
    return s


def _filter_quote(m):
    return ''.join((m.group('quote'),
                    _replace_reserved_char(m.group('str')),
                    m.group('quote')
                    ))


def line_filter(s):
    """Remove brackets from literal string in lines. Remove comments."""
    s = string_regex.sub(_filter_quote, s)
    s = comment_regex.search(s).group(1)
    return s


def get_line_current_indent(string, tab_size=4):
    """Return the index of the first non-blank character of the given string.

    If there is no non-blank characters, return the length of the string.

    argument
    --------
    tab_size: tabs are count as 'tab_size' spaces (default 4).

    """
    indent = 0
    for c in string:
        if c == ' ':
            indent += 1
        elif c == '\t':
            indent += tab_size
        else:
            break
    return indent


def unmatched_bracket_lookup(s, in_counter=None):
    """Look for an unmatched bracket ((), [] and {}) in the given string.

    Arguments
    ---------
    s: string to analyze
    in_counter: dict containing the count of brackets from a following line

    Return
    ------
    ('balanced', None) if there is no unbalanced bracket.
    ('unmatch_close', counter_dict) if the string contain an unmatched closing
        bracket. counter_dict is the dict containing the count of brackets
    ('unmatch_open', index) if the string contains an unmatched opening bracket
        index is the last unmatched opening bracket index (int)

    If there is both opening and closing unmatched brackets, the last one takes
    the priority.
    """
    matching = {')': '(', '}': '{', ']': '['}
    counter = {'(': 0, '{': 0, '[': 0}
    if in_counter:
        counter.update(in_counter)
    for i, c in reverse_enumerate(s):
        if c in '({[':
            if counter[c] is 0:
                return ('unmatch_open', i)
            else:
                counter[c] -= 1
        if c in ')}]':
            counter[matching[c]] += 1

    if counter.values() == [0, 0, 0]:
        return ('balanced', None)
    else:
        return ('unmatch_close', counter)


def string_to_next_line_indent(line, brackets_counter=None):
    """Return the indentation for a line following the given string

    If the given line is not enough to determine the indentation (unmatched
        closing brackets), can be call again, with the brackets_counter
        returned as argument.

    Argument
    --------
    line: current line (string).
    brackets_counter: dict containing a brackets count (as returned by the
        function).

    Return
    ------
    ('increase_level', i) if the indentation level should be increased. i is
        the number of level increase needed.
    ('decrease_level', i) if the indentation level should be decreased. i is
        the number of level decrease needed
    ('absolute', i) to indicate an absolute level of indentation. i is the
        number of spaces to insert before the line.
    ('unchanged', 0) if the indentation level should not be changed
    ('unmatched_closing_bracket', brackets_counter) if there is unmatched
        closing brackets. The function must be called again with the previous
        line.
    """
    status, param = unmatched_bracket_lookup(line, brackets_counter)
    if status == 'balanced':
        if newblock_start_pattern.match(line):
            return ('increase_level', 1)
        elif stopexecution_pattern.match(line):
            return ('decrease_level', 1)
        else:
            return ('unchanged', None)
    elif status == 'unmatch_open':
        if param is len(line)-1:
            if newblock_start_pattern.match(line):
                return ('increase_level', 2)
            else:
                return ('increase_level', 1)
        else:
            return ('absolute', param+1)
    elif status == 'unmatch_close':
        return 'unmatched_closing_bracket', param
    else:
        print "unexcepted return value from unmatched_bracket_lookup"


def get_new_line_indent(view, cursor):
    """Return the proper indentation of a new line inserted at the cursor.

    Arguments
    ---------
    view: sublime.View
    cursor: sublime text's cursor (int)

    Return
    ------
    Number of spaces to insert before a new line inserted at the cursor.

    """
    tab_size = view.settings().get('tab_size')

    start_line = view.line(cursor).begin()
    line = line_filter(view.substr(sublime.Region(start_line, cursor)))

    new_indent, indent_param = string_to_next_line_indent(line)

    line_lookup_count = MAX_LINE_LOOKUP_COUNT
    while new_indent == 'unmatched_closing_bracket' and line_lookup_count:
        line_lookup_count -= 1
        if start_line is 0 or not line_lookup_count:
            new_indent = 'error'
            indent_param = None
            break
        line = view.line(start_line-1)
        start_line = line.begin()
        line = line_filter(view.substr(line))
        if blankline_pattern.match(line):
            continue
        new_indent, indent_param = string_to_next_line_indent(
            line, indent_param)

    current_indent = get_line_current_indent(
        line, view.settings().get('tab_size'))

    if new_indent == 'absolute':
        return indent_param
    elif new_indent == 'unchanged':
        return current_indent
    elif new_indent == 'increase_level':
        return current_indent + tab_size * indent_param
    elif new_indent == 'decrease_level':
        return max(0, current_indent - tab_size * indent_param)
    else:
        return 0


class NewPythonLine(sublime_plugin.TextCommand):
    """Insert a properly indented python line.

    This command should be mapped to any key or shortcut used to add a
    new line.

    """
    def run(self, edit, register='', full_line=False, forward=True):
        try:
            new_sel = []
            for region in self.view.sel():
                # set the insert point
                if full_line:
                    if forward:
                        cursor = self.view.line(region).end()
                    else:
                        cursor = self.view.line(region).begin() - 1
                else:
                    cursor = region.begin()

                indent = get_new_line_indent(self.view, cursor)

                if self.view.line_endings() == 'Windows':
                    new_line_char = '\r\n'
                elif self.view.line_endings() == 'CR':
                    new_line_char = '\r'
                else:
                    new_line_char = '\n'  # Linux is default

                row, col = self.view.rowcol(cursor)

                if not full_line:
                    to_replace = sublime.Region(
                        cursor, self.view.line(region).end())
                    if region.empty():
                        new_line_content = \
                            self.view.substr(to_replace).lstrip()
                    else:
                        new_line_content = self.view.substr(sublime.Region(
                            region.end(), to_replace.end())).lstrip()

                    self.view.replace(
                        edit, to_replace,
                        new_line_char + ' '*indent + new_line_content)
                    cursor += indent + 1
                    new_sel.append(sublime.Region(cursor, cursor))
                else:
                    self.view.insert(edit, cursor, new_line_char + ' '*indent)
                    cursor += indent + 1
                    new_sel.append(sublime.Region(cursor, cursor))

            if new_sel:
                self.view.sel().clear()
                for region in new_sel:
                    self.view.sel().add(region)
        except:
            # fail safe
            print traceback.format_exc()
            if self.view.line_endings() == 'Windows':
                new_line_char = '\r\n'
            elif self.view.line_endings() == 'CR':
                new_line_char = '\r'
            else:
                new_line_char = '\n'  # Linux is default
            for sel in self.view.sel():
                self.view.insert(edit, sel.end(), new_line_char)


## deindent on keywords


def previous_keyword_lookup(view, cursor, keywords, ignore):
    """Search for a previous keyword.

    Arguments
    ---------
    view: sublime.View
    cursor: current sublime text cursor (int)
    keywords: list of keywords to search
    ignore: list of keywords to ignore

    Return
    ------
    Indentation of the line with the searched keyword.
    If it is not found, return -1.
    """

    if isinstance(keywords, basestring):
        keywords = [keywords]

    tab_size = view.settings().get('tab_size')
    line_lookup_count = MAX_LINE_LOOKUP_COUNT

    kw_regex = re.compile(r'^\s*(%s)\b' % '|'.join(keywords))
    ignore_regex = re.compile(r'^\s*(%s)\b' % '|'.join(ignore))

    line = view.line(cursor)
    start_line = line.begin()
    max_indent = get_line_current_indent(view.substr(line), tab_size)

    while line_lookup_count:
        if start_line is 0:
            return -1
        line_lookup_count -= 1

        line = view.line(start_line-1)
        start_line = line.begin()
        str_line = view.substr(line)
        indent = get_line_current_indent(str_line, tab_size)
        if kw_regex.match(str_line):
            if indent <= max_indent:
                return indent
        elif not ignore_regex.match(str_line):
            max_indent = min(indent - tab_size, max_indent)
            if max_indent < 0:
                return -1
    else:
        print "max line lookup reach"
        return -1


indent_regex = re.compile(r'^\s*')


def change_indent(str, new_indent):
    return indent_regex.sub(' '*new_indent, str, count=1)


else_pattern = re.compile(r'^\s*else\s*:')
finally_pattern = re.compile(r'^\s*finally\s*:')
except_pattern = re.compile(r'^\s*except\b')
elif_pattern = re.compile(r'^\s*elif\b')


class PythonDeindenter(sublime_plugin.EventListener):

    """Auto-deindentation on appropriated keywords."""

    def on_modified(self, view):
        cmd, param, count = view.command_history(0, False)
        if cmd != 'insert' or param['characters'][-1] not in ': ':
            return

        sel = view.sel()[0]  # XXX multi selection
        begin_line = view.substr(sublime.Region(view.line(sel).begin(),
                                                sel.end()))
        # new_sel = []
        if sel.empty():
            pattern = ''
            if else_pattern.match(begin_line):
                if param['characters'].endswith(':'):
                    pattern = 'else'
                    align_with = ['if', 'except']
                    ignore = ['elif']
            elif finally_pattern.match(begin_line):
                if param['characters'].endswith(':'):
                    pattern = 'finally'
                    align_with = ['try']
                    ignore = ['except', 'else']
            elif except_pattern.match(begin_line):
                if (param['characters'].endswith(' ')
                        or param['characters'].endswith(':')):
                    pattern = 'except'
                    align_with = ['try']
                    ignore = ['except']
            elif elif_pattern.match(begin_line):
                if param['characters'].endswith(' '):
                    pattern = 'elif'
                    align_with = ['if']
                    ignore = ['elif']

            if pattern:
                str_line = view.substr(view.line(sel))
                indent = previous_keyword_lookup(view, sel.end(), align_with,
                                                 ignore)
                if indent is not -1:
                    edit = view.begin_edit()
                    try:
                        new_line = change_indent(str_line, indent)
                        view.replace(edit, view.line(sel), new_line)
                    finally:
                        view.end_edit(edit)


