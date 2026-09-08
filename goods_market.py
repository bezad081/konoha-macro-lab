# ماژول استخراج‌شده از goods_market.ipynb
# بدون تغییر در توابع و کلاس‌های اصلی

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import ipywidgets as widgets
from IPython.display import display
from dataclasses import dataclass

# تم استاندارد و مینیمال برای نمودارهای کلاسی
PLOT_THEME = {
    "font_family": "Vazirmatn, Tahoma, sans-serif",
    "bg_color": "#ffffff",
    "grid_color": "#f1f5f9",
    "primary_color": "#2563eb",   # آبی برای تقاضای کل
    "secondary_color": "#dc2626", # قرمز برای منحنی IS
    "neutral_color": "#64748b"    # خاکستری برای خط ۴۵ درجه
}

@dataclass
class GoodsMarketModel:
    c0: float = 60.0       # مصرف خودگردان
    mpc: float = 0.75      # میل نهایی به مصرف
    t: float = 0.20        # نرخ مالیات تناسبی
    i0: float = 140.0      # سرمایه‌گذاری خودگردان
    b: float = 600.0       # حساسیت به نرخ بهره
    G: float = 120.0       # مخارج دولت
    
    @property
    def multiplier(self) -> float:
        """ضریب فزاینده کینزی: 1 / [1 - mpc*(1 - t)]"""
        denom = 1.0 - self.mpc * (1.0 - self.t)
        return 1.0 / denom if denom > 0 else np.nan

    def autonomous_spending(self, r: float) -> float:
        """کل تقاضای خودگردان: A(r) = c0 + I(r) + G"""
        return self.c0 + (self.i0 - self.b * r) + self.G

    def solve_equilibrium_output(self, r: float) -> float:
        """محاسبه تولید تعادلی (Y) به ازای یک نرخ بهره معین"""
        return self.multiplier * self.autonomous_spending(r)

    def is_curve_rate(self, Y: np.ndarray) -> np.ndarray:
        """محاسبه نرخ بهره (r) به ازای مقادیر مختلف Y روی منحنی IS"""
        A = self.c0 + self.i0 + self.G
        slope = (1.0 - self.mpc * (1.0 - self.t)) / self.b
        return (A / self.b) - slope * Y

def create_goods_market_figure(model: GoodsMarketModel, r_current: float = 0.05):
    # محاسبه نقطه تعادل جاری
    Y_eq = model.solve_equilibrium_output(r_current)
    
    # دامنه مقادیر درآمد برای رسم
    Y_max = max(1200.0, Y_eq * 1.4)
    Y_vals = np.linspace(0, Y_max, 200)
    
    # توابع نمودار چپ (Keynesian Cross)
    line_45 = Y_vals
    slope = model.mpc * (1.0 - model.t)
    planned_expenditure = model.autonomous_spending(r_current) + slope * Y_vals
    
    # توابع نمودار راست (IS Curve)
    r_vals = model.is_curve_rate(Y_vals)

    # ایجاد بوم دوبخشی
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=("الف) تقاطع کینزی (Keynesian Cross)", "ب) استخراج هندسی منحنی IS"),
        horizontal_spacing=0.12
    )

    # --- پانل چپ: تقاطع کینزی ---
    fig.add_trace(
        go.Scatter(x=Y_vals, y=line_45, mode="lines", line=dict(dash="dash", color=PLOT_THEME["neutral_color"]), name="خط ۴۵ درجه (Y = Z)"),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=Y_vals, y=planned_expenditure, mode="lines", line=dict(color=PLOT_THEME["primary_color"], width=2.5), name="تقاضای برنامه‌ریزی‌شده (Z)"),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=[Y_eq], y=[Y_eq], mode="markers+text", marker=dict(size=10, color="black"), text=["E₀"], textposition="top left", name="تعادل بازار کالا"),
        row=1, col=1
    )

    # --- پانل راست: منحنی IS ---
    fig.add_trace(
        go.Scatter(x=Y_vals, y=r_vals, mode="lines", line=dict(color=PLOT_THEME["secondary_color"], width=2.5), name="منحنی IS"),
        row=1, col=2
    )
    fig.add_trace(
        go.Scatter(x=[Y_eq], y=[r_current], mode="markers+text", marker=dict(size=10, color="black"), text=["E₀"], textposition="top right", showlegend=False),
        row=1, col=2
    )

    # خطوط راهنمای تعادل در پانل راست
    fig.add_shape(type="line", x0=Y_eq, x1=Y_eq, y0=0, y1=r_current, line=dict(dash="dot", color="gray"), row=1, col=2)
    fig.add_shape(type="line", x0=0, x1=Y_eq, y0=r_current, y1=r_current, line=dict(dash="dot", color="gray"), row=1, col=2)

    # تنظیمات نهایی ظاهر
    fig.update_xaxes(title_text="تولید ناخالص داخلی / درآمد ملی (Y)", gridcolor=PLOT_THEME["grid_color"], row=1, col=1)
    fig.update_yaxes(title_text="تقاضای کل (Z)", gridcolor=PLOT_THEME["grid_color"], row=1, col=1)
    fig.update_xaxes(title_text="تولید ناخالص داخلی (Y)", gridcolor=PLOT_THEME["grid_color"], row=1, col=2)
    fig.update_yaxes(title_text="نرخ بهره حقیقی (r)", tickformat=".1%", gridcolor=PLOT_THEME["grid_color"], range=[0, max(0.12, r_current * 1.8)], row=1, col=2)

    fig.update_layout(
        height=480,
        plot_bgcolor=PLOT_THEME["bg_color"],
        paper_bgcolor=PLOT_THEME["bg_color"],
        legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5),
        margin=dict(l=40, r=40, t=50, b=60)
    )
    return fig, Y_eq



