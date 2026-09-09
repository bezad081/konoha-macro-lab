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

    # پارامترهای بخش خارجی (دهکده سنگ و خاک - ایواگاکوره)
    Y_foreign: float = 1000.0
    r_foreign: float = 0.05
    x0: float = 80.0
    x1: float = 0.10
    m0: float = 50.0
    m1: float = 0.15
    eta: float = 60.0
    exchange_rate: float = 1.0
    capital_mobility: float = 12000.0  # تحرک بالای سرمایه
    regime: str = "floating"  # "floating" (شناور) یا "fixed" (ثابت)

    @property
    def open_multiplier(self) -> float:
        denom = 1.0 - self.mpc * (1.0 - self.t) + self.m1
        return 1.0 / denom if denom > 0 else 1.0

    def autonomous_open_demand(self, e: float) -> float:
        nx_auto = (self.x0 + self.x1 * self.Y_foreign) - self.m0 + (self.eta * e)
        return self.c0 + self.i0 + self.G + nx_auto

    def get_is_curve(self, Y: np.ndarray, e: float) -> np.ndarray:
        alpha = self.open_multiplier
        A = self.autonomous_open_demand(e)
        return (A / self.b) - (Y / (alpha * self.b))

    def get_lm_curve(self, Y: np.ndarray, M_val: float) -> np.ndarray:
        real_M = M_val / self.P
        r = (self.k * Y - real_M) / self.h
        return np.maximum(0.001, r)

    def get_bp_curve(self, Y: np.ndarray, e: float) -> np.ndarray:
        nx_auto = (self.x0 + self.x1 * self.Y_foreign) - self.m0 + (self.eta * e)
        return self.r_foreign + (self.m1 * Y - nx_auto) / self.capital_mobility

    def solve_equilibrium(self):
        """حل دقیق تعادل تراز پرداخت‌ها و تعادل عمومی در نظام‌های ارزی"""
        alpha = self.open_multiplier

        if self.regime == "floating":
            # در نرخ ارز شناور، M ثابت است و تعادل روی BP (نزدیک r*) با تعدیل نرخ ارز e حاصل می‌شود
            # با تحرک بالای سرمایه، r به سمت r_foreign میل می‌کند:
            r_eq = self.r_foreign
            # از معادله LM:
            real_M = self.M / self.P
            Y_eq = (real_M + self.h * r_eq) / self.k
            
            # نرخ ارزی که باعث تقاطع IS در این نقطه می‌شود:
            # Y = alpha * [c0 + i0 - b*r + G + x0 + x1*Yf - m0 + eta*e]
            base_A = self.c0 + self.i0 - self.b * r_eq + self.G + (self.x0 + self.x1 * self.Y_foreign) - self.m0
            e_eq = ((Y_eq / alpha) - base_A) / self.eta
            e_eq = max(0.1, float(e_eq))
            endogenous_M = self.M
            
        else:  # نظام نرخ ارز ثابت
            e_eq = self.exchange_rate  # نرخ ارز ثابت است
            r_eq = self.r_foreign
            # تقاضای کل از IS با نرخ ارز تثبیت‌شده و نرخ بهره برابر با جهان به دست می‌آید:
            A = self.autonomous_open_demand(e_eq)
            Y_eq = alpha * (A - self.b * r_eq)
            # بانک مرکزی مجبور است عرضه پول را طوری تطبیق دهد که r با جهان برابر بماند:
            # r = (k*Y - M/P) / h  =>  M/P = k*Y - h*r
            real_M_endogenous = max(50.0, self.k * Y_eq - self.h * r_eq)
            endogenous_M = real_M_endogenous * self.P

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

    # منحنی‌های تعادلی نهایی
    is_base = base_model.get_is_curve(Y_vals, e=eq0["e"])
    is_curr = current_model.get_is_curve(Y_vals, e=eq1["e"])
    lm_base = base_model.get_lm_curve(Y_vals, M_val=eq0["M"])
    lm_curr = current_model.get_lm_curve(Y_vals, M_val=eq1["M"])
    bp_base = base_model.get_bp_curve(Y_vals, e=eq0["e"])
    bp_curr = current_model.get_bp_curve(Y_vals, e=eq1["e"])

    fig = go.Figure()

    # خطوط مبنا
    fig.add_trace(go.Scatter(x=Y_vals, y=is_base, mode="lines", line=dict(dash="dot", color="#cbd5e1", width=1.5), name="IS مبنا"))
    fig.add_trace(go.Scatter(x=Y_vals, y=lm_base, mode="lines", line=dict(dash="dot", color="#cbd5e1", width=1.5), name="LM مبنا"))
    fig.add_trace(go.Scatter(x=Y_vals, y=bp_base, mode="lines", line=dict(dash="dot", color="#a7f3d0", width=1.5), name="BP مبنا"))

    # خطوط جاری
    fig.add_trace(go.Scatter(
        x=Y_vals, y=is_curr, mode="lines",
        line=dict(color=PLOT_THEME["is_color"], width=3), name="منحنی IS (تعادل نهایی)",
        hovertemplate="تولید: %{x:.1f} | بهره: %{y:.2%}<extra></extra>"
    ))
    fig.add_trace(go.Scatter(
        x=Y_vals, y=lm_curr, mode="lines",
        line=dict(color=PLOT_THEME["lm_color"], width=3), name="منحنی LM (تعادل نهایی)",
        hovertemplate="تولید: %{x:.1f} | بهره: %{y:.2%}<extra></extra>"
    ))
    fig.add_trace(go.Scatter(
        x=Y_vals, y=bp_curr, mode="lines",
        line=dict(color=PLOT_THEME["bp_color"], width=3), name="تراز پرداخت‌ها (منحنی BP)",
        hovertemplate="تولید: %{x:.1f} | تعادل خارجی: %{y:.2%}<extra></extra>"
    ))

    # نقاط تعادل
    fig.add_trace(go.Scatter(x=[eq0["Y"]], y=[eq0["r"]], mode="markers+text", marker=dict(size=8, color="#64748b"), text=["E₀"], textposition="top right", name="تعادل اولیه E₀"))
    fig.add_trace(go.Scatter(x=[eq1["Y"]], y=[eq1["r"]], mode="markers+text", marker=dict(size=12, color="#0f172a"), text=["E₁"], textposition="top left", name="تعادل نهایی E₁"))

    # خط نرخ بهره جهانی دهکده سنگ
    fig.add_shape(type="line", x0=y_min, x1=y_max, y0=current_model.r_foreign, y1=current_model.r_foreign, line=dict(dash="dash", color="#10b981", width=1.2))
    fig.add_annotation(x=y_min + 50, y=current_model.r_foreign + 0.005, text="نرخ بهره جهانی دهکده سنگ (r*)", showarrow=False, font=dict(color="#059669", size=11))

    # فلش انتقال تعادل
    delta_y = abs(eq1["Y"] - eq0["Y"])
    delta_r = abs(eq1["r"] - eq0["r"])
    if delta_y > 10.0 or delta_r > 0.003:
        fig.add_annotation(
            ax=eq0["Y"], ay=eq0["r"], x=eq1["Y"], y=eq1["r"],
            xref="x", yref="y", axref="x", ayref="y",
            showarrow=True, arrowhead=2, arrowsize=1.3, arrowwidth=2.5, arrowcolor="#10b981"
        )

    # خطوط راهنما به محورها
    fig.add_shape(type="line", x0=eq1["Y"], x1=eq1["Y"], y0=0, y1=eq1["r"], line=dict(dash="dot", color="#94a3b8"))
    fig.add_shape(type="line", x0=y_min, x1=eq1["Y"], y0=eq1["r"], y1=eq1["r"], line=dict(dash="dot", color="#94a3b8"))

    max_r = max(0.14, eq0["r"] * 1.5, eq1["r"] * 1.5, current_model.r_foreign * 1.6)

    fig.update_xaxes(title_text="تولید ناخالص داخلی کونوها (Y)", range=[y_min, y_max], gridcolor=PLOT_THEME["grid_color"], automargin=True)
    fig.update_yaxes(title_text="نرخ بهره داخلی (r)", tickformat=".1%", range=[0.0, min(0.20, max_r)], gridcolor=PLOT_THEME["grid_color"], automargin=True)

    fig.update_layout(
        height=480, plot_bgcolor=PLOT_THEME["bg_color"], paper_bgcolor=PLOT_THEME["bg_color"],
        legend=dict(orientation="h", y=-0.22, x=0.5, xanchor="center"),
        margin=dict(l=75, r=35, t=40, b=70)
    )
    return fig, eq0, eq1
