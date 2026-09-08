# ماژول استخراج‌شده از islm.ipynb
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
    "is_color": "#dc2626",        # قرمز برای IS
    "lm_color": "#2563eb",        # آبی برای LM
    "is_shifted_color": "#f87171",# قرمز کم‌رنگ برای خط جابه‌جاشده
    "lm_shifted_color": "#60a5fa" # آبی کم‌رنگ برای خط جابه‌جاشده
}

@dataclass
class ISLMEngine:
    # پارامترهای بازار کالا
    c0: float = 60.0
    mpc: float = 0.75
    t: float = 0.20
    i0: float = 140.0
    b: float = 600.0
    G: float = 120.0

    # پارامترهای بازار پول
    M: float = 400.0
    P: float = 1.0
    k: float = 0.50
    h: float = 4000.0

    @property
    def multiplier(self) -> float:
        """ضریب فزاینده کینزی"""
        return 1.0 / (1.0 - self.mpc * (1.0 - self.t))

    @property
    def autonomous_spending(self) -> float:
        """مخارج خودگردان: A = c0 + i0 + G"""
        return self.c0 + self.i0 + self.G

    def solve_equilibrium(self):
        """حل هم‌زمان و دقیق دستگاه دو معادله و دو مجهول"""
        alpha = self.multiplier
        A = self.autonomous_spending
        real_M = self.M / self.P

        # مخرج کسر درآمد ملی تعادلی
        denom = (1.0 / alpha) + (self.b * self.k / self.h)
        Y_star = (A + (self.b / self.h) * real_M) / denom
        r_star = (self.k * Y_star - real_M) / self.h

        # متغیرهای تفصیلی
        T = self.t * Y_star
        C = self.c0 + self.mpc * (Y_star - T)
        I = self.i0 - self.b * r_star

        return {
            "Y": Y_star,
            "r": max(0.0001, r_star),
            "C": C,
            "I": I,
            "T": T,
            "Deficit": self.G - T
        }

    def get_is_curve(self, Y_vals: np.ndarray) -> np.ndarray:
        """معادله منحنی IS"""
        alpha = self.multiplier
        A = self.autonomous_spending
        return (A / self.b) - (Y_vals / (alpha * self.b))

    def get_lm_curve(self, Y_vals: np.ndarray) -> np.ndarray:
        """معادله منحنی LM"""
        real_M = self.M / self.P
        return (self.k * Y_vals - real_M) / self.h

def create_islm_figure(base_engine: ISLMEngine, current_engine: ISLMEngine):
    eq0 = base_engine.solve_equilibrium()
    eq1 = current_engine.solve_equilibrium()

    Y_vals = np.linspace(700, 1350, 200)
    fig = go.Figure()

    # خطوط مبدا
    fig.add_trace(go.Scatter(
        x=Y_vals, y=base_engine.get_is_curve(Y_vals), mode="lines",
        line=dict(dash="dot", color="#94a3b8", width=2), name="IS مبنا",
        hovertemplate="منحنی IS مبنا<extra></extra>"
    ))
    fig.add_trace(go.Scatter(
        x=Y_vals, y=base_engine.get_lm_curve(Y_vals), mode="lines",
        line=dict(dash="dot", color="#94a3b8", width=2), name="LM مبنا",
        hovertemplate="منحنی LM مبنا<extra></extra>"
    ))
    fig.add_trace(go.Scatter(
        x=[eq0["Y"]], y=[eq0["r"]], mode="markers+text",
        marker=dict(size=8, color="#64748b"), text=["E₀"], textposition="top right",
        name="تعادل مبدا E₀"
    ))

    # خطوط جاری
    fig.add_trace(go.Scatter(
        x=Y_vals, y=current_engine.get_is_curve(Y_vals), mode="lines",
        line=dict(color="#dc2626", width=3), name="منحنی IS جاری",
        hovertemplate="تولید کالا: %{x:.1f} | نرخ بهره: %{y:.2%}<extra></extra>"
    ))
    fig.add_trace(go.Scatter(
        x=Y_vals, y=current_engine.get_lm_curve(Y_vals), mode="lines",
        line=dict(color="#2563eb", width=3), name="منحنی LM جاری",
        hovertemplate="تولید پول: %{x:.1f} | نرخ بهره: %{y:.2%}<extra></extra>"
    ))
    fig.add_trace(go.Scatter(
        x=[eq1["Y"]], y=[eq1["r"]], mode="markers+text",
        marker=dict(size=12, color="#0f172a"), text=["E₁"], textposition="top left",
        name="تعادل جدید E₁"
    ))

    # فلش پویا جهت انتقال تعادل کالا و پول
    if abs(eq1["Y"] - eq0["Y"]) > 2 or abs(eq1["r"] - eq0["r"]) > 0.002:
        fig.add_annotation(
            ax=eq0["Y"], ay=eq0["r"], x=eq1["Y"], y=eq1["r"],
            xref="x", yref="y", axref="x", ayref="y",
            showarrow=True, arrowhead=3, arrowsize=1.2, arrowwidth=2, arrowcolor="#10b981"
        )

    fig.update_xaxes(title_text="تولید ناخالص داخلی کونوها (Y)", range=[700, 1350], gridcolor="#f1f5f9")
    fig.update_yaxes(title_text="نرخ بهره تعادلی (r)", tickformat=".1%", range=[0, 0.16], gridcolor="#f1f5f9")
    fig.update_layout(
        height=480, plot_bgcolor="#ffffff", paper_bgcolor="#ffffff",
        legend=dict(orientation="h", y=-0.2, x=0.5, xanchor="center")
    )
    return fig, eq0, eq1


