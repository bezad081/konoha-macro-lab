import numpy as np
import plotly.graph_objects as go
from dataclasses import dataclass

PLOT_THEME = {
    "font_family": "Vazirmatn, Tahoma, sans-serif",
    "bg_color": "#ffffff",
    "grid_color": "#f1f5f9",
    "is_color": "#dc2626",
    "lm_color": "#2563eb",
    "bp_color": "#059669"
}

@dataclass
class MundellFlemingModel:
    c0: float = 60.0
    mpc: float = 0.75
    t: float = 0.20
    i0: float = 140.0
    b: float = 600.0
    G: float = 120.0
    
    M: float = 400.0
    P: float = 1.0
    k: float = 0.50
    h: float = 4000.0

    # متغیرهای تجاری با دهکده سنگ
    Y_foreign: float = 1000.0
    r_foreign: float = 0.05
    x0: float = 80.0
    x1: float = 0.10
    m0: float = 50.0
    m1: float = 0.15
    eta: float = 40.0
    exchange_rate: float = 1.0
    capital_mobility: float = 5000.0

    @property
    def open_multiplier(self) -> float:
        denom = 1.0 - self.mpc * (1.0 - self.t) + self.m1
        return 1.0 / denom if denom > 0 else 1.0

    @property
    def autonomous_open_demand(self) -> float:
        nx_auto = (self.x0 + self.x1 * self.Y_foreign) - self.m0 + (self.eta * self.exchange_rate)
        return self.c0 + self.i0 + self.G + nx_auto

    def get_is_curve(self, Y: np.ndarray) -> np.ndarray:
        alpha = self.open_multiplier
        A = self.autonomous_open_demand
        return (A / self.b) - (Y / (alpha * self.b))

    def get_lm_curve(self, Y: np.ndarray) -> np.ndarray:
        real_M = self.M / self.P
        r = (self.k * Y - real_M) / self.h
        return np.maximum(0.001, r)

    def get_bp_curve(self, Y: np.ndarray) -> np.ndarray:
        nx_auto = (self.x0 + self.x1 * self.Y_foreign) - self.m0 + (self.eta * self.exchange_rate)
        return self.r_foreign + (self.m1 * Y - nx_auto) / self.capital_mobility

    def solve_equilibrium(self):
        alpha = self.open_multiplier
        A = self.autonomous_open_demand
        real_M = self.M / self.P

        denom = (1.0 / alpha) + (self.b * self.k / self.h)
        Y_eq = (A + (self.b / self.h) * real_M) / denom
        r_eq = (self.k * Y_eq - real_M) / self.h

        if r_eq < 0.001:
            r_eq = 0.001
            Y_eq = alpha * (A - self.b * r_eq)

        exports = self.x0 + self.x1 * self.Y_foreign + self.eta * self.exchange_rate
        imports = self.m0 + self.m1 * Y_eq
        nx = exports - imports

        return {
            "Y": float(Y_eq),
            "r": float(r_eq),
            "NX": float(nx),
            "Imports": float(imports),
            "Exports": float(exports)
        }

def create_mundell_fleming_figure(base_model: MundellFlemingModel, current_model: MundellFlemingModel):
    eq0 = base_model.solve_equilibrium()
    eq1 = current_model.solve_equilibrium()

    center_y = (eq0["Y"] + eq1["Y"]) / 2.0
    y_min = max(400.0, center_y - 450.0)
    y_max = max(1350.0, center_y + 450.0)
    Y_vals = np.linspace(y_min, y_max, 250)

    is_base = np.maximum(0.001, base_model.get_is_curve(Y_vals))
    is_curr = np.maximum(0.001, current_model.get_is_curve(Y_vals))
    lm_base = base_model.get_lm_curve(Y_vals)
    lm_curr = current_model.get_lm_curve(Y_vals)
    bp_base = base_model.get_bp_curve(Y_vals)
    bp_curr = current_model.get_bp_curve(Y_vals)

    fig = go.Figure()

    # خطوط مبنا
    fig.add_trace(go.Scatter(x=Y_vals, y=is_base, mode="lines", line=dict(dash="dot", color="#cbd5e1", width=1.5), name="IS مبنا"))
    fig.add_trace(go.Scatter(x=Y_vals, y=lm_base, mode="lines", line=dict(dash="dot", color="#cbd5e1", width=1.5), name="LM مبنا"))
    fig.add_trace(go.Scatter(x=Y_vals, y=bp_base, mode="lines", line=dict(dash="dot", color="#a7f3d0", width=1.5), name="BP مبنا"))

    # خطوط جاری
    fig.add_trace(go.Scatter(
        x=Y_vals, y=is_curr, mode="lines",
        line=dict(color=PLOT_THEME["is_color"], width=3), name="منحنی IS جاری",
        hovertemplate="تولید: %{x:.1f} | بهره: %{y:.2%}<extra></extra>"
    ))
    fig.add_trace(go.Scatter(
        x=Y_vals, y=lm_curr, mode="lines",
        line=dict(color=PLOT_THEME["lm_color"], width=3), name="منحنی LM جاری",
        hovertemplate="تولید: %{x:.1f} | بهره: %{y:.2%}<extra></extra>"
    ))
    fig.add_trace(go.Scatter(
        x=Y_vals, y=bp_curr, mode="lines",
        line=dict(color=PLOT_THEME["bp_color"], width=3), name="تراز پرداخت‌ها (منحنی BP)",
        hovertemplate="تولید: %{x:.1f} | تعادل خارجی: %{y:.2%}<extra></extra>"
    ))

    # نقاط تعادل
    fig.add_trace(go.Scatter(x=[eq0["Y"]], y=[eq0["r"]], mode="markers+text", marker=dict(size=8, color="#64748b"), text=["E₀"], textposition="top right", name="تعادل اولیه E₀"))
    fig.add_trace(go.Scatter(x=[eq1["Y"]], y=[eq1["r"]], mode="markers+text", marker=dict(size=12, color="#0f172a"), text=["E₁"], textposition="top left", name="تعادل داخلی E₁"))

    # خط بهره بین‌المللی دهکده سنگ
    fig.add_shape(type="line", x0=y_min, x1=y_max, y0=current_model.r_foreign, y1=current_model.r_foreign, line=dict(dash="dash", color="#10b981", width=1))

    # فلش کنترل‌شده انتقال تعادل
    delta_y = abs(eq1["Y"] - eq0["Y"])
    delta_r = abs(eq1["r"] - eq0["r"])
    if delta_y > 15.0 or delta_r > 0.005:
        fig.add_annotation(
            ax=eq0["Y"], ay=eq0["r"], x=eq1["Y"], y=eq1["r"],
            xref="x", yref="y", axref="x", ayref="y",
            showarrow=True, arrowhead=2, arrowsize=1.3, arrowwidth=2.5, arrowcolor="#10b981"
        )

    # خطوط راهنما به محورها
    fig.add_shape(type="line", x0=eq1["Y"], x1=eq1["Y"], y0=0, y1=eq1["r"], line=dict(dash="dot", color="#94a3b8"))
    fig.add_shape(type="line", x0=y_min, x1=eq1["Y"], y0=eq1["r"], y1=eq1["r"], line=dict(dash="dot", color="#94a3b8"))

    max_r = max(0.14, eq0["r"] * 1.5, eq1["r"] * 1.5, current_model.r_foreign * 1.5)

    fig.update_xaxes(title_text="تولید ناخالص داخلی کونوها (Y)", range=[y_min, y_max], gridcolor=PLOT_THEME["grid_color"], automargin=True)
    fig.update_yaxes(title_text="نرخ بهره داخلی (r)", tickformat=".1%", range=[0.0, min(0.20, max_r)], gridcolor=PLOT_THEME["grid_color"], automargin=True)

    fig.update_layout(
        height=480, plot_bgcolor=PLOT_THEME["bg_color"], paper_bgcolor=PLOT_THEME["bg_color"],
        legend=dict(orientation="h", y=-0.22, x=0.5, xanchor="center"),
        margin=dict(l=75, r=35, t=40, b=70),
        uirevision="never"
    )
    return fig, eq0, eq1