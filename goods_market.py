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
    c0: float = 60.0       # مصرف خودگردان
    mpc: float = 0.75      # میل نهایی به مصرف
    t: float = 0.20        # نرخ مالیات
    i0: float = 140.0      # سرمایه‌گذاری خودگردان
    b: float = 600.0       # حساسیت سرمایه‌گذاری به بهره
    G: float = 120.0       # مخارج دولت
    
    @property
    def multiplier(self) -> float:
        """ضریب فزاینده کینزی: 1 / [1 - mpc*(1 - t)]"""
        denom = 1.0 - self.mpc * (1.0 - self.t)
        return 1.0 / denom if denom > 0 else np.nan

    def autonomous_spending(self, r: float) -> float:
        """کل مخارج خودگردان: A(r) = c0 + i0 - b*r + G"""
        return self.c0 + (self.i0 - self.b * r) + self.G

    def solve_equilibrium_output(self, r: float) -> float:
        """تولید تعادلی بازار کالا: Y = alpha * A(r)"""
        return self.multiplier * self.autonomous_spending(r)

    def is_curve_rate(self, Y: np.ndarray) -> np.ndarray:
        """معادله منحنی IS: r بر حسب Y"""
        A_max = self.c0 + self.i0 + self.G
        slope = (1.0 - self.mpc * (1.0 - self.t)) / self.b
        return (A_max / self.b) - slope * Y

def create_goods_market_figure(model: GoodsMarketModel, r_current: float = 0.05, base_model: GoodsMarketModel = None, r_base: float = 0.05):
    if base_model is None:
        base_model = GoodsMarketModel()

    Y_eq0 = base_model.solve_equilibrium_output(r_base)
    Y_eq1 = model.solve_equilibrium_output(r_current)

    Y_vals = np.linspace(500, 1400, 250)
    line_45 = Y_vals

    slope_base = base_model.mpc * (1.0 - base_model.t)
    z_base = base_model.autonomous_spending(r_base) + slope_base * Y_vals

    slope_curr = model.mpc * (1.0 - model.t)
    z_curr = model.autonomous_spending(r_current) + slope_curr * Y_vals

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=("الف) تقاطع کینزی (Keynesian Cross)", "ب) استخراج هندسی منحنی IS"),
        horizontal_spacing=0.12
    )

    # --- پانل چپ: تقاطع کینزی ---
    fig.add_trace(go.Scatter(
        x=Y_vals, y=line_45, mode="lines",
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
        name="تقاضای برنامه‌ریزی‌شده جاری (Z)", hovertemplate="تقاضای جاری: %{y:.1f}<extra></extra>"
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
    fig.add_shape(type="line", x0=Y_eq1, x1=Y_eq1, y0=500, y1=Y_eq1, line=dict(dash="dot", color="#94a3b8"), row=1, col=1)
    fig.add_shape(type="line", x0=500, x1=Y_eq1, y0=Y_eq1, y1=Y_eq1, line=dict(dash="dot", color="#94a3b8"), row=1, col=1)

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
    fig.add_shape(type="line", x0=500, x1=Y_eq1, y0=r_current, y1=r_current, line=dict(dash="dot", color="#94a3b8"), row=1, col=2)

    fig.update_xaxes(title_text="تولید ناخالص داخلی (Y)", range=[500, 1400], gridcolor=PLOT_THEME["grid_color"], row=1, col=1)
    fig.update_yaxes(title_text="تقاضای کل (Z)", range=[500, 1400], gridcolor=PLOT_THEME["grid_color"], row=1, col=1)
    fig.update_xaxes(title_text="تولید ناخالص داخلی (Y)", range=[500, 1400], gridcolor=PLOT_THEME["grid_color"], row=1, col=2)
    fig.update_yaxes(title_text="نرخ بهره حقیقی (r)", tickformat=".1%", range=[0, 0.16], gridcolor=PLOT_THEME["grid_color"], row=1, col=2)

    fig.update_layout(
        height=480, plot_bgcolor=PLOT_THEME["bg_color"], paper_bgcolor=PLOT_THEME["bg_color"],
        legend=dict(orientation="h", y=-0.22, x=0.5, xanchor="center"),
        margin=dict(l=40, r=40, t=50, b=60)
    )
    return fig, Y_eq1