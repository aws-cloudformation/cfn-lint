from PyInstaller.utils import hooks

hiddenimports: list[str] = [
    "pydot",
    "junit-xml",
    "samtranslator",
    "jschema_to_python",
    "sarif-om",
]


datas = hooks.collect_all("cfnlint", include_py_files=True)[
    0
] + hooks.collect_data_files("samtranslator")
