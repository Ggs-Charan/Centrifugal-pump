import numpy as np
import plotly.graph_objects as go
import streamlit as st

from lab import look, state
from lab.data import HANDWRITTEN

look.header(
    "Graphs",
    "Characteristic curves at 50 Hz",
    "Flow rate Q on the x-axis, as the manual asks. Circled points are the readings. The red "
    "line is a smooth curve fitted through them, the way you'd draw it by hand on graph paper.",
)

calc = state.calculated()
if len(calc) < 3:
    st.warning("At least three readings are needed to fit the curves.")
    st.stop()
m = state.model()
design = calc.loc[calc.eff_pct.idxmax()]

show_written = False
if state.is_original():
    show_written = st.toggle("Also show the values as first written in the record book", value=False)

q_lo, q_hi = m.q_tested
qq = np.linspace(q_lo * 0.92, q_hi * 1.04, 120)
Q_LABEL = "Q  (×10⁻⁴ m³/s)"


def chart(y_data, y_fit, y_label, written=None, fmt=".2f", y_range=None, mark_design=True):
    fig = go.Figure()
    fig.add_scatter(x=qq, y=y_fit, mode="lines", line=dict(color=look.RED, width=1.8, shape="spline"),
                    name="fitted curve", hoverinfo="skip")
    if written is not None:
        fig.add_scatter(x=HANDWRITTEN.flow_e4, y=written, mode="markers", name="as first written",
                        marker=dict(symbol="x-thin", size=9, color=look.RED, line=dict(width=1.5)),
                        hovertemplate=f"as written<br>Q %{{x:.2f}}<br>%{{y:{fmt}}}<extra></extra>")
    fig.add_scatter(x=calc.flow_e4, y=y_data, mode="markers", marker=look.POINT, name="reading",
                    customdata=np.arange(1, len(calc) + 1),
                    hovertemplate=f"No. %{{customdata}}<br>Q %{{x:.3f}}<br>%{{y:{fmt}}}<extra></extra>")
    if mark_design:
        x0, y0 = design.flow_e4, y_data[design.name]
        fig.add_shape(type="line", x0=x0, x1=x0, y0=0, y1=y0, yref="y", line=dict(color=look.BLUE, width=1, dash="dot"))
        fig.add_shape(type="line", x0=0, x1=x0, y0=y0, y1=y0, line=dict(color=look.BLUE, width=1, dash="dot"))
        fig.add_annotation(x=x0, y=y0, text="design point", showarrow=True, arrowhead=0, arrowwidth=1,
                           arrowcolor=look.BLUE, ax=-46, ay=-30,
                           font=dict(family="Kalam, cursive", size=15, color=look.BLUE))
    fig.update_xaxes(title_text=Q_LABEL, range=[0, max(13, q_hi * 1.1)], dtick=1)
    fig.update_yaxes(title_text=y_label, range=y_range)
    return look.graph_paper(fig, height=340, legend=show_written)


look.section("01", "Total head vs flow rate")
st.plotly_chart(chart(calc.head_m, m.head(qq), "Total head H  (m)",
                      HANDWRITTEN.head_m if show_written else None,
                      y_range=[min(12, calc.head_m.min() - 2), max(22, calc.head_m.max() + 1.5)]),
                config={"displayModeBar": False})
st.caption("Head drops slowly at low flow, then faster as the valve opens. Losses inside the pump grow with the square of the flow.")

look.section("02", "Input power vs flow rate")
st.plotly_chart(chart(calc.power_w, m.power(qq), "Input power Wᵢ  (W)", None, fmt=".0f",
                      y_range=[min(300, calc.power_w.min() - 40), max(620, calc.power_w.max() + 40)]),
                config={"displayModeBar": False})
st.caption("Power drawn rises steadily with flow, flattening a little towards the fully open valve.")

look.section("03", "Efficiency vs flow rate")
st.plotly_chart(chart(calc.eff_pct, m.efficiency(qq), "Efficiency η  (%)",
                      HANDWRITTEN.eff_pct if show_written else None, fmt=".1f",
                      y_range=[0, max(35, calc.eff_pct.max() + 5)]),
                config={"displayModeBar": False})
q_best, e_best = m.best_efficiency()
st.caption(f"Highest measured efficiency is {design.eff_pct:.1f} % at reading {design.name + 1}. "
           f"The fitted curve peaks at about {e_best:.1f} % near Q = {q_best:.1f} × 10⁻⁴ m³/s, "
           "right at the edge of the tested range, so the true best-efficiency point may lie just beyond it.")

look.section("04", "All three together")
fig = go.Figure()
fig.add_scatter(x=qq, y=m.head(qq), name="H (m)", line=dict(color=look.INK, width=1.8))
fig.add_scatter(x=qq, y=m.efficiency(qq), name="η (%)", line=dict(color=look.RED, width=1.8, dash="dash"))
fig.add_scatter(x=qq, y=m.power(qq), name="Wᵢ (W)", yaxis="y2", line=dict(color=look.BLUE, width=1.8, dash="dot"))
fig.update_xaxes(title_text=Q_LABEL, range=[0, max(13, q_hi * 1.1)], dtick=1)
fig.update_yaxes(title_text="H (m)  ·  η (%)", range=[0, 35])
look.graph_paper(fig, height=380, legend=True)
fig.update_layout(yaxis2=dict(title="Wᵢ (W)", overlaying="y", side="right", range=[0, 700], showgrid=False,
                              showline=True, linecolor=look.INK, ticks="outside"),
                  margin=dict(r=60))
st.plotly_chart(fig, config={"displayModeBar": False})

with st.expander("Fitted equations"):
    st.latex(rf"H = {m.A:.3f} {m.B:+.4f}\,q {m.C:+.4f}\,q^2")
    p2, p1, p0 = m.power_coef
    st.latex(rf"W_i = {p0:.1f} {p1:+.2f}\,q {p2:+.3f}\,q^2")
    st.caption("q is flow in units of 10⁻⁴ m³/s. Both are least-squares quadratics through the readings. "
               "Efficiency is then ρgQH ÷ Wᵢ from the two fits.")
