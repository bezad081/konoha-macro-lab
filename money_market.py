import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dataclasses import dataclass

PLOT_THEME = {
    "font_family": "Vazirmatn, Tahoma, sans-serif",
    "bg_color": "#ffffff",
    "grid_color": "#f1f5f9",
    "money_demand_color": "#0284c7",   # آبی تقاضای پول
    "money_supply_color": "#16a34a",   # سبز عرضه پول
    "lm_color": "#7c3aed"              # بنفش منحنی LM
}

@dataclass
class MoneyMarketModel:
    M: float = 400.0
    P: float = 1.0
    k: float = 0.50
    h: float = 4000.0
    
    @property
    def real_money_supply(self) -> float:
        return self.M / self.P

    def solve_interest_rate(self, Y: float) -> float:
        r = (self.k * Y - self.real_money_supply) / self.h
        return max(0.001, r)

    def money_demand(self, r: np.ndarray, Y: float) -> np.ndarray:
        return np.maximum(0.0, self.k * Y - self.h * r)

    def lm_curve_rate(self, Y: np.ndarray) -> np.ndarray:
        r = (self.k * Y - self.real_money_supply) / self.h
        return np.maximum(0.001, r)

def create_money_market_figure(model: MoneyMarketModel, Y_current: float = 1000.0, base_model: MoneyMarketModel = None, Y_base: float = 1000.0):
    if base_model is None:
        base_model = MoneyMarketModel()

    r_eq0 = base_model.solve_interest_rate(Y_base)
    r_eq1 = model.solve_interest_rate(Y_current)

    real_M0 = base_model.real_money_supply
    real_M1 = model.real_money_supply

    # محاسبه حدود دینامیک نمودارها
    m_max = max(700.0, real_M0 * 1.5, real_M1 * 1.5)
    r_max = max(0.14, r_eq0 * 1.6, r_eq1 * 1.6)
    r_vals = np.linspace(0.001, min(0.22, r_max), 250)

    center_y = (Y_base + Y_current) / 2.0
    y_min = max(400.0, center_y - 450.0)
    y_max = max(1350.0, center_y + 450.0)
    Y_vals = np.linspace(y_min, y_max, 250)

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=("الف) تعادل ترجیح نقدینگی در بازار پول", "ب) استخراج هندسی منحنی LM"),
        horizontal_spacing=0.14
    )

    # --- پانل چپ: بازار پول ---
    fig.add_trace(go.Scatter(
        x=base_model.money_demand(r_vals, Y=Y_base), y=r_vals, mode="lines",
        line=dict(color="#cbd5e1", width=1.5, dash="dot"),
        name=f"تقاضای پول مبنا (Y={Y_base:.0f})", hovertemplate="L مبنا<extra></extra>"
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=model.money_demand(r_vals, Y=Y_current), y=r_vals, mode="lines",
        line=dict(color=PLOT_THEME["money_demand_color"], width=3),
        name=f"تقاضای پول جاری L(Y={Y_current:.0f})", hovertemplate="مانده تقاضا: %{x:.1f} | بهره: %{y:.2%}<extra></extra>"
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=[real_M0, real_M0], y=[0, r_max], mode="lines",
        line=dict(color="#a7f3d0", width=1.5, dash="dot"),
        name=f"عرضه پول مبنا ({real_M0:.0f})", hovertemplate="M/P مبنا<extra></extra>"
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=[real_M1, real_M1], y=[0, r_max], mode="lines",
        line=dict(color=PLOT_THEME["money_supply_color"], width=3),
        name=f"عرضه واقعی جاری ({real_M1:.0f})", hovertemplate="عرضه واقعی: %{x:.1f}<extra></extra>"
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=[real_M1], y=[r_eq1], mode="markers+text",
        marker=dict(size=11, color="#0f172a"), text=["E₁"], textposition="top right",
        showlegend=False
    ), row=1, col=1)

    fig.add_shape(type="line", x0=0, x1=real_M1, y0=r_eq1, y1=r_eq1, line=dict(dash="dot", color="#94a3b8"), row=1, col=1)

    # فلش انتقال تعادل بازار پول
    if abs(real_M1 - real_M0) > 15.0 or abs(r_eq1 - r_eq0) > 0.005:
        fig.add_annotation(
            ax=real_M0, ay=r_eq0, x=real_M1, y=r_eq1,
            xref="x1", yref="y1", axref="x1", ayref="y1",
            showarrow=True, arrowhead=2, arrowsize=1.3, arrowwidth=2.5, arrowcolor="#10b981"
        )

    # --- پانل راست: منحنی LM ---
    fig.add_trace(go.Scatter(
        x=Y_vals, y=base_model.lm_curve_rate(Y_vals), mode="lines",
        line=dict(color="#cbd5e1", width=1.5, dash="dot"),
        name="منحنی LM مبنا", hovertemplate="LM مبنا<extra></extra>"
    ), row=1, col=2)

    fig.add_trace(go.Scatter(
        x=Y_vals, y=model.lm_curve_rate(Y_vals), mode="lines",
        line=dict(color=PLOT_THEME["lm_color"], width=3),
        name="منحنی LM جاری", hovertemplate="تولید: %{x:.1f} | بهره تعادلی: %{y:.2%}<extra></extra>"
    ), row=1, col=2)

    fig.add_trace(go.Scatter(
        x=[Y_base], y=[r_eq0], mode="markers+text",
        marker=dict(size=8, color="#64748b"), text=["E₀"], textposition="top left",
        showlegend=False
    ), row=1, col=2)

    fig.add_trace(go.Scatter(
        x=[Y_current], y=[r_eq1], mode="markers+text",
        marker=dict(size=11, color="#0f172a"), text=["E₁"], textposition="top left",
        showlegend=False
    ), row=1, col=2)

    fig.add_shape(type="line", x0=Y_current, x1=Y_current, y0=0, y1=r_eq1, line=dict(dash="dot", color="#94a3b8"), row=1, col=2)
    fig.add_shape(type="line", x0=y_min, x1=Y_current, y0=r_eq1, y1=r_eq1, line=dict(dash="dot", color="#94a3b8"), row=1, col=2)

    # فلش انتقال در پانل LM
    if abs(Y_current - Y_base) > 15.0 or abs(r_eq1 - r_eq0) > 0.005:
        fig.add_annotation(
            ax=Y_base, ay=r_eq0, x=Y_current, y=r_eq1,
            xref="x2", yref="y2", axref="x2", ayref="y2",
            showarrow=True, arrowhead=2, arrowsize=1.3, arrowwidth=2.5, arrowcolor="#10b981"
        )

    fig.update_xaxes(title_text="مانده واقعی نقدینگی (M/P)", range=[50, m_max], gridcolor=PLOT_THEME["grid_color"], automargin=True, row=1, col=1)
    fig.update_yaxes(title_text="نرخ بهره تعادلی (r)", tickformat=".1%", range=[0, min(0.20, r_max)], gridcolor=PLOT_THEME["grid_color"], automargin=True, row=1, col=1)
    fig.update_xaxes(title_text="تولید ناخالص داخلی (Y)", range=[y_min, y_max], gridcolor=PLOT_THEME["grid_color"], automargin=True, row=1, col=2)
    fig.update_yaxes(title_text="نرخ بهره تعادلی (r)", tickformat=".1%", range=[0, min(0.20, r_max)], gridcolor=PLOT_THEME["grid_color"], automargin=True, row=1, col=2)

    fig.update_layout(
        height=480, plot_bgcolor=PLOT_THEME["bg_color"], paper_bgcolor=PLOT_THEME["bg_color"],
        legend=dict(orientation="h", y=-0.24, x=0.5, xanchor="center"),
        margin=dict(l=75, r=35, t=40, b=70),
       
    )
    return fig, r_eq1