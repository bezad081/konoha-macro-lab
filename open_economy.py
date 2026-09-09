import numpy as np
import plotly.graph_objects as go
from dataclasses import dataclass

PLOT_THEME = {
    "font_family": "Vazirmatn, Tahoma, sans-serif",
    "bg_color": "#ffffff",
    "grid_color": "#f1f5f9",
    "is_color": "#dc2626",   # قرمز IS
    "lm_color": "#2563eb",   # آبی LM
    "bp_color": "#16a34a"    # سبز BP
}

@dataclass
class MundellFlemingModel:
    c0: float = 60.0
    mpc: float = 0.75
    t: float = 0.20
    i0: float = 140.0
    b: float = 800.0
    G: float = 120.0
    
    M: float = 400.0
    P: float = 1.0
    k: float = 0.50
    h: float = 4000.0

    # پارامترهای خارجی دهکده سنگ
    Y_foreign: float = 1000.0
    r_foreign: float = 0.05
    x0: float = 80.0
    x1: float = 0.10
    m0: float = 50.0
    m1: float = 0.15
    eta: float = 80.0
    exchange_rate: float = 1.0
    regime: str = "floating"  # "floating" یا "fixed"

    @property
    def open_multiplier(self) -> float:
        denom = 1.0 - self.mpc * (1.0 - self.t) + self.m1
        return 1.0 / denom if denom > 0 else 1.0

    def get_is_curve(self, Y: np.ndarray, e_val: float) -> np.ndarray:
        alpha = self.open_multiplier
        # A_total = c0 + i0 + G + (x0 + x1*Yf - m0 + eta*e)
        A = self.c0 + self.i0 + self.G + (self.x0 + self.x1 * self.Y_foreign - self.m0 + self.eta * e_val)
        return (A / self.b) - (Y / (alpha * self.b))

    def get_lm_curve(self, Y: np.ndarray, M_val: float) -> np.ndarray:
        real_M = M_val / self.P
        r = (self.k * Y - real_M) / self.h
        return np.maximum(0.005, r)

    def solve_equilibrium(self):
        """
        در ماندل-فلمینگ استاندارد با تحرک سرمایه، در تعادل پایدار نرخ بهره داخلی
        با نرخ بهره دهکده سنگ برابر می‌شود (r = r_foreign).
        """
        r_eq = self.r_foreign
        alpha = self.open_multiplier

        if self.regime == "floating":
            # در شناور: عرضه پول تثبیت‌شده است و درآمد از LM در نرخ r* تعیین می‌شود
            real_M = self.M / self.P
            Y_eq = (real_M + self.h * r_eq) / self.k
            endogenous_M = self.M

            # نرخ ارز تعدیل می‌شود تا IS دقیقاً در (Y_eq, r*) تقاطع کند
            # Y = alpha * [c0 + i0 - b*r* + G + x0 + x1*Yf - m0 + eta*e]
            base_spending = self.c0 + self.i0 - self.b * r_eq + self.G + self.x0 + self.x1 * self.Y_foreign - self.m0
            e_eq = ((Y_eq / alpha) - base_spending) / self.eta
            e_eq = max(0.1, float(e_eq))

        else:  # نظام نرخ ارز ثابت
            e_eq = self.exchange_rate  # نرخ ارز ثابت است
            # درآمد توسط IS در نرخ ارز ثابت و r* تعیین می‌شود
            A = self.c0 + self.i0 + self.G + (self.x0 + self.x1 * self.Y_foreign - self.m0 + self.eta * e_eq)
            Y_eq = alpha * (A - self.b * r_eq)

            # عرضه پول توسط بانک مرکزی تعدیل می‌شود تا LM دقیقاً در (Y_eq, r*) قرار گیرد
            real_M_needed = max(50.0, self.k * Y_eq - self.h * r_eq)
            endogenous_M = real_M_needed * self.P

        exports = self.x0 + self.x1 * self.Y_foreign + self.eta * e_eq
        imports = self.m0 + self.m1 * Y_eq
        nx = exports - imports

        return {
            "Y": float(Y_eq),
            "r": float(r_eq),
            "e": float(e_eq),
            "M": float(endogenous_M),
            "NX": float(nx),
            "Imports": float(imports),
            "Exports": float(exports)
        }

def create_mundell_fleming_figure(base_model: MundellFlemingModel, current_model: MundellFlemingModel):
    eq0 = base_model.solve_equilibrium()
    eq1 = current_model.solve_equilibrium()

    center_y = (eq0["Y"] + eq1["Y"]) / 2.0
    y_min = max(350.0, center_y - 450.0)
    y_max = max(1350.0, center_y + 450.0)
    Y_vals = np.linspace(y_min, y_max, 300)

    # محاسبه منحنی‌ها به شکلی که هر ۳ خط در نقطه تعادل دقیقاً متقاطع شوند
    is_base = np.maximum(0.005, base_model.get_is_curve(Y_vals, e_val=eq0["e"]))
    lm_base = base_model.get_lm_curve(Y_vals, M_val=eq0["M"])

    is_curr = np.maximum(0.005, current_model.get_is_curve(Y_vals, e_val=eq1["e"]))
    lm_curr = current_model.get_lm_curve(Y_vals, M_val=eq1["M"])

    fig = go.Figure()

    # خطوط مبنا
    fig.add_trace(go.Scatter(x=Y_vals, y=is_base, mode="lines", line=dict(dash="dot", color="#94a3b8", width=1.5), name="IS مبنا"))
    fig.add_trace(go.Scatter(x=Y_vals, y=lm_base, mode="lines", line=dict(dash="dot", color="#94a3b8", width=1.5), name="LM مبنا"))
    fig.add_trace(go.Scatter(x=[eq0["Y"]], y=[eq0["r"]], mode="markers+text", marker=dict(size=8, color="#64748b"), text=["E₀"], textposition="top right", name="تعادل اولیه E₀"))

    # خطوط تعادل نهایی (هم‌گرا شده)
    fig.add_trace(go.Scatter(x=Y_vals, y=is_curr, mode="lines", line=dict(color=PLOT_THEME["is_color"], width=3), name="منحنی IS جاری"))
    fig.add_trace(go.Scatter(x=Y_vals, y=lm_curr, mode="lines", line=dict(color=PLOT_THEME["lm_color"], width=3), name="منحنی LM جاری"))

    # خط تراز پرداخت‌ها BP (کاملاً تراز روی نرخ بهره جهانی)
    fig.add_trace(go.Scatter(
        x=[y_min, y_max], y=[current_model.r_foreign, current_model.r_foreign],
        mode="lines", line=dict(color=PLOT_THEME["bp_color"], width=3.5, dash="dash"),
        name="تراز پرداخت‌ها BP (r = r*)"
    ))

    # نقطه تعادل نهایی هم‌زمان (تقاطع کامل هر ۳ خط)
    fig.add_trace(go.Scatter(
        x=[eq1["Y"]], y=[eq1["r"]], mode="markers+text",
        marker=dict(size=12, color="#0f172a"), text=["E₁"], textposition="top left",
        name="تعادل نهایی هر ۳ بازار"
    ))

    # فلش دینامیک انتقال
    delta_y = abs(eq1["Y"] - eq0["Y"])
    delta_r = abs(eq1["r"] - eq0["r"])
    if delta_y > 10.0 or delta_r > 0.003:
        fig.add_annotation(
            ax=eq0["Y"], ay=eq0["r"], x=eq1["Y"], y=eq1["r"],
            xref="x", yref="y", axref="x", ayref="y",
            showarrow=True, arrowhead=2, arrowsize=1.3, arrowwidth=2.5, arrowcolor="#10b981"
        )

    # خطوط راهنما
    fig.add_shape(type="line", x0=eq1["Y"], x1=eq1["Y"], y0=0, y1=eq1["r"], line=dict(dash="dot", color="#94a3b8"))
    fig.add_shape(type="line", x0=y_min, x1=eq1["Y"], y0=eq1["r"], y1=eq1["r"], line=dict(dash="dot", color="#94a3b8"))

    max_r = max(0.14, eq0["r"] * 1.6, eq1["r"] * 1.6, current_model.r_foreign * 1.6)

    fig.update_xaxes(title_text="تولید ناخالص داخلی کونوها (Y)", range=[y_min, y_max], gridcolor=PLOT_THEME["grid_color"], automargin=True)
    fig.update_yaxes(title_text="نرخ بهره داخلی (r)", tickformat=".1%", range=[0.0, min(0.20, max_r)], gridcolor=PLOT_THEME["grid_color"], automargin=True)

    fig.update_layout(
        height=480, plot_bgcolor=PLOT_THEME["bg_color"], paper_bgcolor=PLOT_THEME["bg_color"],
        legend=dict(orientation="h", y=-0.22, x=0.5, xanchor="center"),
        margin=dict(l=75, r=35, t=40, b=70)
    )
    return fig, eq0, eq1
