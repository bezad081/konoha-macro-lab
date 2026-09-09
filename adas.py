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
    A: float = 320.0
    alpha: float = 2.5
    b: float = 600.0
    h: float = 4000.0
    k: float = 0.50
    M: float = 400.0
    Y_potential: float = 1000.0
    P_expected: float = 1.0
    lambda_slope: float = 0.0015
    cost_shock: float = 0.0

    @property
    def gamma(self) -> float:
        denom = (1.0 / self.alpha) + (self.b * self.k / self.h)
        return 1.0 / denom

    def ad_output(self, P: np.ndarray) -> np.ndarray:
        return self.gamma * (self.A + (self.b / self.h) * (self.M / P))

    def sras_price(self, Y: np.ndarray) -> np.ndarray:
        return self.P_expected + self.lambda_slope * (Y - self.Y_potential) + self.cost_shock

    def solve_short_run_equilibrium(self):
        B = self.P_expected + self.lambda_slope * (self.gamma * self.A - self.Y_potential) + self.cost_shock
        C = self.lambda_slope * self.gamma * (self.b / self.h) * self.M

        delta = B**2 + 4.0 * C
        P_eq = (B + np.sqrt(delta)) / 2.0
        Y_eq = float(self.ad_output(np.array([P_eq]))[0])

        output_gap = ((Y_eq - self.Y_potential) / self.Y_potential) * 100.0
        inflation_rate = (P_eq - 1.0) * 100.0

        return {
            "P": float(P_eq),
            "Y": float(Y_eq),
            "Output_Gap": float(output_gap),
            "Inflation": float(inflation_rate)
        }

def create_adas_figure(base_model: ADASModel, current_model: ADASModel):
    eq0 = base_model.solve_short_run_equilibrium()
    eq1 = current_model.solve_short_run_equilibrium()

    # کادربندی دینامیک برای قرارگیری تعادل در مرکز کادر
    center_y = (eq0["Y"] + eq1["Y"]) / 2.0
    y_min = max(400.0, center_y - 450.0)
    y_max = max(1350.0, center_y + 450.0)

    center_p = (eq0["P"] + eq1["P"]) / 2.0
    p_min = max(0.3, center_p - 0.9)
    p_max = max(2.2, center_p + 1.0)

    P_vals = np.linspace(p_min, p_max, 250)
    Y_vals = np.linspace(y_min, y_max, 250)

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=("الف) تعادل کل اقتصاد کونوها (AD-AS)", "ب) منحنی فیلیپس و نرخ تورم"),
        horizontal_spacing=0.14
    )

    # سایه‌بندی شکاف تولید
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

    # خط عمودی پتانسیل طبیعی LRAS
    fig.add_trace(go.Scatter(
        x=[y_pot, y_pot], y=[p_min, p_max], mode="lines",
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
        name="AD جاری", hovertemplate="تولید تقاضاشده: %{x:.1f} | قیمت: %{y:.2f}<extra></extra>"
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
        name="SRAS جاری", hovertemplate="تولید عرضه‌شده: %{x:.1f} | قیمت: %{y:.2f}<extra></extra>"
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
    fig.add_shape(type="line", x0=eq1["Y"], x1=eq1["Y"], y0=p_min, y1=eq1["P"], line=dict(dash="dot", color="#94a3b8"), row=1, col=1)
    fig.add_shape(type="line", x0=y_min, x1=eq1["Y"], y0=eq1["P"], y1=eq1["P"], line=dict(dash="dot", color="#94a3b8"), row=1, col=1)

    # فلش کنترل‌شده انتقال تعادل در AD-AS
    delta_y = abs(eq1["Y"] - eq0["Y"])
    delta_p = abs(eq1["P"] - eq0["P"])
    if delta_y > 15.0 or delta_p > 0.05:
        fig.add_annotation(
            ax=eq0["Y"], ay=eq0["P"], x=eq1["Y"], y=eq1["P"],
            xref="x1", yref="y1", axref="x1", ayref="y1",
            showarrow=True, arrowhead=2, arrowsize=1.3, arrowwidth=2.5, arrowcolor="#10b981"
        )

    # --- پانل راست: منحنی فیلیپس ---
    gap_lim = max(25.0, abs(eq0["Output_Gap"]) * 1.4, abs(eq1["Output_Gap"]) * 1.4)
    gap_range = np.linspace(-gap_lim, gap_lim, 200)
    slope_phil = current_model.lambda_slope * current_model.Y_potential

    pi_base = (base_model.P_expected - 1.0) * 100.0 + (base_model.lambda_slope * base_model.Y_potential) * gap_range + (base_model.cost_shock * 100.0)
    pi_curr = (current_model.P_expected - 1.0) * 100.0 + slope_phil * gap_range + (current_model.cost_shock * 100.0)

    fig.add_trace(go.Scatter(
        x=gap_range, y=pi_base, mode="lines",
        line=dict(color="#cbd5e1", width=1.5, dash="dot"),
        name="فیلیپس مبنا", hovertemplate="فیلیپس مبنا<extra></extra>"
    ), row=1, col=2)

    fig.add_trace(go.Scatter(
        x=gap_range, y=pi_curr, mode="lines",
        line=dict(color=PLOT_THEME["phillips_color"], width=3),
        name="منحنی فیلیپس جاری", hovertemplate="شکاف: %{x:.1f}٪ | تورم: %{y:.1f}٪<extra></extra>"
    ), row=1, col=2)

    fig.add_trace(go.Scatter(
        x=[eq0["Output_Gap"]], y=[eq0["Inflation"]], mode="markers+text",
        marker=dict(size=8, color="#64748b"), text=["E₀"], textposition="top left",
        showlegend=False
    ), row=1, col=2)

    fig.add_trace(go.Scatter(
        x=[eq1["Output_Gap"]], y=[eq1["Inflation"]], mode="markers+text",
        marker=dict(size=12, color="#0f172a"), text=["E₁"], textposition="top left",
        showlegend=False, hovertemplate="تورم: %{y:.1f}٪<extra></extra>"
    ), row=1, col=2)

    # فلش در فیلیپس
    delta_gap = abs(eq1["Output_Gap"] - eq0["Output_Gap"])
    delta_inf = abs(eq1["Inflation"] - eq0["Inflation"])
    if delta_gap > 2.0 or delta_inf > 2.0:
        fig.add_annotation(
            ax=eq0["Output_Gap"], ay=eq0["Inflation"], x=eq1["Output_Gap"], y=eq1["Inflation"],
            xref="x2", yref="y2", axref="x2", ayref="y2",
            showarrow=True, arrowhead=2, arrowsize=1.3, arrowwidth=2.5, arrowcolor="#10b981"
        )

    inf_lim = max(25.0, abs(eq0["Inflation"]) * 1.5, abs(eq1["Inflation"]) * 1.5)

    fig.update_xaxes(title_text="تولید ناخالص داخلی کونوها (Y)", range=[y_min, y_max], gridcolor=PLOT_THEME["grid_color"], automargin=True, row=1, col=1)
    fig.update_yaxes(title_text="سطح عمومی قیمت‌ها (P)", range=[p_min, p_max], gridcolor=PLOT_THEME["grid_color"], automargin=True, row=1, col=1)
    fig.update_xaxes(title_text="شکاف تولید (٪)", zeroline=True, range=[-gap_lim, gap_lim], gridcolor=PLOT_THEME["grid_color"], automargin=True, row=1, col=2)
    fig.update_yaxes(title_text="نرخ تورم (٪)", zeroline=True, range=[-inf_lim, inf_lim], gridcolor=PLOT_THEME["grid_color"], automargin=True, row=1, col=2)

    fig.update_layout(
        height=480, plot_bgcolor=PLOT_THEME["bg_color"], paper_bgcolor=PLOT_THEME["bg_color"],
        legend=dict(orientation="h", y=-0.24, x=0.5, xanchor="center"),
        margin=dict(l=75, r=35, t=40, b=70),
        uirevision="never"
    )
    return fig, eq0, eq1