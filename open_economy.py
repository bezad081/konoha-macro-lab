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
    # پارامترهای داخلی کونوها
    c0: float = 60.0
    mpc: float = 0.75
    t: float = 0.20
    i0: float = 140.0
    b: float = 600.0
    G: float = 120.0
    
    # بازار پول کونوها
    M: float = 400.0
    P: float = 1.0
    k: float = 0.50
    h: float = 4000.0

    # پارامترهای بخش خارجی (دهکده سنگ و خاک - ایواگاکوره)
    Y_foreign: float = 1000.0     # درآمد دهکده سنگ (Y*)
    r_foreign: float = 0.05       # نرخ بهره جهانی دهکده سنگ (r*)
    x0: float = 80.0              # صادرات خودگردان
    x1: float = 0.10              # کشش صادرات به تقاضای دهکده سنگ
    m0: float = 50.0              # واردات خودگردان
    m1: float = 0.15              # میل نهایی به واردات
    eta: float = 40.0             # کشش تجاری به نرخ ارز
    exchange_rate: float = 1.0    # برابری نرخ ارز (e)
    capital_mobility: float = 5000.0 # درجه تحرک بین‌المللی سرمایه

    @property
    def open_multiplier(self) -> float:
        """ضریب فزاینده در اقتصاد باز: 1 / [1 - mpc*(1 - t) + m1]"""
        denom = 1.0 - self.mpc * (1.0 - self.t) + self.m1
        return 1.0 / denom

    @property
    def autonomous_open_demand(self) -> float:
        """مخارج خودگردان کل شامل تراز مستقل تجاری"""
        nx_auto = (self.x0 + self.x1 * self.Y_foreign) - self.m0 + (self.eta * self.exchange_rate)
        return self.c0 + self.i0 + self.G + nx_auto

    def get_is_curve(self, Y: np.ndarray) -> np.ndarray:
        alpha = self.open_multiplier
        A = self.autonomous_open_demand
        return (A / self.b) - (Y / (alpha * self.b))

    def get_lm_curve(self, Y: np.ndarray) -> np.ndarray:
        real_M = self.M / self.P
        r = (self.k * Y - real_M) / self.h
        return np.maximum(0.0005, r)

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

        if r_eq < 0.0005:
            r_eq = 0.0005
            Y_eq = alpha * (A - self.b * r_eq)

        exports = self.x0 + self.x1 * self.Y_foreign + self.eta * self.exchange_rate
        imports = self.m0 + self.m1 * Y_eq
        nx = exports - imports

        return {
            "Y": Y_eq,
            "r": r_eq,
            "NX": nx,
            "Imports": imports,
            "Exports": exports
        }

def create_mundell_fleming_figure(base_model: MundellFlemingModel, current_model: MundellFlemingModel):
    eq0 = base_model.solve_equilibrium()
    eq1 = current_model.solve_equilibrium()

    Y_vals = np.linspace(650, 1450, 250)
    fig = go.Figure()

    # خطوط مبنا
    fig.add_trace(go.Scatter(x=Y_vals, y=base_model.get_is_curve(Y_vals), mode="lines", line=dict(dash="dot", color="#cbd5e1", width=1.5), name="IS مبنا"))
    fig.add_trace(go.Scatter(x=Y_vals, y=base_model.get_lm_curve(Y_vals), mode="lines", line=dict(dash="dot", color="#cbd5e1", width=1.5), name="LM مبنا"))
    fig.add_trace(go.Scatter(x=Y_vals, y=base_model.get_bp_curve(Y_vals), mode="lines", line=dict(dash="dot", color="#a7f3d0", width=1.5), name="BP مبنا"))

    # خطوط جاری
    fig.add_trace(go.Scatter(
        x=Y_vals, y=current_model.get_is_curve(Y_vals), mode="lines",
        line=dict(color=PLOT_THEME["is_color"], width=3), name="منحنی IS جاری",
        hovertemplate="تولید: %{x:.1f} | بهره: %{y:.2%}<extra></extra>"
    ))
    fig.add_trace(go.Scatter(
        x=Y_vals, y=current_model.get_lm_curve(Y_vals), mode="lines",
        line=dict(color=PLOT_THEME["lm_color"], width=3), name="منحنی LM جاری",
        hovertemplate="تولید: %{x:.1f} | بهره: %{y:.2%}<extra></extra>"
    ))
    fig.add_trace(go.Scatter(
        x=Y_vals, y=current_model.get_bp_curve(Y_vals), mode="lines",
        line=dict(color=PLOT_THEME["bp_color"], width=3), name="تراز پرداخت‌ها (منحنی BP)",
        hovertemplate="تولید: %{x:.1f} | تعادل خارجی: %{y:.2%}<extra></extra>"
    ))

    # نقاط تعادل
    fig.add_trace(go.Scatter(x=[eq0["Y"]], y=[eq0["r"]], mode="markers+text", marker=dict(size=8, color="#64748b"), text=["E₀"], textposition="top right", name="تعادل اولیه"))
    fig.add_trace(go.Scatter(x=[eq1["Y"]], y=[eq1["r"]], mode="markers+text", marker=dict(size=12, color="#0f172a"), text=["E₁"], textposition="top left", name="تعادل داخلی"))

    # خط راهنمای بهره بین‌المللی دهکده سنگ
    fig.add_shape(type="line", x0=650, x1=1450, y0=current_model.r_foreign, y1=current_model.r_foreign, line=dict(dash="dash", color="#10b981", width=1))

    # خطوط راهنما به محورها
    fig.add_shape(type="line", x0=eq1["Y"], x1=eq1["Y"], y0=0, y1=eq1["r"], line=dict(dash="dot", color="#94a3b8"))
    fig.add_shape(type="line", x0=650, x1=eq1["Y"], y0=eq1["r"], y1=eq1["r"], line=dict(dash="dot", color="#94a3b8"))

    fig.update_xaxes(title_text="تولید ناخالص داخلی کونوها (Y)", range=[650, 1450], gridcolor=PLOT_THEME["grid_color"])
    fig.update_yaxes(title_text="نرخ بهره داخلی (r)", tickformat=".1%", range=[0, 0.16], gridcolor=PLOT_THEME["grid_color"])

    fig.update_layout(
        height=480, plot_bgcolor=PLOT_THEME["bg_color"], paper_bgcolor=PLOT_THEME["bg_color"],
        legend=dict(orientation="h", y=-0.22, x=0.5, xanchor="center"),
        margin=dict(l=40, r=40, t=50, b=60)
    )
    return fig, eq0, eq1