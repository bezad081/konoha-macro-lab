# ماژول استخراج‌شده از money_market.ipynb
# بدون تغییر در توابع و کلاس‌های اصلی

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import ipywidgets as widgets
from IPython.display import display
from dataclasses import dataclass

PLOT_THEME = {
    "font_family": "Vazirmatn, Tahoma, sans-serif",
    "bg_color": "#ffffff",
    "grid_color": "#f1f5f9",
    "money_demand_color": "#0284c7",   # آبی آسمانی برای تقاضای پول (L)
    "money_supply_color": "#16a34a",   # سبز برای عرضه عمودی پول (M/P)
    "lm_color": "#7c3aed",             # بنفش برای منحنی LM
    "neutral_color": "#94a3b8"
}

@dataclass
class MoneyMarketModel:
    M: float = 400.0       # عرضه اسمی پول
    P: float = 1.0         # سطح قیمت‌ها
    k: float = 0.50        # حساسیت تقاضای معاملاتی به درآمد
    h: float = 4000.0      # حساسیت تقاضای سوداگری به نرخ بهره
    
    @property
    def real_money_supply(self) -> float:
        """عرضه واقعی پول: M / P"""
        return self.M / self.P

    def solve_interest_rate(self, Y: float) -> float:
        """محاسبه نرخ بهره تعادلی برای یک سطح تولید معین"""
        r = (self.k * Y - self.real_money_supply) / self.h
        return max(0.001, r)  # نرخ بهره اسمی کمتر از صفر نمی‌شود (ZLB)

    def money_demand(self, r: np.ndarray, Y: float) -> np.ndarray:
        """مقدار مانده واقعی مورد تقاضا در ازای نرخ‌های بهره مختلف"""
        return np.maximum(0.0, self.k * Y - self.h * r)

    def lm_curve_rate(self, Y: np.ndarray) -> np.ndarray:
        """معادله منحنی LM: r بر حسب Y"""
        r = (self.k * Y - self.real_money_supply) / self.h
        return np.maximum(0.001, r)

def create_money_market_figure(model: MoneyMarketModel, Y_current: float = 1000.0):
    r_eq = model.solve_interest_rate(Y_current)
    real_M = model.real_money_supply
    
    # دامنه نرخ بهره برای رسم بازار پول
    r_max = max(0.12, r_eq * 1.8)
    r_vals = np.linspace(0.001, r_max, 200)
    
    # توابع بازار پول (نمودار چپ)
    L_curve = model.money_demand(r_vals, Y=Y_current)
    
    # دامنه تولید برای رسم منحنی LM (نمودار راست)
    Y_vals = np.linspace(600, 1600, 200)
    lm_r = model.lm_curve_rate(Y_vals)

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=("الف) تعادل ترجیح نقدینگی در بازار پول", "ب) استخراج هندسی منحنی LM"),
        horizontal_spacing=0.12
    )

    # --- پانل چپ: بازار پول ---
    # منحنی تقاضای پول L(Y, r)
    fig.add_trace(
        go.Scatter(x=L_curve, y=r_vals, mode="lines", 
                   line=dict(color=PLOT_THEME["money_demand_color"], width=2.5), 
                   name=f"تقاضای پول L(Y={Y_current:.0f})"),
        row=1, col=1
    )
    # خط عرضه پول عمودی M/P
    fig.add_trace(
        go.Scatter(x=[real_M, real_M], y=[0, r_max], mode="lines", 
                   line=dict(color=PLOT_THEME["money_supply_color"], width=2.5, dash="solid"), 
                   name=f"عرضه پول واقعی (M/P={real_M:.0f})"),
        row=1, col=1
    )
    # نقطه تعادل بازار پول
    fig.add_trace(
        go.Scatter(x=[real_M], y=[r_eq], mode="markers+text", 
                   marker=dict(size=10, color="black"), 
                   text=["E₀"], textposition="top right", showlegend=False),
        row=1, col=1
    )

    # --- پانل راست: منحنی LM ---
    fig.add_trace(
        go.Scatter(x=Y_vals, y=lm_r, mode="lines", 
                   line=dict(color=PLOT_THEME["lm_color"], width=2.5), 
                   name="منحنی LM"),
        row=1, col=2
    )
    fig.add_trace(
        go.Scatter(x=[Y_current], y=[r_eq], mode="markers+text", 
                   marker=dict(size=10, color="black"), 
                   text=["E₀"], textposition="top left", showlegend=False),
        row=1, col=2
    )

    # خطوط راهنمای تعادل
    fig.add_shape(type="line", x0=0, x1=real_M, y0=r_eq, y1=r_eq, line=dict(dash="dot", color="gray"), row=1, col=1)
    fig.add_shape(type="line", x0=Y_current, x1=Y_current, y0=0, y1=r_eq, line=dict(dash="dot", color="gray"), row=1, col=2)
    fig.add_shape(type="line", x0=600, x1=Y_current, y0=r_eq, y1=r_eq, line=dict(dash="dot", color="gray"), row=1, col=2)

    # تنظیمات محورها
    fig.update_xaxes(title_text="مانده واقعی پول (M/P)", gridcolor=PLOT_THEME["grid_color"], row=1, col=1)
    fig.update_yaxes(title_text="نرخ بهره (r)", tickformat=".1%", gridcolor=PLOT_THEME["grid_color"], range=[0, r_max], row=1, col=1)
    fig.update_xaxes(title_text="تولید / درآمد ملی (Y)", gridcolor=PLOT_THEME["grid_color"], row=1, col=2)
    fig.update_yaxes(title_text="نرخ بهره تعادلی (r)", tickformat=".1%", gridcolor=PLOT_THEME["grid_color"], range=[0, r_max], row=1, col=2)

    fig.update_layout(
        height=480,
        plot_bgcolor=PLOT_THEME["bg_color"],
        paper_bgcolor=PLOT_THEME["bg_color"],
        legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5),
        margin=dict(l=40, r=40, t=50, b=60)
    )
    return fig, r_eq



