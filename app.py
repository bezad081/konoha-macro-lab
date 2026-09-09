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

    tab1, tab2, tab3 = st.tabs(["📊 نمودارهای تحلیلی", "📋 کارنامه حساب‌ها", "📐 محاسبات و حل تشریحی ریاضی"])
    with tab1:
        st.plotly_chart(fig, use_container_width=True, config={"scrollZoom": True, "displayModeBar": True})
    with tab2:
        T_val = t * Y_eq
        C_val = c0 + mpc * (Y_eq - T_val)
        I_val = model.i0 - model.b * r
        table_goods = f"""
        <table class="custom-table">
            <thead>
                <tr><th>جزء مخارج</th><th>مقدار تعادلی (ریو)</th><th>درصد از کل تقاضا</th></tr>
            </thead>
            <tbody>
                <tr><td>مصرف کل خانوارها (C)</td><td>{C_val:.1f}</td><td>{(C_val/Y_eq)*100:.1f}%</td></tr>
                <tr><td>سرمایه‌گذاری قبیله‌ها (I)</td><td>{I_val:.1f}</td><td>{(I_val/Y_eq)*100:.1f}%</td></tr>
                <tr><td>مخارج دولت هوکاگه (G)</td><td>{g:.1f}</td><td>{(g/Y_eq)*100:.1f}%</td></tr>
                <tr><td>کل درآمدهای مالیاتی (T)</td><td>{T_val:.1f}</td><td>تراز بودجه: {T_val - g:+.1f}</td></tr>
            </tbody>
        </table>
        """
        st.markdown(table_goods, unsafe_allow_html=True)
    with tab3:
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

    tab1, tab2, tab3 = st.tabs(["📊 نمودارهای تعادل بازار پول و LM", "📋 کارنامه اجزای تقاضای پول", "📐 محاسبات و حل تشریحی ریاضی"])
    with tab1:
        st.plotly_chart(fig, use_container_width=True, config={"scrollZoom": True, "displayModeBar": True})
    with tab2:
        lt_val = k * y_curr
        ls_val = h * r_eq
        table_money = f"""
        <table class="custom-table">
            <thead>
                <tr><th>مؤلفه بازار پول</th><th>مقدار محاسباتی</th><th>مفهوم اقتصادی</th></tr>
            </thead>
            <tbody>
                <tr><td>تقاضای معاملاتی و احتیاطی (kY)</td><td>{lt_val:.1f}</td><td>تقاضای وابسته به سطح مبادلات چاکرا و تجارت</td></tr>
                <tr><td>تقاضای سفته‌بازی نقدینگی (hr)</td><td>{ls_val:.1f}</td><td>تقاضای نقدینگی معکوس با نرخ بهره بازار</td></tr>
                <tr><td>مانده واقعی تعادلی عرضه پول (M/P)</td><td>{model.real_money_supply:.1f}</td><td>برابری عرضه واقعی با مجموع تقاضاها</td></tr>
            </tbody>
        </table>
        """
        st.markdown(table_money, unsafe_allow_html=True)
    with tab3:
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

    tab_chart, tab_data, tab_math, tab_pedagogy = st.tabs(["📊 دیاگرام IS-LM", "📋 کارنامه شاخص‌ها", "📐 محاسبات و حل تشریحی ریاضی", "🎓 راهنمای تدریس و حالات خاص"])

    with tab_chart:
        st.plotly_chart(fig, use_container_width=True, config={"scrollZoom": True, "displayModeBar": True})

    with tab_data:
        table_islm = f"""
        <table class="custom-table">
            <thead>
                <tr><th>متغیر کلان اقتصادی</th><th>مقدار در تعادل جاری</th><th>تغییر نسبت به مبدا</th></tr>
            </thead>
            <tbody>
                <tr><td>مصرف کل اهالی کونوها (C)</td><td>{eq1['C']:.1f}</td><td>{eq1['C'] - eq0['C']:+.1f}</td></tr>
                <tr><td>سرمایه‌گذاری قبیله‌ها (I)</td><td>{eq1['I']:.1f}</td><td>{eq1['I'] - eq0['I']:+.1f}</td></tr>
                <tr><td>درآمدهای مالیاتی خزانه (T)</td><td>{eq1['T']:.1f}</td><td>{eq1['T'] - eq0['T']:+.1f}</td></tr>
                <tr><td>کسری بودجه هوکاگه (G - T)</td><td>{eq1['Deficit']:.1f}</td><td>{eq1['Deficit'] - eq0['Deficit']:+.1f}</td></tr>
            </tbody>
        </table>
        """
        st.markdown(table_islm, unsafe_allow_html=True)

    with tab_math:
        show_islm_math(curr_eng, base_eng, eq0, eq1, regime_mode)

    with tab_pedagogy:
        if regime_mode == "liquidity_trap":
            st.info("💡 **در تله نقدینگی:** حساسیت تقاضای پول به بهره بسیار بالاست؛ سیاست مالی بدون برون‌رانی سرمایه‌گذاری ($\Delta I = 0$) تولید را با حداکثر توان فزاینده کینزی منتقل می‌کند.")
        elif regime_mode == "classical":
            st.warning("💡 **در دیدگاه کلاسیک:** تقاضای پول مستقل از نرخ بهره است؛ افزایش مخارج دولت دقیقاً به همان میزان سرمایه‌گذاری بخش خصوصی را خارج می‌کند ($\Delta I = -\Delta G$).")
        else:
            crowding = eq1['I'] - eq0['I']
            if g_val > base_eng.G and crowding < 0:
                st.info(f"💡 **تحلیل برون‌رانی:** افزایش مخارج دولت نرخ بهره را افزایش داده و سرمایه‌گذاری بخش خصوصی را `{abs(crowding):.1f}` واحد کاهش داده است.")

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

    tab1, tab2, tab3 = st.tabs(["📊 دیاگرام‌های AD-AS و فیلیپس", "📋 کارنامه تعادل کل", "📐 محاسبات و حل تشریحی ریاضی"])
    with tab1:
        st.plotly_chart(fig, use_container_width=True, config={"scrollZoom": True, "displayModeBar": True})
    with tab2:
        diag = "رکود تورمی (Stagflation)" if (shock_val > 0 and eq1['Y'] < base_model.Y_potential) else ("انبساط تورمی" if eq1['Y'] > base_model.Y_potential else "تعادل پایدار")
        table_adas = f"""
        <table class="custom-table">
            <thead>
                <tr><th>شاخص کلان</th><th>مقدار تعادلی</th><th>وضعیت نسبت به بالقوه</th></tr>
            </thead>
            <tbody>
                <tr><td>تولید ناخالص کونوها (Y)</td><td>{eq1['Y']:.1f}</td><td>پتانسیل طبیعی: {curr_model.Y_potential:.0f}</td></tr>
                <tr><td>شاخص سطح قیمت‌ها (P)</td><td>{eq1['P']:.2f}</td><td>انتظارات قیمتی: {pe_val:.2f}</td></tr>
                <tr><td>شکاف تولید (Output Gap)</td><td>{eq1['Output_Gap']:+.2f}%</td><td>{diag}</td></tr>
                <tr><td>نرخ تورم سالانه</td><td>{eq1['Inflation']:+.1f}%</td><td>تورم انتظاری: {(pe_val - 1.0)*100:.1f}%</td></tr>
            </tbody>
        </table>
        """
        st.markdown(table_adas, unsafe_allow_html=True)
    with tab3:
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

    tab_mf_chart, tab_mf_metrics, tab_mf_math, tab_mf_pedagogy = st.tabs(["📊 دیاگرام IS-LM-BP", "📋 کارنامه حساب‌های خارجی", "📐 محاسبات و حل تشریحی ریاضی", "🎓 تحلیل اثربخشی سیاست‌ها"])

    with tab_mf_chart:
        st.plotly_chart(fig, use_container_width=True, config={"scrollZoom": True, "displayModeBar": True})

    with tab_mf_metrics:
        table_mf = f"""
        <table class="custom-table">
            <thead>
                <tr><th>شاخص بخش خارجی</th><th>مقدار تعادلی نهایی</th><th>تحلیل حساب</th></tr>
            </thead>
            <tbody>
                <tr><td>خالص صادرات (NX)</td><td>{eq1['NX']:+.1f}</td><td>تراز تجاری کونوها با دهکده سنگ</td></tr>
                <tr><td>صادرات کل کونوها</td><td>{eq1['Exports']:.1f}</td><td>صادرات ادوات نینجایی و خدمات</td></tr>
                <tr><td>واردات کل کونوها</td><td>{eq1['Imports']:.1f}</td><td>واردات مصالح سنگی و سنگ چخماق</td></tr>
                <tr><td>تراز پرداخت‌ها (BP)</td><td>0.0 (تعادل کامل)</td><td>تساوی نرخ بازدهی با دهکده سنگ (r = r*)</td></tr>
            </tbody>
        </table>
        """
        st.markdown(table_mf, unsafe_allow_html=True)

    with tab_mf_math:
        show_open_economy_math(curr_mf, rf_val, regime_code, eq1)

    with tab_mf_pedagogy:
        if regime_code == "floating":
            st.info("""
            💡 **در نظام نرخ ارز شناور:**
            * **سیاست مالی بی‌اثر است:** با افزایش مخارج دولت، پول ملی تقویت شده و افت خالص صادرات تقاضا را مجدداً به نقطه اول بازمی‌گرداند.
            * **سیاست پولی بسیار قوی است:** افزایش عرضه پول ارزش پول ملی را تضعیف کرده، صادرات را جهش داده و تولید را به شدت بالا می‌برد.
            """)
        else:
            st.success("""
            💡 **در نظام نرخ ارز ثابت:**
            * **سیاست مالی فوق‌العاده مؤثر است:** برای حفظ نرخ ارز، بانک مرکزی عرضه پول را همگام با تقاضا بالا می‌برد و رشد اقتصادی بدون برون‌رانی صورت می‌گیرد.
            * **سیاست پولی کاملاً خنثی است:** تلاش برای انبساط پولی با خروج ذخایر ارزی برای دفاع از نرخ ارز خنثی می‌شود.
            """)

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

    tab1, tab2, tab3, tab4 = st.tabs(["📊 نمودار وضعیت پایدار سولو", "📋 کارنامه متغیرهای سرانه", "📐 محاسبات و حل تشریحی ریاضی", "🎓 تحلیل قاعده طلایی"])

    with tab1:
        st.plotly_chart(fig, use_container_width=True, config={"scrollZoom": True, "displayModeBar": True})

    with tab2:
        table_solow = f"""
        <table class="custom-table">
            <thead>
                <tr><th>متغیر سرانه در وضعیت پایدار</th><th>مقدار در وضعیت پایدار جاری</th><th>مقدار در وضعیت قاعده طلایی</th></tr>
            </thead>
            <tbody>
                <tr><td>موجودی سرمایه سرانه (k)</td><td>{ss1['k_star']:.2f}</td><td>{ss1['k_gold']:.2f}</td></tr>
                <tr><td>تولید ناخالص سرانه (y)</td><td>{ss1['y_star']:.2f}</td><td>{curr_solow.production_per_effective_worker(ss1['k_gold']):.2f}</td></tr>
                <tr><td>مصرف سرانه پایدار (c)</td><td>{ss1['c_star']:.2f}</td><td>{ss1['c_gold']:.2f}</td></tr>
                <tr><td>سرمایه‌گذاری سرانه (i)</td><td>{ss1['i_star']:.2f}</td><td>{(curr_solow.break_even_rate * ss1['k_gold']):.2f}</td></tr>
            </tbody>
        </table>
        """
        st.markdown(table_solow, unsafe_allow_html=True)

    with tab3:
        show_solow_math(curr_solow, s_val, tech_val, alpha_val, ss1)

    with tab4:
        if abs(curr_solow.s - ss1["s_gold"]) < 0.02:
            st.success("🏆 **انطباق بر قاعده طلایی:** نرخ پس‌انداز برابر با سهم درآمدی سرمایه ($s = \\alpha$) است و مصرف پایدار نسل حاضر و آینده حداکثر شده است.")
        elif curr_solow.s > ss1["s_gold"]:
            st.warning("⚠️ **پویایی ناکارا (Dynamic Inefficiency):** سرمایه‌گذاری بیش از حد نیاز است؛ با کاهش پس‌انداز می‌توان بدون آسیب به رشد آینده، رفاه امروز را بالا برد.")
        else:
            st.info("💡 **انباشت ناکافی سرمایه:** نرخ پس‌انداز زیر حد طلایی است؛ افزایش تمایل به پس‌انداز در بلندمدت مصرف سرانه را ارتقا می‌دهد.")