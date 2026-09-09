import streamlit as st
import pandas as pd

from goods_market import GoodsMarketModel, create_goods_market_figure
from money_market import MoneyMarketModel, create_money_market_figure
from islm import ISLMEngine, create_islm_figure
from adas import ADASModel, create_adas_figure
from open_economy import MundellFlemingModel, create_mundell_fleming_figure
from solow import SolowModel, create_solow_figure

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
if "۱." in topic:
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
# فصل ۳: تعادل هم‌زمان IS-LM و حالات خاص
# ==========================================
elif "۳." in topic:
    st.header("⚖️ تعادل عمومی بازار کالا و پول (IS-LM)")

    st.sidebar.subheader("🎯 حالات خاص و تئوریک:")
    special_case = st.sidebar.selectbox(
        "انتخاب سناریوی مکاتب اقتصادی:",
        ["تعادل استاندارد نئوکینزی", "تله نقدینگی کینزی (Liquidity Trap)", "دیدگاه کلاسیک (تئوری مقداری پول)"]
    )

    if special_case == "تله نقدینگی کینزی (Liquidity Trap)":
        h_param = 50000.0  # کشش بی‌نهایت به نرخ بهره
        b_param = 600.0
    elif special_case == "دیدگاه کلاسیک (تئوری مقداری پول)":
        h_param = 100.0    # تقاضای پول مستقل از نرخ بهره
        b_param = 600.0
    else:
        h_param = 4000.0
        b_param = 600.0

    st.sidebar.subheader("تنظیم متغیرهای سیاستی:")
    g_val = st.sidebar.slider("مخارج بازسازی هوکاگه (G):", 40.0, 260.0, 120.0, step=10.0)
    t_val = st.sidebar.slider("نرخ مالیات (t):", 0.05, 0.40, 0.20, step=0.02)
    m_val = st.sidebar.slider("عرضه اسمی پول دهکده (M):", 150.0, 800.0, 400.0, step=25.0)

    base_eng = ISLMEngine()
    curr_eng = ISLMEngine(G=g_val, t=t_val, M=m_val, h=h_param, b=b_param)
    fig, eq0, eq1 = create_islm_figure(base_eng, curr_eng)

    tab_chart, tab_data, tab_pedagogy = st.tabs(["📊 دیاگرام IS-LM", "📋 کارنامه شاخص‌ها", "🎓 راهنمای تدریس و حالات خاص"])

    with tab_chart:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("تولید تعادلی (Y)", f"{eq1['Y']:.1f}", delta=f"{eq1['Y'] - eq0['Y']:+.1f}")
        c2.metric("نرخ بهره تعادلی (r)", f"{eq1['r']*100:.2f}%", delta=f"{(eq1['r'] - eq0['r'])*100:+.2f}%")
        c3.metric("سرمایه‌گذاری خصوصی (I)", f"{eq1['I']:.1f}", delta=f"{eq1['I'] - eq0['I']:+.1f}")
        c4.metric("تراز بودجه دولت (T - G)", f"{-eq1['Deficit']:+.1f}")
        st.plotly_chart(fig, use_container_width=True)

    with tab_data:
        table_islm = f"""
        <table class="custom-table">
            <thead>
                <tr><th>متغیر</th><th>مقدار تعادلی</th></tr>
            </thead>
            <tbody>
                <tr><td>مصرف کل اهالی (C)</td><td>{eq1['C']:.1f}</td></tr>
                <tr><td>سرمایه‌گذاری قبیله‌ها (I)</td><td>{eq1['I']:.1f}</td></tr>
                <tr><td>درآمدهای مالیاتی (T)</td><td>{eq1['T']:.1f}</td></tr>
                <tr><td>کسری بودجه هوکاگه</td><td>{eq1['Deficit']:.1f}</td></tr>
            </tbody>
        </table>
        """
        st.markdown(table_islm, unsafe_allow_html=True)

    with tab_pedagogy:
        if special_case == "تله نقدینگی کینزی (Liquidity Trap)":
            st.info("💡 **در تله نقدینگی:** منحنی LM تقریباً افقی است. سیاست پولی کاملاً بی‌اثر بوده و سیاست مالی بالاترین میزان کارایی (بدون برون‌رانی سرمایه‌گذاری) را داراست.")
        elif special_case == "دیدگاه کلاسیک (تئوری مقداری پول)":
            st.warning("💡 **در دیدگاه کلاسیک:** منحنی LM تقریباً عمودی است. سیاست مالی با برون‌رانی ۱۰۰٪ خنثی می‌شود و تنها سیاست پولی می‌تواند تولید را جابه‌جا کند.")

# ==========================================
# فصل ۴: مدل AD-AS و فیلیپس
# ==========================================
elif "۴." in topic:
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

    if shock_val > 0 and eq1["Y"] < base_model.Y_potential:
        st.error("⚠️ **تشخیص رکود تورمی (Stagflation):** هم‌زمانی کاهش تولید و جهش شاخص قیمت‌ها.")
    st.plotly_chart(fig, use_container_width=True)

# ==========================================
# فصل ۵: ماندل-فلمینگ (اقتصاد باز)
# ==========================================
elif "۵." in topic:
    st.header("🌐 اقتصاد باز: تجارت کونوها با دهکده سنگ و خاک (Iwagakure)")
    g_val = st.sidebar.slider("مخارج دولت کونوها (G):", 50.0, 250.0, 120.0, step=10.0)
    m_val = st.sidebar.slider("عرضه اسمی پول (M):", 200.0, 700.0, 400.0, step=25.0)
    e_val = st.sidebar.slider("نرخ ارز برابری (e):", 0.5, 2.0, 1.0, step=0.1)
    rf_val = st.sidebar.slider("نرخ بهره دهکده سنگ (r*):", 0.01, 0.10, 0.05, step=0.01, format="%.2f")

    base_mf = MundellFlemingModel()
    curr_mf = MundellFlemingModel(G=g_val, M=m_val, exchange_rate=e_val, r_foreign=rf_val)
    fig, eq0, eq1 = create_mundell_fleming_figure(base_mf, curr_mf)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("تولید ناخالص کونوها (Y)", f"{eq1['Y']:.1f}", delta=f"{eq1['Y'] - eq0['Y']:+.1f}")
    c2.metric("نرخ بهره داخلی (r)", f"{eq1['r']*100:.2f}%", delta=f"{(eq1['r'] - eq0['r'])*100:+.2f}%")
    c3.metric("خالص صادرات (NX)", f"{eq1['NX']:+.1f}")
    c4.metric("صادرات / واردات", f"{eq1['Exports']:.0f} / {eq1['Imports']:.0f}")
    st.plotly_chart(fig, use_container_width=True)

# ==========================================
# فصل ۶: مدل رشد سولو
# ==========================================
elif "۶." in topic:
    st.header("📈 مدل رشد نئوکلاسیک سولو و انباشت بلندمدت سرمایه")
    st.markdown("""
    در این مدل، وضعیت پایدار (Steady State)، انباشت سرمایه سرانه، و سطح پس‌انداز منطبق بر **قاعده طلایی (Golden Rule)** برای بیشینه‌سازی رفاه اهالی کونوها بررسی می‌شود.
    """)

    st.sidebar.subheader("پارامترهای بلندمدت اقتصاد:")
    s_val = st.sidebar.slider("نرخ پس‌انداز دهکده (s):", 0.05, 0.60, 0.25, step=0.05)
    tech_val = st.sidebar.slider("سطح بهره‌وری و فناوری کونوها (A):", 0.6, 2.5, 1.0, step=0.1)
    alpha_val = st.sidebar.slider("کشش تولید نسبت به سرمایه (α):", 0.20, 0.50, 0.35, step=0.05)
    delta_val = st.sidebar.slider("نرخ استهلاک فیزیکی (δ):", 0.02, 0.12, 0.05, step=0.01)
    pop_val = st.sidebar.slider("نرخ رشد جمعیت (n):", 0.00, 0.05, 0.02, step=0.01)

    base_solow = SolowModel()
    curr_solow = SolowModel(s=s_val, A=tech_val, alpha=alpha_val, delta=delta_val, n=pop_val)
    fig, ss0, ss1 = create_solow_figure(base_solow, curr_solow)

    tab_solow_chart, tab_solow_metrics, tab_solow_pedagogy = st.tabs(["📊 نمودار وضعیت پایدار", "📋 کارنامه شاخص‌های سرانه", "🎓 تحلیل قاعده طلایی"])

    with tab_solow_chart:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("سرمایه پایدار سرانه (k*)", f"{ss1['k_star']:.2f}", delta=f"{ss1['k_star'] - ss0['k_star']:+.2f}")
        c2.metric("تولید سرانه (y*)", f"{ss1['y_star']:.2f}", delta=f"{ss1['y_star'] - ss0['y_star']:+.2f}")
        c3.metric("مصرف سرانه (c*)", f"{ss1['c_star']:.2f}", delta=f"{ss1['c_star'] - ss0['c_star']:+.2f}")
        c4.metric("نرخ پس‌انداز قاعده طلایی", f"{ss1['s_gold']*100:.0f}%")
        st.plotly_chart(fig, use_container_width=True)

    with tab_solow_metrics:
        table_solow = f"""
        <table class="custom-table">
            <thead>
                <tr><th>شاخص سرانه در وضعیت پایدار</th><th>مقدار جاری</th><th>مقدار در قاعده طلایی</th></tr>
            </thead>
            <tbody>
                <tr><td>موجودی سرمایه سرانه (k)</td><td>{ss1['k_star']:.2f}</td><td>{ss1['k_gold']:.2f}</td></tr>
                <tr><td>تولید ناخالص سرانه (y)</td><td>{ss1['y_star']:.2f}</td><td>{curr_solow.production_per_effective_worker(ss1['k_gold']):.2f}</td></tr>
                <tr><td>مصرف پایدار سرانه (c)</td><td>{ss1['c_star']:.2f}</td><td>{ss1['c_gold']:.2f}</td></tr>
                <tr><td>نرخ پس‌انداز (s)</td><td>{curr_solow.s*100:.1f}%</td><td>{ss1['s_gold']*100:.1f}%</td></tr>
            </tbody>
        </table>
        """
        st.markdown(table_solow, unsafe_allow_html=True)

    with tab_solow_pedagogy:
        if abs(curr_solow.s - ss1["s_gold"]) < 0.02:
            st.success("🏆 **انطباق بر قاعده طلایی:** نرخ پس‌انداز انتخابی هوکاگه برابر با سهم سرمایه ($s = \\alpha$) است و مصرف پایدار نسل حاضر و آینده حداکثر شده است.")
        elif curr_solow.s > ss1["s_gold"]:
            st.warning("⚠️ **پویایی ناکارا (Dynamic Inefficiency):** نرخ پس‌انداز دهکده بیش از حد بالاست؛ با کاهش پس‌انداز می‌توان بدون آسیب به آینده، مصرف امروز اهالی را افزایش داد.")
        else:
            st.info("💡 **انباشت ناکافی سرمایه:** نرخ پس‌انداز کمتر از قاعده طلایی است. افزایش پس‌انداز در بلندمدت منجر به افزایش موجودی سرمایه و سطح مصرف پایدار خواهد شد.")