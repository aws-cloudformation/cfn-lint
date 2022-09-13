"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
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


with open('README.md', encoding='utf-8') as f:
    readme = f.read()

setup(
    name='cfn-lint',
    version=version,
    description=('Checks CloudFormation templates for practices and behaviour \
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
        'data/ExtendedSpecs/*/*.json',
        'data/CfnLintCli/config/schema.json'
    ]},
    packages=find_packages('src'),
    zip_safe=False,
    install_requires=[
        'pyyaml>5.4',
        'aws-sam-translator>=1.50.0',
        'jsonpatch',
        'jsonschema>=3.0,<5',
        'importlib_resources>=1.4,<4;python_version<"3.7"',
        'networkx~=2.4',
        'junit-xml~=1.9',
        'jschema_to_python~=1.2.3',
        'sarif-om~=1.0.4'
    ],
    python_requires='>=3.7, <=4.0, !=4.0',
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
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
)
