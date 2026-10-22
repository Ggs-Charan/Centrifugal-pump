import streamlit as st

from lab import look, state

ss = st.session_state

look.header(
    "Observations & calculations",
    "Readings at 50 Hz",
    "These are the six readings from the record book. Edit any measured value, or add a row, "
    "and every calculated column, graph and result on the site updates to match.",
)

look.section("01", "Observation table")
st.caption("Only measured and set quantities can be edited. The calculated values are in the next table.")

base = state.readings()
edited = st.data_editor(
    base,
    key=f"readings_editor_{ss.editor_version}",
    num_rows="dynamic",
    hide_index=True,
    width="stretch",
    column_config={
        "speed_hz": st.column_config.NumberColumn("Motor speed n (Hz)", min_value=10.0, max_value=60.0, step=1.0, format="%.0f"),
        "volume_l": st.column_config.NumberColumn("Volume V (L)", min_value=0.5, step=0.5, format="%.1f"),
        "time_s":   st.column_config.NumberColumn("Time t (s)", min_value=0.01, step=0.01, format="%.2f"),
        "inlet_m":  st.column_config.NumberColumn("Inlet head hᵢ (m)", step=0.1, format="%.2f"),
        "outlet_m": st.column_config.NumberColumn("Outlet head hₒ (m)", step=0.5, format="%.2f"),
        "power_w":  st.column_config.NumberColumn("Input power Wᵢ (W)", min_value=1.0, step=10.0, format="%.0f"),
    },
)
edited = edited.astype(float).reset_index(drop=True)
if not edited.equals(base.astype(float).reset_index(drop=True)):
    ss.readings = edited
    ss.editor_version += 1
    st.rerun()

c1, c2, _ = st.columns([1, 1, 2])
with c1:
    new_datum = st.number_input("Datum head Hd (m)", value=float(ss.datum), step=0.01, format="%.2f")
    if new_datum != ss.datum:
        ss.datum = new_datum
        st.rerun()
with c2:
    st.html('<div style="height:1.75rem"></div>')
    if st.button("Restore original readings", disabled=state.is_original()):
        state.reset()
        st.rerun()

calc = state.calculated()
if calc.empty:
    st.warning("No complete readings to calculate from.")
    st.stop()

look.section("02", "Calculated values")
rows = "".join(
    "<tr>"
    f'<td class="num">{i + 1}</td>'
    f'<td class="num">{r.time_s:.2f}</td>'
    f'<td class="num">{r.flow_e4:.3f}</td>'
    f'<td class="num">{r.head_m:.2f}</td>'
    f'<td class="num">{r.power_w:.0f}</td>'
    f'<td class="num">{r.out_w:.2f}</td>'
    f'<td class="num">{r.eff_pct:.1f}</td>'
    "</tr>"
    for i, r in calc.iterrows())
st.html(f"""
<table class="rec">
<tr><th class="num">No.</th><th class="num">t (s)</th><th class="num">Q (&times;10&#8315;&#8308; m&sup3;/s)</th>
<th class="num">H (m)</th><th class="num">W&#7522; (W)</th><th class="num">W&#8338; (W)</th><th class="num">&eta; (%)</th></tr>
{rows}
</table>""")

look.section("03", "Worked example")
n = st.segmented_control("Reading", options=list(range(1, len(calc) + 1)), default=min(3, len(calc)),
                         format_func=lambda i: f"No. {i}")
r = calc.iloc[(n or 1) - 1]
steps = [
    ("Flow rate", rf"Q = \frac{{V}}{{t}} = \frac{{{r.volume_l:g}\times10^{{-3}}}}{{{r.time_s:.2f}}} = {r.flow_e4:.3f}\times10^{{-4}}\ \mathrm{{m^3/s}}"),
    ("Total head", rf"H = H_d + (h_o - h_i) = {ss.datum:.2f} + ({r.outlet_m:g} - {r.inlet_m:g}) = {r.head_m:.2f}\ \mathrm{{m}}"),
    ("Output power", rf"W_o = \rho g Q H = 9810 \times {r.flow_e4:.3f}\times10^{{-4}} \times {r.head_m:.2f} = {r.out_w:.2f}\ \mathrm{{W}}"),
    ("Efficiency", rf"\eta = \frac{{W_o}}{{W_i}} \times 100 = \frac{{{r.out_w:.2f}}}{{{r.power_w:.0f}}} \times 100 = {r.eff_pct:.1f}\ \%"),
]
for label, eq in steps:
    a, b = st.columns([1, 4], vertical_alignment="center")
    a.markdown(f"**{label}**")
    b.latex(eq)

look.section("04", "Export")
export = calc.rename(columns={
    "speed_hz": "n (Hz)", "volume_l": "V (L)", "time_s": "t (s)", "inlet_m": "hi (m)", "outlet_m": "ho (m)",
    "power_w": "Wi (W)", "flow": "Q (m3/s)", "flow_e4": "Q (x1e-4 m3/s)", "head_m": "H (m)",
    "out_w": "Wo (W)", "eff_pct": "eta (%)"})
st.download_button("Download table as CSV", export.round(4).to_csv(index_label="No.").encode(),
                   file_name="centrifugal_pump_readings.csv", mime="text/csv")
