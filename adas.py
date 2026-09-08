# ماژول استخراج‌شده از adas.ipynb
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
from plotly.subplots import make_subplots
import ipywidgets as widgets
from IPython.display import display
from dataclasses import dataclass

PLOT_THEME = {
    "font_family": "Vazirmatn, Tahoma, sans-serif",
    "bg_color": "#ffffff",
    "grid_color": "#f1f5f9",
    "ad_color": "#2563eb",         # آبی برای تقاضای کل AD
    "sras_color": "#dc2626",       # قرمز برای عرضه کوتاه‌مدت SRAS
    "lras_color": "#16a34a",       # سبز برای پتانسیل بلندمدت LRAS
    "phillips_color": "#d97706"    # کهربایی برای منحنی فیلیپس
}

@dataclass
class ADASModel:
    # پارامترهای تقاضای کل (مشتق از IS-LM)
    A: float = 320.0       # مخارج خودگردان کل (c0 + i0 + G)
    alpha: float = 2.5     # ضریب فزاینده بازار کالا
    b: float = 600.0       # حساسیت سرمایه‌گذاری به بهره
    h: float = 4000.0      # حساسیت تقاضای پول به بهره
    k: float = 0.50        # حساسیت تقاضای پول به درآمد
    M: float = 400.0       # عرضه اسمی پول

    # پارامترهای طرف عرضه
    Y_potential: float = 1000.0  # سطح تولید طبیعی / پتانسیل (Y_n)
    P_expected: float = 1.0      # انتظارات قیمتی (P^e)
    lambda_slope: float = 0.0015 # شیب عرضه کل کوتاه‌مدت
    cost_shock: float = 0.0      # شوک هزینه/عرضه (z)

    @property
    def gamma(self) -> float:
        """ضریب تجمیعی اثر IS بر AD"""
        denom = (1.0 / self.alpha) + (self.b * self.k / self.h)
        return 1.0 / denom

    def ad_output(self, P: np.ndarray) -> np.ndarray:
        """مقدار تولید تقاضاشده بر اساس سطح قیمت: Y(P)"""
        return self.gamma * (self.A + (self.b / self.h) * (self.M / P))

    def sras_price(self, Y: np.ndarray) -> np.ndarray:
        """سطح قیمت ارائه‌شده توسط بنگاه‌ها بر اساس تولید: P(Y)"""
        return self.P_expected + self.lambda_slope * (Y - self.Y_potential) + self.cost_shock

    def solve_short_run_equilibrium(self):
        """یافتن نقطه تقاطع تعادل کوتاه‌مدت AD و SRAS با روش حل عددی ساده"""
        # بازه جستجوی قیمت تعادلی
        P_candidates = np.linspace(0.4, 3.0, 1000)
        Y_ad = self.ad_output(P_candidates)
        P_sras = self.sras_price(Y_ad)
        
        # نقطه حداقل اختلاف بین قیمت SRAS و قیمت AD
        idx = np.argmin(np.abs(P_candidates - P_sras))
        P_eq = P_candidates[idx]
        Y_eq = Y_ad[idx]
        
        output_gap = ((Y_eq - self.Y_potential) / self.Y_potential) * 100
        inflation_rate = (P_eq - 1.0) * 100  # نرخ تورم تقریبی نسبت به پایه
        
        return {
            "P": P_eq,
            "Y": Y_eq,
            "Output_Gap": output_gap,
            "Inflation": inflation_rate
        }

def create_adas_figure(base_model: ADASModel, current_model: ADASModel):
    eq0 = base_model.solve_short_run_equilibrium()
    eq1 = current_model.solve_short_run_equilibrium()

    P_vals = np.linspace(0.5, 2.5, 200)
    Y_vals = np.linspace(700, 1300, 200)

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=("الف) مدل تقاضا و عرضه کل (AD-AS)", "ب) منحنی فیلیپس و تورم کونوها"),
        horizontal_spacing=0.12
    )

    # سایه‌بندی ناحیه شکاف تولید (قرمز برای رکود، سبز برای تورم)
    y_pot = current_model.Y_potential
    y_eq = eq1["Y"]
    fill_color = "rgba(239, 68, 68, 0.18)" if y_eq < y_pot else "rgba(34, 197, 94, 0.18)"
    gap_label = "شکاف رکودی" if y_eq < y_pot else "شکاف تورمی"

    fig.add_vrect(
        x0=min(y_pot, y_eq), x1=max(y_pot, y_eq),
        fillcolor=fill_color, opacity=1, layer="below", line_width=0,
        annotation_text=gap_label, annotation_position="top left",
        row=1, col=1
    )

    # منحنی‌های تقاضای کل با Hovertemplate سفارشی فارسی
    fig.add_trace(go.Scatter(
        x=[y_pot, y_pot], y=[0.5, 2.5], mode="lines",
        line=dict(color="#16a34a", width=3, dash="dash"),
        name="LRAS (تولید طبیعی)",
        hovertemplate="تولید طبیعی: %{x:.0f}<extra></extra>"
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=base_model.ad_output(P_vals), y=P_vals, mode="lines",
        line=dict(color="#94a3b8", width=1.5, dash="dot"),
        name="AD مبنا", hovertemplate="AD اولیه<extra></extra>"
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=current_model.ad_output(P_vals), y=P_vals, mode="lines",
        line=dict(color="#2563eb", width=3),
        name="AD جاری", hovertemplate="تولید تقاضاشده: %{x:.1f} | قیمت: %{y:.2f}<extra></extra>"
    ), row=1, col=1)

    # منحنی‌های عرضه کل
    fig.add_trace(go.Scatter(
        x=base_model.sras_price(Y_vals), y=P_vals, mode="lines",
        line=dict(color="#cbd5e1", width=1.5, dash="dot"),
        name="SRAS مبنا", hovertemplate="SRAS اولیه<extra></extra>"
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=Y_vals, y=current_model.sras_price(Y_vals), mode="lines",
        line=dict(color="#dc2626", width=3),
        name="SRAS جاری", hovertemplate="تولید عرضه‌شده: %{x:.1f} | قیمت: %{y:.2f}<extra></extra>"
    ), row=1, col=1)

    # نقاط تعادل و فلش انتقال تعادل
    fig.add_trace(go.Scatter(
        x=[eq0["Y"]], y=[eq0["P"]], mode="markers+text",
        marker=dict(size=8, color="#64748b"), text=["E₀"], textposition="top right",
        name="تعادل اولیه", hovertemplate="تعادل اولیه E0<extra></extra>"
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=[eq1["Y"]], y=[eq1["P"]], mode="markers+text",
        marker=dict(size=12, color="#0f172a"), text=["E₁"], textposition="top left",
        name="تعادل جدید", hovertemplate="تولید نهایی: %{x:.1f} | قیمت: %{y:.2f}<extra></extra>"
    ), row=1, col=1)

    # فلش پویا بین تعادل قدیم و جدید
    if abs(eq1["Y"] - eq0["Y"]) > 2 or abs(eq1["P"] - eq0["P"]) > 0.02:
        fig.add_annotation(
            ax=eq0["Y"], ay=eq0["P"], x=eq1["Y"], y=eq1["P"],
            xref="x1", yref="y1", axref="x1", ayref="y1",
            showarrow=True, arrowhead=3, arrowsize=1.2, arrowwidth=2, arrowcolor="#e11d48"
        )

    # منحنی فیلیپس
    gap_range = np.linspace(-25, 25, 200)
    pi_curr = 0.0 + 0.35 * gap_range + (current_model.cost_shock * 100)
    fig.add_trace(go.Scatter(
        x=gap_range, y=pi_curr, mode="lines",
        line=dict(color="#d97706", width=3), name="منحنی فیلیپس جاری",
        hovertemplate="شکاف: %{x:.1f}٪ | تورم: %{y:.1f}٪<extra></extra>"
    ), row=1, col=2)

    fig.add_trace(go.Scatter(
        x=[eq1["Output_Gap"]], y=[eq1["Inflation"]], mode="markers+text",
        marker=dict(size=11, color="#0f172a"), text=["E₁"], textposition="top left",
        showlegend=False, hovertemplate="تورم جاری: %{y:.1f}٪<extra></extra>"
    ), row=1, col=2)

    fig.update_xaxes(title_text="تولید ناخالص کونوها (Y)", range=[700, 1300], row=1, col=1)
    fig.update_yaxes(title_text="سطح عمومی قیمت‌ها (P)", range=[0.5, 2.5], row=1, col=1)
    fig.update_xaxes(title_text="شکاف تولید (٪)", zeroline=True, range=[-25, 25], row=1, col=2)
    fig.update_yaxes(title_text="نرخ تورم (٪)", zeroline=True, range=[-15, 35], row=1, col=2)

    fig.update_layout(
        height=500, plot_bgcolor="#ffffff", paper_bgcolor="#ffffff",
        legend=dict(orientation="h", y=-0.22, x=0.5, xanchor="center")
    )
    return fig, eq0, eq1



