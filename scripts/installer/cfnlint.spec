# -*- mode: python -*-
block_cipher = None
exe_name = 'cfn-lint'
analysis = Analysis(
    ['../../src/cfnlint/runner.py'],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=['./scripts/installer'],
    excludes=[],
    cipher=block_cipher
)
pyz = PYZ(analysis.pure, analysis.zipped_data, cipher=block_cipher)
exe = EXE(
    pyz,
    analysis.scripts,
    [],
    exclude_binaries=True,
    name=exe_name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True
)
coll = COLLECT(
    exe,
    analysis.binaries,
    analysis.zipfiles,
    analysis.datas,
    strip=False,
    upx=True,
    name='cfn-lint'
)
