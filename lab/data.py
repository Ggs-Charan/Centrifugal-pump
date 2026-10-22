"""Readings, calculations and the fitted pump model for Experiment 9.

Nothing in here touches Streamlit, so it can be tested on its own.
The chain of dependence follows the lab manual:

    set by you      ->  read off the rig        ->  worked out
    speed n, valve      t, h_i, h_o, W_i            Q, H, W_o, eta
"""
import numpy as np
import pandas as pd

RHO = 1000.0          # kg/m^3, water
G = 9.81              # m/s^2
N_RATED = 50.0        # Hz, all six readings were taken at this speed
DATUM_HEAD = 0.15     # m, H_d (15 cm, printed under the observation table)
VOLUME_L = 10.0       # litres collected for each reading

# Readings exactly as entered in the record book.
RECORDED = pd.DataFrame({
    "speed_hz": [50.0] * 6,
    "volume_l": [VOLUME_L] * 6,
    "time_s":   [40.70, 19.70, 11.01, 11.15, 10.03, 8.59],
    "inlet_m":  [1.5] * 6,
    "outlet_m": [21.0, 20.0, 19.0, 18.0, 17.0, 16.0],
    "power_w":  [390.0, 480.0, 520.0, 530.0, 560.0, 570.0],
})

# The calculated columns as they were first written by hand. Kept only so the
# site can show where the arithmetic was corrected.
HANDWRITTEN = pd.DataFrame({
    "flow_e4": [2.45, 5.07, 9.08, 8.968, 9.97, 11.16],
    "head_m":  [19.65, 18.65, 17.65, 16.65, 15.65, 14.65],
    "out_w":   [47.22, 92.75, 157.21, 146.48, 153.04, 160.38],
    "eff_pct": [12.0, 19.0, 30.0, 27.0, 28.0, 28.0],
})

INPUT_COLUMNS = list(RECORDED.columns)


def calculate(readings: pd.DataFrame, datum: float = DATUM_HEAD) -> pd.DataFrame:
    """Work out Q, H, W_o and efficiency from the measured columns."""
    df = readings[INPUT_COLUMNS].astype(float).copy()
    df["flow"] = df.volume_l / 1000.0 / df.time_s           # m^3/s
    df["flow_e4"] = df.flow * 1e4                           # x10^-4 m^3/s
    df["head_m"] = datum + (df.outlet_m - df.inlet_m)       # H = H_d + (h_o - h_i)
    df["out_w"] = RHO * G * df.head_m * df.flow             # W_o = rho g Q H
    df["eff_pct"] = df.out_w / df.power_w * 100.0           # eta = W_o / W_i
    return df


def design_point(calc: pd.DataFrame) -> pd.Series:
    """The reading with the highest efficiency, which the manual calls the design point."""
    return calc.loc[calc.eff_pct.idxmax()]


def corrections(calc: pd.DataFrame) -> list[dict]:
    """Cells where the handwritten value disagrees with the recomputed one."""
    tolerance = {"flow_e4": 0.02, "head_m": 0.02, "out_w": 0.6, "eff_pct": 0.6}
    found = []
    if len(calc) != len(HANDWRITTEN):
        return found
    for col, tol in tolerance.items():
        for i, (written, actual) in enumerate(zip(HANDWRITTEN[col], calc[col])):
            if abs(written - actual) > tol:
                found.append({"row": i, "col": col, "written": written, "actual": actual})
    return found


class PumpModel:
    """Pump curves fitted to the readings at 50 Hz, scaled to other speeds.

    Flow is handled in units of 1e-4 m^3/s (call it q) to keep the
    polynomial coefficients readable.

    Head:  H(q, r) = A r^2 + B r q + C q^2        (r = n / 50 Hz)
    Power: W_i(q, r) = r^3 P(q / r)               (P fitted at 50 Hz)

    Both forms obey the affinity laws, so the 50 Hz fit carries over to
    other speeds. The delivery valve is modelled as a resistance,
    H_sys = k q^2, with k growing as the valve closes.
    """

    def __init__(self, calc: pd.DataFrame):
        q = calc.flow_e4.to_numpy()
        self.C, self.B, self.A = np.polyfit(q, calc.head_m.to_numpy(), 2)
        self.power_coef = np.polyfit(q, calc.power_w.to_numpy(), 2)
        self.q_tested = (float(q.min()), float(q.max()))
        # Fully open valve lets the pump reach roughly 12e-4 m^3/s at 50 Hz,
        # a little past the largest flow measured on the day.
        self.k_open = float(self.head(12.0) / 12.0**2)

    def head(self, q, speed_hz=N_RATED):
        r = speed_hz / N_RATED
        return self.A * r * r + self.B * r * q + self.C * q * q

    def power(self, q, speed_hz=N_RATED):
        r = speed_hz / N_RATED
        return r**3 * np.polyval(self.power_coef, q / r)

    def efficiency(self, q, speed_hz=N_RATED):
        return RHO * G * self.head(q, speed_hz) * q * 1e-4 / self.power(q, speed_hz) * 100.0

    def system_k(self, opening: float) -> float:
        """Valve resistance for an opening between 0 and 1."""
        return self.k_open / max(opening, 0.05) ** 2

    def system_head(self, q, opening):
        return self.system_k(opening) * q * q

    def operating_flow(self, speed_hz: float, opening: float) -> float:
        """Where the pump curve meets the valve's system curve (q, x1e-4 m^3/s)."""
        r = speed_hz / N_RATED
        a = self.C - self.system_k(opening)
        b = self.B * r
        c = self.A * r * r
        return float((-b - np.sqrt(b * b - 4 * a * c)) / (2 * a))

    def bench_readings(self, speed_hz: float, opening: float,
                       volume_l: float = VOLUME_L, inlet_m: float = 1.5,
                       datum: float = DATUM_HEAD) -> dict:
        """What the instruments would show, rounded to how they are read in the lab.

        Stopwatch to 0.01 s, outlet gauge to 0.5 m, inverter display to 10 W.
        The inlet gauge stayed at 1.5 m for every reading on the day, so it is
        held there.
        """
        q = self.operating_flow(speed_hz, opening)
        head = self.head(q, speed_hz)
        return {
            "speed_hz": float(speed_hz),
            "volume_l": float(volume_l),
            "time_s": round(volume_l / 1000.0 / (q * 1e-4), 2),
            "inlet_m": inlet_m,
            "outlet_m": round((head - datum + inlet_m) * 2) / 2,
            "power_w": round(float(self.power(q, speed_hz)) / 10) * 10,
            "_q_true": q,
        }

    def best_efficiency(self, speed_hz=N_RATED):
        r = speed_hz / N_RATED
        q = np.linspace(self.q_tested[0] * r, 12.5 * r, 400)
        e = self.efficiency(q, speed_hz)
        i = int(np.argmax(e))
        return float(q[i]), float(e[i])
