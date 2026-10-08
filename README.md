# Beyond Cash — UPI Adoption Demonstration Dashboard

B.Sc. Data Science Semester III field-project **prototype**.

**Topic:** Adoption of UPI and Cashless Economy: A Field Investigation  
**Title:** Beyond Cash: Understanding UPI Adoption, Trust and Digital Payment Behaviour

## Important data notice

The bundled dataset is **SYNTHETIC / DEMONSTRATION DATA**.

- It was generated with Python (`src/generate_sample_data.py`).
- It does **not** come from real respondents.
- **No field survey was conducted** for this prototype.
- Every row is labelled `SYNTHETIC_DEMONSTRATION`.

Do not present the charts as findings from people you interviewed.

## What the app does

- Project overview and column dictionary
- Data cleaning log (missing values, inconsistent labels, impossible ages)
- UPI adoption analysis, including a documented **UPI Adoption Score**
- Cash vs UPI comparison
- Trust and security views
- Demographic breakdowns
- Interactive Plotly charts with sidebar filters
- Chi-square and Pearson correlation on the sample file
- Key findings and recommendations computed from the current filters
- CSV downloads of the synthetic tables

Percentages, scores and charts are calculated from the dataset (or the filtered subset) when the app runs.

## UPI Adoption Score (0–100)

```
Score = 30% × Account + 25% × Frequency + 20% × Digital share
      + 15% × Tenure + 10% × Preference
```

Each component is scaled 0–100. Details are shown on the UPI Adoption page. This is a student-defined index, not an official NPCI or RBI indicator.

## Folder layout

- `app.py` — home / project overview
- `pages/` — Streamlit multipage sections
- `src/` — data generation, cleaning, metrics, UI helpers
- `data/synthetic_upi_survey.csv` — generated on first run if missing

## How to run

```powershell
Set-Location -LiteralPath "<path-to-project-folder>"
python -m pip install -r requirements.txt
python -m src.generate_sample_data
python -m streamlit run app.py
```

If `python` is not recognised, use `py` instead of `python`.

Alternatively, from Command Prompt (`cmd`):

```cmd
cd /d "<path-to-project-folder>"
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

The terminal will show a local URL (usually `http://localhost:8501`). Open that address in a browser. Do not deploy this prototype unless you are asked to.

## Regenerating the sample file

```powershell
python -m src.generate_sample_data
```

The generator uses a fixed random seed (`42`) so the same 300 rows can be reproduced.

## Tools

Python, Pandas, NumPy, Streamlit, Plotly, Seaborn, Matplotlib.
