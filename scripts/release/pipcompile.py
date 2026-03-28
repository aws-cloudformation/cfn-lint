#!/usr/bin/env python
import tempfile
import subprocess
import hashlib
import re
import sys

version = sys.argv[1]

with open(f"dist/cfn_lint-{version}.tar.gz", "rb") as f:
    sha256_cfn_lint = hashlib.file_digest(f, "sha256").hexdigest()

with open(f"dist/cfn_lint-{version}-py3-none-any.whl", "rb") as f:
    sha256_cfn_lint_whl = hashlib.file_digest(f, "sha256").hexdigest()

with tempfile.NamedTemporaryFile(suffix="-requirements.txt") as requirements_txt:
    p = subprocess.Popen(
        ["uv", "pip", "compile", "requirements/base.txt", "--generate-hashes"],
        stdout=requirements_txt,
    )
    p.communicate()
    result = [
        f"cfn-lint=={version} \\\n".encode("utf8"),
        f"    --hash=sha256:{sha256_cfn_lint} \\\n".encode("utf8"),
        f"    --hash=sha256:{sha256_cfn_lint_whl}\n".encode("utf8"),
    ]
    requirements_txt.seek(0)
    for line in requirements_txt.readlines():
        if not re.match(rb"^ *#.*", line):
            result.append(line)
    result = b"".join(result)
    with open("requirements.txt", "wb") as f:
        f.write(result)
