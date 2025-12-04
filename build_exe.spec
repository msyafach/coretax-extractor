# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['coretax_extractor_flet.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('db_manager.py', '.'),
        ('update_ui_helper.py', '.'),
        ('version.json', '.'),
        ('rsm.svg', '.'),
        ('rsm.png', '.'),
        ('coretax.db', '.'),
    ],
    hiddenimports=[
        'flet',
        'flet.core',
        'flet.utils',
        'fitz',
        'pandas',
        'openpyxl',
        'sqlite3',
        'hashlib',
        'requests',
        'urllib',
        'urllib.request',
        'urllib.error',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Testing frameworks
        'pytest',
        'unittest',
        'test',
        '_pytest',
        
        # Unused standard library
        'tkinter',
        'turtle',
        'pydoc',
        'doctest',
        'pdb',
        
        # Unused data science
        'matplotlib',
        'scipy',
        'numpy.testing',
        
        # Unused networking
        'http.server',
        'xmlrpc',
        
        # Development tools
        'IPython',
        'jupyter',
        'notebook',
        
        # Other unused
        'PIL.ImageQt',
        'PyQt5',
        'PyQt6',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Coretax Extractor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon/app.ico',  # Application icon
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=['python3.dll', 'vcruntime140.dll', 'msvcp140.dll', 'ucrtbase.dll'],
    name='CoretaxExtractor',
)
