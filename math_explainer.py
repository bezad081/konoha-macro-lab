import streamlit as st

def show_goods_market_math(model, r: float, Y_eq: float, c0: float, mpc: float, t: float, g: float):
    st.markdown("### ۱. محاسبه ضریب فزاینده مخارج کینزی (α)")
    st.latex(r"\alpha = \frac{1}{1 - mpc(1 - t)} = \frac{1}{1 - " + f"{mpc:.2f}" + r"(1 - " + f"{t:.2f}" + r")} = " + f"{model.multiplier:.3f}")

    st.markdown("### ۲. محاسبه کل مخارج خودگردان متأثر از نرخ بهره")
    i_curr = model.i0 - model.b * r
    st.latex(r"I = I_0 - b \cdot r = " + f"{model.i0:.1f} - ({model.b:.0f} \\times {r:.3f}) = {i_curr:.2f}")
    st.latex(r"A = c_0 + I + G = " + f"{c0:.1f} + {i_curr:.2f} + {g:.1f} = {model.autonomous_spending(r):.2f}")

    st.markdown("### ۳. برابری عرضه کل و تقاضای برنامه‌ریزی‌شده")
    st.latex(r"Y^* = \alpha \times A = " + f"{model.multiplier:.3f} \\times {model.autonomous_spending(r):.2f} = {Y_eq:.2f}")

def show_money_market_math(model, y_curr: float, m: float, p: float, k: float, h: float, r_eq: float):
    st.markdown("### ۱. مانده حقیقی عرضه پول")
    st.latex(r"\frac{M}{P} = \frac{" + f"{m:.1f}" + r"}{" + f"{p:.2f}" + r"} = " + f"{model.real_money_supply:.2f}")

    st.markdown("### ۲. برابری عرضه و تقاضای پول در نظریه ترجیح نقدینگی کینز")
    st.latex(r"\frac{M}{P} = L(Y, r) = kY - hr")
    st.latex(f"{model.real_money_supply:.2f}" + r" = (" + f"{k:.2f}" + r" \times " + f"{y_curr:.1f}" + r") - (" + f"{h:.0f}" + r" \times r)")

    st.markdown("### ۳. حل تحلیلی برای استخراج نرخ بهره تعادلی")
    st.latex(r"r^* = \frac{kY - \frac{M}{P}}{h} = \frac{(" + f"{k:.2f}" + r" \times " + f"{y_curr:.1f}" + r") - " + f"{model.real_money_supply:.2f}" + r"}{" + f"{h:.0f}" + r"} = " + f"{r_eq:.4f}" + r" \quad (" + f"{r_eq*100:.2f}" + r"\%)")

def show_islm_math(curr_eng, base_eng, eq0: dict, eq1: dict, regime_mode: str):
    alpha = curr_eng.multiplier
    A = curr_eng.autonomous_spending
    real_M = curr_eng.M / curr_eng.P

    st.markdown("### ۱. معادله جبری منحنی IS")
    st.latex(r"Y = \alpha [A - b \cdot r] \implies r = \frac{A}{b} - \frac{Y}{\alpha b}")
    st.latex(r"r = \frac{" + f"{A:.1f}" + r"}{" + f"{curr_eng.b:.0f}" + r"} - \frac{Y}{" + f"{alpha*curr_eng.b:.1f}" + r"}")

    st.markdown("### ۲. معادله جبری منحنی LM")
    if regime_mode == "classical":
        st.latex(r"\frac{M}{P} = kY \implies Y^* = \frac{M/P}{k} = \frac{" + f"{real_M:.1f}" + r"}{" + f"{curr_eng.k:.2f}" + r"} = " + f"{eq1['Y']:.2f}")
    elif regime_mode == "liquidity_trap":
        st.latex(r"r^* = r_{\text{floor}} = " + f"{curr_eng.r_floor*100:.2f}" + r"\%")
        st.latex(r"Y^* = \alpha [A - b \cdot r_{\text{floor}}] = " + f"{alpha:.2f}" + r" \times [" + f"{A:.1f}" + r" - (" + f"{curr_eng.b:.0f}" + r" \times " + f"{curr_eng.r_floor:.3f}" + r")] = " + f"{eq1['Y']:.2f}")
    else:
        st.latex(r"r = \frac{kY - M/P}{h} = \frac{" + f"{curr_eng.k:.2f}" + r"Y - " + f"{real_M:.1f}" + r"}{" + f"{curr_eng.h:.0f}" + r"}")
        st.markdown("### ۳. حل دستگاه دومعادله و دو مجهول")
        st.latex(r"Y^* = \frac{A + \frac{b}{h}\frac{M}{P}}{\frac{1}{\alpha} + \frac{bk}{h}} = " + f"{eq1['Y']:.2f}")
        st.latex(r"r^* = " + f"{eq1['r']:.4f}" + r" \quad (" + f"{eq1['r']*100:.2f}" + r"\%)")

    st.markdown("### ۴. محاسبه اثر برون‌رانی سرمایه‌گذاری (Crowding-out)")
    crowding = eq1['I'] - eq0['I']
    st.latex(r"\Delta I = -b \cdot \Delta r = -" + f"{curr_eng.b:.0f}" + r" \times (" + f"{eq1['r']:.4f}" + r" - " + f"{eq0['r']:.4f}" + r") = " + f"{crowding:+.2f}")

def show_adas_math(curr_model, a_val: float, m_val: float, pe_val: float, shock_val: float, eq1: dict):
    st.markdown("### ۱. استخراج تحلیلی منحنی تقاضای کل (AD)")
    st.latex(r"\gamma = \frac{1}{\frac{1}{\alpha} + \frac{bk}{h}} = " + f"{curr_model.gamma:.3f}")
    st.latex(r"Y^{AD}(P) = \gamma \left[ A + \frac{b}{h}\frac{M}{P} \right] = " + f"{curr_model.gamma:.3f}" + r" \left[ " + f"{a_val:.1f}" + r" + \frac{" + f"({curr_model.b:.0f} \\times {m_val:.0f})" + r"}{" + f"{curr_model.h:.0f}" + r" P} \right]")

    st.markdown("### ۲. استخراج منحنی عرضه کل کوتاه‌مدت (SRAS)")
    st.latex(r"P = P^e + \lambda(Y - Y_n) + z = " + f"{pe_val:.2f}" + r" + " + f"{curr_model.lambda_slope:.4f}" + r"(Y - " + f"{curr_model.Y_potential:.0f}" + r") + " + f"{shock_val:+.2f}")

    st.markdown("### ۳. برابری AD = SRAS و تعادل عمومی")
    st.latex(r"P^* = " + f"{eq1['P']:.3f}" + r" \implies Y^* = " + f"{eq1['Y']:.2f}")
    st.latex(r"\text{Output Gap} = \frac{Y^* - Y_n}{Y_n} \times 100 = " + f"{eq1['Output_Gap']:+.2f}" + r"\%")

def show_open_economy_math(curr_mf, rf_val: float, regime_code: str, eq1: dict):
    st.markdown("### ۱. ضریب فزاینده اقتصاد باز با نشت واردات ($m_1$)")
    st.latex(r"\alpha_{\text{open}} = \frac{1}{1 - mpc(1 - t) + m_1} = \frac{1}{1 - 0.75(0.8) + 0.15} = " + f"{curr_mf.open_multiplier:.3f}")

    st.markdown("### ۲. شرط تعادل تراز پرداخت‌ها (BP)")
    st.latex(r"r^* = r_{\text{foreign}} = " + f"{rf_val*100:.1f}" + r"\%")

    if regime_code == "floating":
        st.markdown("### ۳. حل تعادل در رژیم نرخ ارز شناور (عرضه پول برون‌زا)")
        st.latex(r"Y^* = \frac{M/P + h \cdot r^*}{k} = \frac{" + f"{curr_mf.M:.1f}" + r" + (" + f"{curr_mf.h:.0f}" + r" \times " + f"{rf_val:.3f}" + r")}{" + f"{curr_mf.k:.2f}" + r"} = " + f"{eq1['Y']:.2f}")
        st.latex(r"e^* = " + f"{eq1['e']:.3f}" + r" \implies NX^* = " + f"{eq1['NX']:+.2f}")
    else:
        st.markdown("### ۳. حل تعادل در رژیم نرخ ارز ثابت (عرضه پول درون‌زا)")
        st.latex(r"Y^* = \alpha_{\text{open}} [A(e_{\text{fixed}}) - b \cdot r^*] = " + f"{eq1['Y']:.2f}")
        st.latex(r"M_{\text{endogenous}} = P \cdot (kY^* - h \cdot r^*) = " + f"{eq1['M']:.1f}")

def show_solow_math(curr_solow, s_val: float, tech_val: float, alpha_val: float, ss1: dict):
    break_even = curr_solow.break_even_rate
    st.markdown("### ۱. شرط تعادل پایدار (Steady-State Condition)")
    st.latex(r"\Delta k = s \cdot f(k) - (\delta + n + g)k = 0 \implies s \cdot A \cdot (k^*)^\alpha = (\delta + n + g)k^*")
    st.latex(r"k^* = \left[ \frac{s \cdot A}{\delta + n + g} \right]^{\frac{1}{1 - \alpha}} = \left[ \frac{" + f"{s_val:.2f}" + r" \times " + f"{tech_val:.2f}" + r"}{" + f"{break_even:.3f}" + r"} \right]^{\frac{1}{1 - " + f"{alpha_val:.2f}" + r"}} = " + f"{ss1['k_star']:.3f}")

    st.markdown("### ۲. مقادیر تعادلی سرانه")
    st.latex(r"y^* = A \cdot (k^*)^\alpha = " + f"{ss1['y_star']:.3f}")
    st.latex(r"i^* = s \cdot y^* = " + f"{ss1['i_star']:.3f}")
    st.latex(r"c^* = y^* - i^* = " + f"{ss1['c_star']:.3f}")

    st.markdown("### ۳. بررسی انطباق بر قاعده طلایی (Golden Rule)")
    st.latex(r"MPK = f'(k_{\text{gold}}) = \delta + n + g \implies s_{\text{gold}} = \alpha = " + f"{ss1['s_gold']*100:.1f}" + r"\%")
    st.latex(r"k_{\text{gold}} = \left[ \frac{\alpha \cdot A}{\delta + n + g} \right]^{\frac{1}{1 - \alpha}} = " + f"{ss1['k_gold']:.3f}" + r" \implies c_{\text{gold}} = " + f"{ss1['c_gold']:.3f}")