"""Readings shared between pages, so edits on the observations page carry over."""
import streamlit as st

from lab.data import DATUM_HEAD, RECORDED, PumpModel, calculate


def _init():
    ss = st.session_state
    if "readings" not in ss:
        ss.readings = RECORDED.copy()
        ss.datum = DATUM_HEAD
        ss.editor_version = 0
        ss.bench_log = []


def readings():
    _init()
    return st.session_state.readings


def datum():
    _init()
    return st.session_state.datum


def calculated():
    """Calculated table, skipping rows that are blank or physically impossible."""
    r = readings().dropna()
    r = r[(r.time_s > 0) & (r.volume_l > 0) & (r.power_w > 0)]
    return calculate(r.reset_index(drop=True), datum())


def model():
    return _fit(calculated())


@st.cache_resource(show_spinner=False)
def _fit(calc):
    return PumpModel(calc)


def reset():
    st.session_state.readings = RECORDED.copy()
    st.session_state.datum = DATUM_HEAD
    st.session_state.editor_version += 1


def is_original():
    _init()
    return st.session_state.readings.equals(RECORDED) and st.session_state.datum == DATUM_HEAD
