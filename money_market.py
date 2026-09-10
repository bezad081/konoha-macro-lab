import numpy as np
import plotly.graph_objects as go
from dataclasses import dataclass

PLOT_THEME = {
    "font_family": "Vazirmatn, Tahoma, sans-serif",
    "bg_color": "#ffffff",
    "grid_color": "#f1f5f9",
    "ms_color": "#2563eb",   # آبی عرضه پول
    "md_color": "#dc2626",   # قرمز تقاضای پول
    "trap_color": "#9333ea"  # بنفش تله نقدینگی
}

@dataclass
class MoneyMarketModel:
    M: float = 400.0
    P: float = 1.0
    k: float = 0.50
    h: float = 4000.0
    r_floor: float = 0.015  # حداقل نرخ بهره (کف دام نقدینگی)

    @property
    def real_money_supply(self) -> float:
        return self.M / self.P

    def demand_curve_r(self, m_vals: np.ndarray, Y: float) -> np.ndarray:
        """تابع تقاضای پول غیرخطی مجانب طبق متن کتاب مدرسان شریف"""
        ky = self.k * Y
        # تقاضای سفته‌بازی معکوس با نرخ بهره با مجانب افقی r_floor
        # r = r_floor + (h / (m - ky + epsilon))
        denom = np.maximum(10.0, m_vals - ky + 150.0)
        r = self.r_floor + (self.h * 0.08) / denom
        return np.maximum(self.r_floor, r)

    def solve_equilibrium_rate(self, Y: float) -> float:
        ky = self.k * Y
        ms = self.real_money_supply
        denom = max(10.0, ms - ky + 150.0)
        r = self.r_floor + (self.h * 0.08) / denom
        return float(max(self.r_floor, r))

def create_money_market_figure(model: MoneyMarketModel, Y_current: float = 1000.0, base_model: MoneyMarketModel = None, Y_base: float = 1000.0):
    if base_model is None:
        base_model = MoneyMarketModel()

    ms0 = base_model.real_money_supply
    ms1 = model.real_money_supply
    r0 = base_model.solve_equilibrium_rate(Y_base)
    r1 = model.solve_equilibrium_rate(Y_current)

    m_min = max(50.0, min(ms0, ms1, base_model.k * Y_base) - 150.0)
    m_max = max(ms0, ms1, model.k * Y_current) + 300.0
    m_vals = np.linspace(m_min, m_max, 300)

    # منحنی‌های تقاضای پول
    md_base = base_model.demand_curve_r(m_vals, Y=Y_base)
    md_curr = model.demand_curve_r(m_vals, Y=Y_current)

    max_r = max(0.14, r0 * 1.5, r1 * 1.5)

    fig = go.Figure()

    # خط تقاضای معاملاتی KY (مجانب عمودی طبق شکل ۷ کتاب)
    ky_curr = model.k * Y_current
    fig.add_trace(go.Scatter(
        x=[ky_curr, ky_curr], y=[0, max_r],
        mode="lines", line=dict(dash="dot", color="#94a3b8", width=1.5),
        name=f"مجانب عمودی تقاضای معاملاتی (kY={ky_curr:.0f})"
    ))

    # خط حداقل نرخ بهره (دام نقدینگی طبق متن کتاب)
    fig.add_trace(go.Scatter(
        x=[m_min, m_max], y=[model.r_floor, model.r_floor],
        mode="lines", line=dict(dash="dash", color=PLOT_THEME["trap_color"], width=1.8),
        name=f"کف دام نقدینگی ({model.r_floor*100:.1f}%)"
    ))

    # منحنی‌های تقاضای پول L(r, Y)
    fig.add_trace(go.Scatter(
        x=m_vals, y=md_base, mode="lines",
        line=dict(dash="dot", color="#cbd5e1", width=1.5), name="تقاضای پول مبنا (L₀)"
    ))
    fig.add_trace(go.Scatter(
        x=m_vals, y=md_curr, mode="lines",
        line=dict(color=PLOT_THEME["md_color"], width=3), name="منحنی تقاضای کل پول (Mᵈ/P)"
    ))

    # خطوط عرضه عمودی پول M/P (کاملاً منطبق بر شکل ۸ کتاب)
    fig.add_trace(go.Scatter(
        x=[ms0, ms0], y=[0, max_r], mode="lines",
        line=dict(dash="dot", color="#94a3b8", width=1.5), name=f"عرضه پول مبنا (M₀/P={ms0:.0f})"
    ))
    fig.add_trace(go.Scatter(
        x=[ms1, ms1], y=[0, max_r], mode="lines",
        line=dict(color=PLOT_THEME["ms_color"], width=3.5), name=f"عرضه پول جاری (M₁/P={ms1:.0f})"
    ))

    # نقاط تعادل E0 و E1
    fig.add_trace(go.Scatter(
        x=[ms0], y=[r0], mode="markers+text",
        marker=dict(size=8, color="#64748b"), text=["E₀"], textposition="top right", name="تعادل اولیه E₀"
    ))
    fig.add_trace(go.Scatter(
        x=[ms1], y=[r1], mode="markers+text",
        marker=dict(size=12, color="#0f172a"), text=["E₁"], textposition="top right", name="تعادل جدید E₁"
    ))

    # فلش تغییر نرخ بهره
    if abs(r1 - r0) > 0.003 or abs(ms1 - ms0) > 10.0:
        fig.add_annotation(
            ax=ms0, ay=r0, x=ms1, y=r1,
            xref="x", yref="y", axref="x", ayref="y",
            showarrow=True, arrowhead=2, arrowsize=1.3, arrowwidth=2.5, arrowcolor="#10b981"
        )

    # خط راهنمای تعادل به محور نرخ بهره
    fig.add_shape(type="line", x0=m_min, x1=ms1, y0=r1, y1=r1, line=dict(dash="dot", color="#94a3b8"))

    fig.update_xaxes(
        title_text="حجم حقیقی عرضه و تقاضای پول (M/P)",
        range=[m_min, m_max], gridcolor=PLOT_THEME["grid_color"], automargin=True
    )
    fig.update_yaxes(
        title_text="نرخ بهره بازار (r)",
        tickformat=".1%", range=[0.0, min(0.20, max_r)], gridcolor=PLOT_THEME["grid_color"], automargin=True
    )

    fig.update_layout(
        height=480, plot_bgcolor=PLOT_THEME["bg_color"], paper_bgcolor=PLOT_THEME["bg_color"],
        legend=dict(orientation="h", y=-0.22, x=0.5, xanchor="center"),
        margin=dict(l=75, r=35, t=40, b=70)
    )
    return fig, r1