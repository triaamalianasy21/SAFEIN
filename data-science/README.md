SAFEIN Financial Dashboard ✨
Dashboard ini dirancang untuk menganalisis tren keuangan pribadi, mencakup visualisasi pemasukan, pengeluaran, hingga deteksi defisit anggaran dalam project SAFEIN.

Setup Environment - Anaconda
``
conda create --name safein-ds python=3.9
conda activate safein-ds
pip install -r requirements.txt
``
Setup Environment - Shell/Terminal
``
mkdir safein_project
cd safein_project
pipenv install
pipenv shell
pip install -r requirements.txt
``
Run Streamlit App
``
streamlit run dashboard/dashboard.py
``
