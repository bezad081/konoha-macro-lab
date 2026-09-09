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

    @property
    def multiplier(self) -> float:
        denom = 1.0 - self.mpc * (1.0 - self.t)
        return 1.0 / denom if denom > 0 else 1.0

    @property
    def autonomous_spending(self) -> float:
        return self.c0 + self.i0 + self.G

    def solve_equilibrium(self):
        alpha = self.multiplier
        A = self.autonomous_spending
        real_M = self.M / self.P

        denom = (1.0 / alpha) + (self.b * self.k / self.h)
        Y_star = (A + (self.b / self.h) * real_M) / denom
        r_star = (self.k * Y_star - real_M) / self.h

        if r_star < 0.001:
            r_star = 0.001
            Y_star = alpha * (A - self.b * r_star)

        T = self.t * Y_star
        C = self.c0 + self.mpc * (Y_star - T)
        I = self.i0 - self.b * r_star

        return {
            "Y": float(Y_star),
            "r": float(r_star),
            "C": float(C),
            "I": float(I),
            "T": float(T),
            "Deficit": float(self.G - T)
        }

    def get_is_curve(self, Y_vals: np.ndarray) -> np.ndarray:
        alpha = self.multiplier
        A = self.autonomous_spending
        return (A / self.b) - (Y_vals / (alpha * self.b))

    def get_lm_curve(self, Y_vals: np.ndarray) -> np.ndarray:
        real_M = self.M / self.P
        r = (self.k * Y_vals - real_M) / self.h
        return np.maximum(0.001, r)

def create_islm_figure(base_engine: ISLMEngine, current_engine: ISLMEngine):
    eq0 = base_engine.solve_equilibrium()
    eq1 = current_engine.solve_equilibrium()

    # تنظیم پویای دامنه نمودار متناسب با نقطه تعادل تا هرگز به گوشه نچسبد
    center_y = (eq0["Y"] + eq1["Y"]) / 2.0
    y_min = max(400.0, center_y - 450.0)
    y_max = max(1350.0, center_y + 450.0)
    Y_vals = np.linspace(y_min, y_max, 250)

    is_base = np.maximum(0.001, base_engine.get_is_curve(Y_vals))
    is_curr = np.maximum(0.001, current_engine.get_is_curve(Y_vals))
    lm_base = base_engine.get_lm_curve(Y_vals)
    lm_curr = current_engine.get_lm_curve(Y_vals)

    fig = go.Figure()

    # خطوط مبنا
    fig.add_trace(go.Scatter(
        x=Y_vals, y=is_base, mode="lines",
        line=dict(dash="dot", color="#94a3b8", width=1.5), name="IS مبنا"
    ))
    fig.add_trace(go.Scatter(
        x=Y_vals, y=lm_base, mode="lines",
        line=dict(dash="dot", color="#94a3b8", width=1.5), name="LM مبنا"
    ))
    fig.add_trace(go.Scatter(
        x=[eq0["Y"]], y=[eq0["r"]], mode="markers+text",
        marker=dict(size=8, color="#64748b"), text=["E₀"], textposition="top right",
        name="تعادل مبدا E₀"
    ))

    # خطوط جاری
    fig.add_trace(go.Scatter(
        x=Y_vals, y=is_curr, mode="lines",
        line=dict(color=PLOT_THEME["is_color"], width=3), name="منحنی IS جاری"
    ))
    fig.add_trace(go.Scatter(
        x=Y_vals, y=lm_curr, mode="lines",
        line=dict(color=PLOT_THEME["lm_color"], width=3), name="منحنی LM جاری"
    ))
    fig.add_trace(go.Scatter(
        x=[eq1["Y"]], y=[eq1["r"]], mode="markers+text",
        marker=dict(size=11, color="#0f172a"), text=["E₁"], textposition="top left",
        name="تعادل جاری E₁"
    ))

    # رفع ایراد فلش سبز: تنها در صورتی رسم شود که جابه‌جایی کاملاً مشخص و معنادار باشد
    delta_y = abs(eq1["Y"] - eq0["Y"])
    delta_r = abs(eq1["r"] - eq0["r"])
    if delta_y > 15.0 or delta_r > 0.006:
        fig.add_annotation(
            ax=eq0["Y"], ay=eq0["r"], x=eq1["Y"], y=eq1["r"],
            xref="x", yref="y", axref="x", ayref="y",
            showarrow=True, arrowhead=2, arrowsize=1.3, arrowwidth=2.5,
            arrowcolor="#059669", opacity=0.9
        )

    # خطوط راهنمای تعادل جاری
    fig.add_shape(type="line", x0=eq1["Y"], x1=eq1["Y"], y0=0, y1=eq1["r"], line=dict(dash="dot", color="#94a3b8"))
    fig.add_shape(type="line", x0=y_min, x1=eq1["Y"], y0=eq1["r"], y1=eq1["r"], line=dict(dash="dot", color="#94a3b8"))

    # سقف نرخ بهره متناسب با تعادل
    max_r = max(0.14, eq0["r"] * 1.5, eq1["r"] * 1.5)

    fig.update_xaxes(
        title_text="تولید ناخالص داخلی تعادلی (Y)",
        range=[y_min, y_max],
        gridcolor=PLOT_THEME["grid_color"],
        automargin=True,
        fixedrange=False
    )
    fig.update_yaxes(
        title_text="نرخ بهره تعادلی (r)",
        tickformat=".1%",
        range=[0.0, min(0.20, max_r)],
        gridcolor=PLOT_THEME["grid_color"],
        automargin=True,
        fixedrange=False
    )

    fig.update_layout(
        height=480,
        plot_bgcolor=PLOT_THEME["bg_color"],
        paper_bgcolor=PLOT_THEME["bg_color"],
        legend=dict(orientation="h", y=-0.22, x=0.5, xanchor="center"),
        margin=dict(l=75, r=35, t=40, b=70),
        uirevision="never"  # ریست خودکار زاویه دید با هر تغییر ورودی
    )
    return fig, eq0, eq1