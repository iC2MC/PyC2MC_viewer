call C:/Users/sueurma1/Anaconda3/Scripts/activate.bat C:/Users/sueurma1/Anaconda3
call conda activate PyC2MC_viewer
call pyuic5 PyC2MC.ui -o modules/pyc2mc_ui.py -x
call python -m PyQt5.pyrcc_main resources.qrc -o resources_rc.py
call pyuic5 splitFinder.ui -o src/splitFinder/splitfinder_ui.py -x
pause