# ==========================================
# فصل ۵: ماندل-فلمینگ (اقتصاد باز)
# ==========================================
elif "۵." in topic:
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

    if regime_code == "fixed":
        fixed_e = st.sidebar.slider("نرخ ارز تثبیت‌شده (e):", 0.5, 2.0, 1.0, step=0.1)
    else:
        fixed_e = 1.0

    base_mf = MundellFlemingModel(regime=regime_code)
    curr_mf = MundellFlemingModel(G=g_val, M=m_val, exchange_rate=fixed_e, r_foreign=rf_val, regime=regime_code)
    fig, eq0, eq1 = create_mundell_fleming_figure(base_mf, curr_mf)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("تولید ناخالص کونوها (Y)", f"{eq1['Y']:.1f}", delta=f"{eq1['Y'] - eq0['Y']:+.1f}")
    c2.metric("نرخ بهره تعادلی (r)", f"{eq1['r']*100:.2f}%", delta=f"{(eq1['r'] - eq0['r'])*100:+.2f}%")
    
    if regime_code == "floating":
        c3.metric("نرخ ارز تعادلی شناور (e)", f"{eq1['e']:.2f}", delta=f"{eq1['e'] - eq0['e']:+.2f}")
        c4.metric("عرضه پول (ثابت)", f"{eq1['M']:.0f}")
    else:
        c3.metric("نرخ ارز تثبیت‌شده (e)", f"{eq1['e']:.2f}")
        c4.metric("عرضه پول تعدیل‌شده بانک مرکزی", f"{eq1['M']:.0f}", delta=f"{eq1['M'] - eq0['M']:+.0f}")

    st.plotly_chart(fig, use_container_width=True, config={"scrollZoom": True, "displayModeBar": True})
