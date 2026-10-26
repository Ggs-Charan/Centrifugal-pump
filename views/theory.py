import streamlit as st

from lab import look

look.header(
    "Theory",
    "Formulae, and what depends on what",
    "In this experiment you set two things, read four, and work out the rest. "
    "Keeping those apart is what makes the results trustworthy.",
)

look.section("01", "Chain of dependence")
st.html("""
<div class="chain">
  <div class="box">
    <h4><span class="tag set">set</span>&nbsp; independent</h4>
    <ul>
      <li>Motor speed, <i>n</i> = 50 Hz (fixed)</li>
      <li>Delivery valve opening</li>
      <li>Volume collected, <i>V</i> (10 L in the lab)</li>
    </ul>
  </div>
  <div class="arrow">&rarr;</div>
  <div class="box">
    <h4><span class="tag read">read</span>&nbsp; measured</h4>
    <ul>
      <li>Time to collect, <i>t</i></li>
      <li>Inlet gauge, <i>h<sub>i</sub></i> (suction side)</li>
      <li>Outlet gauge, <i>h<sub>o</sub></i> (delivery side)</li>
      <li>Input power, <i>W<sub>i</sub></i></li>
    </ul>
  </div>
  <div class="arrow">&rarr;</div>
  <div class="box">
    <h4><span class="tag calc">calc</span>&nbsp; dependent</h4>
    <ul>
      <li>Flow rate, <i>Q</i></li>
      <li>Total head, <i>H</i></li>
      <li>Output power, <i>W<sub>o</sub></i></li>
      <li>Efficiency, <i>&eta;</i></li>
    </ul>
  </div>
</div>""")
st.html("""
<p class="prose">
The valve is the real control. Opening it lowers the resistance the pump works against, so
more water flows (the stopwatch time drops) and the pump can't hold as much pressure (the outlet
gauge falls). The motor has to do more work, so the inverter shows more power. None of the
measured values can be chosen freely. They are whatever the pump gives you at that valve setting.
That is why the <i>Observations</i> page only lets you edit the measured columns, and why the
<i>Virtual bench</i> only gives you the valve and the volume to collect.
</p>""")

look.section("02", "The two gauges")
st.html("""
<p class="prose">
Both gauges show pressure as a <b>head</b>: the height of a column of water that pressure could hold up,
in metres. 1 m of water is about 9.81 kPa, so a reading of 19 m means roughly 186 kPa, or 1.9 bar.
</p>
<table class="rec">
<tr><th>Gauge</th><th>Where it is</th><th>What it tells you</th><th class="num">In the lab</th></tr>
<tr><td><b>Inlet gauge, <i>h<sub>i</sub></i></b></td><td>On the suction pipe, just before the pump</td>
    <td>The pressure the water already has as it arrives at the pump.</td><td class="num">1.5 m (steady)</td></tr>
<tr><td><b>Outlet gauge, <i>h<sub>o</sub></i></b></td><td>On the delivery pipe, just after the pump</td>
    <td>The pressure after the impeller has worked on it. Rises as the valve closes.</td><td class="num">21 m &rarr; 16 m</td></tr>
</table>
<p class="prose">
The difference <i>h<sub>o</sub></i> &minus; <i>h<sub>i</sub></i> is the head the pump adds. The datum correction
<i>H<sub>d</sub></i> = 0.15 m accounts for the two gauges being mounted at different heights, so the total head is
<i>H</i> = <i>H<sub>d</sub></i> + (<i>h<sub>o</sub></i> &minus; <i>h<sub>i</sub></i>).
</p>""")

look.section("03", "Formulae")
c1, c2 = st.columns(2, gap="large")
with c1:
    st.markdown("**Flow rate**")
    st.latex(r"Q = \frac{V}{t} \qquad \left[\mathrm{m^3/s}\right]")
    st.caption("V in litres ÷ 1000 to get m³.")
    st.markdown("**Total head, single pump**")
    st.latex(r"H = H_d + \left(h_o - h_i\right) \qquad [\mathrm{m\ of\ water}]")
    st.caption("Hd is the datum head correction, the height between the gauges (0.15 m here).")
with c2:
    st.markdown("**Pump output power** (power given to the water)")
    st.latex(r"W_o = \rho\, g\, Q\, H \qquad [\mathrm{W}]")
    st.caption("ρ = 1000 kg/m³, g = 9.81 m/s², so ρg = 9810 N/m³.")
    st.markdown("**Overall efficiency**")
    st.latex(r"\eta = \frac{W_o}{W_i} \times 100 \qquad [\%]")
    st.caption("Wᵢ is read off the inverter, so this is motor and pump together.")

with st.expander("Total head when two pumps are used"):
    st.latex(r"\text{Series:}\quad H = H_d + h_o")
    st.latex(r"\text{Parallel:}\quad H = H_d + \left(h_m - h_i\right)")
    st.caption("hₘ is the discharge manifold gauge. Not used in this single-pump run.")

look.section("04", "Variables")
rows = [
    ("Motor speed", "n", "Hz", "set", "Pump speed for the F1-27, set on the inverter."),
    ("Volume of water", "V", "m³", "set", "Volume collected in the measuring tank. Read in litres, ÷ 1000."),
    ("Time to collect", "t", "s", "read", "Stopwatch time for the known volume to collect."),
    ("Inlet head", "h<sub>i</sub>", "m", "read", "Inlet gauge: pressure just before the pump (suction side), in metres of water."),
    ("Outlet head", "h<sub>o</sub>", "m", "read", "Outlet gauge: pressure just after the pump (delivery side), in metres of water."),
    ("Pump power input", "W<sub>i</sub>", "W", "read", "From the inverter display (kW LED flashing)."),
    ("Head correction factor", "h<sub>d</sub>", "m", "given", "Height of a gauge above the impeller centre line."),
    ("Datum head correction", "H<sub>d</sub>", "m", "given", "Vertical distance between the gauges used; 0.15 m."),
    ("Flow rate", "Q", "m³/s", "calc", "V / t"),
    ("Total head", "H", "m", "calc", "H<sub>d</sub> + (h<sub>o</sub> − h<sub>i</sub>)"),
    ("Pump power output", "W<sub>o</sub>", "W", "calc", "ρ g Q H"),
    ("Efficiency", "η", "%", "calc", "W<sub>o</sub> / W<sub>i</sub>"),
]
body = "".join(
    f'<tr><td>{name}</td><td><i>{sym}</i></td><td class="num">{unit}</td>'
    f'<td><span class="tag {role}">{role}</span></td><td>{what}</td></tr>'
    for name, sym, unit, role, what in rows)
st.html(f'<table class="rec"><tr><th>Quantity</th><th>Symbol</th><th class="num">Unit</th>'
        f'<th>Role</th><th>Definition</th></tr>{body}</table>')

look.section("05", "Why the curves look the way they do")
st.html("""
<p class="prose">
<b>Head falls as flow rises.</b> At a fixed speed the impeller can only give each kilogram of water
so much energy. Losses through the vanes and casing grow roughly with the square of the flow,
so the more water you push through, the less head is left over.
</p>
<p class="prose">
<b>Input power rises with flow.</b> Moving more water takes more work, even though each kilogram
is lifted a little less.
</p>
<p class="prose">
<b>Efficiency climbs, peaks, then drops.</b> Near shut-off almost all the power goes into
churning water, so efficiency is low. It improves as flow increases, peaks at the
<i>best efficiency point</i>, and falls again once losses take over. On this rig the
efficiency was still close to its peak at the widest valve setting tested.
</p>""")
