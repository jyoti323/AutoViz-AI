# AutoViz-AI

A Streamlit-based AI Data Visualization Assistant that loads a CSV file, previews the dataset, displays summary statistics, and generates an automatic Plotly scatter plot for the first two numeric columns.

## Features

- Upload CSV files via a Streamlit interface
- Preview dataset contents in a table
- Display dataset summary statistics
- Detect numeric and categorical columns automatically
- Generate an automatic Plotly scatter plot for the first two numeric columns

## Requirements

- Python 3.10+ (or compatible Python 3.x)
- `streamlit`
- `pandas`
- `plotly`

## Setup

```bash
cd "C:\Users\CCS\Desktop\AutoViz AI"
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install streamlit pandas plotly
```

## Run

```bash
.\venv\Scripts\Activate.ps1
streamlit run app.py
```

Then open the local URL shown in the terminal.

## Notes

- Upload a CSV file to enable dataset preview and plotting
- The app creates a scatter plot only if at least two numeric columns are present

##Deplo link:

  https://jyoti323-autoviz-ai-app-svfbds.streamlit.app/
