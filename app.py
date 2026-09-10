# ==========================================
# فصل ۱: بازار کالا
# ==========================================
if "IS" in topic or "کالا" in topic:
    st.header("📦 " + ("Goods Market & Keynesian Cross" if lang == "en" else "بازار کالا و تقاطع کینزی"))
    
    st.sidebar.subheader("⚙️ " + ("Dynamic Settings" if lang == "en" else "تنظیمات پویایی زمانی:"))
    show_cobweb = st.sidebar.checkbox(
        "نمایش فرآیند پله‌ای تعدیل انبار (Cobweb Path)" if lang == "fa" else "Show Stepped Inventory Adjustment",
        value=True
    )

    c0 = st.sidebar.slider("c₀:" if lang == "en" else "مصرف خودگردان (c₀):", 20.0, 150.0, 60.0, step=5.0)
    mpc = st.sidebar.slider("mpc:" if lang == "en" else "میل نهایی به مصرف (mpc):", 0.4, 0.95, 0.75, step=0.05)
    t = st.sidebar.slider("t:" if lang == "en" else "نرخ مالیات (t):", 0.05, 0.45, 0.20, step=0.05)
    g = st.sidebar.slider("G:" if lang == "en" else "مخارج دولت هوکاگه (G):", 40.0, 250.0, 120.0, step=10.0)
    r = st.sidebar.slider("r:" if lang == "en" else "نرخ بهره جاری (r):", 0.01, 0.15, 0.05, step=0.005, format="%.3f")

    model = GoodsMarketModel(c0=c0, mpc=mpc, t=t, G=g)
    fig, Y_eq = create_goods_market_figure(model, r_current=r, lang=lang, show_dynamic_path=show_cobweb)

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