# Python PEP 8 Indent

Sublime text 2 extension to add automatic python indentation, with compliance to [PEP8](http://www.python.org/dev/peps/pep-0008/).

## Features

New lines are indented properly, depending on the previous line. Continuation lines are handled, as "end of block"
keywords ('return', 'pass', ...).

On new block keywords ('elif', 'else', 'except', ...), the indent is aligned with the proper
previous block.

The file 'example.py' were typed without pressing the `tab` or `backspace` key.

## Caveat

PythonPEP8Indent works only with space indent, no tab indent.

## Requirement
This plugin has no requirement beside sublime text 2. Sublime text 3 is currently not supported.

## Install
### Manual installation
Copy the `PythonPEP8Indent` directory into your sublime text package directory.

If you use the vintage mode, see "Settings".

## Settings
### Use with vintage mode
Add the following lines to your keymap file, to remap the "new line" command:

    { "keys": ["o"], "command": "enter_insert_mode", "args":
        {"insert_command": "new_python_line", "insert_args":{"full_line":true}},
        "context": [{"key": "setting.command_mode", "match_all":true},
                     {"key":"selector", "operator":"equal",
                     "operand":"source.python", "match_all":true}]
    },

    { "keys": ["O"], "command": "enter_insert_mode", "args":
        {"insert_command": "new_python_line", "insert_args":{"full_line":true, "forward":false}},
        "context": [{"key": "setting.command_mode"},
                    {"key":"selector", "operator":"equal", "operand":"source.python"}]
    }

## Testing

### Requirement
The test script requires the python libraries [pytest](http://pytest.org/latest/) and [mock](http://www.voidspace.org.uk/python/mock/).
They can be installed through `pip` or `easy_install`.

    $ pip install -U pytest
    $ pip install -U mock

    $ easy_install -U pytest
    $ easy_install -U mock

### Execution

    $ cd python_PEP8_indent
    $ py.test

## Bug reports & Contributions

Bug reports and contributions are welcome.
PythonPEP8Indent is hosted on [github](https://github.com/bperriot/...).

## License
Copyright (c) 2013 Bruno Perriot <bperriot@gmail.com>

This sublime text plugin is released under the terms of the MIT license.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
