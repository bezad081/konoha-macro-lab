import numpy as np
import plotly.graph_objects as go
from dataclasses import dataclass

PLOT_THEME = {
    "font_family": "Vazirmatn, Tahoma, sans-serif",
    "bg_color": "#ffffff",
    "grid_color": "#f1f5f9",
    "is_color": "#dc2626",
    "lm_color": "#2563eb"
}

@dataclass
class ISLMEngine:
    # متغیرهای بازار کالا
    c0: float = 60.0
    mpc: float = 0.75
    t: float = 0.20
    i0: float = 140.0
    b: float = 600.0
    G: float = 120.0

    # متغیرهای بازار پول
    M: float = 400.0
    P: float = 1.0
    k: float = 0.50
    h: float = 4000.0

    @property
    def multiplier(self) -> float:
        return 1.0 / (1.0 - self.mpc * (1.0 - self.t))

    @property
    def autonomous_spending(self) -> float:
        return self.c0 + self.i0 + self.G

    def solve_equilibrium(self):
        """حل دقیق دستگاه هم‌زمان با اعمال قید عدم منفی بودن نرخ بهره (ZLB)"""
        alpha = self.multiplier
        A = self.autonomous_spending
        real_M = self.M / self.P

        denom = (1.0 / alpha) + (self.b * self.k / self.h)
        Y_star = (A + (self.b / self.h) * real_M) / denom
        r_star = (self.k * Y_star - real_M) / self.h

        # قید تله نقدینگی و نرخ بهره صفر: اگر r منفی شود، نرخ روی صفر قفل شده و تولید از IS تعیین می‌شود
        if r_star < 0.0005:
            r_star = 0.0005
            Y_star = alpha * (A - self.b * r_star)

        T = self.t * Y_star
        C = self.c0 + self.mpc * (Y_star - T)
        I = self.i0 - self.b * r_star

        return {
            "Y": Y_star,
            "r": r_star,
            "C": C,
            "I": I,
            "T": T,
            "Deficit": self.G - T
        }

    def get_is_curve(self, Y_vals: np.ndarray) -> np.ndarray:
        alpha = self.multiplier
        A = self.autonomous_spending
        return (A / self.b) - (Y_vals / (alpha * self.b))

    def get_lm_curve(self, Y_vals: np.ndarray) -> np.ndarray:
        real_M = self.M / self.P
        r = (self.k * Y_vals - real_M) / self.h
        return np.maximum(0.0005, r)

def create_islm_figure(base_engine: ISLMEngine, current_engine: ISLMEngine):
    eq0 = base_engine.solve_equilibrium()
    eq1 = current_engine.solve_equilibrium()

    Y_vals = np.linspace(650, 1400, 250)
    fig = go.Figure()

    # منحنی‌های اولیه (مبنا)
    fig.add_trace(go.Scatter(
        x=Y_vals, y=base_engine.get_is_curve(Y_vals), mode="lines",
        line=dict(dash="dot", color="#94a3b8", width=1.5), name="IS مبنا",
        hovertemplate="IS مبنا<extra></extra>"
    ))
    fig.add_trace(go.Scatter(
        x=Y_vals, y=base_engine.get_lm_curve(Y_vals), mode="lines",
        line=dict(dash="dot", color="#94a3b8", width=1.5), name="LM مبنا",
        hovertemplate="LM مبنا<extra></extra>"
    ))
    fig.add_trace(go.Scatter(
        x=[eq0["Y"]], y=[eq0["r"]], mode="markers+text",
        marker=dict(size=8, color="#64748b"), text=["E₀"], textposition="top right",
        name="تعادل مبدا E₀"
    ))

    # منحنی‌های جاری
    fig.add_trace(go.Scatter(
        x=Y_vals, y=current_engine.get_is_curve(Y_vals), mode="lines",
        line=dict(color=PLOT_THEME["is_color"], width=3), name="منحنی IS جاری",
        hovertemplate="تولید: %{x:.1f} | نرخ بهره: %{y:.2%}<extra></extra>"
    ))
    fig.add_trace(go.Scatter(
        x=Y_vals, y=current_engine.get_lm_curve(Y_vals), mode="lines",
        line=dict(color=PLOT_THEME["lm_color"], width=3), name="منحنی LM جاری",
        hovertemplate="تولید: %{x:.1f} | نرخ بهره: %{y:.2%}<extra></extra>"
    ))
    fig.add_trace(go.Scatter(
        x=[eq1["Y"]], y=[eq1["r"]], mode="markers+text",
        marker=dict(size=12, color="#0f172a"), text=["E₁"], textposition="top left",
        name="تعادل جدید E₁"
    ))

    # فلش پویا بین تعادل قدیم و جدید
    if abs(eq1["Y"] - eq0["Y"]) > 2 or abs(eq1["r"] - eq0["r"]) > 0.001:
        fig.add_annotation(
            ax=eq0["Y"], ay=eq0["r"], x=eq1["Y"], y=eq1["r"],
            xref="x", yref="y", axref="x", ayref="y",
            showarrow=True, arrowhead=3, arrowsize=1.2, arrowwidth=2, arrowcolor="#10b981"
        )

    # خطوط راهنمای تعادل جدید به محورها
    fig.add_shape(type="line", x0=eq1["Y"], x1=eq1["Y"], y0=0, y1=eq1["r"], line=dict(dash="dash", color="#cbd5e1"))
    fig.add_shape(type="line", x0=650, x1=eq1["Y"], y0=eq1["r"], y1=eq1["r"], line=dict(dash="dash", color="#cbd5e1"))

    fig.update_xaxes(title_text="تولید ناخالص داخلی تعادلی (Y)", range=[650, 1400], gridcolor=PLOT_THEME["grid_color"])
    fig.update_yaxes(title_text="نرخ بهره تعادلی (r)", tickformat=".1%", range=[0, 0.16], gridcolor=PLOT_THEME["grid_color"])

    fig.update_layout(
        height=480, plot_bgcolor=PLOT_THEME["bg_color"], paper_bgcolor=PLOT_THEME["bg_color"],
        legend=dict(orientation="h", y=-0.22, x=0.5, xanchor="center"),
        margin=dict(l=40, r=40, t=50, b=60)
    )
    return fig, eq0, eq1