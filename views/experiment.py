import streamlit as st

from lab import look, schematic, state

look.header(
    "Experiment No. 9 · Fluid machinery lab",
    "Performance of a centrifugal pump",
    "Run a single-stage centrifugal pump at constant speed, throttle its delivery valve "
    "step by step, and see how head, input power and efficiency change with the flow it delivers.",
)

calc = state.calculated()
design = calc.loc[calc.eff_pct.idxmax()]

schematic.draw(
    height=380, speed_hz=50, flow_e4=float(design.flow_e4), opening=0.55,
    collect_s=float(design.time_s), inlet_m=float(design.inlet_m),
    outlet_m=float(design.outlet_m),
)
st.caption("The rig, not to scale. The numbers match the apparatus list below. "
           "The impeller turns, water moves through the pipes, and the measuring tank fills and drains.")

left, right = st.columns([1, 1.6], gap="large")
with left:
    look.section("01", "Aim")
    st.html('<p class="prose">To study the performance characteristics of a single-stage centrifugal pump.</p>')
    look.note("Only the valve changes between readings. Everything else follows from it.")

with right:
    look.section("02", "How it works")
    st.html("""
<p class="prose">
A centrifugal pump is a rotodynamic machine. The motor spins an impeller with curved vanes
inside an airtight spiral casing. Water arrives at the centre (the <i>eye</i>) through the
suction pipe, gets flung outward by the vanes, and leaves the rim moving fast. The casing
widens around the impeller, slowing that water down and turning its speed into pressure. That
pressure is what lifts water to a higher level.
</p>
<p class="prose">
If more water keeps arriving at the eye, the pump keeps delivering at the higher level.
A valve on the delivery side lets you choose how much flows: close it a little and the pump
works against more resistance, so it gives more head but less flow.
</p>""")

look.section("03", "Apparatus")
rows = "".join(
    f'<tr><td class="num" style="width:2.2rem">{n}</td><td style="width:15rem"><b>{name}</b></td><td>{what}</td></tr>'
    for n, name, what in schematic.PARTS)
st.html(f'<table class="rec"><tr><th class="num">No.</th><th>Part</th><th>What it does here</th></tr>{rows}</table>')
st.html('<p class="prose" style="font-size:.92rem;color:var(--ink-soft)">Also used: a stopwatch, '
        'for timing the 10-litre collection.</p>')

look.section("04", "Procedure")
st.html("""
<ol class="prose" style="padding-left:1.2rem">
  <li>Start the motor and let water circulate until the gauges settle.</li>
  <li>Set the flow with the delivery valve. Start nearly closed and open it a little more for each reading.</li>
  <li>Note the inlet (vacuum) and outlet (pressure) gauge readings.</li>
  <li>Note the input power on the inverter display. The <i>kW</i> LED must be flashing, which means the
      display shows power into the pump. A steady LED means power into the inverter.</li>
  <li>Close the tank's drain and time how long the water takes to rise by 10 litres.</li>
  <li>Repeat for at least six valve settings, keeping the motor at 50 Hz throughout.</li>
</ol>""")

c1, c2, c3 = st.columns(3)
with c1:
    st.page_link("views/theory.py", label="Formulae and what depends on what")
with c2:
    st.page_link("views/observations.py", label="Observations and calculations")
with c3:
    st.page_link("views/bench.py", label="Try it on the virtual bench")
