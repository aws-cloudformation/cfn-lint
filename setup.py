"""
  Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.

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
import codecs
import re
from setuptools import find_packages
from setuptools import setup


def get_version(filename):
    with codecs.open(filename, 'r', 'utf-8') as fp:
        contents = fp.read()
    return re.search(r"__version__ = ['\"]([^'\"]+)['\"]", contents).group(1)


version = get_version('src/cfnlint/version.py')


with open('README.md') as f:
    readme = f.read()

setup(
    name='cfn-lint',
    version=version,
    description=('checks cloudformation for practices and behaviour \
        that could potentially be improved'),
    long_description=readme,
    long_description_content_type="text/markdown",
    keywords='aws, lint',
    author='kddejong',
    author_email='kddejong@amazon.com',
    url='https://github.com/aws-cloudformation/cfn-python-lint',
    package_dir={'': 'src'},
    package_data={'cfnlint': [
        'data/CloudSpecs/*.json',
        'data/AdditionalSpecs/*.json',
        'data/Serverless/*.json',
        'data/ExtendedSpecs/all/*.json',
        'data/ExtendedSpecs/ap-northeast-1/*.json',
        'data/ExtendedSpecs/ap-northeast-2/*.json',
        'data/ExtendedSpecs/ap-northeast-3/*.json',
        'data/ExtendedSpecs/ap-south-1/*.json',
        'data/ExtendedSpecs/ap-southeast-1/*.json',
        'data/ExtendedSpecs/ap-southeast-2/*.json',
        'data/ExtendedSpecs/ca-central-1/*.json',
        'data/ExtendedSpecs/eu-central-1/*.json',
        'data/ExtendedSpecs/eu-north-1/*.json',
        'data/ExtendedSpecs/eu-west-1/*.json',
        'data/ExtendedSpecs/eu-west-2/*.json',
        'data/ExtendedSpecs/eu-west-3/*.json',
        'data/ExtendedSpecs/sa-east-1/*.json',
        'data/ExtendedSpecs/us-east-1/*.json',
        'data/ExtendedSpecs/us-east-2/*.json',
        'data/ExtendedSpecs/us-gov-east-1/*.json',
        'data/ExtendedSpecs/us-gov-west-1/*.json',
        'data/ExtendedSpecs/us-west-1/*.json',
        'data/ExtendedSpecs/us-west-2/*.json',
        'data/CfnLintCli/config/schema.json'
    ]},
    packages=find_packages('src'),
    zip_safe=False,
    install_requires=[
        'pyyaml',
        'six~=1.11',
        'requests>=2.15.0',
        'aws-sam-translator>=1.10.0',
        'jsonpatch',
        'jsonschema~=2.6',
        'pathlib2>=2.3.0;python_version<"3.4"'
    ],
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*',
    entry_points={
        'console_scripts': [
            'cfn-lint = cfnlint.__main__:main'
        ]
    },
    license='MIT no attribution',
    test_suite="unittest",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
)
