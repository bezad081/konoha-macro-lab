import streamlit as st
import pandas as pd

from goods_market import GoodsMarketModel, create_goods_market_figure
from money_market import MoneyMarketModel, create_money_market_figure
from islm import ISLMEngine, create_islm_figure
from adas import ADASModel, create_adas_figure
from open_economy import MundellFlemingModel, create_mundell_fleming_figure
from solow import SolowModel, create_solow_figure

from math_explainer import (
    show_goods_market_math,
    show_money_market_math,
    show_islm_math,
    show_adas_math,
    show_open_economy_math,
    show_solow_math
)
from translations import TEXTS

# ==========================================
# نقشه ترجمه المان‌های نمودار پلاتلی
# ==========================================
PLOT_TRANSLATIONS = {
    # محورها
    "تولید ناخالص داخلی (Y)": "Real GDP (Y)",
    "تولید ناخالص داخلی تعادلی (Y)": "Equilibrium Real GDP (Y)",
    "تولید ناخالص داخلی کونوها (Y)": "Konoha Real GDP (Y)",
    "تقاضای کل برنامه‌ریزی‌شده (Z)": "Planned Aggregate Demand (Z)",
    "نرخ بهره حقیقی (r)": "Real Interest Rate (r)",
    "نرخ بهره تعادلی (r)": "Equilibrium Interest Rate (r)",
    "نرخ بهره داخلی (r)": "Domestic Interest Rate (r)",
    "نرخ بهره بازار (r)": "Market Interest Rate (r)",
    "حجم حقیقی عرضه و تقاضای پول (M/P)": "Real Money Balances (M/P)",
    "مانده واقعی نقدینگی (M/P)": "Real Money Balances (M/P)",
    "سطح عمومی قیمت‌ها (P)": "Price Level (P)",
    "شکاف تولید (٪)": "Output Gap (%)",
    "نرخ تورم (٪)": "Inflation Rate (%)",
    "سرمایه سرانه مؤثر (k)": "Effective Capital per Worker (k)",
    "تولید و سرمایه‌گذاری سرانه": "Output & Investment per Worker",

    # لژاندها و برچسب‌های خطوط
    "خط ۴۵ درجه (Y = Z)": "45° Line (Y = Z)",
    "تقاضای برنامه‌ریزی‌شده مبنا": "Baseline Planned Demand",
    "تقاضای جاری (Z)": "Current Planned Demand (Z)",
    "IS مبنا": "Baseline IS",
    "منحنی IS مبنا": "Baseline IS Curve",
    "منحنی IS جاری": "Current IS Curve",
    "LM مبنا": "Baseline LM",
    "منحنی LM مبنا": "Baseline LM Curve",
    "منحنی LM جاری": "Current LM Curve",
    "LM مبنا (عمودی)": "Baseline Classical LM",
    "منحنی LM (کلاسیک)": "Classical Vertical LM",
    "منحنی تقاضای کل پول (Mᵈ/P)": "Total Money Demand (Mᵈ/P)",
    "تقاضای پول مبنا (L₀)": "Baseline Money Demand (L₀)",
    "تعادل اولیه E₀": "Initial Equilibrium E₀",
    "تعادل اولیه": "Initial Equilibrium",
    "تعادل جدید E₁": "New Equilibrium E₁",
    "تعادل جدید": "New Equilibrium",
    "تعادل مبدا E₀": "Baseline Equilibrium E₀",
    "تعادل جاری E₁": "Current Equilibrium E₁",
    "BP مبنا": "Baseline BP",
    "تراز پرداخت‌ها (منحنی BP)": "Balance of Payments (BP Curve)",
    "تراز پرداخت‌ها BP (r = r*)": "Balance of Payments BP (r = r*)",
    "تعادل نهایی هر ۳ بازار": "Final Equilibrium (IS-LM-BP)",
    "تولید سرانه f(k)": "Output per Worker f(k)",
    "سرمایه‌گذاری سرانه s·f(k)": "Investment per Worker s·f(k)",
    "خط استهلاک مؤثر (δ+n+g)k": "Break-even Investment (δ+n+g)k",
    "وضعیت پایدار (k*)": "Steady State (k*)",
    "قاعده طلایی (k_gold)": "Golden Rule (k_gold)",
    "LRAS (پتانسیل طبیعی)": "LRAS (Potential Output)",
    "AD جاری": "Current AD",
    "AD مبنا": "Baseline AD",
    "SRAS جاری": "Current SRAS",
    "SRAS مبنا": "Baseline SRAS",
    "منحنی فیلیپس جاری": "Current Phillips Curve",
    "فیلیپس مبنا": "Baseline Phillips Curve"
}

def translate_figure_to_en(fig):
    for trace in fig.data:
        if hasattr(trace, "name") and trace.name in PLOT_TRANSLATIONS:
            trace.name = PLOT_TRANSLATIONS[trace.name]

    for axis in fig.layout:
        if (axis.startswith("xaxis") or axis.startswith("yaxis")) and hasattr(fig.layout[axis], "title"):
            title_text = getattr(fig.layout[axis].title, "text", None)
            if title_text in PLOT_TRANSLATIONS:
                fig.layout[axis].title.text = PLOT_TRANSLATIONS[title_text]

    if hasattr(fig.layout, "annotations"):
        for ann in fig.layout.annotations:
            txt = ann.text or ""
            if "تقاطع کینزی" in txt:
                ann.text = "A) Keynesian Cross"
            elif "استخراج هندسی منحنی IS" in txt:
                ann.text = "B) IS Curve Derivation"
            elif "ترجیح نقدینگی" in txt:
                ann.text = "A) Liquidity Preference Equilibrium"
            elif "استخراج هندسی منحنی LM" in txt:
                ann.text = "B) LM Curve Derivation"
            elif "AD-AS" in txt:
                ann.text = "A) Aggregate Equilibrium (AD-AS)"
            elif "فیلیپس" in txt:
                ann.text = "B) Phillips Curve"
            elif "نرخ بهره جهانی" in txt:
                ann.text = "World Interest Rate (r*)"
            elif txt in PLOT_TRANSLATIONS:
                ann.text = PLOT_TRANSLATIONS[txt]

    return fig

# ==========================================
# تنظیمات صفحه و استایل (رفع جا ماندن سایدبار)
# ==========================================
st.set_page_config(
    page_title="Konoha Macroeconomic Simulator",
    page_icon="🍃",
    layout="wide",
    initial_sidebar_state="expanded"
)

# انتخاب زبان در بالاترین بخش سایدبار
lang_choice = st.sidebar.selectbox("🌐 زبان / Language:", ["فارسی (FA)", "English (EN)"])
lang = "en" if "EN" in lang_choice else "fa"
T = TEXTS[lang]

# استایل CSS: جهت صفحه و رفع دقیق باگ باز/بسته شدن سایدبار
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;500;700;900&family=Inter:wght@400;600;700&display=swap');

    /* اعمال استایل فونت و جهت صرفاً به کانتینر اصلی صفحه */
    .main .block-container {{
        font-family: {"'Inter', sans-serif" if lang == "en" else "'Vazirmatn', Tahoma, sans-serif"};
        direction: {T["dir"]};
        text-align: {T["align"]};
    }}

    /* جلوگیری از ماندن متون و سرریز المان‌ها هنگام جمع شدن سایدبار */
    [data-testid="stSidebar"] {{
        overflow-x: hidden !important;
    }}
    [data-testid="stSidebarContent"] {{
        overflow-x: hidden !important;
    }}
    [data-testid="stSidebarCollapseButton"] {{
        z-index: 999999 !important;
    }}

    .stMetric {{
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        padding: 12px;
        border-radius: 10px;
        border-{'left' if lang == 'en' else 'right'}: 4px solid #16a34a;
    }}
    .banner {{
        background: linear-gradient(90deg, #f0fdf4 0%, #ecfdf5 100%);
        border-{'left' if lang == 'en' else 'right'}: 6px solid #10b981;
        padding: 16px;
        border-radius: 10px;
        margin-bottom: 20px;
    }}
    .custom-table {{
        width: 100%;
        border-collapse: collapse;
        margin: 15px 0;
        font-size: 15px;
        text-align: {T["align"]};
    }}
    .custom-table th {{
        background-color: #f1f5f9;
        color: #0f172a;
        padding: 10px 14px;
        border: 1px solid #cbd5e1;
    }}
    .custom-table td {{
        padding: 10px 14px;
        border: 1px solid #e2e8f0;
    }}
    .custom-table tr:nth-child(even) {{
        background-color: #f8fafc;
    }}
</style>
""", unsafe_allow_html=True)

st.title(T["app_title"])
st.markdown(f'<div class="banner">{T["banner"]}</div>', unsafe_allow_html=True)

st.sidebar.title(T["course_syllabus"])
topic = st.sidebar.selectbox(T["select_chapter"], T["chapters"])
st.sidebar.markdown("---")

# ==========================================
# فصل ۱: بازار کالا
# ==========================================
if "IS" in topic or "کالا" in topic:
    st.header("📦 " + ("Goods Market & Keynesian Cross" if lang == "en" else "بازار کالا و تقاطع کینزی"))
    c0 = st.sidebar.slider("c₀:" if lang == "en" else "مصرف خودگردان (c₀):", 20.0, 150.0, 60.0, step=5.0)
    mpc = st.sidebar.slider("mpc:" if lang == "en" else "میل نهایی به مصرف (mpc):", 0.4, 0.95, 0.75, step=0.05)
    t = st.sidebar.slider("t:" if lang == "en" else "نرخ مالیات (t):", 0.05, 0.45, 0.20, step=0.05)
    g = st.sidebar.slider("G:" if lang == "en" else "مخارج دولت هوکاگه (G):", 40.0, 250.0, 120.0, step=10.0)
    r = st.sidebar.slider("r:" if lang == "en" else "نرخ بهره جاری (r):", 0.01, 0.15, 0.05, step=0.005, format="%.3f")

    model = GoodsMarketModel(c0=c0, mpc=mpc, t=t, G=g)
    fig, Y_eq = create_goods_market_figure(model, r_current=r)

    c1, c2, c3 = st.columns(3)
    c1.metric(T["metrics_labels"]["multiplier"], f"{model.multiplier:.2f}")
    c2.metric(T["metrics_labels"]["output"], f"{Y_eq:.1f}")
    c3.metric(T["metrics_labels"]["spending"], f"{model.autonomous_spending(r):.1f}")

    tab1, tab2, tab3 = st.tabs([T["tabs"]["charts"], T["tabs"]["metrics"], T["tabs"]["math"]])
    with tab1:
        if lang == "en":
            fig = translate_figure_to_en(fig)
        st.plotly_chart(fig, use_container_width=True, config={"scrollZoom": True, "displayModeBar": True})
    with tab2:
        T_val = t * Y_eq
        C_val = c0 + mpc * (Y_eq - T_val)
        I_val = model.i0 - model.b * r
        st.markdown(f"""
        <table class="custom-table">
            <thead>
                <tr><th>{"Component" if lang=="en" else "جزء مخارج"}</th><th>{"Value" if lang=="en" else "مقدار تعادلی"}</th><th>{"Share" if lang=="en" else "سهم از کل"}</th></tr>
            </thead>
            <tbody>
                <tr><td>{"Private Consumption (C)" if lang=="en" else "مصرف کل خانوارها (C)"}</td><td>{C_val:.1f}</td><td>{(C_val/Y_eq)*100:.1f}%</td></tr>
                <tr><td>{"Private Investment (I)" if lang=="en" else "سرمایه‌گذاری قبیله‌ها (I)"}</td><td>{I_val:.1f}</td><td>{(I_val/Y_eq)*100:.1f}%</td></tr>
                <tr><td>{"Government Spending (G)" if lang=="en" else "مخارج دولت هوکاگه (G)"}</td><td>{g:.1f}</td><td>{(g/Y_eq)*100:.1f}%</td></tr>
                <tr><td>{"Tax Revenue (T)" if lang=="en" else "کل درآمدهای مالیاتی (T)"}</td><td>{T_val:.1f}</td><td>{"Balance: " if lang=="en" else "تراز بودجه: "}{T_val - g:+.1f}</td></tr>
            </tbody>
        </table>
        """, unsafe_allow_html=True)
    with tab3:
        show_goods_market_math(model, r, Y_eq, c0, mpc, t, g)

# ==========================================
# فصل ۲: بازار پول (منطبق بر شکل‌های ۷ تا ۱۰ کتاب)
# ==========================================
elif "LM" in topic or "پول" in topic:
    st.header("🏦 " + ("Money Market & Liquidity Preference (Keynesian Model)" if lang == "en" else "بازار پول و نظریه ترجیح نقدینگی کینز"))
    m = st.sidebar.slider("M:" if lang == "en" else "عرضه اسمی پول (M):", 200.0, 800.0, 400.0, step=25.0)
    p = st.sidebar.slider("P:" if lang == "en" else "شاخص سطح قیمت‌ها (P):", 0.5, 2.0, 1.0, step=0.1)
    k = st.sidebar.slider("k:" if lang == "en" else "حساسیت تقاضای پول به درآمد (k):", 0.2, 0.8, 0.50, step=0.05)
    h = st.sidebar.slider("h:" if lang == "en" else "حساسیت تقاضای پول به بهره (h):", 1000.0, 8000.0, 4000.0, step=500.0)
    y_curr = st.sidebar.slider("Y:" if lang == "en" else "درآمد ناخالص جاری (Y):", 600.0, 1500.0, 1000.0, step=50.0)

    model = MoneyMarketModel(M=m, P=p, k=k, h=h)
    fig, r_eq = create_money_market_figure(model, Y_current=y_curr)

    c1, c2 = st.columns(2)
    c1.metric(T["metrics_labels"]["real_m"], f"{model.real_money_supply:.1f}")
    c2.metric(T["metrics_labels"]["interest"], f"{r_eq * 100:.2f}%")

    tab1, tab2, tab3 = st.tabs([T["tabs"]["charts"], T["tabs"]["metrics"], T["tabs"]["math"]])
    with tab1:
        if lang == "en":
            fig = translate_figure_to_en(fig)
        st.plotly_chart(fig, use_container_width=True, config={"scrollZoom": True, "displayModeBar": True})
    with tab2:
        ky_val = k * y_curr
        st.markdown(f"""
        <table class="custom-table">
            <thead>
                <tr><th>{"Indicator" if lang=="en" else "مؤلفه بازار پول"}</th><th>{"Value" if lang=="en" else "مقدار"}</th><th>{"Theoretical Feature" if lang=="en" else "ویژگی در منحنی کتاب"}</th></tr>
            </thead>
            <tbody>
                <tr><td>{"Transactions Demand (kY)" if lang=="en" else "تقاضای معاملاتی (kY)"}</td><td>{ky_val:.1f}</td><td>{"Vertical asymptote at high interest rates" if lang=="en" else "مجانب عمودی در نرخ‌های بهره بسیار بالا"}</td></tr>
                <tr><td>{"Liquidity Trap Floor" if lang=="en" else "کف نرخ بهره (دام نقدینگی)"}</td><td>{model.r_floor*100:.1f}%</td><td>{"Horizontal asymptote at low rates" if lang=="en" else "مجانب افقی (عدم رغبت به خرید اوراق)"}</td></tr>
                <tr><td>{"Real Money Supply (M/P)" if lang=="en" else "مانده حقیقی عرضه پول (M/P)"}</td><td>{model.real_money_supply:.1f}</td><td>{"Vertical exogenous policy line" if lang=="en" else "خط کاملاً عمودی سیاست پولی"}</td></tr>
            </tbody>
        </table>
        """, unsafe_allow_html=True)
    with tab3:
        show_money_market_math(model, y_curr, m, p, k, h, r_eq)

# ==========================================
# فصل ۳: تعادل هم‌زمان IS-LM و حالات خاص
# ==========================================
elif "IS-LM" in topic:
    st.header("⚖️ " + ("General Equilibrium (IS-LM) & Special Cases" if lang == "en" else "تعادل عمومی بازار کالا و پول (IS-LM) و حالات خاص"))

    st.sidebar.subheader("🎯 " + ("Policy Presets" if lang == "en" else "بسته‌های سیاستی هوکاگه:"))
    col_s1, col_s2 = st.sidebar.columns(2)
    if "islm_g" not in st.session_state:
        st.session_state.islm_g = 120.0
        st.session_state.islm_m = 400.0

    if col_s1.button(T["buttons"]["rescue_tsunade"]):
        st.session_state.islm_g = 200.0
        st.session_state.islm_m = 400.0
    if col_s2.button(T["buttons"]["baseline"]):
        st.session_state.islm_g = 120.0
        st.session_state.islm_m = 400.0

    cases = [
        "Standard Neo-Keynesian", "Keynesian Liquidity Trap", "Classical Case (Quantity Theory)"
    ] if lang == "en" else [
        "تعادل استاندارد نئوکینزی", "تله نقدینگی کینزی (Liquidity Trap)", "دیدگاه کلاسیک (تئوری مقداری پول)"
    ]

    special_case = st.sidebar.selectbox("Special Regimes:" if lang == "en" else "حالات خاص و مکاتب اقتصادی:", cases)
    regime_mode = "liquidity_trap" if ("Trap" in special_case or "تله" in special_case) else ("classical" if ("Classical" in special_case or "کلاسیک" in special_case) else "standard")

    g_val = st.sidebar.slider("G:" if lang == "en" else "مخارج دولت هوکاگه (G):", 40.0, 260.0, st.session_state.islm_g, step=10.0)
    t_val = st.sidebar.slider("t:" if lang == "en" else "نرخ مالیات (t):", 0.05, 0.40, 0.20, step=0.02)
    m_val = st.sidebar.slider("M:" if lang == "en" else "عرضه اسمی پول دهکده (M):", 150.0, 800.0, st.session_state.islm_m, step=25.0)

    base_eng = ISLMEngine(regime=regime_mode)
    curr_eng = ISLMEngine(G=g_val, t=t_val, M=m_val, regime=regime_mode)
    fig, eq0, eq1 = create_islm_figure(base_eng, curr_eng)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric(T["metrics_labels"]["output"], f"{eq1['Y']:.1f}", delta=f"{eq1['Y'] - eq0['Y']:+.1f}")
    c2.metric(T["metrics_labels"]["interest"], f"{eq1['r']*100:.2f}%", delta=f"{(eq1['r'] - eq0['r'])*100:+.2f}%")
    c3.metric(T["metrics_labels"]["invest"], f"{eq1['I']:.1f}", delta=f"{eq1['I'] - eq0['I']:+.1f}")
    c4.metric(T["metrics_labels"]["budget"], f"{-eq1['Deficit']:+.1f}")

    tab1, tab2, tab3, tab4 = st.tabs([T["tabs"]["charts"], T["tabs"]["metrics"], T["tabs"]["math"], T["tabs"]["pedagogy"]])
    with tab1:
        if lang == "en":
            fig = translate_figure_to_en(fig)
        st.plotly_chart(fig, use_container_width=True, config={"scrollZoom": True, "displayModeBar": True})
    with tab2:
        st.markdown(f"""
        <table class="custom-table">
            <thead><tr><th>{"Variable" if lang=="en" else "متغیر کلان اقتصادی"}</th><th>{"Current Equilibrium" if lang=="en" else "مقدار در تعادل جاری"}</th><th>{"Change" if lang=="en" else "تغییر نسبت به مبدا"}</th></tr></thead>
            <tbody>
                <tr><td>{"Consumption (C)" if lang=="en" else "مصرف کل اهالی کونوها (C)"}</td><td>{eq1['C']:.1f}</td><td>{eq1['C'] - eq0['C']:+.1f}</td></tr>
                <tr><td>{"Private Investment (I)" if lang=="en" else "سرمایه‌گذاری قبیله‌ها (I)"}</td><td>{eq1['I']:.1f}</td><td>{eq1['I'] - eq0['I']:+.1f}</td></tr>
                <tr><td>{"Tax Revenues (T)" if lang=="en" else "درآمدهای مالیاتی خزانه (T)"}</td><td>{eq1['T']:.1f}</td><td>{eq1['T'] - eq0['T']:+.1f}</td></tr>
                <tr><td>{"Budget Deficit (G - T)" if lang=="en" else "کسری بودجه هوکاگه (G - T)"}</td><td>{eq1['Deficit']:.1f}</td><td>{eq1['Deficit'] - eq0['Deficit']:+.1f}</td></tr>
            </tbody>
        </table>
        """, unsafe_allow_html=True)
    with tab3:
        show_islm_math(curr_eng, base_eng, eq0, eq1, regime_mode)
    with tab4:
        if regime_mode == "liquidity_trap":
            st.info("In a Liquidity Trap: LM is horizontal. Fiscal policy has 100% Keynesian multiplier power without any investment crowding out (ΔI = 0)." if lang == "en" else "در تله نقدینگی: حساسیت تقاضای پول به بهره نامحدود است؛ سیاست مالی بدون برون‌رانی سرمایه‌گذاری (ΔI = 0) تولید را با حداکثر توان فزاینده منتقل می‌کند.")
        elif regime_mode == "classical":
            st.warning("In the Classical Case: LM is vertical. Fiscal policy leads to 100% crowding out of private investment (ΔI = -ΔG)." if lang == "en" else "در دیدگاه کلاسیک: تقاضای پول مستقل از نرخ بهره است؛ افزایش مخارج دولت دقیقاً به همان میزان سرمایه‌گذاری بخش خصوصی را خارج می‌کند (ΔI = -ΔG).")
        else:
            crowding = eq1['I'] - eq0['I']
            if g_val > base_eng.G and crowding < 0:
                msg = f"Crowding-out Analysis: Higher government spending increased the interest rate, adjusting private investment by {abs(crowding):.1f} units." if lang == "en" else f"تحلیل برون‌رانی: افزایش مخارج دولت نرخ بهره را بالا برده و سرمایه‌گذاری بخش خصوصی را {abs(crowding):.1f} واحد کاهش داده است."
                st.info(msg)

# ==========================================
# فصل ۴: مدل AD-AS
# ==========================================
elif "AD-AS" in topic or "Supply" in topic:
    st.header("💥 " + ("Aggregate Equilibrium & Phillips Curve" if lang == "en" else "تعادل کل اقتصاد (AD-AS) و منحنی فیلیپس"))
    a_val = st.sidebar.slider("A:" if lang == "en" else "مخارج خودگردان کل (A):", 200.0, 450.0, 320.0, step=10.0)
    m_val = st.sidebar.slider("M:" if lang == "en" else "عرضه اسمی پول (M):", 200.0, 700.0, 400.0, step=25.0)
    shock_val = st.sidebar.slider("z:" if lang == "en" else "شوک منفی عرضه / بحران چاکرا (z):", -0.3, 0.6, 0.0, step=0.05)
    pe_val = st.sidebar.slider("Pᵉ:" if lang == "en" else "انتظارات قیمتی (Pᵉ):", 0.7, 1.5, 1.0, step=0.05)

    base_model = ADASModel()
    curr_model = ADASModel(A=a_val, M=m_val, cost_shock=shock_val, P_expected=pe_val)
    fig, eq0, eq1 = create_adas_figure(base_model, curr_model)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric(T["metrics_labels"]["output"], f"{eq1['Y']:.1f}", delta=f"{eq1['Y'] - base_model.Y_potential:+.1f}")
    c2.metric(T["metrics_labels"]["price"], f"{eq1['P']:.2f}", delta=f"{eq1['P'] - base_model.P_expected:+.2f}")
    c3.metric(T["metrics_labels"]["gap"], f"{eq1['Output_Gap']:+.2f}%")
    c4.metric(T["metrics_labels"]["inflation"], f"{eq1['Inflation']:+.1f}%")

    tab1, tab2, tab3 = st.tabs([T["tabs"]["charts"], T["tabs"]["metrics"], T["tabs"]["math"]])
    with tab1:
        if lang == "en":
            fig = translate_figure_to_en(fig)
        st.plotly_chart(fig, use_container_width=True, config={"scrollZoom": True, "displayModeBar": True})
    with tab2:
        diag = ("Stagflation" if lang=="en" else "رکود تورمی") if (shock_val > 0 and eq1['Y'] < base_model.Y_potential) else (("Inflationary Boom" if lang=="en" else "انبساط تورمی") if eq1['Y'] > base_model.Y_potential else ("General Equilibrium" if lang=="en" else "تعادل پایدار"))
        st.markdown(f"""
        <table class="custom-table">
            <thead><tr><th>{"Macro Metric" if lang=="en" else "شاخص کلان"}</th><th>{"Value" if lang=="en" else "مقدار تعادلی"}</th><th>{"Potential Benchmark" if lang=="en" else "وضعیت نسبت به بالقوه"}</th></tr></thead>
            <tbody>
                <tr><td>{"Real Output (Y)" if lang=="en" else "تولید ناخالص کونوها (Y)"}</td><td>{eq1['Y']:.1f}</td><td>{"Potential (Yn): " if lang=="en" else "پتانسیل طبیعی: "}{curr_model.Y_potential:.0f}</td></tr>
                <tr><td>{"Price Level (P)" if lang=="en" else "شاخص سطح قیمت‌ها (P)"}</td><td>{eq1['P']:.2f}</td><td>{"Expected (Pe): " if lang=="en" else "انتظارات قیمتی: "}{pe_val:.2f}</td></tr>
                <tr><td>{"Output Gap" if lang=="en" else "شکاف تولید"}</td><td>{eq1['Output_Gap']:+.2f}%</td><td>{diag}</td></tr>
                <tr><td>{"Inflation Rate" if lang=="en" else "نرخ تورم سالانه"}</td><td>{eq1['Inflation']:+.1f}%</td><td>{"Expected Inflation: " if lang=="en" else "تورم انتظاری: "}{(pe_val - 1.0)*100:.1f}%</td></tr>
            </tbody>
        </table>
        """, unsafe_allow_html=True)
    with tab3:
        show_adas_math(curr_model, a_val, m_val, pe_val, shock_val, eq1)

# ==========================================
# فصل ۵: اقتصاد باز ماندل-فلمینگ
# ==========================================
elif "Mundell" in topic or "اقتصاد باز" in topic:
    st.header("🌐 " + ("Open Economy (Mundell-Fleming Model)" if lang == "en" else "اقتصاد باز: تعامل کونوها با دهکده سنگ و خاک (Mundell-Fleming)"))

    exchange_system = st.sidebar.radio(
        "Exchange Rate Regime:" if lang == "en" else "انتخاب رژیم ارزی:",
        ["Floating Exchange Rate", "Fixed Exchange Rate"] if lang == "en" else ["نظام نرخ ارز شناور (Floating)", "نظام نرخ ارز ثابت (Fixed)"]
    )
    regime_code = "floating" if ("Floating" in exchange_system or "شناور" in exchange_system) else "fixed"

    g_val = st.sidebar.slider("G:" if lang == "en" else "مخارج دولت کونوها (G):", 50.0, 250.0, 120.0, step=10.0)
    m_val = st.sidebar.slider("M:" if lang == "en" else "عرضه پول هدف اولیه (M):", 200.0, 700.0, 400.0, step=25.0)
    rf_val = st.sidebar.slider("r*:" if lang == "en" else "نرخ بهره بین‌المللی دهکده سنگ (r*):", 0.02, 0.10, 0.05, step=0.01, format="%.2f")
    fixed_e = st.sidebar.slider("e:" if lang == "en" else "نرخ ارز تثبیت‌شده (e):", 0.5, 2.0, 1.0, step=0.1) if regime_code == "fixed" else 1.0

    base_mf = MundellFlemingModel(regime=regime_code)
    curr_mf = MundellFlemingModel(G=g_val, M=m_val, exchange_rate=fixed_e, r_foreign=rf_val, regime=regime_code)
    fig, eq0, eq1 = create_mundell_fleming_figure(base_mf, curr_mf)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric(T["metrics_labels"]["output"], f"{eq1['Y']:.1f}", delta=f"{eq1['Y'] - eq0['Y']:+.1f}")
    c2.metric(T["metrics_labels"]["interest"], f"{eq1['r']*100:.2f}%")
    if regime_code == "floating":
        c3.metric(T["metrics_labels"]["rate_e"], f"{eq1['e']:.2f}", delta=f"{eq1['e'] - eq0['e']:+.2f}")
        c4.metric("Exogenous Money Supply" if lang == "en" else "عرضه پول (برون‌زا)", f"{eq1['M']:.0f}")
    else:
        c3.metric("Fixed Exchange Rate" if lang == "en" else "نرخ ارز تثبیت‌شده", f"{eq1['e']:.2f}")
        c4.metric(T["metrics_labels"]["money_adj"], f"{eq1['M']:.0f}", delta=f"{eq1['M'] - eq0['M']:+.0f}")

    tab1, tab2, tab3, tab4 = st.tabs([T["tabs"]["charts"], T["tabs"]["metrics"], T["tabs"]["math"], T["tabs"]["pedagogy"]])
    with tab1:
        if lang == "en":
            fig = translate_figure_to_en(fig)
        st.plotly_chart(fig, use_container_width=True, config={"scrollZoom": True, "displayModeBar": True})
    with tab2:
        st.markdown(f"""
        <table class="custom-table">
            <thead><tr><th>{"External Account" if lang=="en" else "شاخص بخش خارجی"}</th><th>{"Final Value" if lang=="en" else "مقدار تعادلی نهایی"}</th><th>{"Description" if lang=="en" else "تحلیل حساب"}</th></tr></thead>
            <tbody>
                <tr><td>{"Net Exports (NX)" if lang=="en" else "خالص صادرات (NX)"}</td><td>{eq1['NX']:+.1f}</td><td>{"Trade balance with Stone Village" if lang=="en" else "تراز تجاری با دهکده سنگ"}</td></tr>
                <tr><td>{"Total Exports" if lang=="en" else "صادرات کل کونوها"}</td><td>{eq1['Exports']:.1f}</td><td>{"Ninja equipment & scrolls" if lang=="en" else "صادرات ادوات نینجایی"}</td></tr>
                <tr><td>{"Total Imports" if lang=="en" else "واردات کل کونوها"}</td><td>{eq1['Imports']:.1f}</td><td>{"Raw materials and flint" if lang=="en" else "واردات مصالح و سنگ"}</td></tr>
                <tr><td>{"Balance of Payments (BP)" if lang=="en" else "تراز پرداخت‌ها (BP)"}</td><td>0.0</td><td>{"Complete capital return parity (r = r*)" if lang=="en" else "برابری کامل بازدهی (r = r*)"}</td></tr>
            </tbody>
        </table>
        """, unsafe_allow_html=True)
    with tab3:
        show_open_economy_math(curr_mf, rf_val, regime_code, eq1)
    with tab4:
        if regime_code == "floating":
            st.info("""
            💡 **Floating Exchange Rate Regime:**
            * **Fiscal Policy is Ineffective:** Higher spending appreciates the local currency, destroying net exports and returning IS to its initial spot.
            * **Monetary Policy is Highly Effective:** Higher money supply depreciates currency, boosting exports and strongly lifting output.
            """ if lang == "en" else """
            💡 **در نظام نرخ ارز شناور:**
            * **سیاست مالی بی‌اثر است:** افزایش مخارج دولت پول ملی را تقویت کرده و افت خالص صادرات تقاضا را مجدداً به نقطه اول بازمی‌گرداند.
            * **سیاست پولی بسیار قوی است:** افزایش عرضه پول ارزش پول ملی را تضعیف کرده، صادرات را جهش داده و تولید را به شدت بالا می‌برد.
            """)
        else:
            st.success("""
            💡 **Fixed Exchange Rate Regime:**
            * **Fiscal Policy is Fully Effective:** To defend the pegged rate, the central bank accommodates by injecting money, expanding output without crowding out.
            * **Monetary Policy is Ineffective:** Any attempt to expand money leads to FX reserve outflows, forcing money supply back to baseline.
            """ if lang == "en" else """
            💡 **در نظام نرخ ارز ثابت:**
            * **سیاست مالی فوق‌العاده مؤثر است:** برای حفظ نرخ ارز، بانک مرکزی عرضه پول را همگام با تقاضا بالا می‌برد و رشد اقتصادی بدون برون‌رانی صورت می‌گیرد.
            * **سیاست پولی کاملاً خنثی است:** تلاش برای انبساط پولی با خروج ذخایر ارزی برای دفاع از نرخ ارز خنثی می‌شود.
            """)

# ==========================================
# فصل ۶: مدل رشد سولو
# ==========================================
elif "Solow" in topic or "سولو" in topic:
    st.header("📈 " + ("Solow-Swan Neoclassical Growth Model" if lang == "en" else "مدل رشد نئوکلاسیک سولو و انباشت بلندمدت سرمایه"))
    s_val = st.sidebar.slider("s:" if lang == "en" else "نرخ پس‌انداز دهکده (s):", 0.05, 0.60, 0.25, step=0.05)
    tech_val = st.sidebar.slider("A:" if lang == "en" else "سطح بهره‌وری و فناوری کونوها (A):", 0.6, 2.5, 1.0, step=0.1)
    alpha_val = st.sidebar.slider("α:" if lang == "en" else "کشش تولید نسبت به سرمایه (α):", 0.20, 0.50, 0.35, step=0.05)
    delta_val = st.sidebar.slider("δ:" if lang == "en" else "نرخ استهلاک فیزیکی (δ):", 0.02, 0.12, 0.05, step=0.01)
    pop_val = st.sidebar.slider("n:" if lang == "en" else "نرخ رشد جمعیت (n):", 0.00, 0.05, 0.02, step=0.01)

    base_solow = SolowModel()
    curr_solow = SolowModel(s=s_val, A=tech_val, alpha=alpha_val, delta=delta_val, n=pop_val)
    fig, ss0, ss1 = create_solow_figure(base_solow, curr_solow)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric(T["metrics_labels"]["k_star"], f"{ss1['k_star']:.2f}", delta=f"{ss1['k_star'] - ss0['k_star']:+.2f}")
    c2.metric(T["metrics_labels"]["y_star"], f"{ss1['y_star']:.2f}", delta=f"{ss1['y_star'] - ss0['y_star']:+.2f}")
    c3.metric(T["metrics_labels"]["c_star"], f"{ss1['c_star']:.2f}", delta=f"{ss1['c_star'] - ss0['c_star']:+.2f}")
    c4.metric(T["metrics_labels"]["s_gold"], f"{ss1['s_gold']*100:.0f}%")

    tab1, tab2, tab3, tab4 = st.tabs([T["tabs"]["charts"], T["tabs"]["metrics"], T["tabs"]["math"], T["tabs"]["pedagogy"]])
    with tab1:
        if lang == "en":
            fig = translate_figure_to_en(fig)
        st.plotly_chart(fig, use_container_width=True, config={"scrollZoom": True, "displayModeBar": True})
    with tab2:
        st.markdown(f"""
        <table class="custom-table">
            <thead><tr><th>{"Variable per Worker" if lang=="en" else "متغیر سرانه در وضعیت پایدار"}</th><th>{"Current Steady-State" if lang=="en" else "وضعیت پایدار جاری"}</th><th>{"Golden Rule Benchmark" if lang=="en" else "مقدار در وضعیت قاعده طلایی"}</th></tr></thead>
            <tbody>
                <tr><td>{"Capital Stock (k)" if lang=="en" else "موجودی سرمایه سرانه (k)"}</td><td>{ss1['k_star']:.2f}</td><td>{ss1['k_gold']:.2f}</td></tr>
                <tr><td>{"Output (y)" if lang=="en" else "تولید ناخالص سرانه (y)"}</td><td>{ss1['y_star']:.2f}</td><td>{curr_solow.production_per_effective_worker(ss1['k_gold']):.2f}</td></tr>
                <tr><td>{"Consumption (c)" if lang=="en" else "مصرف سرانه پایدار (c)"}</td><td>{ss1['c_star']:.2f}</td><td>{ss1['c_gold']:.2f}</td></tr>
                <tr><td>{"Investment (i)" if lang=="en" else "سرمایه‌گذاری سرانه (i)"}</td><td>{ss1['i_star']:.2f}</td><td>{(curr_solow.break_even_rate * ss1['k_gold']):.2f}</td></tr>
            </tbody>
        </table>
        """, unsafe_allow_html=True)
    with tab3:
        show_solow_math(curr_solow, s_val, tech_val, alpha_val, ss1)
    with tab4:
        if abs(curr_solow.s - ss1["s_gold"]) < 0.02:
            st.success("🏆 Operates at the Golden Rule level of capital accumulation (s = α)." if lang == "en" else "🏆 انطباق بر قاعده طلایی: نرخ پس‌انداز برابر با سهم سرمایه است و مصرف نسل‌ها حداکثر شده است.")
        elif curr_solow.s > ss1["s_gold"]:
            st.warning("⚠️ Dynamic Inefficiency: Excessive savings reduce consumption today without long-run benefits." if lang == "en" else "⚠️ پویایی ناکارا: سرمایه‌گذاری بیش از حد نیاز است؛ با کاهش پس‌انداز رفاه امروز افزایش می‌یابد.")
        else:
            st.info("💡 Sub-optimal Accumulation: Savings rate is below Golden Rule level." if lang == "en" else "💡 انباشت ناکافی سرمایه: نرخ پس‌انداز زیر حد طلایی است.")