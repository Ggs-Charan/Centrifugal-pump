"""Shared styling: page CSS, small HTML helpers and the graph-paper chart style."""
import streamlit as st

INK = "#23211c"
INK_SOFT = "#5c574c"
PAPER = "#f6f3ea"
RULE = "#d6cdb6"
BLUE = "#2a4d8f"     # ballpoint
RED = "#b5382a"      # correction pen
GRID = "#c4d4b6"     # graph sheet, major
GRID_MINOR = "#e2eadb"
WATER = "#9dbbd6"

CSS = """
<style>
/* Loaded here as well as in config.toml: on Streamlit Cloud the theme's font URLs don't always load. */
@import url('https://fonts.googleapis.com/css2?family=Kalam:wght@400;700&family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600&family=Source+Serif+4:opsz,wght@8..60,500;8..60,600&display=swap');

:root {
  --ink: #23211c; --ink-soft: #5c574c; --paper: #f6f3ea; --rule: #d6cdb6;
  --blue: #2a4d8f; --red: #b5382a; --olive: #5f7a4f;
  --mono: 'IBM Plex Mono', ui-monospace, monospace;
  --hand: 'Kalam', 'Segoe Print', cursive;
}

[data-testid="stAppViewContainer"] {
  background-color: var(--paper);
  background-image:
    linear-gradient(rgba(111,143,94,.07) 1px, transparent 1px),
    linear-gradient(90deg, rgba(111,143,94,.07) 1px, transparent 1px);
  background-size: 22px 22px;
}
[data-testid="stHeader"] {
  background: rgba(246,243,234,.94);
  border-bottom: 1px solid var(--rule);
}
[data-testid="stMainBlockContainer"] {
  max-width: 1100px;
  padding-top: 4.2rem;
  padding-bottom: 4rem;
}

/* page header */
.kicker {
  font-family: var(--mono); font-size: .76rem; letter-spacing: .14em;
  text-transform: uppercase; color: var(--ink-soft); margin-bottom: .2rem;
}
.lede { font-size: 1.08rem; color: var(--ink-soft); max-width: 64ch; line-height: 1.6; }
h1 { letter-spacing: -.01em; }

/* numbered section headings, like a record book */
.sec {
  display: flex; align-items: baseline; gap: .7rem;
  border-bottom: 1px solid var(--ink); padding-bottom: .3rem; margin: 2.2rem 0 1rem;
  font-family: 'Source Serif 4', Georgia, serif; font-size: 1.45rem; font-weight: 600;
}
.sec .no { font-family: var(--mono); font-size: .85rem; color: var(--blue); font-weight: 500; }

/* margin notes in pen */
.pen { font-family: var(--hand); color: var(--blue); font-size: 1.12rem; line-height: 1.35; }
.pen.red { color: var(--red); }
.note {
  font-family: var(--hand); color: var(--blue); font-size: 1.08rem; line-height: 1.4;
  border-left: 2px solid var(--blue); padding: .1rem 0 .1rem .8rem; margin: .8rem 0;
  transform: rotate(-.4deg);
}
.note.red { color: var(--red); border-color: var(--red); }

/* plain prose blocks */
.prose { max-width: 70ch; line-height: 1.65; }
.prose b { font-weight: 600; }

/* record-book table */
table.rec { border-collapse: collapse; width: 100%; font-size: .9rem; margin: .4rem 0 1rem; }
table.rec th {
  font-family: var(--mono); font-weight: 500; font-size: .78rem; letter-spacing: .02em;
  color: var(--ink-soft); text-align: left;
  border-bottom: 1.5px solid var(--ink); padding: .45rem .5rem; vertical-align: bottom;
}
table.rec td { border-bottom: 1px solid var(--rule); padding: .45rem .5rem; vertical-align: top; }
table.rec td.num { font-family: var(--mono); text-align: right; white-space: nowrap; }
table.rec th.num { text-align: right; }

/* role tags in the variable table */
.tag {
  display: inline-block; font-family: var(--mono); font-size: .68rem; letter-spacing: .06em;
  text-transform: uppercase; border: 1px solid currentColor; border-radius: 2px;
  padding: 0 .35rem; line-height: 1.5;
}
.tag.set { color: var(--blue); }
.tag.read { color: #8a5a12; }
.tag.given { color: var(--ink-soft); }
.tag.calc { color: var(--olive); }

/* chain of dependence */
.chain { display: grid; grid-template-columns: 1fr auto 1fr auto 1fr; gap: .6rem; align-items: stretch; margin: .6rem 0 1rem; }
.chain .box { border: 1px solid var(--ink); background: #fbf9f3; padding: .8rem .9rem; }
.chain .box h4 { margin: 0 0 .4rem; font-family: var(--mono); font-size: .74rem; letter-spacing: .1em; text-transform: uppercase; font-weight: 500; }
.chain .box ul { margin: 0; padding-left: 1.1rem; font-size: .92rem; line-height: 1.55; }
.chain .arrow { align-self: center; font-family: var(--mono); color: var(--ink-soft); font-size: 1.2rem; }
@media (max-width: 760px) {
  .chain { grid-template-columns: 1fr; }
  .chain .arrow { transform: rotate(90deg); justify-self: center; }
}

/* instrument read-outs on the virtual bench */
.panel { display: grid; grid-template-columns: repeat(4, 1fr); gap: .7rem; margin: .4rem 0 .6rem; }
@media (max-width: 760px) { .panel { grid-template-columns: repeat(2, 1fr); } }
.inst { border: 1px solid var(--ink); background: #fbf9f3; padding: .55rem .7rem .6rem; }
.inst .lbl { font-family: var(--mono); font-size: .76rem; letter-spacing: .02em; color: var(--ink-soft); }
.lcd {
  margin-top: .35rem; background: #c5ccad; color: #1c2014; border: 1px solid #8a9172;
  box-shadow: inset 0 1px 3px rgba(0,0,0,.25); font-family: var(--mono); font-size: 1.55rem;
  padding: .15rem .5rem; text-align: right; letter-spacing: .04em;
}
.lcd small { font-size: .78rem; margin-left: .25rem; }
.inst .sub { font-size: .78rem; color: var(--ink-soft); margin-top: .3rem; }

/* result sheet */
.result { border: 1px solid var(--ink); background: #fbf9f3; padding: 1rem 1.2rem; max-width: 640px; }
.result .row { display: flex; justify-content: space-between; border-bottom: 1px dotted var(--rule); padding: .45rem 0; }
.result .row:last-child { border-bottom: 0; }
.result .val { font-family: var(--hand); color: var(--blue); font-size: 1.25rem; }

/* metrics: ruled, not boxed */
[data-testid="stMetric"] { border-left: 2px solid var(--ink); padding: .1rem 0 .1rem .8rem; }
[data-testid="stMetricValue"] { font-family: var(--mono); font-size: 1.7rem; }
[data-testid="stMetricLabel"] p { font-family: var(--mono); font-size: .8rem; letter-spacing: .02em; }

/* page links read like cross-references */
[data-testid="stPageLink"] a { border-bottom: 1px solid var(--ink); border-radius: 0; padding-left: 0; }
[data-testid="stPageLink"] a:hover { background: transparent; border-color: var(--blue); }
[data-testid="stPageLink"] a p::after { content: "  \\2192"; color: var(--blue); }

/* buttons */
.stButton button, .stDownloadButton button { border: 1px solid var(--ink); font-weight: 500; }

.foot {
  margin-top: 3.5rem; padding-top: .8rem; border-top: 1px solid var(--rule);
  font-family: var(--mono); font-size: .72rem; color: var(--ink-soft); letter-spacing: .04em;
}
</style>
"""


def apply():
    st.html(CSS)


def header(kicker: str, title: str, lede: str = ""):
    st.html(f'<div class="kicker">{kicker}</div>')
    st.title(title, anchor=False)
    if lede:
        st.html(f'<p class="lede">{lede}</p>')


def section(no: str, title: str):
    st.html(f'<div class="sec"><span class="no">{no}</span>{title}</div>')


def note(text: str, red: bool = False):
    st.html(f'<div class="note{" red" if red else ""}">{text}</div>')


def footer():
    st.html('<div class="foot">Fluid Machinery Laboratory &middot; Experiment 9 &middot; '
            'Performance of a single-stage centrifugal pump</div>')


def graph_paper(fig, height: int = 360, legend: bool = False):
    """Style a Plotly figure like the green graph sheet in the record book."""
    axis = dict(
        showline=True, linecolor=INK, linewidth=1, mirror=True,
        ticks="outside", tickcolor=INK, ticklen=4,
        gridcolor=GRID, gridwidth=1, zeroline=False,
        minor=dict(showgrid=True, gridcolor=GRID_MINOR, gridwidth=1),
        title_font=dict(family="IBM Plex Sans, sans-serif", size=13, color=INK),
    )
    fig.update_xaxes(**axis)
    fig.update_yaxes(**axis)
    fig.update_layout(
        height=height,
        margin=dict(l=60, r=18, t=18 if not legend else 40, b=52),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#fbfaf4",
        font=dict(family="IBM Plex Mono, monospace", size=12, color=INK),
        showlegend=legend,
        legend=dict(orientation="h", x=0, y=1.02, yanchor="bottom", bgcolor="rgba(0,0,0,0)",
                    font=dict(family="IBM Plex Sans, sans-serif", size=12)),
        hoverlabel=dict(bgcolor="#fbf9f3", bordercolor=INK,
                        font=dict(family="IBM Plex Mono, monospace", color=INK)),
    )
    return fig


# Marker used for every measured point: the circled dot drawn on graph sheets.
POINT = dict(symbol="circle-open-dot", size=11, color=BLUE, line=dict(width=1.6))
