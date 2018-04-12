"""
  Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.

  Permission is hereby granted, free of charge, to any person obtaining a copy of this
  software and associated documentation files (the "Software"), to deal in the Software
  without restriction, including without limitation the rights to use, copy, modify,
  merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
  permit persons to whom the Software is furnished to do so.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
  INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
  PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
  HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
  OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
  SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import json
import os
import glob
import imp
import logging
import pkg_resources

LOGGER = logging.getLogger(__name__)

TAG_MAP = "tag:yaml.org,2002:map"
UNCONVERTED_SUFFIXES = ["Ref", "Condition"]
FN_PREFIX = "Fn::"
CONDITION_FUNCTIONS = ['Fn::If']


def load_resources(filename='/data/CloudSpecs/us-east-1.json'):
    """Load resources"""

    filename = pkg_resources.resource_filename(
        __name__,
        filename
    )

    data = json.load(open(filename))

    return data


def load_plugins(directory):
    """Load plugins"""
    result = []
    fh = None

    paths = [
        '*/[A-Za-z]*.py',
        '*/*/[A-Za-z]*.py',
    ]
    for path in paths:
        for pluginfile in glob.glob(os.path.join(directory, path)):
            pluginname = os.path.basename(pluginfile.replace('.py', ''))
            dir_name = os.path.dirname(pluginfile)
            try:
                fh, filename, desc = imp.find_module(pluginname, [dir_name])
                mod = imp.load_module(pluginname, fh, filename, desc)
                obj = getattr(mod, pluginname)()
                result.append(obj)
            finally:
                if fh:
                    fh.close()
    return result
