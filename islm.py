import numpy as np
import plotly.graph_objects as go
from dataclasses import dataclass

PLOT_THEME = {
    "font_family": "Vazirmatn, Tahoma, sans-serif",
    "bg_color": "#ffffff",
    "grid_color": "#f1f5f9",
    "is_color": "#dc2626",
    "lm_color": "#2563eb"
}

@dataclass
class ISLMEngine:
    c0: float = 60.0
    mpc: float = 0.75
    t: float = 0.20
    i0: float = 140.0
    b: float = 600.0
    G: float = 120.0
    M: float = 400.0
    P: float = 1.0
    k: float = 0.50
    h: float = 4000.0
    regime: str = "standard"  # "standard", "liquidity_trap", "classical"
    r_floor: float = 0.015    # کف نرخ بهره در تله نقدینگی (1.5%)

    @property
    def multiplier(self) -> float:
        denom = 1.0 - self.mpc * (1.0 - self.t)
        return 1.0 / denom if denom > 0 else 1.0

    @property
    def autonomous_spending(self) -> float:
        return self.c0 + self.i0 + self.G

    @property
    def trap_threshold_y(self) -> float:
        """مرز تولیدی که پس از آن تقاضای معاملاتی پول، نرخ بهره را از کف بالا می‌کشد"""
        real_M = self.M / self.P
        # در تله نقدینگی، فرض آموزشی بر این است که دامنه تله تا تولیدات بالاتر ادامه دارد
        effective_h = 25000.0 if self.regime == "liquidity_trap" else self.h
        return (real_M + effective_h * self.r_floor) / self.k

    def solve_equilibrium(self):
        alpha = self.multiplier
        A = self.autonomous_spending
        real_M = self.M / self.P

        if self.regime == "classical":
            # در دیدگاه کلاسیک، منحنی LM عمودی است: Y = (M/P)/k
            Y_star = real_M / self.k
            r_star = (A / self.b) - (Y_star / (alpha * self.b))
            r_star = max(0.002, r_star)

        elif self.regime == "liquidity_trap":
            effective_h = 25000.0
            y_trap = (real_M + effective_h * self.r_floor) / self.k

            # آزمون تقاطع با شاخه افقی:
            Y_flat = alpha * (A - self.b * self.r_floor)

            if Y_flat <= y_trap:
                # تقاطع در داخل تله نقدینگی رخ می‌دهد
                Y_star = Y_flat
                r_star = self.r_floor
            else:
                # تقاطع با شاخه صعودی LM رخ می‌دهد (خروج از تله)
                denom = (1.0 / alpha) + (self.b * self.k / effective_h)
                Y_star = (A + (self.b / effective_h) * real_M) / denom
                r_star = (self.k * Y_star - real_M) / effective_h

        else:  # استاندارد
            denom = (1.0 / alpha) + (self.b * self.k / self.h)
            Y_star = (A + (self.b / self.h) * real_M) / denom
            r_star = (self.k * Y_star - real_M) / self.h
            if r_star < self.r_floor:
                r_star = self.r_floor
                Y_star = alpha * (A - self.b * r_star)

        T = self.t * Y_star
        C = self.c0 + self.mpc * (Y_star - T)
        I = self.i0 - self.b * r_star

        return {
            "Y": float(Y_star),
            "r": float(r_star),
            "C": float(C),
            "I": float(I),
            "T": float(T),
            "Deficit": float(self.G - T)
        }

    def get_is_curve(self, Y_vals: np.ndarray) -> np.ndarray:
        alpha = self.multiplier
        A = self.autonomous_spending
        return (A / self.b) - (Y_vals / (alpha * self.b))

    def get_lm_curve(self, Y_vals: np.ndarray) -> np.ndarray:
        real_M = self.M / self.P
        if self.regime == "classical":
            return np.full_like(Y_vals, np.nan)
        elif self.regime == "liquidity_trap":
            effective_h = 25000.0
            r_normal = (self.k * Y_vals - real_M) / effective_h
            return np.maximum(self.r_floor, r_normal)
        else:
            r = (self.k * Y_vals - real_M) / self.h
            return np.maximum(0.005, r)

def create_islm_figure(base_engine: ISLMEngine, current_engine: ISLMEngine):
    eq0 = base_engine.solve_equilibrium()
    eq1 = current_engine.solve_equilibrium()

    center_y = (eq0["Y"] + eq1["Y"]) / 2.0
    y_min = max(300.0, center_y - 450.0)
    y_max = max(1350.0, center_y + 450.0)
    Y_vals = np.linspace(y_min, y_max, 300)

    is_base = base_engine.get_is_curve(Y_vals)
    is_curr = current_engine.get_is_curve(Y_vals)

    fig = go.Figure()

    # خطوط مبنا
    fig.add_trace(go.Scatter(
        x=Y_vals, y=is_base, mode="lines",
        line=dict(dash="dot", color="#94a3b8", width=1.5), name="IS مبنا"
    ))

    if base_engine.regime == "classical":
        y_class_base = (base_engine.M / base_engine.P) / base_engine.k
        fig.add_trace(go.Scatter(
            x=[y_class_base, y_class_base], y=[0.001, 0.20], mode="lines",
            line=dict(dash="dot", color="#94a3b8", width=1.5), name="LM مبنا (عمودی)"
        ))
    else:
        fig.add_trace(go.Scatter(
            x=Y_vals, y=base_engine.get_lm_curve(Y_vals), mode="lines",
            line=dict(dash="dot", color="#94a3b8", width=1.5), name="LM مبنا"
        ))

    fig.add_trace(go.Scatter(
        x=[eq0["Y"]], y=[eq0["r"]], mode="markers+text",
        marker=dict(size=8, color="#64748b"), text=["E₀"], textposition="top right",
        name="تعادل مبدا E₀"
    ))

    # خطوط جاری
    fig.add_trace(go.Scatter(
        x=Y_vals, y=is_curr, mode="lines",
        line=dict(color=PLOT_THEME["is_color"], width=3), name="منحنی IS جاری"
    ))

    if current_engine.regime == "classical":
        y_class_curr = (current_engine.M / current_engine.P) / current_engine.k
        fig.add_trace(go.Scatter(
            x=[y_class_curr, y_class_curr], y=[0.001, 0.20], mode="lines",
            line=dict(color=PLOT_THEME["lm_color"], width=3.5), name="منحنی LM (کلاسیک)"
        ))
    else:
        lm_name = "منحنی LM (شامل کف نقدینگی)" if current_engine.regime == "liquidity_trap" else "منحنی LM جاری"
        fig.add_trace(go.Scatter(
            x=Y_vals, y=current_engine.get_lm_curve(Y_vals), mode="lines",
            line=dict(color=PLOT_THEME["lm_color"], width=3), name=lm_name
        ))

    # نقطه تعادل جدید E1 (دقیقاً بر روی تقاطع هندسی دو منحنی)
    fig.add_trace(go.Scatter(
        x=[eq1["Y"]], y=[eq1["r"]], mode="markers+text",
        marker=dict(size=12, color="#0f172a"), text=["E₁"], textposition="top left",
        name="تعادل جاری E₁"
    ))

    # فلش دینامیک انتقال تعادل
    delta_y = abs(eq1["Y"] - eq0["Y"])
    delta_r = abs(eq1["r"] - eq0["r"])
    if delta_y > 8.0 or delta_r > 0.002:
        fig.add_annotation(
            ax=eq0["Y"], ay=eq0["r"], x=eq1["Y"], y=eq1["r"],
            xref="x", yref="y", axref="x", ayref="y",
            showarrow=True, arrowhead=2, arrowsize=1.3, arrowwidth=2.5,
            arrowcolor="#10b981", opacity=0.9
        )

    # خطوط راهنما به محورها
    fig.add_shape(type="line", x0=eq1["Y"], x1=eq1["Y"], y0=0, y1=eq1["r"], line=dict(dash="dot", color="#94a3b8"))
    fig.add_shape(type="line", x0=y_min, x1=eq1["Y"], y0=eq1["r"], y1=eq1["r"], line=dict(dash="dot", color="#94a3b8"))

    max_r = max(0.14, eq0["r"] * 1.5, eq1["r"] * 1.5)

    fig.update_xaxes(
        title_text="تولید ناخالص داخلی تعادلی (Y)",
        range=[y_min, y_max],
        gridcolor=PLOT_THEME["grid_color"],
        automargin=True
    )
    fig.update_yaxes(
        title_text="نرخ بهره تعادلی (r)",
        tickformat=".1%",
        range=[0.0, min(0.20, max_r)],
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
    return fig, eq0, eq1
