import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dataclasses import dataclass

PLOT_THEME = {
    "font_family": "Vazirmatn, Tahoma, sans-serif",
    "bg_color": "#ffffff",
    "grid_color": "#f1f5f9",
    "ad_color": "#2563eb",
    "sras_color": "#dc2626",
    "lras_color": "#16a34a",
    "phillips_color": "#d97706"
}

@dataclass
class ADASModel:
    A: float = 320.0             # مخارج خودگردان کل (c0 + i0 + G)
    alpha: float = 2.5           # ضریب فزاینده کینزی
    b: float = 600.0             # کشش سرمایه‌گذاری به بهره
    h: float = 4000.0            # کشش تقاضای پول به بهره
    k: float = 0.50              # کشش تقاضای پول به درآمد
    M: float = 400.0             # عرضه اسمی پول
    Y_potential: float = 1000.0  # سطح طبیعی تولید
    P_expected: float = 1.0      # انتظارات قیمتی
    lambda_slope: float = 0.0015 # شیب عرضه کوتاه‌مدت SRAS
    cost_shock: float = 0.0      # شوک منفی عرضه (z)

    @property
    def gamma(self) -> float:
        denom = (1.0 / self.alpha) + (self.b * self.k / self.h)
        return 1.0 / denom

    def ad_output(self, P: np.ndarray) -> np.ndarray:
        return self.gamma * (self.A + (self.b / self.h) * (self.M / P))

    def sras_price(self, Y: np.ndarray) -> np.ndarray:
        return self.P_expected + self.lambda_slope * (Y - self.Y_potential) + self.cost_shock

    def solve_short_run_equilibrium(self):
        """حل دقیق تحلیلی تقاطع AD و SRAS از طریق معادله درجه دوم: P^2 - B*P - C = 0"""
        B = self.P_expected + self.lambda_slope * (self.gamma * self.A - self.Y_potential) + self.cost_shock
        C = self.lambda_slope * self.gamma * (self.b / self.h) * self.M

        delta = B**2 + 4.0 * C
        P_eq = (B + np.sqrt(delta)) / 2.0
        Y_eq = float(self.ad_output(np.array([P_eq]))[0])

        output_gap = ((Y_eq - self.Y_potential) / self.Y_potential) * 100.0
        inflation_rate = (P_eq - 1.0) * 100.0

        return {
            "P": P_eq,
            "Y": Y_eq,
            "Output_Gap": output_gap,
            "Inflation": inflation_rate
        }

def create_adas_figure(base_model: ADASModel, current_model: ADASModel):
    eq0 = base_model.solve_short_run_equilibrium()
    eq1 = current_model.solve_short_run_equilibrium()

    P_vals = np.linspace(0.4, 2.8, 250)
    Y_vals = np.linspace(650, 1350, 250)

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=("الف) تعادل کل اقتصاد کونوها (مدل AD-AS)", "ب) منحنی فیلیپس و نرخ تورم"),
        horizontal_spacing=0.12
    )

    # --- سایه‌بندی ناحیه شکاف تولید ---
    y_pot = current_model.Y_potential
    y_eq = eq1["Y"]
    fill_col = "rgba(239, 68, 68, 0.16)" if y_eq < y_pot else "rgba(34, 197, 94, 0.16)"
    gap_text = "شکاف رکودی" if y_eq < y_pot else "شکاف تورمی"

    fig.add_vrect(
        x0=min(y_pot, y_eq), x1=max(y_pot, y_eq),
        fillcolor=fill_col, line_width=0,
        annotation_text=gap_text, annotation_position="top left",
        row=1, col=1
    )

    # عرضه بلندمدت عمودی LRAS
    fig.add_trace(go.Scatter(
        x=[y_pot, y_pot], y=[0.4, 2.8], mode="lines",
        line=dict(color=PLOT_THEME["lras_color"], width=3, dash="dash"),
        name="LRAS (پتانسیل طبیعی)", hovertemplate="تولید طبیعی: %{x:.0f}<extra></extra>"
    ), row=1, col=1)

    # منحنی‌های AD
    fig.add_trace(go.Scatter(
        x=base_model.ad_output(P_vals), y=P_vals, mode="lines",
        line=dict(color="#94a3b8", width=1.5, dash="dot"),
        name="AD مبنا", hovertemplate="AD مبنا<extra></extra>"
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=current_model.ad_output(P_vals), y=P_vals, mode="lines",
        line=dict(color=PLOT_THEME["ad_color"], width=3),
        name="AD جاری", hovertemplate="تولید تقاضاشده: %{x:.1f} | شاخص قیمت: %{y:.2f}<extra></extra>"
    ), row=1, col=1)

    # منحنی‌های SRAS
    fig.add_trace(go.Scatter(
        x=Y_vals, y=base_model.sras_price(Y_vals), mode="lines",
        line=dict(color="#cbd5e1", width=1.5, dash="dot"),
        name="SRAS مبنا", hovertemplate="SRAS مبنا<extra></extra>"
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=Y_vals, y=current_model.sras_price(Y_vals), mode="lines",
        line=dict(color=PLOT_THEME["sras_color"], width=3),
        name="SRAS جاری", hovertemplate="تولید عرضه‌شده: %{x:.1f} | شاخص قیمت: %{y:.2f}<extra></extra>"
    ), row=1, col=1)

    # نقاط تعادل E0 و E1
    fig.add_trace(go.Scatter(
        x=[eq0["Y"]], y=[eq0["P"]], mode="markers+text",
        marker=dict(size=8, color="#64748b"), text=["E₀"], textposition="top right",
        name="تعادل اولیه E₀"
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=[eq1["Y"]], y=[eq1["P"]], mode="markers+text",
        marker=dict(size=12, color="#0f172a"), text=["E₁"], textposition="top left",
        name="تعادل جدید E₁"
    ), row=1, col=1)

    # خطوط راهنما
    fig.add_shape(type="line", x0=eq1["Y"], x1=eq1["Y"], y0=0.4, y1=eq1["P"], line=dict(dash="dot", color="#94a3b8"), row=1, col=1)
    fig.add_shape(type="line", x0=650, x1=eq1["Y"], y0=eq1["P"], y1=eq1["P"], line=dict(dash="dot", color="#94a3b8"), row=1, col=1)

    # فلش انتقال تعادل
    if abs(eq1["Y"] - eq0["Y"]) > 2 or abs(eq1["P"] - eq0["P"]) > 0.02:
        fig.add_annotation(
            ax=eq0["Y"], ay=eq0["P"], x=eq1["Y"], y=eq1["P"],
            xref="x1", yref="y1", axref="x1", ayref="y1",
            showarrow=True, arrowhead=3, arrowsize=1.2, arrowwidth=2, arrowcolor="#e11d48"
        )

    # --- پانل راست: منحنی فیلیپس سازگار ریاضی ---
    gap_range = np.linspace(-25, 25, 200)
    # شیب دقیق برگرفته از عرضه کل: slope = lambda * Y_potential
    slope_phil = current_model.lambda_slope * current_model.Y_potential
    pi_base = (base_model.P_expected - 1.0) * 100.0 + (base_model.lambda_slope * base_model.Y_potential) * gap_range + (base_model.cost_shock * 100.0)
    pi_curr = (current_model.P_expected - 1.0) * 100.0 + slope_phil * gap_range + (current_model.cost_shock * 100.0)

    fig.add_trace(go.Scatter(
        x=gap_range, y=pi_base, mode="lines",
        line=dict(color="#cbd5e1", width=1.5, dash="dot"),
        name="منحنی فیلیپس مبنا", hovertemplate="فیلیپس مبنا<extra></extra>"
    ), row=1, col=2)

    fig.add_trace(go.Scatter(
        x=gap_range, y=pi_curr, mode="lines",
        line=dict(color=PLOT_THEME["phillips_color"], width=3),
        name="منحنی فیلیپس جاری", hovertemplate="شکاف تولید: %{x:.1f}٪ | تورم: %{y:.1f}٪<extra></extra>"
    ), row=1, col=2)

    fig.add_trace(go.Scatter(
        x=[eq1["Output_Gap"]], y=[eq1["Inflation"]], mode="markers+text",
        marker=dict(size=12, color="#0f172a"), text=["E₁"], textposition="top left",
        showlegend=False, hovertemplate="تعادل تورمی: %{y:.1f}٪<extra></extra>"
    ), row=1, col=2)

    fig.update_xaxes(title_text="تولید ناخالص داخلی کونوها (Y)", range=[650, 1350], gridcolor=PLOT_THEME["grid_color"], row=1, col=1)
    fig.update_yaxes(title_text="سطح عمومی قیمت‌ها (P)", range=[0.4, 2.8], gridcolor=PLOT_THEME["grid_color"], row=1, col=1)
    fig.update_xaxes(title_text="شکاف تولید (٪)", zeroline=True, range=[-25, 25], gridcolor=PLOT_THEME["grid_color"], row=1, col=2)
    fig.update_yaxes(title_text="نرخ تورم (٪)", zeroline=True, range=[-15, 35], gridcolor=PLOT_THEME["grid_color"], row=1, col=2)

    fig.update_layout(
        height=480, plot_bgcolor=PLOT_THEME["bg_color"], paper_bgcolor=PLOT_THEME["bg_color"],
        legend=dict(orientation="h", y=-0.22, x=0.5, xanchor="center"),
        margin=dict(l=40, r=40, t=50, b=60)
    )
    return fig, eq0, eq1