import numpy as np
import plotly.graph_objects as go
from dataclasses import dataclass

PLOT_THEME = {
    "font_family": "Vazirmatn, Tahoma, sans-serif",
    "bg_color": "#ffffff",
    "grid_color": "#f1f5f9",
    "prod_color": "#0284c7",       # آبی تابع تولید
    "savings_color": "#16a34a",    # سبز منحنی پس‌انداز و سرمایه‌گذاری
    "deprec_color": "#dc2626",     # قرمز خط تجهیز سرمایه و استهلاک
    "golden_color": "#d97706"      # نارنجی قاعده طلایی
}

@dataclass
class SolowModel:
    A: float = 1.0         # بهره‌وری و سطح فناوری کونوها
    alpha: float = 0.35    # سهم درآمدی سرمایه در تابع تولید کاب-داگلاس
    s: float = 0.25        # نرخ پس‌انداز اهالی دهکده
    delta: float = 0.05    # نرخ استهلاک ماشین‌آلات و زیرساخت‌ها
    n: float = 0.02        # نرخ رشد جمعیت شینوبی‌ها
    g: float = 0.01        # نرخ رشد پیشرفت فنی

    @property
    def break_even_rate(self) -> float:
        """نرخ استهلاک مؤثر: (delta + n + g)"""
        return self.delta + self.n + self.g

    def production_per_effective_worker(self, k: np.ndarray) -> np.ndarray:
        """تابع تولید سرانه: y = A * k^alpha"""
        return self.A * (k ** self.alpha)

    def savings_per_effective_worker(self, k: np.ndarray) -> np.ndarray:
        """سرمایه‌گذاری سرانه: i = s * f(k)"""
        return self.s * self.production_per_effective_worker(k)

    def break_even_investment(self, k: np.ndarray) -> np.ndarray:
        """سرمایه‌گذاری مورد نیاز جبران استهلاک و رشد جمعیت: (delta + n + g) * k"""
        return self.break_even_rate * k

    def solve_steady_state(self):
        """محاسبه دقیق ریاضی وضعیت پایدار (Steady State): k* = [ (s*A) / (delta + n + g) ]^(1 / (1 - alpha))"""
        denom = self.break_even_rate
        k_star = ((self.s * self.A) / denom) ** (1.0 / (1.0 - self.alpha))
        y_star = self.production_per_effective_worker(k_star)
        i_star = self.s * y_star
        c_star = y_star - i_star  # مصرف سرانه تعادلی

        # محاسبه قاعده طلایی (Golden Rule): MPK = delta + n + g  =>  s_gold = alpha
        s_gold = self.alpha
        k_gold = ((s_gold * self.A) / denom) ** (1.0 / (1.0 - self.alpha))
        y_gold = self.production_per_effective_worker(k_gold)
        c_gold = y_gold - (denom * k_gold)

        return {
            "k_star": k_star,
            "y_star": y_star,
            "c_star": c_star,
            "i_star": i_star,
            "s_gold": s_gold,
            "k_gold": k_gold,
            "c_gold": c_gold
        }

def create_solow_figure(base_model: SolowModel, current_model: SolowModel):
    ss0 = base_model.solve_steady_state()
    ss1 = current_model.solve_steady_state()

    k_max = max(ss1["k_gold"] * 1.5, ss1["k_star"] * 1.5, 25.0)
    k_vals = np.linspace(0.01, k_max, 300)

    fig = go.Figure()

    # خطوط مبنا (خاکستری کم‌رنگ)
    fig.add_trace(go.Scatter(
        x=k_vals, y=base_model.savings_per_effective_worker(k_vals), mode="lines",
        line=dict(dash="dot", color="#cbd5e1", width=1.5), name="پس‌انداز مبنا"
    ))
    fig.add_trace(go.Scatter(
        x=k_vals, y=base_model.break_even_investment(k_vals), mode="lines",
        line=dict(dash="dot", color="#fca5a5", width=1.5), name="استهلاک مبنا"
    ))

    # تابع تولید جاری f(k)
    fig.add_trace(go.Scatter(
        x=k_vals, y=current_model.production_per_effective_worker(k_vals), mode="lines",
        line=dict(color=PLOT_THEME["prod_color"], width=2.5), name="تولید سرانه f(k)",
        hovertemplate="سرمایه: %{x:.2f} | تولید سرانه: %{y:.2f}<extra></extra>"
    ))

    # سرمایه‌گذاری جاری s*f(k)
    fig.add_trace(go.Scatter(
        x=k_vals, y=current_model.savings_per_effective_worker(k_vals), mode="lines",
        line=dict(color=PLOT_THEME["savings_color"], width=3), name="سرمایه‌گذاری سرانه s·f(k)",
        hovertemplate="سرمایه: %{x:.2f} | سرمایه‌گذاری: %{y:.2f}<extra></extra>"
    ))

    # خط استهلاک و تجهیز سرمایه (delta + n + g)*k
    fig.add_trace(go.Scatter(
        x=k_vals, y=current_model.break_even_investment(k_vals), mode="lines",
        line=dict(color=PLOT_THEME["deprec_color"], width=2.5), name="خط استهلاک مؤثر (δ+n+g)k",
        hovertemplate="سرمایه: %{x:.2f} | استهلاک: %{y:.2f}<extra></extra>"
    ))

    # نقطه وضعیت پایدار جاری (k*, i*)
    fig.add_trace(go.Scatter(
        x=[ss1["k_star"]], y=[ss1["i_star"]], mode="markers+text",
        marker=dict(size=11, color="#0f172a"), text=["وضعیت پایدار (k*)"], textposition="bottom right",
        name="تعادل پایدار جاری"
    ))

    # نقطه مصرف قاعده طلایی (Golden Rule)
    fig.add_trace(go.Scatter(
        x=[ss1["k_gold"]], y=[(current_model.break_even_rate * ss1["k_gold"])], mode="markers+text",
        marker=dict(size=9, color=PLOT_THEME["golden_color"], symbol="diamond"),
        text=["قاعده طلایی (k_gold)"], textposition="top left", name="سرمایه قاعده طلایی"
    ))

    # خط‌چین‌های کمکی وضعیت پایدار
    fig.add_shape(type="line", x0=ss1["k_star"], x1=ss1["k_star"], y0=0, y1=ss1["y_star"], line=dict(dash="dot", color="#94a3b8"))
    fig.add_shape(type="line", x0=0, x1=ss1["k_star"], y0=ss1["y_star"], y1=ss1["y_star"], line=dict(dash="dot", color="#94a3b8"))
    fig.add_shape(type="line", x0=0, x1=ss1["k_star"], y0=ss1["i_star"], y1=ss1["i_star"], line=dict(dash="dot", color="#94a3b8"))

    # نمایش فاصله مصرفی به صورت سایه یا خط عمودی
    fig.add_annotation(
        x=ss1["k_star"], y=(ss1["i_star"] + ss1["y_star"]) / 2.0,
        text=f"مصرف سرانه (c*) = {ss1['c_star']:.2f}", showarrow=True, arrowhead=2,
        ax=40, ay=0, font=dict(color="#0f172a", size=11), bgcolor="#f8fafc"
    )

    fig.update_xaxes(title_text="سرمایه سرانه مؤثر (k)", range=[0, k_max], gridcolor=PLOT_THEME["grid_color"])
    fig.update_yaxes(title_text="مقادیر سرانه (تولید، پس‌انداز، استهلاک)", range=[0, ss1["y_star"] * 1.35], gridcolor=PLOT_THEME["grid_color"])

    fig.update_layout(
        height=500, plot_bgcolor=PLOT_THEME["bg_color"], paper_bgcolor=PLOT_THEME["bg_color"],
        legend=dict(orientation="h", y=-0.22, x=0.5, xanchor="center"),
        margin=dict(l=40, r=40, t=50, b=60)
    )
    return fig, ss0, ss1