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
    "The motor runs at a fixed 50 Hz, just as in the lab. You set the delivery valve and how much "
    "water to collect; everything else follows from the pump. Watch the rig, read the instruments, "
    "and record as many readings as you like.",
)

calc = state.calculated()
if len(calc) < 3:
    st.warning("The bench needs at least three readings on the Observations page to model the pump.")
    st.stop()
m = state.model()
state.readings()  # makes sure the log exists

look.section("01", "Controls")
c_speed, c_valve, c_vol = st.columns([0.8, 1.2, 1.2], gap="large")
with c_speed:
    st.html('<div class="inst"><div class="lbl">Motor speed n</div>'
            '<div class="lcd">50<small>Hz</small></div><div class="sub">fixed for the whole experiment</div></div>')
with c_valve:
    opening = st.slider("Delivery valve opening (%)", min_value=15, max_value=100, value=55, step=5,
                        help="0 % would be fully shut (no flow), 100 % fully open. The six lab readings "
                             "fall roughly between 18 % and 96 % on this scale.") / 100
with c_vol:
    volume = st.slider("Volume to collect V (litres)", min_value=1, max_value=20, value=10, step=1,
                       help="How much water you time into the measuring tank. The lab used 10 L.")

inlet = float(calc.inlet_m.median())
reading = m.bench_readings(N_RATED, opening, volume_l=float(volume), inlet_m=inlet, datum=state.datum())
row = calculate(pd.DataFrame([reading]), state.datum()).iloc[0]

look.section("02", "The rig, live")
schematic.draw(height=470, flow_e4=reading["_q_true"], opening=opening, volume_l=float(volume),
               collect_s=reading["time_s"], inlet_m=reading["inlet_m"], outlet_m=reading["outlet_m"])
st.caption("White dots show water moving: faster when the valve is more open. The tank fills to the red "
           f"{volume} L mark while the stopwatch runs, then drains and starts again. Use ×5 or ×10 to speed up long fills.")

look.section("03", "Instruments")
st.html(f"""
<div class="panel">
  <div class="inst"><div class="lbl">Stopwatch &middot; time for {volume} L</div>
    <div class="lcd">{reading['time_s']:.2f}<small>s</small></div><div class="sub">read to 0.01 s</div></div>
  <div class="inst"><div class="lbl">Inlet gauge h&#7522; &middot; suction side</div>
    <div class="lcd">{reading['inlet_m']:.1f}<small>m</small></div><div class="sub">pressure going into the pump</div></div>
  <div class="inst"><div class="lbl">Outlet gauge h&#8338; &middot; delivery side</div>
    <div class="lcd">{reading['outlet_m']:.1f}<small>m</small></div><div class="sub">pressure coming out, read to 0.5 m</div></div>
  <div class="inst"><div class="lbl">Inverter &middot; kW flashing</div>
    <div class="lcd">{reading['power_w'] / 1000:.2f}<small>kW</small></div><div class="sub">= {reading['power_w']:.0f} W into the pump</div></div>
</div>""")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Q (×10⁻⁴ m³/s)", f"{row.flow_e4:.2f}", help=f"V ÷ t = {volume} L ÷ {reading['time_s']:.2f} s")
c2.metric("Total head H", f"{row.head_m:.2f} m", help="Hd + (hₒ − hᵢ)")
c3.metric("Output power Wₒ", f"{row.out_w:.1f} W", help="ρ g Q H")
c4.metric("Efficiency η", f"{row.eff_pct:.1f} %", help="Wₒ ÷ Wᵢ")

if reading["time_s"] < 5:
    look.note(f"Only {reading['time_s']:.2f} s to collect {volume} L. A hand-timed stopwatch is easily 0.2 s out, "
              f"which here is about {0.2 / reading['time_s'] * 100:.0f} % error in Q. Collecting a larger volume keeps that error small.")

with st.expander("What each instrument tells you", expanded=True):
    st.html(f"""
<table class="rec">
<tr><th>Instrument</th><th>What it measures</th><th>On this reading</th></tr>
<tr><td><b>Inlet gauge, h&#7522;</b><br><span style="color:var(--ink-soft)">suction side</span></td>
    <td>The pressure of the water just <i>before</i> it enters the pump, written as the height of a water column
        it could hold up (metres of water). On this rig the water reaches the pump with a small positive pressure,
        and it stayed at 1.5 m for every lab reading.</td>
    <td class="num">{reading['inlet_m']:.1f} m</td></tr>
<tr><td><b>Outlet gauge, h&#8338;</b><br><span style="color:var(--ink-soft)">delivery side</span></td>
    <td>The pressure of the water just <i>after</i> it leaves the pump, in the same units. This is where the
        pump's work shows: it rises when you close the valve and falls as you open it.</td>
    <td class="num">{reading['outlet_m']:.1f} m</td></tr>
<tr><td><b>Total head, H</b></td>
    <td>What the pump adds: the outlet reading minus the inlet reading, plus H<sub>d</sub> = {state.datum():.2f} m
        because the outlet gauge sits that much higher than the inlet gauge.
        1 m of water &asymp; 9.81 kPa, so {row.head_m:.1f} m &asymp; {row.head_m * 9.81:.0f} kPa.</td>
    <td class="num">{row.head_m:.2f} m</td></tr>
<tr><td><b>Stopwatch</b></td>
    <td>Time for the measuring tank to fill by your chosen volume. Volume &divide; time gives the flow rate Q.</td>
    <td class="num">{reading['time_s']:.2f} s</td></tr>
<tr><td><b>Inverter display</b></td>
    <td>Electrical power going into the pump motor, W&#7522;, read with the kW LED flashing.</td>
    <td class="num">{reading['power_w']:.0f} W</td></tr>
</table>""")

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
        f'<tr><td class="num">{i + 1}</td><td class="num">{r.opening * 100:.0f}</td><td class="num">{r.volume_l:.0f}</td>'
        f'<td class="num">{r.time_s:.2f}</td><td class="num">{r.inlet_m:.1f}</td><td class="num">{r.outlet_m:.1f}</td>'
        f'<td class="num">{r.power_w:.0f}</td><td class="num">{r.flow_e4:.3f}</td><td class="num">{r.head_m:.2f}</td>'
        f'<td class="num">{r.out_w:.1f}</td><td class="num">{r.eff_pct:.1f}</td></tr>'
        for i, r in log.iterrows())
    st.html(f"""
<table class="rec">
<tr><th class="num">No.</th><th class="num">Valve (%)</th><th class="num">V (L)</th><th class="num">t (s)</th>
<th class="num">h&#7522; (m)</th><th class="num">h&#8338; (m)</th><th class="num">W&#7522; (W)</th>
<th class="num">Q (&times;10&#8315;&#8308;)</th><th class="num">H (m)</th><th class="num">W&#8338; (W)</th><th class="num">&eta; (%)</th></tr>
{body}</table>""")
    st.download_button("Download these readings as CSV", log.round(4).to_csv(index_label="No.").encode(),
                       file_name="virtual_bench_readings.csv", mime="text/csv")
else:
    st.caption("No readings recorded yet. Try six valve settings and compare them with the lab table.")

look.section("04", "Where the pump is running")
st.html('<p class="prose">The pump can only run where its own curve meets the curve of the pipework and valve. '
        'Close the valve and the system curve gets steeper, so the meeting point slides up and to the left.</p>')

qq = np.linspace(0, 13.5, 160)
q_op = reading["_q_true"]
left, right = st.columns(2, gap="large")
with left:
    fig = go.Figure()
    fig.add_scatter(x=qq, y=m.head(qq), name="pump curve", line=dict(color=look.INK, width=2))
    fig.add_scatter(x=qq, y=m.system_head(qq, opening), name=f"valve {opening * 100:.0f}% open",
                    line=dict(color=look.BLUE, width=1.6, dash="dash"))
    fig.add_scatter(x=calc.flow_e4, y=calc.head_m, mode="markers", marker=look.POINT, name="lab readings")
    if log is not None:
        fig.add_scatter(x=log.flow_e4, y=log.head_m, mode="markers", name="your readings",
                        marker=dict(symbol="square-open", size=9, color=look.RED, line=dict(width=1.5)))
    fig.add_scatter(x=[q_op], y=[m.head(q_op)], mode="markers", name="running here",
                    marker=dict(size=11, color=look.RED))
    fig.update_xaxes(title_text="Q  (×10⁻⁴ m³/s)", range=[0, 13.5], dtick=1)
    fig.update_yaxes(title_text="Head H  (m)", range=[0, 23])
    st.plotly_chart(look.graph_paper(fig, height=380, legend=True), config={"displayModeBar": False})
with right:
    q_eff = np.linspace(2.0, 12.5, 120)
    fig = go.Figure()
    fig.add_scatter(x=q_eff, y=m.efficiency(q_eff), name="efficiency curve", line=dict(color=look.RED, width=1.8))
    fig.add_scatter(x=calc.flow_e4, y=calc.eff_pct, mode="markers", marker=look.POINT, name="lab readings")
    if log is not None:
        fig.add_scatter(x=log.flow_e4, y=log.eff_pct, mode="markers", name="your readings",
                        marker=dict(symbol="square-open", size=9, color=look.RED, line=dict(width=1.5)))
    fig.add_scatter(x=[q_op], y=[m.efficiency(q_op)], mode="markers", name="running here",
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
</p>
<p class="prose">
From that flow the bench works out each instrument value and rounds it the way you'd read it in the
lab: stopwatch to 0.01 s, outlet gauge to the nearest 0.5 m, inverter to 10 W. The volume you choose
doesn't change how the pump runs; it only changes how long the stopwatch runs, and so how much a
timing slip matters.
</p>""")
