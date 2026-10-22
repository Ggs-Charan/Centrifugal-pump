import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from lab import look, schematic, state
from lab.data import N_RATED, calculate

ss = st.session_state

look.header(
    "Virtual bench",
    "Run the pump yourself",
    "You get the same two controls as in the lab: motor speed and the delivery valve. Everything "
    "else follows from the pump, just as it did on the day. Set them, read the instruments, "
    "and record as many readings as you like.",
)

calc = state.calculated()
if len(calc) < 3:
    st.warning("The bench needs at least three readings on the Observations page to model the pump.")
    st.stop()
m = state.model()
state.readings()  # makes sure the log exists

controls, rig = st.columns([1, 1.6], gap="large")
with controls:
    look.section("01", "Controls")
    speed = st.slider("Motor speed n (Hz)", min_value=30, max_value=50, value=50, step=1,
                      help="Set on the inverter. The lab readings were all at 50 Hz.")
    opening = st.slider("Delivery valve opening (%)", min_value=15, max_value=100, value=55, step=5,
                        help="Fully closed is shut-off. The tested readings cover roughly 18–95 %.") / 100
    inlet = float(calc.inlet_m.median())
    reading = m.bench_readings(speed, opening, inlet_m=inlet, datum=state.datum())
    if speed != N_RATED:
        look.note(f"{speed} Hz wasn't tested in the lab. These values are predicted "
                  "from the 50 Hz readings using the affinity laws.")

with rig:
    schematic.draw(height=290, speed_hz=speed, flow_e4=reading["_q_true"], opening=opening,
                   collect_s=reading["time_s"], inlet_m=reading["inlet_m"],
                   outlet_m=reading["outlet_m"], show_tags=False)

look.section("02", "Instruments")
st.html(f"""
<div class="panel">
  <div class="inst"><div class="lbl">Stopwatch &middot; time for 10 L</div>
    <div class="lcd">{reading['time_s']:.2f}<small>s</small></div><div class="sub">read to 0.01 s</div></div>
  <div class="inst"><div class="lbl">Inlet gauge h&#7522;</div>
    <div class="lcd">{reading['inlet_m']:.1f}<small>m</small></div><div class="sub">steady at 1.5 m in the lab</div></div>
  <div class="inst"><div class="lbl">Outlet gauge h&#8338;</div>
    <div class="lcd">{reading['outlet_m']:.1f}<small>m</small></div><div class="sub">read to 0.5 m</div></div>
  <div class="inst"><div class="lbl">Inverter &middot; kW flashing</div>
    <div class="lcd">{reading['power_w'] / 1000:.2f}<small>kW</small></div><div class="sub">= {reading['power_w']:.0f} W</div></div>
</div>""")

row = calculate(pd.DataFrame([reading]), state.datum()).iloc[0]
c1, c2, c3, c4 = st.columns(4)
c1.metric("Flow rate Q (×10⁻⁴ m³/s)", f"{row.flow_e4:.2f}")
c2.metric("Total head H", f"{row.head_m:.2f} m")
c3.metric("Output power Wₒ", f"{row.out_w:.1f} W")
c4.metric("Efficiency η", f"{row.eff_pct:.1f} %")

b1, b2, _ = st.columns([1, 1, 3])
if b1.button("Record this reading", type="primary"):
    ss.bench_log.append({k: v for k, v in reading.items() if not k.startswith("_")} | {"opening": opening})
    st.rerun()
if b2.button("Clear readings", disabled=not ss.bench_log):
    ss.bench_log = []
    st.rerun()

log = None
if ss.bench_log:
    raw = pd.DataFrame(ss.bench_log)
    log = calculate(raw, state.datum())
    log["opening"] = raw.opening
    body = "".join(
        f'<tr><td class="num">{i + 1}</td><td class="num">{r.speed_hz:.0f}</td><td class="num">{r.opening * 100:.0f}</td>'
        f'<td class="num">{r.time_s:.2f}</td><td class="num">{r.outlet_m:.1f}</td><td class="num">{r.power_w:.0f}</td>'
        f'<td class="num">{r.flow_e4:.3f}</td><td class="num">{r.head_m:.2f}</td><td class="num">{r.out_w:.1f}</td>'
        f'<td class="num">{r.eff_pct:.1f}</td></tr>'
        for i, r in log.iterrows())
    st.html(f"""
<table class="rec">
<tr><th class="num">No.</th><th class="num">n (Hz)</th><th class="num">Valve (%)</th><th class="num">t (s)</th>
<th class="num">h&#8338; (m)</th><th class="num">W&#7522; (W)</th><th class="num">Q (&times;10&#8315;&#8308;)</th>
<th class="num">H (m)</th><th class="num">W&#8338; (W)</th><th class="num">&eta; (%)</th></tr>
{body}</table>""")
    st.download_button("Download these readings as CSV", log.round(4).to_csv(index_label="No.").encode(),
                       file_name="virtual_bench_readings.csv", mime="text/csv")
else:
    st.caption("No readings recorded yet. Try six valve settings at 50 Hz and compare them with the lab table.")

look.section("03", "Where the pump is running")
st.html('<p class="prose">The pump can only run where its own curve meets the curve of the pipework and valve. '
        'Close the valve and the system curve gets steeper, so the meeting point slides up and to the left.</p>')

r = speed / N_RATED
qq = np.linspace(0, 13.5 * max(r, 0.6), 160)
q_op = reading["_q_true"]
left, right = st.columns(2, gap="large")
with left:
    fig = go.Figure()
    if speed != N_RATED:
        fig.add_scatter(x=qq, y=m.head(qq, N_RATED), name="pump at 50 Hz", line=dict(color=look.INK_SOFT, width=1, dash="dot"))
    fig.add_scatter(x=qq, y=m.head(qq, speed), name=f"pump at {speed} Hz", line=dict(color=look.INK, width=2))
    fig.add_scatter(x=qq, y=m.system_head(qq, opening), name=f"valve {opening * 100:.0f}% open",
                    line=dict(color=look.BLUE, width=1.6, dash="dash"))
    fig.add_scatter(x=calc.flow_e4, y=calc.head_m, mode="markers", marker=look.POINT, name="lab readings")
    if log is not None:
        fig.add_scatter(x=log.flow_e4, y=log.head_m, mode="markers", name="your readings",
                        marker=dict(symbol="square-open", size=9, color=look.RED, line=dict(width=1.5)))
    fig.add_scatter(x=[q_op], y=[m.head(q_op, speed)], mode="markers", name="running here",
                    marker=dict(size=11, color=look.RED))
    fig.update_xaxes(title_text="Q  (×10⁻⁴ m³/s)", range=[0, 13.5], dtick=1)
    fig.update_yaxes(title_text="Head H  (m)", range=[0, 23])
    st.plotly_chart(look.graph_paper(fig, height=380, legend=True), config={"displayModeBar": False})
with right:
    q_eff = np.linspace(2.0 * r, 12.5 * r, 120)
    fig = go.Figure()
    fig.add_scatter(x=q_eff, y=m.efficiency(q_eff, speed), name=f"η at {speed} Hz", line=dict(color=look.RED, width=1.8))
    fig.add_scatter(x=calc.flow_e4, y=calc.eff_pct, mode="markers", marker=look.POINT, name="lab readings")
    if log is not None:
        fig.add_scatter(x=log.flow_e4, y=log.eff_pct, mode="markers", name="your readings",
                        marker=dict(symbol="square-open", size=9, color=look.RED, line=dict(width=1.5)))
    fig.add_scatter(x=[q_op], y=[m.efficiency(q_op, speed)], mode="markers", name="running here",
                    marker=dict(size=11, color=look.RED))
    fig.update_xaxes(title_text="Q  (×10⁻⁴ m³/s)", range=[0, 13.5], dtick=1)
    fig.update_yaxes(title_text="Efficiency η  (%)", range=[0, 35])
    st.plotly_chart(look.graph_paper(fig, height=380, legend=True), config={"displayModeBar": False})

with st.expander("How the bench works out its readings"):
    st.html("""
<p class="prose">
The six lab readings are fitted with two smooth curves at 50 Hz: head against flow and input power
against flow. The valve is treated as a resistance whose head loss grows with the square of flow
and gets larger as the valve closes. The flow the pump settles at is where those two curves cross.
From that flow the bench works out each instrument value and rounds it the way you'd read it in the
lab: stopwatch to 0.01 s, outlet gauge to the nearest 0.5 m, inverter to 10 W.
</p>
<p class="prose">
For other speeds the 50 Hz curves are scaled with the affinity laws (Q &prop; n, H &prop; n&sup2;,
W &prop; n&sup3;). Real pumps follow these well over moderate speed changes, but they are still
predictions. Only the 50 Hz values come from measurement.
</p>""")
