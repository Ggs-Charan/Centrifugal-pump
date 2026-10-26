"""Live drawing of the F1-27 rig on the hydraulic bench.

Water moves through the pipes at a pace set by the flow rate, the gauge
needles sit at the current heads, and the measuring tank fills to the chosen
volume against a running stopwatch, then drains and starts again.
"""
import json

import streamlit.components.v1 as components

INK = "#23211c"
PAPER = "#f6f3ea"
BLUE = "#2a4d8f"
RED = "#b5382a"

# Measuring tank geometry (SVG units): bottom of the water and pixels per litre.
TANK_FLOOR = 268
PX_PER_L = 5.9
TANK_MAX_L = 20

FONT_LINK = ('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
             'family=IBM+Plex+Mono:wght@400;500&family=Kalam&display=swap">')


def _gauge(cx, cy, gid, label, value_id, anchor_x, anchor):
    ticks = "".join(
        f'<line x1="{cx}" y1="{cy - 15}" x2="{cx}" y2="{cy - 12}" stroke="{INK}" stroke-width="1" '
        f'transform="rotate({a} {cx} {cy})"/>' for a in range(-120, 121, 30))
    return f"""
  <circle cx="{cx}" cy="{cy}" r="17" fill="#fffdf7" stroke="{INK}" stroke-width="1.8"/>
  <path d="M{cx - 11.3} {cy + 6.5} A13 13 0 0 1 {cx + 11.3} {cy + 6.5}" fill="none" stroke="#e7dfca" stroke-width="3"/>
  {ticks}
  <line id="{gid}" x1="{cx}" y1="{cy}" x2="{cx}" y2="{cy - 12}" stroke="{RED}" stroke-width="1.8" stroke-linecap="round"/>
  <circle cx="{cx}" cy="{cy}" r="2" fill="{INK}"/>
  <text x="{anchor_x}" y="{cy - 3}" class="lb" text-anchor="{anchor}">{label}</text>
  <text x="{anchor_x}" y="{cy + 12}" class="val" text-anchor="{anchor}" id="{value_id}"></text>"""


def _tags():
    spots = [(102, 140, 1), (296, 214, 2), (178, 222, 3), (310, 79, 4),
             (546, 32, 5), (506, 152, 6), (676, 302, 7)]
    return "".join(
        f'<circle cx="{x}" cy="{y}" r="8" fill="{PAPER}" stroke="{INK}" stroke-width="1"/>'
        f'<text x="{x}" y="{y + 3.5}" class="tg" text-anchor="middle">{n}</text>' for x, y, n in spots)


def rig_html(flow_e4=9.0, opening=0.55, volume_l=10.0, collect_s=11.0,
             inlet_m=1.5, outlet_m=19.0, show_tags=False, height=440) -> str:
    q_lps = flow_e4 * 0.1                    # 1e-4 m^3/s = 0.1 L/s
    params = {
        "flow": flow_e4, "qlps": q_lps, "opening": opening, "volume": volume_l,
        "tFill": volume_l / q_lps,          # exact time the animation fills over
        "tShown": collect_s,                 # rounded reading shown when it stops
        "hi": inlet_m, "ho": outlet_m,
        "floor": TANK_FLOOR, "pxl": PX_PER_L,
    }
    mark_y = TANK_FLOOR - volume_l * PX_PER_L
    scale = "".join(
        f'<line x1="640" y1="{TANK_FLOOR - v * PX_PER_L:.1f}" x2="{647 if v % 10 == 0 else 644}" '
        f'y2="{TANK_FLOOR - v * PX_PER_L:.1f}" stroke="{INK}" stroke-width="1"/>'
        + (f'<text x="651" y="{TANK_FLOOR - v * PX_PER_L + 3:.1f}" class="sc">{v}</text>' if v % 5 == 0 else "")
        for v in range(0, TANK_MAX_L + 1))
    gate_h = 12 * (1 - opening)
    stem = 8 + 14 * opening
    vanes = "".join(
        f'<path d="M0 -8 Q 13 -19 7 -35" fill="none" stroke="{INK}" stroke-width="2.4" '
        f'stroke-linecap="round" transform="rotate({a})"/>' for a in range(0, 360, 60))

    return f"""{FONT_LINK}
<style>
  html, body {{ margin: 0; background: transparent; font-family: 'IBM Plex Mono', monospace; }}
  svg {{ width: 100%; height: auto; max-height: {height - 46}px; display: block; margin: 0 auto; }}
  .lb  {{ font: 10.5px 'IBM Plex Mono', monospace; fill: {INK}; }}
  .val {{ font: 500 11.5px 'IBM Plex Mono', monospace; fill: {BLUE}; }}
  .sc  {{ font: 9px 'IBM Plex Mono', monospace; fill: #5c574c; }}
  .tg  {{ font: 500 10px 'IBM Plex Mono', monospace; fill: {INK}; }}
  .hand {{ font: 15px 'Kalam', cursive; fill: {BLUE}; }}
  .pt {{ fill: #ffffff; opacity: .9; }}
  .drain {{ stroke-dasharray: 3 4; }}
  .drain.on {{ stroke: #6f9cc4; stroke-width: 3; animation: d .5s linear infinite; }}
  @keyframes d {{ to {{ stroke-dashoffset: -14; }} }}
  .bar {{ display: flex; gap: 6px; justify-content: center; align-items: center; margin-top: 6px; flex-wrap: wrap; }}
  .bar span {{ font-size: 11px; color: #5c574c; margin-right: 4px; }}
  .bar button {{ font: 500 11px 'IBM Plex Mono', monospace; background: #fbf9f3; color: {INK};
                 border: 1px solid {INK}; padding: 3px 10px; cursor: pointer; border-radius: 2px; }}
  .bar button.on {{ background: {INK}; color: {PAPER}; }}
</style>
<svg id="rig" viewBox="0 18 720 336" role="img" aria-label="Live schematic of the centrifugal pump test rig">
  <defs>
    <linearGradient id="wTank" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#b9d2e7"/><stop offset="1" stop-color="#7ea7cb"/>
    </linearGradient>
    <linearGradient id="wSump" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#bfd5e8"/><stop offset="1" stop-color="#94b6d4"/>
    </linearGradient>
    <linearGradient id="casing" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#fffdf7"/><stop offset="1" stop-color="#e9e2cf"/>
    </linearGradient>
    <clipPath id="tankClip"><rect x="523" y="141" width="114" height="128"/></clipPath>
  </defs>

  <!-- sump / hydraulic bench -->
  <rect x="30" y="292" width="660" height="54" fill="#fbf9f3" stroke="{INK}" stroke-width="1.8"/>
  <path id="sumpWater" fill="url(#wSump)"/>
  <text x="300" y="303" class="lb">sump &middot; hydraulic bench</text>

  <!-- pipes: ink outline, water inside, particles on top -->
  <path id="pathS" d="M235 332 L235 222" fill="none" stroke="{INK}" stroke-width="13"/>
  <path d="M235 332 L235 222" fill="none" stroke="#cfe0ee" stroke-width="8.5"/>
  <path id="pathD" d="M262 139 L262 70 L580 70 L580 128" fill="none" stroke="{INK}" stroke-width="13" stroke-linejoin="round"/>
  <path d="M262 139 L262 70 L580 70 L580 128" fill="none" stroke="#cfe0ee" stroke-width="8.5" stroke-linejoin="round"/>
  <g id="ptsS"></g><g id="ptsD"></g>

  <!-- motor and shaft -->
  <rect x="55" y="152" width="95" height="46" rx="3" fill="url(#casing)" stroke="{INK}" stroke-width="1.8"/>
  {''.join(f'<line x1="{x}" y1="156" x2="{x}" y2="162" stroke="{INK}" stroke-width="1"/>' for x in range(64, 146, 8))}
  <text x="102" y="178" class="lb" text-anchor="middle">motor</text>
  <text x="102" y="191" class="lb" text-anchor="middle">50 Hz &middot; fixed</text>
  <line x1="150" y1="175" x2="190" y2="175" stroke="{INK}" stroke-width="4"/>
  <rect x="166" y="168" width="8" height="14" fill="{INK}"/>

  <!-- pump casing and impeller -->
  <circle cx="235" cy="175" r="47" fill="url(#casing)" stroke="{INK}" stroke-width="2"/>
  <circle cx="235" cy="175" r="39" fill="none" stroke="#d8cfb8" stroke-width="1"/>
  <g transform="translate(235 175)"><g id="imp">{vanes}<circle r="7" fill="{INK}"/></g></g>

  <!-- gauges -->
  <line x1="229" y1="250" x2="195" y2="250" stroke="{INK}" stroke-width="1.6"/>
  {_gauge(178, 250, "needleI", "inlet gauge h&#7522;", "valI", 154, "end")}
  <line x1="268" y1="105" x2="293" y2="105" stroke="{INK}" stroke-width="1.6"/>
  {_gauge(310, 105, "needleO", "outlet gauge h&#8338;", "valO", 334, "start")}

  <!-- delivery valve: gate closes the pipe as the stem drops -->
  <path d="M492 58 L528 82 L528 58 L492 82 Z" fill="#fffdf7" stroke="{INK}" stroke-width="1.8"/>
  <rect x="507" y="64.5" width="6" height="{gate_h:.1f}" fill="{INK}"/>
  <line x1="510" y1="58" x2="510" y2="{58 - stem:.1f}" stroke="{INK}" stroke-width="2"/>
  <ellipse cx="510" cy="{58 - stem:.1f}" rx="13" ry="3.2" fill="#fffdf7" stroke="{INK}" stroke-width="2"/>
  <text x="510" y="98" class="lb" text-anchor="middle">delivery valve</text>
  <text x="510" y="112" class="val" text-anchor="middle">{opening * 100:.0f}% open</text>

  <!-- stream into the tank -->
  <rect id="stream" fill="#9fc0dd"/>
  <ellipse id="splash" rx="7" ry="2" fill="#ffffff" opacity=".7"/>

  <!-- measuring tank -->
  <g clip-path="url(#tankClip)">
    <rect id="tankWater" x="523" width="114" fill="url(#wTank)"/>
    <rect id="tankSurf" x="523" width="114" height="1.5" fill="#ffffff" opacity=".8"/>
  </g>
  <path d="M520 140 L520 272 L640 272 L640 140" fill="none" stroke="{INK}" stroke-width="2"/>
  <line x1="527" y1="146" x2="527" y2="262" stroke="#ffffff" stroke-width="2" opacity=".6"/>
  {scale}
  <line x1="521" y1="{mark_y:.1f}" x2="639" y2="{mark_y:.1f}" stroke="{RED}" stroke-width="1.2" stroke-dasharray="4 3"/>
  <text x="526" y="{mark_y - 4:.1f}" class="lb" fill="{RED}" style="fill:{RED}">{volume_l:g} L</text>
  <text x="580" y="286" class="lb" text-anchor="middle">measuring tank</text>
  <line id="drain" class="drain" x1="628" y1="272" x2="628" y2="300" stroke="{INK}" stroke-width="1.6"/>

  <!-- stopwatch -->
  <text x="650" y="86" class="lb" text-anchor="middle">stopwatch</text>
  <rect x="604" y="92" width="92" height="28" fill="#c5ccad" stroke="#8a9172"/>
  <text id="watch" x="690" y="112" text-anchor="end" style="font: 500 16px 'IBM Plex Mono', monospace; fill:#1c2014">0.00 s</text>
  <text id="status" x="650" y="136" class="hand" text-anchor="middle" style="font-size:13px"></text>

  <text x="330" y="210" class="hand">Q &#8776; {q_lps:.2f} L/s</text>
  {_tags() if show_tags else ""}
</svg>
<div class="bar">
  <span>playback</span>
  <button data-m="1" class="on">real time</button>
  <button data-m="5">&times;5</button>
  <button data-m="10">&times;10</button>
  <button id="restart">restart</button>
</div>
<script>
(() => {{
  const P = {json.dumps(params)};
  const NS = "http://www.w3.org/2000/svg";
  const $ = id => document.getElementById(id);
  const pathS = $("pathS"), pathD = $("pathD");
  const LS = pathS.getTotalLength(), LD = pathD.getTotalLength();
  const GAP = 15;

  function particles(g, L) {{
    const out = [];
    for (let i = 0; i < Math.floor(L / GAP); i++) {{
      const c = document.createElementNS(NS, "circle");
      c.setAttribute("r", 1.8); c.setAttribute("class", "pt"); g.appendChild(c); out.push(c);
    }}
    return out;
  }}
  const ps = particles($("ptsS"), LS), pd = particles($("ptsD"), LD);
  function place(arr, path, L, off) {{
    arr.forEach((c, i) => {{
      const p = path.getPointAtLength((i * GAP + off) % L);
      c.setAttribute("cx", p.x); c.setAttribute("cy", p.y);
    }});
  }}

  function needle(id, value, full, wobble) {{
    const a = -120 + 240 * Math.min(1, Math.max(0, value / full)) + wobble;
    const n = $(id); n.setAttribute("transform", `rotate(${{a.toFixed(2)}} ${{n.getAttribute("x1")}} ${{n.getAttribute("y1")}})`);
  }}
  $("valI").textContent = `${{P.hi.toFixed(1)}} m`;
  $("valO").textContent = `${{P.ho.toFixed(1)}} m`;

  let mult = 1, phase = "fill", simT = 0, phaseT = 0, level = 0, off = 0, spin = 0, last = null;
  document.querySelectorAll(".bar button[data-m]").forEach(b => b.onclick = () => {{
    mult = +b.dataset.m;
    document.querySelectorAll(".bar button[data-m]").forEach(x => x.classList.toggle("on", x === b));
  }});
  $("restart").onclick = () => {{ phase = "fill"; simT = 0; level = 0; }};

  const speed = 18 + 9 * P.flow;   // particle pace, px per second
  function frame(now) {{
    const dt = last === null ? 0 : Math.min(0.1, (now - last) / 1000);
    last = now;

    off = (off + speed * dt) % 100000;
    place(ps, pathS, LS, off); place(pd, pathD, LD, off);
    spin = (spin + 540 * dt) % 360;
    $("imp").setAttribute("transform", `rotate(${{spin.toFixed(1)}})`);

    const t = now / 1000;
    needle("needleI", P.hi, 5, Math.sin(t * 7.1) * 0.6);
    needle("needleO", P.ho, 25, Math.sin(t * 9.3) * 0.8 + Math.sin(t * 23) * 0.4 * P.flow / 10);

    if (phase === "fill") {{
      simT += dt * mult;
      level = P.qlps * simT;
      $("watch").textContent = `${{simT.toFixed(2)}} s`;
      $("status").textContent = "collecting…";
      if (simT >= P.tFill) {{ phase = "hold"; phaseT = 0; level = P.volume; }}
    }} else if (phase === "hold") {{
      phaseT += dt;
      $("watch").textContent = `${{P.tShown.toFixed(2)}} s`;
      $("status").textContent = `✓ ${{P.volume}} L in ${{P.tShown.toFixed(2)}} s`;
      if (phaseT > 2.2) {{ phase = "drain"; phaseT = 0; }}
    }} else {{
      phaseT += dt;
      level = Math.max(0, P.volume * (1 - phaseT / 1.6));
      $("status").textContent = "draining";
      if (phaseT > 1.8) {{ phase = "fill"; simT = 0; level = 0; }}
    }}
    $("drain").classList.toggle("on", phase === "drain");

    const surf = P.floor - level * P.pxl;
    $("tankWater").setAttribute("y", surf); $("tankWater").setAttribute("height", Math.max(0, P.floor + 1 - surf));
    $("tankSurf").setAttribute("y", surf - 0.5);
    const w = 3 + 0.55 * P.flow;
    const st = $("stream");
    st.setAttribute("x", 580 - w / 2); st.setAttribute("y", 128);
    st.setAttribute("width", w); st.setAttribute("height", Math.max(0, surf - 128));
    $("splash").setAttribute("cx", 580); $("splash").setAttribute("cy", surf);

    let d = "M31 312";
    for (let x = 31; x <= 689; x += 14) d += ` L${{x}} ${{(312 + 1.4 * Math.sin(x * 0.045 + t * 1.8)).toFixed(2)}}`;
    $("sumpWater").setAttribute("d", d + " L689 345 L31 345 Z");

    if (!still) requestAnimationFrame(frame);
  }}
  const still = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (still) {{ simT = P.tFill * 0.6; }}
  requestAnimationFrame(frame);
}})();
</script>
"""


def draw(height: int = 440, **kwargs):
    # st.html sanitises SVG and scripts away, so the rig runs in its own small frame.
    components.html(rig_html(height=height, **kwargs), height=height)


PARTS = [
    ("1", "Motor", "Drives the pump through an inverter at a fixed 50 Hz for the whole experiment."),
    ("2", "Centrifugal pump (F1-27)", "Single stage. The impeller flings water outward and the casing turns that speed into pressure."),
    ("3", "Inlet gauge, hᵢ", "Pressure of the water just before it enters the pump (suction side), read as metres of water."),
    ("4", "Outlet gauge, hₒ", "Pressure of the water just after it leaves the pump (delivery side), read as metres of water."),
    ("5", "Delivery valve", "The only thing changed between readings. Closing it raises the outlet pressure and cuts the flow."),
    ("6", "Measuring tank", "Time how long a known volume takes to collect; that gives the flow rate."),
    ("7", "Sump", "The digital hydraulic bench's reservoir. The pump draws from it and the tank drains back into it."),
]
