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

st.set_page_config(
    page_title="اتاق عملیات اقتصاد کلان کونوها",
    page_icon="🍃",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;500;700;900&display=swap');
    html, body, [class*="css"] {
        font-family: 'Vazirmatn', Tahoma, sans-serif;
        direction: rtl;
        text-align: right;
    }
    .stMetric {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        padding: 12px;
        border-radius: 10px;
        border-right: 4px solid #16a34a;
    }
    .banner {
        background: linear-gradient(90deg, #f0fdf4 0%, #ecfdf5 100%);
        border-right: 6px solid #10b981;
        padding: 16px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .custom-table {
        width: 100%;
        border-collapse: collapse;
        margin: 15px 0;
        font-size: 15px;
        text-align: right;
    }
    .custom-table th {
        background-color: #f1f5f9;
        color: #0f172a;
        padding: 10px 14px;
        border: 1px solid #cbd5e1;
    }
    .custom-table td {
        padding: 10px 14px;
        border: 1px solid #e2e8f0;
    }
    .custom-table tr:nth-child(even) {
        background-color: #f8fafc;
    }
</style>
""", unsafe_allow_html=True)

st.title("🍃 اتاق عملیات اقتصادی هوکاگه | شبیه‌ساز اقتصاد کلان کونوها")
st.markdown("""
<div class="banner">
<b>سامانه تعاملی تدریس اقتصاد کلان:</b> این ابزار جهت تحلیل زنده تعادل عمومی، سیاست‌های پولی و مالی، نظام‌های ارزی و رشد اقتصادی طراحی شده است.
</div>
""", unsafe_allow_html=True)

st.sidebar.title("طرح درس اقتصاد کلان")
topic = st.sidebar.selectbox(
    "فصل مورد نظر را انتخاب کنید:",
    [
        "۱. بازار کالا و تقاطع کینزی (IS)",
        "۲. بازار پول و ترجیح نقدینگی (LM)",
        "۳. تعادل هم‌زمان کالا و پول و حالات خاص (IS-LM)",
        "۴. تعادل کل و منحنی فیلیپس (AD-AS)",
        "۵. اقتصاد باز و تعامل با دهکده سنگ (ماندل-فلمینگ)",
        "۶. رشد بلندمدت و انباشت سرمایه (مدل سولو)"
    ]
)
st.sidebar.markdown("---")

# ==========================================
# فصل ۱: بازار کالا
# ==========================================
if "بازار کالا" in topic:
    st.header("📦 بازار کالا و تقاطع کینزی")
    c0 = st.sidebar.slider("مصرف خودگردان (c₀):", 20.0, 150.0, 60.0, step=5.0)
    mpc = st.sidebar.slider("میل نهایی به مصرف (mpc):", 0.4, 0.95, 0.75, step=0.05)
    t = st.sidebar.slider("نرخ مالیات (t):", 0.05, 0.45, 0.20, step=0.05)
    g = st.sidebar.slider("مخارج دولت هوکاگه (G):", 40.0, 250.0, 120.0, step=10.0)
    r = st.sidebar.slider("نرخ بهره جاری (r):", 0.01, 0.15, 0.05, step=0.005, format="%.3f")

    model = GoodsMarketModel(c0=c0, mpc=mpc, t=t, G=g)
    fig, Y_eq = create_goods_market_figure(model, r_current=r)

    c1, c2, c3 = st.columns(3)
    c1.metric("ضریب فزاینده کینزی (α)", f"{model.multiplier:.2f}")
    c2.metric("تولید تعادلی بازار کالا (Y)", f"{Y_eq:.1f} ریو")
    c3.metric("مخارج خودگردان کل (A)", f"{model.autonomous_spending(r):.1f}")

    tab1, tab2 = st.tabs(["📊 نمودارهای تحلیلی", "📐 محاسبات و حل تشریحی ریاضی"])
    with tab1:
        st.plotly_chart(fig, use_container_width=True, config={"scrollZoom": True, "displayModeBar": True})
    with tab2:
        show_goods_market_math(model, r, Y_eq, c0, mpc, t, g)

# ==========================================
# فصل ۲: بازار پول
# ==========================================
elif "بازار پول" in topic:
    st.header("🏦 بازار پول و ترجیح نقدینگی")
    m = st.sidebar.slider("عرضه اسمی پول (M):", 200.0, 800.0, 400.0, step=25.0)
    p = st.sidebar.slider("شاخص سطح قیمت‌ها (P):", 0.5, 2.0, 1.0, step=0.1)
    k = st.sidebar.slider("حساسیت تقاضای پول به درآمد (k):", 0.2, 0.8, 0.50, step=0.05)
    h = st.sidebar.slider("حساسیت تقاضای پول به بهره (h):", 1000.0, 8000.0, 4000.0, step=500.0)
    y_curr = st.sidebar.slider("درآمد ناخالص جاری (Y):", 600.0, 1500.0, 1000.0, step=50.0)

    model = MoneyMarketModel(M=m, P=p, k=k, h=h)
    fig, r_eq = create_money_market_figure(model, Y_current=y_curr)

    c1, c2 = st.columns(2)
    c1.metric("مانده واقعی پول (M/P)", f"{model.real_money_supply:.1f}")
    c2.metric("نرخ بهره تعادلی (r)", f"{r_eq * 100:.2f}%")

    tab1, tab2 = st.tabs(["📊 نمودارهای تعادل بازار پول و LM", "📐 محاسبات و حل تشریحی ریاضی"])
    with tab1:
        st.plotly_chart(fig, use_container_width=True, config={"scrollZoom": True, "displayModeBar": True})
    with tab2:
        show_money_market_math(model, y_curr, m, p, k, h, r_eq)

# ==========================================
# فصل ۳: تعادل IS-LM
# ==========================================
elif "حالات خاص" in topic or "IS-LM" in topic:
    st.header("⚖️ تعادل عمومی بازار کالا و پول (IS-LM)")

    st.sidebar.subheader("🎯 بسته‌های سیاستی هوکاگه:")
    col_s1, col_s2 = st.sidebar.columns(2)
    if "islm_g" not in st.session_state:
        st.session_state.islm_g = 120.0
        st.session_state.islm_m = 400.0

    if col_s1.button("🏛️ بسته نجات تسوناده"):
        st.session_state.islm_g = 200.0
        st.session_state.islm_m = 400.0
    if col_s2.button("🔄 تعادل پایه"):
        st.session_state.islm_g = 120.0
        st.session_state.islm_m = 400.0

    special_case = st.sidebar.selectbox(
        "حالات خاص و مکاتب اقتصادی:",
        ["تعادل استاندارد نئوکینزی", "تله نقدینگی کینزی (Liquidity Trap)", "دیدگاه کلاسیک (تئوری مقداری پول)"]
    )

    regime_mode = "liquidity_trap" if "تله نقدینگی" in special_case else ("classical" if "کلاسیک" in special_case else "standard")

    st.sidebar.subheader("تنظیم متغیرهای سیاستی:")
    g_val = st.sidebar.slider("مخارج بازسازی هوکاگه (G):", 40.0, 260.0, st.session_state.islm_g, step=10.0)
    t_val = st.sidebar.slider("نرخ مالیات (t):", 0.05, 0.40, 0.20, step=0.02)
    m_val = st.sidebar.slider("عرضه اسمی پول دهکده (M):", 150.0, 800.0, st.session_state.islm_m, step=25.0)

    base_eng = ISLMEngine(regime=regime_mode)
    curr_eng = ISLMEngine(G=g_val, t=t_val, M=m_val, regime=regime_mode)
    fig, eq0, eq1 = create_islm_figure(base_eng, curr_eng)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("تولید تعادلی (Y)", f"{eq1['Y']:.1f}", delta=f"{eq1['Y'] - eq0['Y']:+.1f}")
    c2.metric("نرخ بهره تعادلی (r)", f"{eq1['r']*100:.2f}%", delta=f"{(eq1['r'] - eq0['r'])*100:+.2f}%")
    c3.metric("سرمایه‌گذاری خصوصی (I)", f"{eq1['I']:.1f}", delta=f"{eq1['I'] - eq0['I']:+.1f}")
    c4.metric("تراز بودجه دولت (T - G)", f"{-eq1['Deficit']:+.1f}")

    tab_chart, tab_math, tab_pedagogy = st.tabs(["📊 دیاگرام IS-LM", "📐 محاسبات و حل تشریحی ریاضی", "🎓 راهنمای تدریس و حالات خاص"])

    with tab_chart:
        st.plotly_chart(fig, use_container_width=True, config={"scrollZoom": True, "displayModeBar": True})
    with tab_math:
        show_islm_math(curr_eng, base_eng, eq0, eq1, regime_mode)
    with tab_pedagogy:
        if regime_mode == "liquidity_trap":
            st.info("💡 **در تله نقدینگی:** حساسیت تقاضای پول به بهره نامحدود است؛ تغییر سیاست مالی بدون هیچ‌گونه برون‌رانی تولید را با حداکثر توان فزاینده منتقل می‌کند.")
        elif regime_mode == "classical":
            st.warning("💡 **در دیدگاه کلاسیک:** تقاضای پول مستقل از نرخ بهره است؛ افزایش مخارج دولت دقیقاً به همان میزان سرمایه‌گذاری بخش خصوصی را خارج می‌کند.")
        else:
            crowding = eq1['I'] - eq0['I']
            if g_val > base_eng.G and crowding < 0:
                st.info(f"💡 **تحلیل برون‌رانی:** افزایش مخارج دولت نرخ بهره را افزایش داده و سرمایه‌گذاری بخش خصوصی را `{abs(crowding):.1f}` واحد تعدیل کرده است.")

# ==========================================
# فصل ۴: مدل AD-AS
# ==========================================
elif "AD-AS" in topic or "فیلیپس" in topic:
    st.header("💥 تعادل کل اقتصاد (AD-AS) و منحنی فیلیپس")
    a_val = st.sidebar.slider("مخارج خودگردان کل (A):", 200.0, 450.0, 320.0, step=10.0)
    m_val = st.sidebar.slider("عرضه اسمی پول (M):", 200.0, 700.0, 400.0, step=25.0)
    shock_val = st.sidebar.slider("شوک منفی عرضه / بحران چاکرا (z):", -0.3, 0.6, 0.0, step=0.05)
    pe_val = st.sidebar.slider("انتظارات قیمتی (Pᵉ):", 0.7, 1.5, 1.0, step=0.05)

    base_model = ADASModel()
    curr_model = ADASModel(A=a_val, M=m_val, cost_shock=shock_val, P_expected=pe_val)
    fig, eq0, eq1 = create_adas_figure(base_model, curr_model)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("تولید تعادلی (Y)", f"{eq1['Y']:.1f}", delta=f"{eq1['Y'] - base_model.Y_potential:+.1f}")
    c2.metric("شاخص قیمت (P)", f"{eq1['P']:.2f}", delta=f"{eq1['P'] - base_model.P_expected:+.2f}")
    c3.metric("شکاف تولید", f"{eq1['Output_Gap']:+.2f}%")
    c4.metric("نرخ تورم", f"{eq1['Inflation']:+.1f}%")

    tab1, tab2 = st.tabs(["📊 دیاگرام‌های AD-AS و فیلیپس", "📐 محاسبات و حل تشریحی ریاضی"])
    with tab1:
        st.plotly_chart(fig, use_container_width=True, config={"scrollZoom": True, "displayModeBar": True})
    with tab2:
        show_adas_math(curr_model, a_val, m_val, pe_val, shock_val, eq1)

# ==========================================
# فصل ۵: اقتصاد باز ماندل-فلمینگ
# ==========================================
elif "اقتصاد باز" in topic or "ماندل" in topic:
    st.header("🌐 اقتصاد باز: تعامل کونوها با دهکده سنگ و خاک (Mundell-Fleming)")

    st.sidebar.subheader("💱 نظام ارزی دهکده کونوها:")
    exchange_system = st.sidebar.radio(
        "انتخاب رژیم ارزی:",
        ["نظام نرخ ارز شناور (Floating)", "نظام نرخ ارز ثابت (Fixed)"]
    )
    regime_code = "floating" if "شناور" in exchange_system else "fixed"

    st.sidebar.subheader("تنظیم متغیرهای سیاستی:")
    g_val = st.sidebar.slider("مخارج دولت کونوها (G):", 50.0, 250.0, 120.0, step=10.0)
    m_val = st.sidebar.slider("عرضه پول هدف اولیه (M):", 200.0, 700.0, 400.0, step=25.0)
    rf_val = st.sidebar.slider("نرخ بهره بین‌المللی دهکده سنگ (r*):", 0.02, 0.10, 0.05, step=0.01, format="%.2f")

    fixed_e = st.sidebar.slider("نرخ ارز تثبیت‌شده (e):", 0.5, 2.0, 1.0, step=0.1) if regime_code == "fixed" else 1.0

    base_mf = MundellFlemingModel(regime=regime_code)
    curr_mf = MundellFlemingModel(G=g_val, M=m_val, exchange_rate=fixed_e, r_foreign=rf_val, regime=regime_code)
    fig, eq0, eq1 = create_mundell_fleming_figure(base_mf, curr_mf)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("تولید ناخالص کونوها (Y)", f"{eq1['Y']:.1f}", delta=f"{eq1['Y'] - eq0['Y']:+.1f}")
    c2.metric("نرخ بهره تعادلی (r)", f"{eq1['r']*100:.2f}%")
    if regime_code == "floating":
        c3.metric("نرخ ارز تعادلی شناور (e)", f"{eq1['e']:.2f}", delta=f"{eq1['e'] - eq0['e']:+.2f}")
        c4.metric("عرضه پول (برون‌زا)", f"{eq1['M']:.0f}")
    else:
        c3.metric("نرخ ارز تثبیت‌شده (e)", f"{eq1['e']:.2f}")
        c4.metric("عرضه پول تعدیل‌شده بانک مرکزی", f"{eq1['M']:.0f}", delta=f"{eq1['M'] - eq0['M']:+.0f}")

    tab1, tab2 = st.tabs(["📊 دیاگرام تعادل هم‌زمان IS-LM-BP", "📐 محاسبات و حل تشریحی ریاضی"])
    with tab1:
        st.plotly_chart(fig, use_container_width=True, config={"scrollZoom": True, "displayModeBar": True})
    with tab2:
        show_open_economy_math(curr_mf, rf_val, regime_code, eq1)

# ==========================================
# فصل ۶: مدل رشد سولو
# ==========================================
elif "سولو" in topic or "رشد بلندمدت" in topic:
    st.header("📈 مدل رشد نئوکلاسیک سولو و انباشت بلندمدت سرمایه")
    s_val = st.sidebar.slider("نرخ پس‌انداز دهکده (s):", 0.05, 0.60, 0.25, step=0.05)
    tech_val = st.sidebar.slider("سطح بهره‌وری و فناوری کونوها (A):", 0.6, 2.5, 1.0, step=0.1)
    alpha_val = st.sidebar.slider("کشش تولید نسبت به سرمایه (α):", 0.20, 0.50, 0.35, step=0.05)
    delta_val = st.sidebar.slider("نرخ استهلاک فیزیکی (δ):", 0.02, 0.12, 0.05, step=0.01)
    pop_val = st.sidebar.slider("نرخ رشد جمعیت (n):", 0.00, 0.05, 0.02, step=0.01)

    base_solow = SolowModel()
    curr_solow = SolowModel(s=s_val, A=tech_val, alpha=alpha_val, delta=delta_val, n=pop_val)
    fig, ss0, ss1 = create_solow_figure(base_solow, curr_solow)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("سرمایه پایدار سرانه (k*)", f"{ss1['k_star']:.2f}", delta=f"{ss1['k_star'] - ss0['k_star']:+.2f}")
    c2.metric("تولید سرانه (y*)", f"{ss1['y_star']:.2f}", delta=f"{ss1['y_star'] - ss0['y_star']:+.2f}")
    c3.metric("مصرف سرانه (c*)", f"{ss1['c_star']:.2f}", delta=f"{ss1['c_star'] - ss0['c_star']:+.2f}")
    c4.metric("نرخ پس‌انداز قاعده طلایی", f"{ss1['s_gold']*100:.0f}%")

    tab1, tab2 = st.tabs(["📊 نمودار وضعیت پایدار سولو", "📐 محاسبات و حل تشریحی ریاضی"])
    with tab1:
        st.plotly_chart(fig, use_container_width=True, config={"scrollZoom": True, "displayModeBar": True})
    with tab2:
        show_solow_math(curr_solow, s_val, tech_val, alpha_val, ss1)