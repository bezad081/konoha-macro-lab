import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dataclasses import dataclass

PLOT_THEME = {
    "font_family": "Vazirmatn, Tahoma, sans-serif",
    "bg_color": "#ffffff",
    "grid_color": "#f1f5f9",
    "primary_color": "#2563eb",
    "secondary_color": "#dc2626",
    "neutral_color": "#64748b",
    "step_color": "#10b981"  # سبز نمایش تعدیل انبار
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

    def compute_inventory_adjustment_path(self, r_current: float, Y_start: float, max_steps: int = 12):
        """
        محاسبه نقاط مسیر تعدیل پله‌ای موجودی انبار:
        حرکت عمودی: تقاضای کل تعیین می‌شود (Z_t = A + c1*(1-t)*Y_t)
        حرکت افقی: بنگاه‌ها در دوره بعد تولید را با تقاضا برابر می‌کنند (Y_{t+1} = Z_t)
        """
        path_x = []
        path_y = []
        
        y_curr = Y_start
        slope = self.mpc * (1.0 - self.t)
        A = self.autonomous_spending(r_current)
        
        path_x.append(y_curr)
        path_y.append(y_curr)
        
        for _ in range(max_steps):
            # گام عمودی: تشکیل تقاضای Z بر اساس درآمد دوره فعلی
            z_next = A + slope * y_curr
            path_x.append(y_curr)
            path_y.append(z_next)
            
            # گام افقی: تصمیم بنگاه‌ها برای رساندن تولید دوره بعد به سطح تقاضای Z
            path_x.append(z_next)
            path_y.append(z_next)
            
            if abs(z_next - y_curr) < 0.5:
                break
            y_curr = z_next
            
        return np.array(path_x), np.array(path_y)


def create_goods_market_figure(
    model: GoodsMarketModel,
    r_current: float = 0.05,
    base_model: GoodsMarketModel = None,
    r_base: float = 0.05,
    lang: str = "fa",
    show_dynamic_path: bool = True
):
    if base_model is None:
        base_model = GoodsMarketModel()

    Y_eq0 = base_model.solve_equilibrium_output(r_base)
    Y_eq1 = model.solve_equilibrium_output(r_current)

    center_y = (Y_eq0 + Y_eq1) / 2.0
    y_min = max(250.0, center_y - 500.0)
    y_max = max(1350.0, center_y + 500.0)
    Y_vals = np.linspace(y_min, y_max, 300)

    slope_base = base_model.mpc * (1.0 - base_model.t)
    z_base = base_model.autonomous_spending(r_base) + slope_base * Y_vals

    slope_curr = model.mpc * (1.0 - model.t)
    z_curr = model.autonomous_spending(r_current) + slope_curr * Y_vals

    txt = {
        "title1": "A) Keynesian Cross & Adjustment" if lang == "en" else "الف) تقاطع کینزی و مسیر پویای تعدیل انبار",
        "title2": "B) IS Curve Derivation" if lang == "en" else "ب) استخراج هندسی منحنی IS",
        "line45": "45° Line (Y = Z)" if lang == "en" else "خط ۴۵ درجه (Y = Z)",
        "z_base": "Baseline Demand" if lang == "en" else "تقاضای مبنا",
        "z_curr": "Current Demand (Z)" if lang == "en" else "تقاضای جاری (Z)",
        "is_base": "Baseline IS" if lang == "en" else "منحنی IS مبنا",
        "is_curr": "Current IS" if lang == "en" else "منحنی IS جاری",
        "e0": "E₀ Initial" if lang == "en" else "تعادل اولیه E₀",
        "e1": "E₁ Final" if lang == "en" else "تعادل نهایی E₁",
        "step_path": "Inventory Adjustment Path" if lang == "en" else "مسیر پله‌ای تعدیل موجودی انبار",
        "x_label": "Real GDP / Output (Y)" if lang == "en" else "تولید ناخالص داخلی (Y)",
        "y1_label": "Planned Demand (Z)" if lang == "en" else "تقاضای برنامه‌ریزی‌شده (Z)",
        "y2_label": "Real Interest Rate (r)" if lang == "en" else "نرخ بهره حقیقی (r)"
    }

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=(txt["title1"], txt["title2"]),
        horizontal_spacing=0.14
    )

    # --- پنل ۱: تقاطع کینزی و مسیر پله‌ای تعدیل ---
    fig.add_trace(go.Scatter(
        x=Y_vals, y=Y_vals, mode="lines",
        line=dict(dash="dash", color=PLOT_THEME["neutral_color"], width=1.5),
        name=txt["line45"]
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=Y_vals, y=z_base, mode="lines",
        line=dict(color="#cbd5e1", width=1.5, dash="dot"),
        name=txt["z_base"]
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=Y_vals, y=z_curr, mode="lines",
        line=dict(color=PLOT_THEME["primary_color"], width=3),
        name=txt["z_curr"]
    ), row=1, col=1)

    # رسم پویای مسیر پله‌ای تعدیل موجودی انبار
    if show_dynamic_path and abs(Y_eq1 - Y_eq0) > 10.0:
        px, py = model.compute_inventory_adjustment_path(r_current, Y_start=Y_eq0)
        fig.add_trace(go.Scatter(
            x=px, y=py, mode="lines+markers",
            line=dict(color=PLOT_THEME["step_color"], width=2.2),
            marker=dict(size=4, color=PLOT_THEME["step_color"]),
            name=txt["step_path"]
        ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=[Y_eq0], y=[Y_eq0], mode="markers+text",
        marker=dict(size=8, color="#64748b"), text=["E₀"], textposition="top left",
        name=txt["e0"]
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=[Y_eq1], y=[Y_eq1], mode="markers+text",
        marker=dict(size=11, color="#0f172a"), text=["E₁"], textposition="top left",
        name=txt["e1"]
    ), row=1, col=1)

    fig.add_shape(type="line", x0=Y_eq1, x1=Y_eq1, y0=y_min, y1=Y_eq1, line=dict(dash="dot", color="#94a3b8"), row=1, col=1)
    fig.add_shape(type="line", x0=y_min, x1=Y_eq1, y0=Y_eq1, y1=Y_eq1, line=dict(dash="dot", color="#94a3b8"), row=1, col=1)

    # --- پنل ۲: منحنی IS ---
    fig.add_trace(go.Scatter(
        x=Y_vals, y=base_model.is_curve_rate(Y_vals), mode="lines",
        line=dict(color="#cbd5e1", width=1.5, dash="dot"),
        name=txt["is_base"]
    ), row=1, col=2)

    fig.add_trace(go.Scatter(
        x=Y_vals, y=model.is_curve_rate(Y_vals), mode="lines",
        line=dict(color=PLOT_THEME["secondary_color"], width=3),
        name=txt["is_curr"]
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

    fig.add_shape(type="line", x0=Y_eq1, x1=Y_eq1, y0=0, y1=r_current, line=dict(dash="dot", color="#94a3b8"), row=1, col=2)
    fig.add_shape(type="line", x0=y_min, x1=Y_eq1, y0=r_current, y1=r_current, line=dict(dash="dot", color="#94a3b8"), row=1, col=2)

    max_r = max(0.15, r_base * 1.5, r_current * 1.5)

    fig.update_xaxes(title_text=txt["x_label"], range=[y_min, y_max], gridcolor=PLOT_THEME["grid_color"], automargin=True, row=1, col=1)
    fig.update_yaxes(title_text=txt["y1_label"], range=[y_min, y_max], gridcolor=PLOT_THEME["grid_color"], automargin=True, row=1, col=1)
    fig.update_xaxes(title_text=txt["x_label"], range=[y_min, y_max], gridcolor=PLOT_THEME["grid_color"], automargin=True, row=1, col=2)
    fig.update_yaxes(title_text=txt["y2_label"], tickformat=".1%", range=[0, min(0.20, max_r)], gridcolor=PLOT_THEME["grid_color"], automargin=True, row=1, col=2)

    fig.update_layout(
        height=480, plot_bgcolor=PLOT_THEME["bg_color"], paper_bgcolor=PLOT_THEME["bg_color"],
        legend=dict(orientation="h", y=-0.24, x=0.5, xanchor="center"),
        margin=dict(l=75, r=35, t=40, b=70)
    )
    return fig, Y_eq1