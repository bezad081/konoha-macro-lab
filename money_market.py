import numpy as np
import plotly.graph_objects as go
from dataclasses import dataclass

PLOT_THEME = {
    "font_family": "Vazirmatn, Tahoma, sans-serif",
    "bg_color": "#ffffff",
    "grid_color": "#f1f5f9",
    "ms_base_color": "#94a3b8",
    "ms_curr_color": "#2563eb",   # آبی عرضه پول
    "md_base_color": "#cbd5e1",
    "md_curr_color": "#dc2626",   # قرمز تقاضای پول
    "asymptote_color": "#64748b", # خاکستری مجانب‌ها
    "trap_color": "#7c3aed"       # بنفش دام نقدینگی
}

@dataclass
class MoneyMarketModel:
    M: float = 400.0
    P: float = 1.0
    k: float = 0.50               # نسبت تقاضای معاملاتی به درآمد
    h: float = 4000.0             # ضریب حساسیت به بهره
    r_floor: float = 0.015        # حداقل نرخ بهره (دام نقدینگی: ۱.۵٪)
    regime: str = "standard"      # "standard", "liquidity_trap", "classical"

    @property
    def real_money_supply(self) -> float:
        return self.M / self.P

    def demand_curve_exact(self, m_grid: np.ndarray, Y: float) -> np.ndarray:
        """
        معادله هذلولی استاندارد کینزی با دو مجانب:
        - مجانب عمودی در m = k*Y (تقاضای صرفاً معاملاتی در بهره بسیار بالا)
        - مجانب افقی در r = r_floor (دام نقدینگی در مانده‌های نقدینگی بالا)
        """
        ky = self.k * Y

        if self.regime == "classical":
            # در نظریه مقداری کلاسیک: تقاضا کاملاً عمودی در kY است
            return np.full_like(m_grid, np.nan)

        if self.regime == "liquidity_trap":
            # در تله نقدینگی کشش بی‌نهایت روی کف r_floor است
            return np.full_like(m_grid, self.r_floor)

        # ضریب هذلولی بر اساس حساسیت ترجیح نقدینگی h
        gamma = self.h * 0.0035
        # فاصله از مجانب عمودی
        dist = m_grid - ky
        # فقط در نقاط سمت راست مجانب عمودی تعریف می‌شود
        r_vals = np.where(dist > 0.5, self.r_floor + (gamma / dist), np.nan)
        return r_vals

    def solve_equilibrium_rate(self, Y: float) -> float:
        """حل دقیق نرخ بهره تعادلی بازار پول"""
        ky = self.k * Y
        ms = self.real_money_supply

        if self.regime == "classical":
            return 0.05  # در مکتب کلاسیک بازار پول نرخ بهره را تعیین نمی‌کند
        elif self.regime == "liquidity_trap":
            return self.r_floor

        dist = max(1.0, ms - ky)
        gamma = self.h * 0.0035
        r_eq = self.r_floor + (gamma / dist)
        return float(max(self.r_floor, r_eq))


def create_money_market_figure(model: MoneyMarketModel, Y_current: float = 1000.0, base_model: MoneyMarketModel = None, Y_base: float = 1000.0):
    if base_model is None:
        base_model = MoneyMarketModel(regime=model.regime)

    ms0 = base_model.real_money_supply
    ms1 = model.real_money_supply
    r0 = base_model.solve_equilibrium_rate(Y_base)
    r1 = model.solve_equilibrium_rate(Y_current)

    ky0 = base_model.k * Y_base
    ky1 = model.k * Y_current

    # محدوده متناسب محور افقی
    m_min = max(20.0, min(ky0, ky1) - 60.0)
    m_max = max(ms0, ms1, ky0, ky1) + 260.0
    m_vals = np.linspace(m_min, m_max, 500)

    max_r = min(0.18, max(0.12, r0 * 1.6, r1 * 1.6))

    fig = go.Figure()

    # ۱. مجانب افقی: کف دام نقدینگی (شکل ۷ کتاب)
    fig.add_trace(go.Scatter(
        x=[m_min, m_max], y=[model.r_floor, model.r_floor],
        mode="lines", line=dict(dash="dash", color=PLOT_THEME["trap_color"], width=1.5),
        name=f"مجانب افقی: کف دام نقدینگی ({model.r_floor*100:.1f}%)"
    ))

    # ۲. مجانب عمودی تقاضای معاملاتی KY (شکل ۷ و ۹ کتاب)
    fig.add_trace(go.Scatter(
        x=[ky1, ky1], y=[0, max_r],
        mode="lines", line=dict(dash="dot", color=PLOT_THEME["asymptote_color"], width=1.8),
        name=f"مجانب عمودی: تقاضای معاملاتی (kY = {ky1:.0f})"
    ))

    # ۳. منحنی‌های تقاضای کل پول Md/P
    if model.regime == "classical":
        fig.add_trace(go.Scatter(
            x=[ky1, ky1], y=[0, max_r],
            mode="lines", line=dict(color=PLOT_THEME["md_curr_color"], width=3.5),
            name="تقاضای کلاسیک عمودی (Mᵈ/P = kY)"
        ))
    elif model.regime == "liquidity_trap":
        fig.add_trace(go.Scatter(
            x=[m_min, m_max], y=[model.r_floor, model.r_floor],
            mode="lines", line=dict(color=PLOT_THEME["md_curr_color"], width=3.5),
            name="تقاضا در دام نقدینگی (کشش بی‌نهایت در کف)"
        ))
    else:
        # منحنی تقاضای مبنا (خط چین خاکستری)
        r_curve_base = base_model.demand_curve_exact(m_vals, Y=Y_base)
        fig.add_trace(go.Scatter(
            x=m_vals, y=r_curve_base, mode="lines",
            line=dict(dash="dot", color=PLOT_THEME["md_base_color"], width=1.8),
            name="تقاضای مبنا L₀(r, Y₀)"
        ))

        # منحنی تقاضای جاری (قرمز پررنگ هایپربولیک)
        r_curve_curr = model.demand_curve_exact(m_vals, Y=Y_current)
        fig.add_trace(go.Scatter(
            x=m_vals, y=r_curve_curr, mode="lines",
            line=dict(color=PLOT_THEME["md_curr_color"], width=3),
            name="تقاضای کل پول Mᵈ/P = L(r, Y₁)"
        ))

    # ۴. خطوط عمودی عرضه برون‌زای پول Ms/P (شکل ۸ کتاب)
    fig.add_trace(go.Scatter(
        x=[ms0, ms0], y=[0, max_r], mode="lines",
        line=dict(dash="dot", color=PLOT_THEME["ms_base_color"], width=1.5),
        name=f"عرضه پول مبنا (M₀/P = {ms0:.0f})"
    ))
    fig.add_trace(go.Scatter(
        x=[ms1, ms1], y=[0, max_r], mode="lines",
        line=dict(color=PLOT_THEME["ms_curr_color"], width=3.5),
        name=f"عرضه پول جاری (M₁/P = {ms1:.0f})"
    ))

    # ۵. نقاط تعادل E0 و E1 (شکل ۸ و ۹ کتاب)
    fig.add_trace(go.Scatter(
        x=[ms0], y=[r0], mode="markers+text",
        marker=dict(size=8, color="#64748b"),
        text=["E₀"], textposition="top right",
        name="تعادل اولیه E₀"
    ))
    fig.add_trace(go.Scatter(
        x=[ms1], y=[r1], mode="markers+text",
        marker=dict(size=12, color="#0f172a"),
        text=["E₁"], textposition="top right",
        name="تعادل نهایی E₁"
    ))

    # ۶. فلش بردار انتقال تعادل
    delta_m = abs(ms1 - ms0)
    delta_r = abs(r1 - r0)
    if delta_m > 5.0 or delta_r > 0.002:
        fig.add_annotation(
            ax=ms0, ay=r0, x=ms1, y=r1,
            xref="x", yref="y", axref="x", ayref="y",
            showarrow=True, arrowhead=2, arrowsize=1.3, arrowwidth=2.5,
            arrowcolor="#10b981"
        )

    # خطوط راهنمای نقطه‌چین از نقطه تعادل به محور نرخ بهره
    fig.add_shape(type="line", x0=m_min, x1=ms1, y0=r1, y1=r1, line=dict(dash="dot", color="#94a3b8"))

    fig.update_xaxes(
        title_text="حجم حقیقی عرضه و تقاضای پول (M/P)",
        range=[m_min, m_max],
        gridcolor=PLOT_THEME["grid_color"],
        automargin=True
    )
    fig.update_yaxes(
        title_text="نرخ بهره بازار (r)",
        tickformat=".1%",
        range=[0.0, max_r],
        gridcolor=PLOT_THEME["grid_color"],
        automargin=True
    )

    fig.update_layout(
        height=480,
        plot_bgcolor=PLOT_THEME["bg_color"],
        paper_bgcolor=PLOT_THEME["bg_color"],
        legend=dict(orientation="h", y=-0.22, x=0.5, xanchor="center"),
        margin=dict(l=75, r=35, t=40, b=70)
    )
    return fig, r1
