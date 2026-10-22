# Performance of a centrifugal pump

An interactive write-up of Experiment 9 from the fluid machinery lab: a single-stage
centrifugal pump run at 50 Hz while the delivery valve is throttled step by step.

**Pages**

- **Experiment**: aim, how the pump works, an animated schematic of the rig, apparatus and procedure.
- **Theory**: formulae, the variable table, and the chain from what you set to what you read to what you calculate.
- **Observations**: the six readings in an editable table, calculated values, a worked example and CSV export.
- **Graphs**: head, input power and efficiency against flow rate, with fitted curves and the design point.
- **Virtual bench**: set motor speed and valve opening, read the instruments and record your own readings.
- **Result**: design head, discharge and efficiency, inference, sources of error and precautions.

## Run it locally

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Project layout

```
app.py                 navigation and page setup
lab/data.py            readings, calculations, fitted pump model (no Streamlit)
lab/look.py            styling and chart theme
lab/schematic.py       the animated rig drawing
lab/state.py           readings shared across pages
views/                 one file per page
.streamlit/config.toml theme
```

## How the virtual bench works

The six 50 Hz readings are fitted with quadratics for head and input power against flow.
The valve is a resistance, H = kQ², with k growing as it closes, and the pump runs where
the two curves cross. Other speeds are scaled with the affinity laws (Q ∝ n, H ∝ n², P ∝ n³).
Only the 50 Hz values are measured. Everything at other speeds is a prediction.
