call %UserProfile%\Anaconda3\Scripts\activate.bat %UserProfile%\Anaconda3
call conda activate PyC2MC_viewer
cd docs
call make html
pause