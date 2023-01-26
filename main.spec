# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(['main.py'],
             pathex=[],
             binaries=[('C:\\Users\\sueurma1\\Anaconda3\\Library\\bin\\pythoncom39.dll','.')],
             datas=[('src/AtomicWeightsAndIsotopicCompNIST2019.txt','.'),('src/Py2MC_icon.png','.')],
             hiddenimports=['sklearn.utils._typedefs',"sklearn.neighbors._quad_tree","sklearn._tree",'sklearn.neighbors._partition_nodes','sklearn.utils._cython_blas',"sklearn.tree._utils",'sklearn.utils._weight_vector','chemparse','openpyxl','openpyxl.cell._writer','scipy.cluster.hierarchy'],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
splash = Splash('splash.jpg',
                binaries=a.binaries,
                datas=a.datas,
                text_pos=None,
                text_size=12,
                minify_script=True)

exe = EXE(pyz,
          a.scripts,
          splash,
          [],
          exclude_binaries=True,
          name='PyC2MC_Viewer',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None , icon='src\Py2MC_icon.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               splash.binaries,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='PyC2MC_Viewer')
