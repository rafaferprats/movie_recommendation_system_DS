@echo off
echo "Starting environment variables"
set /p path_to_repo="Path to repo: "
echo "Installing packages and setting up the virtual environment"
cd  %path_to_repo%\bin\local\
conda env create -p %path_to_repo%\venv -f %path_to_repo%\bin\local\environment.yml
echo "Done"