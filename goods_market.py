import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dataclasses import dataclass

PLOT_THEME = {
    "font_family": "Vazirmatn, Tahoma, sans-serif",
    "bg_color": "#ffffff",
    "grid_color": "#f1f5f9",
    "primary_color": "#2563eb",   # آبی تقاضای کل
    "secondary_color": "#dc2626", # قرمز منحنی IS
    "neutral_color": "#64748b"    # خط ۴۵ درجه
}

@dataclass
class GoodsMarketModel:
    c0: float = 60.0
    mpc: float = 0.75
    t: float = 0.20
    i0: float = 140.0
    b: float = 600.0
    G: float = 120.0
    
    @property
    def multiplier(self) -> float:
        denom = 1.0 - self.mpc * (1.0 - self.t)
        return 1.0 / denom if denom > 0 else 1.0

    def autonomous_spending(self, r: float) -> float:
        return self.c0 + (self.i0 - self.b * r) + self.G

    def solve_equilibrium_output(self, r: float) -> float:
        return self.multiplier * self.autonomous_spending(r)

    def is_curve_rate(self, Y: np.ndarray) -> np.ndarray:
        A_max = self.c0 + self.i0 + self.G
        slope = (1.0 - self.mpc * (1.0 - self.t)) / self.b
        return (A_max / self.b) - slope * Y

def create_goods_market_figure(model: GoodsMarketModel, r_current: float = 0.05, base_model: GoodsMarketModel = None, r_base: float = 0.05):
    if base_model is None:
        base_model = GoodsMarketModel()

    Y_eq0 = base_model.solve_equilibrium_output(r_base)
    Y_eq1 = model.solve_equilibrium_output(r_current)

    # محدوده دینامیک برای اینکه نقطه تعادل همواره در مرکز کادر قرار گیرد
    center_y = (Y_eq0 + Y_eq1) / 2.0
    y_min = max(300.0, center_y - 450.0)
    y_max = max(1300.0, center_y + 450.0)
    Y_vals = np.linspace(y_min, y_max, 250)

    slope_base = base_model.mpc * (1.0 - base_model.t)
    z_base = base_model.autonomous_spending(r_base) + slope_base * Y_vals

    slope_curr = model.mpc * (1.0 - model.t)
    z_curr = model.autonomous_spending(r_current) + slope_curr * Y_vals

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=("الف) تقاطع کینزی (Keynesian Cross)", "ب) استخراج هندسی منحنی IS"),
        horizontal_spacing=0.14
    )

    # --- پانل چپ: تقاطع کینزی ---
    fig.add_trace(go.Scatter(
        x=Y_vals, y=Y_vals, mode="lines",
        line=dict(dash="dash", color=PLOT_THEME["neutral_color"], width=1.5),
        name="خط ۴۵ درجه (Y = Z)", hovertemplate="تولید = تقاضا: %{x:.0f}<extra></extra>"
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=Y_vals, y=z_base, mode="lines",
        line=dict(color="#cbd5e1", width=1.5, dash="dot"),
        name="تقاضای برنامه‌ریزی‌شده مبنا", hovertemplate="تقاضای مبنا: %{y:.1f}<extra></extra>"
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=Y_vals, y=z_curr, mode="lines",
        line=dict(color=PLOT_THEME["primary_color"], width=3),
        name="تقاضای جاری (Z)", hovertemplate="تقاضای جاری: %{y:.1f}<extra></extra>"
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=[Y_eq0], y=[Y_eq0], mode="markers+text",
        marker=dict(size=8, color="#64748b"), text=["E₀"], textposition="top left",
        name="تعادل اولیه"
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=[Y_eq1], y=[Y_eq1], mode="markers+text",
        marker=dict(size=11, color="#0f172a"), text=["E₁"], textposition="top left",
        name="تعادل جدید"
    ), row=1, col=1)

    # خطوط راهنمای تعادل در تقاطع کینزی
    fig.add_shape(type="line", x0=Y_eq1, x1=Y_eq1, y0=y_min, y1=Y_eq1, line=dict(dash="dot", color="#94a3b8"), row=1, col=1)
    fig.add_shape(type="line", x0=y_min, x1=Y_eq1, y0=Y_eq1, y1=Y_eq1, line=dict(dash="dot", color="#94a3b8"), row=1, col=1)

    # فلش انتقال تعادل تقاطع کینزی
    if abs(Y_eq1 - Y_eq0) > 15.0:
        fig.add_annotation(
            ax=Y_eq0, ay=Y_eq0, x=Y_eq1, y=Y_eq1,
            xref="x1", yref="y1", axref="x1", ayref="y1",
            showarrow=True, arrowhead=2, arrowsize=1.3, arrowwidth=2.5, arrowcolor="#10b981"
        )

    # --- پانل راست: منحنی IS ---
    fig.add_trace(go.Scatter(
        x=Y_vals, y=base_model.is_curve_rate(Y_vals), mode="lines",
        line=dict(color="#cbd5e1", width=1.5, dash="dot"),
        name="منحنی IS مبنا", hovertemplate="IS مبنا<extra></extra>"
    ), row=1, col=2)

    fig.add_trace(go.Scatter(
        x=Y_vals, y=model.is_curve_rate(Y_vals), mode="lines",
        line=dict(color=PLOT_THEME["secondary_color"], width=3),
        name="منحنی IS جاری", hovertemplate="تولید: %{x:.1f} | بهره: %{y:.2%}<extra></extra>"
    ), row=1, col=2)

    fig.add_trace(go.Scatter(
        x=[Y_eq0], y=[r_base], mode="markers+text",
        marker=dict(size=8, color="#64748b"), text=["E₀"], textposition="top right",
        showlegend=False
    ), row=1, col=2)

    fig.add_trace(go.Scatter(
        x=[Y_eq1], y=[r_current], mode="markers+text",
        marker=dict(size=11, color="#0f172a"), text=["E₁"], textposition="top right",
        showlegend=False
    ), row=1, col=2)

    # خطوط راهنما در پانل IS
    fig.add_shape(type="line", x0=Y_eq1, x1=Y_eq1, y0=0, y1=r_current, line=dict(dash="dot", color="#94a3b8"), row=1, col=2)
    fig.add_shape(type="line", x0=y_min, x1=Y_eq1, y0=r_current, y1=r_current, line=dict(dash="dot", color="#94a3b8"), row=1, col=2)

    # فلش انتقال در پانل IS
    if abs(Y_eq1 - Y_eq0) > 15.0 or abs(r_current - r_base) > 0.005:
        fig.add_annotation(
            ax=Y_eq0, ay=r_base, x=Y_eq1, y=r_current,
            xref="x2", yref="y2", axref="x2", ayref="y2",
            showarrow=True, arrowhead=2, arrowsize=1.3, arrowwidth=2.5, arrowcolor="#10b981"
        )

    max_r = max(0.15, r_base * 1.5, r_current * 1.5)

    fig.update_xaxes(title_text="تولید ناخالص داخلی (Y)", range=[y_min, y_max], gridcolor=PLOT_THEME["grid_color"], automargin=True, row=1, col=1)
    fig.update_yaxes(title_text="تقاضای کل برنامه‌ریزی‌شده (Z)", range=[y_min, y_max], gridcolor=PLOT_THEME["grid_color"], automargin=True, row=1, col=1)
    fig.update_xaxes(title_text="تولید ناخالص داخلی (Y)", range=[y_min, y_max], gridcolor=PLOT_THEME["grid_color"], automargin=True, row=1, col=2)
    fig.update_yaxes(title_text="نرخ بهره حقیقی (r)", tickformat=".1%", range=[0, min(0.20, max_r)], gridcolor=PLOT_THEME["grid_color"], automargin=True, row=1, col=2)

    fig.update_layout(
        height=480, plot_bgcolor=PLOT_THEME["bg_color"], paper_bgcolor=PLOT_THEME["bg_color"],
        legend=dict(orientation="h", y=-0.24, x=0.5, xanchor="center"),
        margin=dict(l=75, r=35, t=40, b=70),
       
    )
    return fig, Y_eq1