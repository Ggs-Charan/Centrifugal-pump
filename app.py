import streamlit as st

from lab import look

st.set_page_config(
    page_title="Centrifugal Pump · Experiment 9",
    layout="wide",
    initial_sidebar_state="collapsed",
)
look.apply()

pages = [
    st.Page("views/experiment.py", title="Experiment", default=True),
    st.Page("views/theory.py", title="Theory"),
    st.Page("views/observations.py", title="Observations"),
    st.Page("views/graphs.py", title="Graphs"),
    st.Page("views/bench.py", title="Virtual bench"),
    st.Page("views/result.py", title="Result"),
]
st.navigation(pages, position="top").run()
look.footer()
