# ماژول استخراج‌شده از open_economy.ipynb
# بدون تغییر در توابع و کلاس‌های اصلی

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import ipywidgets as widgets

# تنظیمات تم پیش‌فرض نمودارها
import plotly.io as pio
pio.templates.default = 'plotly_white'

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import ipywidgets as widgets
from IPython.display import display
from dataclasses import dataclass

PLOT_THEME = {
    "font_family": "Vazirmatn, Tahoma, sans-serif",
    "bg_color": "#ffffff",
    "grid_color": "#f1f5f9",
    "is_color": "#dc2626",      # قرمز برای IS
    "lm_color": "#2563eb",      # آبی برای LM
    "bp_color": "#059669",      # سبز زمردی برای تراز پرداخت‌ها BP
}

@dataclass
class MundellFlemingModel:
    # پارامترهای داخلی اوبیتویا
    c0: float = 60.0
    mpc: float = 0.75
    t: float = 0.20
    i0: float = 140.0
    b: float = 600.0
    G: float = 120.0
    
    # بازار پول داخلی
    M: float = 400.0
    P: float = 1.0
    k: float = 0.50
    h: float = 4000.0

    # پارامترهای بخش خارجی (نئوترا)
    Y_neoterra: float = 1000.0    # درآمد نئوترا (Y*)
    r_neoterra: float = 0.05      # نرخ بهره جهانی نئوترا (r*)
    x0: float = 80.0              # صادرات خودگردان
    x1: float = 0.10              # کشش صادرات به درآمد نئوترا
    m0: float = 50.0              # واردات خودگردان
    m1: float = 0.15              # میل نهایی به واردات
    eta: float = 40.0             # حساسیت تجاری به نرخ ارز
    exchange_rate: float = 1.0    # نرخ ارز (e)
    capital_mobility: float = 5000.0 # کشش تحرک سرمایه (sigma)

    @property
    def open_multiplier(self) -> float:
        """ضریب فزاینده در اقتصاد باز: 1 / [1 - mpc*(1 - t) + m1]"""
        denom = 1.0 - self.mpc * (1.0 - self.t) + self.m1
        return 1.0 / denom

    @property
    def autonomous_open_demand(self) -> float:
        """مخارج خودگردان شامل تراز تجاری مستقل"""
        nx_auto = (self.x0 + self.x1 * self.Y_neoterra) - self.m0 + (self.eta * self.exchange_rate)
        return self.c0 + self.i0 + self.G + nx_auto

    def get_is_curve(self, Y: np.ndarray) -> np.ndarray:
        alpha = self.open_multiplier
        A = self.autonomous_open_demand
        return (A / self.b) - (Y / (alpha * self.b))

    def get_lm_curve(self, Y: np.ndarray) -> np.ndarray:
        real_M = self.M / self.P
        return (self.k * Y - real_M) / self.h

    def get_bp_curve(self, Y: np.ndarray) -> np.ndarray:
        nx_auto = (self.x0 + self.x1 * self.Y_neoterra) - self.m0 + (self.eta * self.exchange_rate)
        # r = r* + (m1 * Y - nx_auto) / capital_mobility
        return self.r_neoterra + (self.m1 * Y - nx_auto) / self.capital_mobility

    def solve_equilibrium(self):
        alpha = self.open_multiplier
        A = self.autonomous_open_demand
        real_M = self.M / self.P

        denom = (1.0 / alpha) + (self.b * self.k / self.h)
        Y_eq = (A + (self.b / self.h) * real_M) / denom
        r_eq = (self.k * Y_eq - real_M) / self.h

        # تراز تجاری
        exports = self.x0 + self.x1 * self.Y_neoterra + self.eta * self.exchange_rate
        imports = self.m0 + self.m1 * Y_eq
        nx = exports - imports

        return {
            "Y": Y_eq,
            "r": max(0.0001, r_eq),
            "NX": nx,
            "Imports": imports,
            "Exports": exports
        }

def create_mundell_fleming_figure(base_model: MundellFlemingModel, current_model: MundellFlemingModel):
    eq0 = base_model.solve_equilibrium()
    eq1 = current_model.solve_equilibrium()

    Y_min = min(eq0["Y"], eq1["Y"]) * 0.70
    Y_max = max(eq0["Y"], eq1["Y"]) * 1.30
    Y_vals = np.linspace(Y_min, Y_max, 250)

    fig = go.Figure()

    # خطوط مبدا (نقطه چین خاکستری)
    fig.add_trace(go.Scatter(
        x=Y_vals, y=base_model.get_is_curve(Y_vals),
        mode="lines", line=dict(dash="dot", color="#cbd5e1", width=1.5), name="IS اولیه"
    ))
    fig.add_trace(go.Scatter(
        x=Y_vals, y=base_model.get_lm_curve(Y_vals),
        mode="lines", line=dict(dash="dot", color="#cbd5e1", width=1.5), name="LM اولیه"
    ))
    fig.add_trace(go.Scatter(
        x=Y_vals, y=base_model.get_bp_curve(Y_vals),
        mode="lines", line=dict(dash="dot", color="#a7f3d0", width=1.5), name="BP اولیه"
    ))

    # خطوط جاری پس از تغییر پارامترها
    fig.add_trace(go.Scatter(
        x=Y_vals, y=current_model.get_is_curve(Y_vals),
        mode="lines", line=dict(color=PLOT_THEME["is_color"], width=3), name="منحنی IS جاری"
    ))
    fig.add_trace(go.Scatter(
        x=Y_vals, y=current_model.get_lm_curve(Y_vals),
        mode="lines", line=dict(color=PLOT_THEME["lm_color"], width=3), name="منحنی LM جاری"
    ))
    fig.add_trace(go.Scatter(
        x=Y_vals, y=current_model.get_bp_curve(Y_vals),
        mode="lines", line=dict(color=PLOT_THEME["bp_color"], width=3), name="تراز پرداخت‌ها (منحنی BP)"
    ))

    # نقاط تعادل
    fig.add_trace(go.Scatter(
        x=[eq0["Y"]], y=[eq0["r"]], mode="markers+text",
        marker=dict(size=8, color="#64748b"), text=["E₀"], textposition="top right", name="تعادل اولیه"
    ))
    fig.add_trace(go.Scatter(
        x=[eq1["Y"]], y=[eq1["r"]], mode="markers+text",
        marker=dict(size=12, color="#000000"), text=["E₁"], textposition="top left", name="تعادل داخلی"
    ))

    # خط راهنمای نرخ بهره جهانی نئوترا
    fig.add_shape(type="line", x0=Y_min, x1=Y_max, y0=current_model.r_neoterra, y1=current_model.r_neoterra,
                  line=dict(dash="dash", color="#10b981", width=1))

    r_max = max(eq0["r"], eq1["r"], current_model.r_neoterra, 0.10) * 1.5
    fig.update_xaxes(title_text="تولید ناخالص داخلی اوبیتویا (Y)", gridcolor=PLOT_THEME["grid_color"], range=[Y_min, Y_max])
    fig.update_yaxes(title_text="نرخ بهره داخلی (r)", tickformat=".1%", gridcolor=PLOT_THEME["grid_color"], range=[0, r_max])

    fig.update_layout(
        title="تعادل اقتصاد باز اوبیتویا در تعامل با نئوترا (مدل IS-LM-BP)",
        height=520,
        plot_bgcolor=PLOT_THEME["bg_color"],
        paper_bgcolor=PLOT_THEME["bg_color"],
        legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5),
        margin=dict(l=50, r=40, t=60, b=70)
    )
    return fig, eq0, eq1



