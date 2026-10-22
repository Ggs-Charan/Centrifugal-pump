"""Line-drawing of the F1-27 rig on the hydraulic bench, lightly animated.

Impeller spin follows motor speed, the water dashes follow flow rate and the
measuring tank fills in proportion to the real collection time.
"""
import streamlit.components.v1 as components

INK = "#23211c"
PAPER = "#f6f3ea"
WATER = "#9dbbd6"
FLOW = "#2a4d8f"
RED = "#b5382a"


def _needle(cx, cy, value, full_scale):
    """Gauge needle sweeping -120 to +120 degrees across the scale."""
    frac = max(0.0, min(1.0, value / full_scale))
    angle = -120 + 240 * frac
    return (f'<line x1="{cx}" y1="{cy}" x2="{cx}" y2="{cy - 9}" stroke="{RED}" stroke-width="1.6" '
            f'stroke-linecap="round" transform="rotate({angle:.0f} {cx} {cy})"/>')


def _gauge(cx, cy, value, full_scale, label):
    ticks = "".join(
        f'<line x1="{cx}" y1="{cy - 12}" x2="{cx}" y2="{cy - 10}" stroke="{INK}" stroke-width="1" '
        f'transform="rotate({a} {cx} {cy})"/>' for a in range(-120, 121, 40))
    return (f'<circle cx="{cx}" cy="{cy}" r="13" fill="#fbf9f3" stroke="{INK}" stroke-width="1.5"/>'
            f'{ticks}{_needle(cx, cy, value, full_scale)}'
            f'<circle cx="{cx}" cy="{cy}" r="1.6" fill="{INK}"/>'
            f'<text x="{cx}" y="{cy + 27}" class="lb" text-anchor="middle">{label}</text>')


def _pipe(d, flow_class="flow"):
    return (f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="10" stroke-linejoin="round"/>'
            f'<path d="{d}" fill="none" stroke="{PAPER}" stroke-width="7" stroke-linejoin="round"/>'
            f'<path d="{d}" fill="none" stroke="{FLOW}" stroke-width="2.4" class="{flow_class}"/>')


def _tag(x, y, n):
    return (f'<circle cx="{x}" cy="{y}" r="8" fill="{PAPER}" stroke="{INK}" stroke-width="1"/>'
            f'<text x="{x}" y="{y + 3.5}" class="tg" text-anchor="middle">{n}</text>')


def bench_svg(speed_hz=50.0, flow_e4=9.0, opening=0.6, collect_s=11.0,
              inlet_m=1.5, outlet_m=19.0, show_tags=True) -> str:
    # Animation timings. Kept within a calm range so slow flows still move
    # and fast ones don't flicker.
    spin_s = max(0.25, min(2.0, 0.45 * 50.0 / max(speed_hz, 1)))
    flow_s = max(0.5, min(4.0, 9.0 / max(flow_e4, 0.5)))
    fill_s = max(3.0, min(14.0, collect_s / 3.0))

    vane = "M0 -7 Q 11 -16 6 -30"
    vanes = "".join(
        f'<path d="{vane}" fill="none" stroke="{INK}" stroke-width="2" stroke-linecap="round" '
        f'transform="rotate({a})"/>' for a in range(0, 360, 60))

    # Valve drawn as the usual bow-tie; the hand-wheel stem rises as it opens.
    stem = 10 + 12 * opening
    valve = (f'<path d="M366 49 L394 71 L394 49 L366 71 Z" fill="{PAPER}" stroke="{INK}" stroke-width="1.5"/>'
             f'<line x1="380" y1="60" x2="380" y2="{60 - stem - 6:.1f}" stroke="{INK}" stroke-width="1.5"/>'
             f'<line x1="370" y1="{60 - stem - 6:.1f}" x2="390" y2="{60 - stem - 6:.1f}" stroke="{INK}" stroke-width="2.2"/>')

    tags = ""
    if show_tags:
        tags = (_tag(87, 116, 1) + _tag(248, 172, 2) + _tag(132, 236, 3) + _tag(290, 98, 4)
                + _tag(408, 30, 5) + _tag(586, 128, 6) + _tag(612, 262, 7))

    return f"""
<div class="rig">
<style>
  .rig svg {{ width: 100%; height: auto; display: block; }}
  .rig .lb {{ font: 10.5px 'IBM Plex Mono', monospace; fill: {INK}; }}
  .rig .tg {{ font: 500 10px 'IBM Plex Mono', monospace; fill: {INK}; }}
  .rig .hand {{ font: 15px 'Kalam', cursive; fill: {FLOW}; }}
  .rig .imp {{ animation: rig-spin {spin_s:.2f}s linear infinite; transform-origin: 0 0; }}
  .rig .flow {{ stroke-dasharray: 6 10; animation: rig-flow {flow_s:.2f}s linear infinite; }}
  .rig .fill {{ transform-box: fill-box; transform-origin: 50% 100%; animation: rig-fill {fill_s:.1f}s linear infinite; }}
  @keyframes rig-spin {{ to {{ transform: rotate(360deg); }} }}
  @keyframes rig-flow {{ to {{ stroke-dashoffset: -32; }} }}
  @keyframes rig-fill {{ 0% {{ transform: scaleY(.04); }} 92% {{ transform: scaleY(1); }} 100% {{ transform: scaleY(1); }} }}
  @media (prefers-reduced-motion: reduce) {{ .rig .imp, .rig .flow, .rig .fill {{ animation: none; }} }}
</style>
<svg viewBox="0 0 640 320" role="img" aria-label="Schematic of the centrifugal pump test rig">
  <!-- sump / hydraulic bench -->
  <rect x="30" y="252" width="580" height="56" fill="none" stroke="{INK}" stroke-width="1.6"/>
  <rect x="31" y="270" width="578" height="37" fill="{WATER}" opacity=".55"/>
  <text x="232" y="265" class="lb">sump &middot; hydraulic bench</text>

  <!-- pipes: suction, delivery, drain -->
  {_pipe("M200 292 L200 192")}
  {_pipe("M226 120 L226 60 L500 60 L500 116")}
  <path d="M556 230 L556 270" fill="none" stroke="{INK}" stroke-width="1.4" stroke-dasharray="4 4"/>
  <text x="562" y="265" class="lb">drain</text>

  <!-- motor and shaft -->
  <rect x="48" y="128" width="78" height="44" fill="#fbf9f3" stroke="{INK}" stroke-width="1.6"/>
  <text x="87" y="147" class="lb" text-anchor="middle">motor</text>
  <text x="87" y="162" class="lb" text-anchor="middle">{speed_hz:.0f} Hz</text>
  <line x1="126" y1="150" x2="160" y2="150" stroke="{INK}" stroke-width="3"/>

  <!-- pump casing and impeller -->
  <circle cx="200" cy="150" r="41" fill="#fbf9f3" stroke="{INK}" stroke-width="1.8"/>
  <g transform="translate(200 150)"><g class="imp">{vanes}<circle r="6" fill="{INK}"/></g></g>

  <!-- gauges -->
  <line x1="200" y1="226" x2="176" y2="226" stroke="{INK}" stroke-width="1.4"/>
  {_gauge(162, 226, inlet_m, 5.0, "h&#7522;")}
  <line x1="226" y1="86" x2="248" y2="86" stroke="{INK}" stroke-width="1.4"/>
  {_gauge(262, 86, outlet_m, 25.0, "h&#8338;")}

  <!-- delivery valve -->
  {valve}
  <text x="380" y="90" class="lb" text-anchor="middle">{opening * 100:.0f}% open</text>

  <!-- measuring tank -->
  <rect x="456" y="118" width="112" height="112" fill="none" stroke="{INK}" stroke-width="1.6"/>
  <rect x="457" y="129" width="110" height="100" fill="{WATER}" opacity=".7" class="fill"/>
  <line x1="456" y1="140" x2="568" y2="140" stroke="{RED}" stroke-width="1" stroke-dasharray="3 3"/>
  <text x="462" y="136" class="lb" fill="{RED}">10 L</text>
  <text x="500" y="244" class="lb" text-anchor="middle">measuring tank</text>

  <text x="292" y="196" class="hand">t &#8776; {collect_s:.1f} s for 10 L</text>
  {tags}
</svg>
</div>
"""


FONT_LINK = ('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
             'family=IBM+Plex+Mono:wght@400;500&family=Kalam&display=swap">')


def draw(height: int = 340, **kwargs):
    # st.html sanitises SVG away, so the drawing goes in its own small frame.
    components.html(
        f'{FONT_LINK}<style>html,body{{margin:0;background:transparent}}'
        f'.rig svg{{max-height:{height - 6}px;margin:0 auto}}</style>{bench_svg(**kwargs)}',
        height=height,
    )


PARTS = [
    ("1", "Motor", "Driven through an inverter, so speed is set in Hz. All readings were taken at 50 Hz."),
    ("2", "Centrifugal pump (F1-27)", "Single stage. The impeller flings water outward and the casing turns that speed into pressure."),
    ("3", "Inlet gauge", "Head at the pump inlet, hᵢ."),
    ("4", "Outlet gauge", "Head just after the pump, hₒ."),
    ("5", "Delivery valve", "The only thing changed between readings. Closing it raises head and cuts flow."),
    ("6", "Measuring tank", "Time how long 10 litres takes to collect; that gives the flow rate."),
    ("7", "Sump", "The digital hydraulic bench's reservoir. Water drains back here."),
]
