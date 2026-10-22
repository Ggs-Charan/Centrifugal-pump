import streamlit as st

from lab import look, state

look.header(
    "Result",
    "Result and inference",
    "What the readings show, written up the way it goes in the record book.",
)

calc = state.calculated()
if calc.empty:
    st.warning("No readings to report.")
    st.stop()
design = calc.loc[calc.eff_pct.idxmax()]
first, last = calc.iloc[0], calc.iloc[-1]

look.section("01", "Result")
st.html(f"""
<div class="result">
  <p class="prose" style="margin-top:0">The operating characteristic curves of the centrifugal pump were drawn
  at a constant speed of {design.speed_hz:.0f} Hz.</p>
  <div class="row"><span>Design head</span><span class="val">{design.head_m:.2f} m</span></div>
  <div class="row"><span>Design discharge</span><span class="val">{design.flow_e4:.2f} &times; 10&#8315;&#8308; m&sup3;/s</span></div>
  <div class="row"><span>Efficiency of the pump</span><span class="val">{design.eff_pct:.1f} %</span></div>
</div>""")
st.caption(f"Design point taken as the reading with the highest efficiency, reading {design.name + 1}.")

look.section("02", "Inference")
st.html(f"""
<p class="prose">
As the delivery valve was opened, the flow rate rose from {first.flow_e4:.2f} to {last.flow_e4:.2f} &times; 10&#8315;&#8308; m&sup3;/s
and the total head fell from {first.head_m:.2f} m to {last.head_m:.2f} m. Over the same range the input power rose
from {first.power_w:.0f} W to {last.power_w:.0f} W. Efficiency climbed from {first.eff_pct:.1f} % to a highest
measured value of {design.eff_pct:.1f} % at {design.flow_e4:.2f} &times; 10&#8315;&#8308; m&sup3;/s, and stayed close to
that for the rest of the range. This is the expected falling head curve and rising power curve of a centrifugal pump
at constant speed.
</p>
<p class="prose">
The efficiency is overall (water power &divide; electrical power into the pump motor), so it includes motor
losses as well as pump losses. That's why it is low compared with a pump-only figure.
</p>""")

look.section("03", "Sources of error")
st.html("""
<ul class="prose" style="padding-left:1.2rem">
  <li>Stopwatch timing. Starting and stopping by hand at the 10-litre mark easily adds &plusmn;0.2 s, which matters
      most at high flow when the time is short. This is the likely cause of reading 4 coming out slightly below reading 3.</li>
  <li>Reading the gauges to the nearest metre, and needle flutter at high flow.</li>
  <li>Not waiting long enough for the flow to settle after moving the valve.</li>
  <li>Power read from the inverter includes motor losses, so it isn't the shaft power going into the pump.</li>
  <li>Arithmetic slips when working by hand. Slips in readings 4, 5 and 6 were found and corrected in this record.</li>
</ul>""")

look.section("04", "Precautions")
st.html("""
<ul class="prose" style="padding-left:1.2rem">
  <li>Prime the pump and check there's no air in the suction line before starting.</li>
  <li>Never run the pump for long with the delivery valve fully shut.</li>
  <li>Make sure the kW LED is flashing before noting the power.</li>
  <li>Let the gauges settle before reading, and read them at eye level.</li>
  <li>Close the measuring tank's drain fully before timing.</li>
</ul>""")

look.section("05", "Viva questions")
qa = [
    ("Why is a centrifugal pump primed before starting?",
     "The impeller can only build a small pressure in air, nowhere near enough to lift water up the suction pipe. "
     "Filling the casing and suction line with water first lets it develop full head."),
    ("Why does the head fall as the flow increases?",
     "At fixed speed the impeller gives the water a limited amount of energy. Friction and shock losses inside the "
     "pump grow roughly with flow squared, so more flow leaves less head."),
    ("Why is a centrifugal pump started with the delivery valve closed?",
     "Power drawn is lowest at shut-off, so starting there keeps the starting load on the motor low. Open the valve "
     "once the pump is up to speed."),
    ("What is the best efficiency point?",
     "The flow at which the pump converts input power to water power most efficiently. Pumps are selected to run "
     "near it, as that also minimises wear and vibration."),
    ("What are the affinity laws?",
     "For the same pump at different speeds: Q ∝ n, H ∝ n², P ∝ n³. They let you predict performance at a new speed "
     "from one measured curve."),
    ("What is cavitation and when does it happen?",
     "Vapour bubbles form where local pressure at the impeller eye drops below the water's vapour pressure, then collapse "
     "violently further in. It happens with high suction lift or high flow, and causes noise, pitting and a drop in head."),
    ("Why is the measured efficiency only about 30 %?",
     "It's overall efficiency, including motor and inverter losses. Small bench pumps are also less efficient than "
     "large ones because clearances and friction matter more at small size."),
]
for q, a in qa:
    with st.expander(q):
        st.html(f'<p class="prose">{a}</p>')
