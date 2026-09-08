import streamlit as st
import pandas as pd

# ایمپورت مستقیم ماژول‌های ۵گانه از فایل‌های مستقل
from goods_market import GoodsMarketModel, create_goods_market_figure
from money_market import MoneyMarketModel, create_money_market_figure
from islm import ISLMEngine, create_islm_figure
from adas import ADASModel, create_adas_figure
from open_economy import MundellFlemingModel, create_mundell_fleming_figure

# پیکربندی صفحه
st.set_page_config(
    page_title="اتاق عملیات اقتصاد کلان کونوها",
    page_icon="🍃",
    layout="wide",
    initial_sidebar_state="expanded"
)

# استایل‌دهی اختصاصی، فونت و جدول‌های بدون نیاز به Arrow
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
<b>سامانه تعاملی تدریس اقتصاد کلان:</b> این ابزار جهت شبیه‌سازی زنده سیاست‌های مالی هوکاگه، سیاست‌های پولی و شوک‌های اقتصادی روی روستای کونوها طراحی شده است.
</div>
""", unsafe_allow_html=True)

# منوی فصول در سایدبار
st.sidebar.title("طرح درس اقتصاد کلان")
topic = st.sidebar.selectbox(
    "فصل مورد نظر را انتخاب کنید:",
    [
        "۱. بازار کالا و تقاطع کینزی (IS)",
        "۲. بازار پول و ترجیح نقدینگی (LM)",
        "۳. تعادل عمومی کالا و پول (IS-LM)",
        "۴. تعادل کل و منحنی فیلیپس (AD-AS)",
        "۵. اقتصاد باز و تعامل با دهکده سنگ/خاک (ماندل-فلمینگ)"
    ]
)
st.sidebar.markdown("---")

# ==========================================
# فصل ۴: مدل AD-AS و منحنی فیلیپس
# ==========================================
if "۴." in topic:
    st.header("💥 تعادل کل اقتصاد (AD-AS) و منحنی فیلیپس")

    st.sidebar.subheader("🎯 سناریوهای بحران و مأموریت:")
    col_btn1, col_btn2 = st.sidebar.columns(2)
    
    if "adas_shock" not in st.session_state:
        st.session_state.adas_shock = 0.0
        st.session_state.adas_m = 400.0
        st.session_state.adas_a = 320.0

    if col_btn1.button("🚨 حمله پین (شوک عرضه)"):
        st.session_state.adas_shock = 0.35
        st.session_state.adas_m = 400.0
    if col_btn2.button("🔄 تعادل پایه"):
        st.session_state.adas_shock = 0.0
        st.session_state.adas_m = 400.0
        st.session_state.adas_a = 320.0

    st.sidebar.subheader("تنظیم دستی متغیرها:")
    a_val = st.sidebar.slider("مخارج خودگردان کل (A):", 200.0, 450.0, st.session_state.adas_a, step=10.0)
    m_val = st.sidebar.slider("عرضه اسمی پول (M):", 200.0, 700.0, st.session_state.adas_m, step=25.0)
    shock_val = st.sidebar.slider("شوک منفی عرضه / بحران چاکرا (z):", -0.3, 0.6, st.session_state.adas_shock, step=0.05)
    pe_val = st.sidebar.slider("انتظارات قیمتی (Pᵉ):", 0.7, 1.5, 1.0, step=0.05)

    base_model = ADASModel()
    curr_model = ADASModel(A=a_val, M=m_val, cost_shock=shock_val, P_expected=pe_val)
    fig, eq0, eq1 = create_adas_figure(base_model, curr_model)

    tab_chart, tab_data, tab_pedagogy = st.tabs(["📊 نمودارهای تحلیلی زنده", "📋 کارنامه شاخص‌ها", "🎓 راهنمای تدریس در کلاس"])

    with tab_chart:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("تولید تعادلی (Y)", f"{eq1['Y']:.1f}", delta=f"{eq1['Y'] - base_model.Y_potential:+.1f}")
        c2.metric("شاخص سطح قیمت‌ها (P)", f"{eq1['P']:.2f}", delta=f"{eq1['P'] - base_model.P_expected:+.2f}")
        c3.metric("شکاف تولید", f"{eq1['Output_Gap']:+.2f}%")
        c4.metric("نرخ تورم کونوها", f"{eq1['Inflation']:+.1f}%")

        if shock_val > 0 and eq1["Y"] < base_model.Y_potential:
            st.error("⚠️ **تشخیص حالت رکود تورمی (Stagflation):** کاهش هم‌زمان تولید ملی و جهش قیمت‌ها رخ داده است.")
        st.plotly_chart(fig, use_container_width=True)

    with tab_data:
        st.write("مقایسه کمی تعادل مبدا نسبت به تعادل جاری:")
        # ساخت جدول به صورت HTML مستقیم برای دور زدن خطای pyarrow
        table_html = f"""
        <table class="custom-table">
            <thead>
                <tr>
                    <th>شاخص اقتصادی</th>
                    <th>وضعیت مبدا</th>
                    <th>وضعیت جاری</th>
                    <th>میزان تغییرات</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>تولید ناخالص داخلی (Y)</td>
                    <td>{eq0['Y']:.1f}</td>
                    <td>{eq1['Y']:.1f}</td>
                    <td>{eq1['Y'] - eq0['Y']:+.1f}</td>
                </tr>
                <tr>
                    <td>سطح عمومی قیمت‌ها (P)</td>
                    <td>{eq0['P']:.2f}</td>
                    <td>{eq1['P']:.2f}</td>
                    <td>{eq1['P'] - eq0['P']:+.2f}</td>
                </tr>
                <tr>
                    <td>شکاف تولید (Output Gap)</td>
                    <td>{eq0['Output_Gap']:.2f}%</td>
                    <td>{eq1['Output_Gap']:.2f}%</td>
                    <td>{eq1['Output_Gap'] - eq0['Output_Gap']:+.2f}%</td>
                </tr>
                <tr>
                    <td>نرخ تورم (π)</td>
                    <td>{eq0['Inflation']:.1f}%</td>
                    <td>{eq1['Inflation']:.1f}%</td>
                    <td>{eq1['Inflation'] - eq0['Inflation']:+.1f}%</td>
                </tr>
            </tbody>
        </table>
        """
        st.markdown(table_html, unsafe_allow_html=True)

    with tab_pedagogy:
        st.info("""
        * **مفهوم شکاف تولید:** ناحیه سایه‌خورده در نمودار، فاصله تولید جاری تا پتانسیل طبیعی را نشان می‌دهد.
        * **پرسش کلاسی:** شوک منفی عرضه چه اثری بر نرخ بیکاری و تورم هم‌زمان می‌گذارد؟
        """)

# ==========================================
# فصل ۳: تعادل هم‌زمان IS-LM
# ==========================================
elif "۳." in topic:
    st.header("⚖️ تعادل عمومی بازار کالا و پول (مدل IS-LM)")

    st.sidebar.subheader("🎯 بسته‌های سیاستی هوکاگه:")
    col_s1, col_s2 = st.sidebar.columns(2)

    if "islm_g" not in st.session_state:
        st.session_state.islm_g = 120.0
        st.session_state.islm_m = 400.0

    if col_s1.button("🏛️ بسته نجات تسوناده"):
        st.session_state.islm_g = 220.0
    if col_s2.button("🔄 تعادل پایه"):
        st.session_state.islm_g = 120.0
        st.session_state.islm_m = 400.0

    st.sidebar.subheader("تنظیم متغیرها:")
    g_val = st.sidebar.slider("مخارج بازسازی هوکاگه (G):", 40.0, 260.0, st.session_state.islm_g, step=10.0)
    t_val = st.sidebar.slider("نرخ مالیات (t):", 0.05, 0.40, 0.20, step=0.02)
    m_val = st.sidebar.slider("عرضه اسمی پول دهکده (M):", 150.0, 800.0, st.session_state.islm_m, step=25.0)
    p_val = st.sidebar.slider("سطح عمومی قیمت‌ها (P):", 0.6, 2.2, 1.0, step=0.1)

    base_eng = ISLMEngine()
    curr_eng = ISLMEngine(G=g_val, t=t_val, M=m_val, P=p_val)
    fig, eq0, eq1 = create_islm_figure(base_eng, curr_eng)

    tab_chart, tab_data, tab_pedagogy = st.tabs(["📊 دیاگرام IS-LM", "📋 تراز مالی و سرمایه‌گذاری", "🎓 تحلیل برون‌رانی"])

    with tab_chart:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("تولید تعادلی جدید (Y)", f"{eq1['Y']:.1f}", delta=f"{eq1['Y'] - eq0['Y']:+.1f}")
        c2.metric("نرخ بهره تعادلی (r)", f"{eq1['r']*100:.2f}%", delta=f"{(eq1['r'] - eq0['r'])*100:+.2f}%")
        c3.metric("سرمایه‌گذاری خصوصی (I)", f"{eq1['I']:.1f}", delta=f"{eq1['I'] - eq0['I']:+.1f}")
        c4.metric("کسری بودجه کونوها", f"{eq1['Deficit']:.1f}")
        st.plotly_chart(fig, use_container_width=True)

    with tab_data:
        st.write("تفکیک اجزای تقاضای کل کونوها:")
        # جدول بدون نیاز به Arrow
        table_islm = f"""
        <table class="custom-table">
            <thead>
                <tr>
                    <th>بخش اقتصادی</th>
                    <th>مقدار تعادلی (ریو)</th>
                </tr>
            </thead>
            <tbody>
                <tr><td>مصرف کل اهالی (C)</td><td>{eq1['C']:.1f}</td></tr>
                <tr><td>سرمایه‌گذاری قبیله‌ها (I)</td><td>{eq1['I']:.1f}</td></tr>
                <tr><td>مخارج دولتی هوکاگه (G)</td><td>{curr_eng.G:.1f}</td></tr>
                <tr><td>درآمدهای مالیاتی (T)</td><td>{eq1['T']:.1f}</td></tr>
                <tr><td>تراز بودجه دولتی (T - G)</td><td>{-eq1['Deficit']:+.1f}</td></tr>
            </tbody>
        </table>
        """
        st.markdown(table_islm, unsafe_allow_html=True)

    with tab_pedagogy:
        crowding = eq1["I"] - eq0["I"]
        if g_val > base_eng.G and crowding < 0:
            st.warning(f"💡 **تحلیل اثر برون‌رانی (Crowding-out):** افزایش مخارج دولت نرخ بهره را بالا برده و سرمایه‌گذاری بخش خصوصی را `{abs(crowding):.1f}` واحد کاهش داده است.")

# ==========================================
# فصل ۱: بازار کالا
# ==========================================
elif "۱." in topic:
    st.header("📦 تعادل بازار کالا و تقاطع کینزی")
    c0 = st.sidebar.slider("مصرف خودگردان (c₀):", 20.0, 150.0, 60.0, step=5.0)
    mpc = st.sidebar.slider("میل نهایی به مصرف (mpc):", 0.4, 0.95, 0.75, step=0.05)
    t = st.sidebar.slider("نرخ مالیات (t):", 0.05, 0.45, 0.20, step=0.05)
    g = st.sidebar.slider("مخارج دولت (G):", 40.0, 250.0, 120.0, step=10.0)
    r = st.sidebar.slider("نرخ بهره جاری (r):", 0.01, 0.15, 0.05, step=0.005, format="%.3f")

    model = GoodsMarketModel(c0=c0, mpc=mpc, t=t, G=g)
    fig, Y_eq = create_goods_market_figure(model, r_current=r)

    c1, c2, c3 = st.columns(3)
    c1.metric("ضریب فزاینده (α)", f"{model.multiplier:.2f}")
    c2.metric("تولید تعادلی بازار کالا (Y)", f"{Y_eq:.1f} ریو")
    c3.metric("مخارج خودگردان (A)", f"{model.autonomous_spending(r):.1f}")
    st.plotly_chart(fig, use_container_width=True)

# ==========================================
# فصل ۲: بازار پول
# ==========================================
elif "۲." in topic:
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
    st.plotly_chart(fig, use_container_width=True)

# ==========================================
# فصل ۵: مدل ماندل-فلمینگ (تجارت با دهکده سنگ/خاک - Iwagakure)
# ==========================================
elif "۵." in topic:
    st.header("🌐 اقتصاد باز: تجارت کونوها با دهکده سنگ و خاک (Iwagakure)")
    st.markdown("""
    در این مدل، کونوها وارد تعامل تجاری و مالی با **روستای مخفی در سنگ (کشور خاک)** شده است. 
    برابری نرخ ارز ($e$)، تقاضای واردات سنگ و مواد معدنی، و نرخ بهره بین‌المللی دهکده خاک ($r^*$) بررسی می‌شود.
    """)

    st.sidebar.subheader("پارامترهای تجاری با دهکده سنگ:")
    g_val = st.sidebar.slider("مخارج دولت کونوها (G):", 50.0, 250.0, 120.0, step=10.0)
    m_val = st.sidebar.slider("عرضه اسمی پول کونوها (M):", 200.0, 700.0, 400.0, step=25.0)
    e_val = st.sidebar.slider("نرخ ارز برابری (ریو به پول دهکده سنگ):", 0.5, 2.0, 1.0, step=0.1)
    m1_val = st.sidebar.slider("میل به واردات مواد معدنی از دهکده سنگ (m₁):", 0.05, 0.40, 0.15, step=0.05)
    rf_val = st.sidebar.slider("نرخ بهره دهکده سنگ و خاک (r*):", 0.01, 0.10, 0.05, step=0.01, format="%.2f")

    base_mf = MundellFlemingModel()
    curr_mf = MundellFlemingModel(G=g_val, M=m_val, exchange_rate=e_val, m1=m1_val, r_neoterra=rf_val)
    fig, eq0, eq1 = create_mundell_fleming_figure(base_mf, curr_mf)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("تولید ناخالص داخلی کونوها (Y)", f"{eq1['Y']:.1f}", delta=f"{eq1['Y'] - eq0['Y']:+.1f}")
    c2.metric("نرخ بهره داخلی (r)", f"{eq1['r']*100:.2f}%", delta=f"{(eq1['r'] - eq0['r'])*100:+.2f}%")
    c3.metric("خالص صادرات به دهکده سنگ (NX)", f"{eq1['NX']:+.1f}")
    c4.metric("صادرات / واردات", f"{eq1['Exports']:.0f} / {eq1['Imports']:.0f}")

    if eq1["r"] > curr_mf.r_neoterra:
        st.success("🟢 **مازاد در تراز پرداخت‌ها:** نرخ بهره کونوها بالاتر از دهکده سنگ است؛ در نتیجه سرمایه از دهکده سنگ وارد کونوها شده و ارزش پول کونوها تقویت می‌شود.")
    else:
        st.warning("🔴 **کسری در تراز پرداخت‌ها:** نرخ بهره کونوها کمتر از دهکده سنگ است؛ سرمایه‌ها به سمت دهکده سنگ خارج شده و ارزش پول کونوها تضعیف می‌شود.")

    st.plotly_chart(fig, use_container_width=True)