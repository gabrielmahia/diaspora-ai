"""DiasporaAI — US-Kenya dual-life navigator."""
import sys, os, json, urllib.request, urllib.error
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import streamlit as st

st.set_page_config(page_title="DiasporaAI", page_icon="🌍", layout="centered")
st.markdown("""<style>
    .main > div { padding: 0.5rem 0.8rem 2rem; }
    h1 { font-size: 1.5rem !important; }
</style>""", unsafe_allow_html=True)


def _get_key():
    try:
        import streamlit as st
        k = st.secrets.get("GOOGLE_API_KEY") or st.secrets.get("GEMINI_API_KEY")
        if k: return k
    except: pass
    return os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY", "")

def _gemini(system, user, api_key, max_tokens=900):
    _BASE = "https://generativelanguage.googleapis.com"
    models = ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-flash-8b"]
    payload = {
        "system_instruction": {"parts": [{"text": system}]},
        "contents": [{"role": "user", "parts": [{"text": user}]}],
        "generationConfig": {"maxOutputTokens": max_tokens, "temperature": 0.3},
    }
    for model in models:
        url = f"{_BASE}/v1beta/models/{model}:generateContent?key={api_key}"
        req = urllib.request.Request(url, data=json.dumps(payload).encode(),
              headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=25) as r:
                data = json.loads(r.read())
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except urllib.error.HTTPError as e:
            if e.code in (400, 404): continue
            raise
        except Exception: continue
    raise RuntimeError("Gemini unavailable")


SYSTEM = """You are DiasporaAI, a knowledgeable advisor for Kenyans living in the USA navigating dual-life decisions.

You know:
REMITTANCES: IRS gift tax exclusion ($18,000/year per recipient, 2024), FBAR filing requirement ($10,000+ in foreign accounts), FATCA, wire transfer vs M-Pesa Global vs Remitly/Wise cost differences, World Bank 5% benchmark.
KENYA INVESTMENT: Non-citizens can own leasehold land (not freehold), title deed process, stamp duty (4% in cities, 2% elsewhere), NSSF portability for returnees, KRA PIN required for any transaction.
DUAL CITIZENSHIP: Kenya restored dual citizenship in 2010 Constitution. Process: apply at nearest Kenya High Commission or Embassy. US does not generally restrict dual citizenship. Oath of renunciation not required.
US TAXES: Foreign Earned Income Exclusion (FEIE up to $126,500 for 2024), Foreign Tax Credit, Social Security totalization agreement (Kenya-US not currently in force).
HEALTHCARE: NHIF can be paid from abroad (M-Pesa Global, bank transfer). Linda Mama is free. County referral hospitals for specialist care.
RETURN PLANNING: KRA PIN (online at itax.kra.go.ke), notify US Social Security if returning, HELB loan clearance, driving licence conversion, school curriculum (CBC in Kenya, different from US common core).

Rules:
- Always note: "This is general information — consult a licensed CPA, attorney, or financial advisor for your situation."
- Give specific figures where known (tax thresholds, fee percentages)
- For remittances, always mention the World Bank 5% cost benchmark
- Be warm — diaspora questions are often emotional, not just logistical"""

api_key = _get_key()

st.title("🌍 DiasporaAI")
st.caption("US-Kenya life navigator · Free · No signup")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["💸 Send Money", "🏘️ Invest in Kenya", "🛂 Citizenship", "🏥 Family Care", "💬 Ask Anything"])

with tab1:
    st.subheader("Sending Money Home")
    col1, col2 = st.columns(2)
    with col1:
        amount = st.number_input("Amount (USD):", min_value=10, value=500, step=50)
        currency = st.selectbox("From:", ["USD", "GBP", "EUR", "CAD"])
    with col2:
        kes_rate = st.number_input("KES rate:", min_value=100, value=129, step=1)
        freq = st.selectbox("How often?", ["One-time", "Monthly", "Weekly"])

    providers = {
        "Wise": {"fee_pct": 0.45, "fx_margin": 0.0},
        "Remitly": {"fee_pct": 0.00, "fx_margin": 2.1},
        "M-Pesa Global": {"fee_pct": 0.00, "fx_margin": 2.5},
        "Western Union": {"fee_pct": 2.50, "fx_margin": 3.5},
    }
    if st.button("Compare", type="primary"):
        st.markdown("**How much arrives:**")
        for name, p in providers.items():
            fee = amount * p["fee_pct"] / 100
            arrives = round((amount - fee) * kes_rate * (1 - p["fx_margin"] / 100))
            bar_pct = arrives / (amount * kes_rate)
            st.markdown(f"**{name}**: KES {arrives:,} ({bar_pct:.1%} of potential)")
        st.caption("⚠️ Gift tax: IRS allows $18,000/year per recipient before reporting. FBAR required if you hold $10,000+ in Kenyan accounts at any point during the year.")

with tab2:
    st.subheader("Investing in Kenya from the USA")
    st.markdown("""
**What you can own as a non-citizen:**
- ✅ Leasehold land (up to 99 years) — apartments, townhouses, some plots
- ✅ Company shares (through a Kenya-registered company)
- ❌ Freehold land in agricultural zones (restricted for non-citizens)

**Process to buy property:**
1. Get a Kenya KRA PIN (apply at [itax.kra.go.ke](https://itax.kra.go.ke))
2. Hire a Kenya-licensed advocate for title deed search
3. Stamp duty: 4% (urban) / 2% (rural) of property value
4. Title transfer at Land Registry (4-8 weeks)

**Watch out for:** sale agreements without title deed search, off-plan developments without escrow, land banking schemes.
""")
    st.caption("Always use a licensed advocate registered with the Law Society of Kenya.")

with tab3:
    st.subheader("Dual Citizenship")
    st.success("🇰🇪 Kenya restored dual citizenship in 2010. You do NOT have to give up US citizenship.")
    st.markdown("""
**To register/confirm Kenya citizenship from the USA:**
1. Contact the nearest **Kenya Embassy or High Commission**
2. US: Washington DC — +1 202 387 6101 · New York — +1 212 421 4741
3. Documents: birth certificate, Kenyan parent's ID/passport, your US passport
4. Fee: varies by mission — typically $50-150

**US position:** The US does not formally restrict dual citizenship. You may need to use your US passport to enter/exit the US.

**Kenya passport:** Apply at any Kenya Embassy. Allows visa-free or visa-on-arrival to 72+ countries.
""")

with tab4:
    st.subheader("Supporting Family Back Home")
    st.markdown("""
**NHIF from abroad:**
- Pay via M-Pesa Global, bank transfer, or through a family member
- NHIF paybill: **200220** (via M-Pesa)
- Covers inpatient at public hospitals for all listed dependants

**Medical emergencies:**
- Kenya National Ambulance: **0800 723 253** (free)
- Kenyatta National Hospital: **020 272 6300**
- Aga Khan Hospital Nairobi: **020 366 2000** (private, accepts foreign insurance)

**Paying hospital bills from USA:**
- Western Union / Wise to family member's M-Pesa
- Some hospitals accept international card payments directly
- Get itemised bills emailed — many hospitals will do this on request
""")

with tab5:
    st.subheader("Ask DiasporaAI anything")
    if not api_key:
        st.info("Get a free Google AI key at [aistudio.google.com](https://aistudio.google.com) to chat with DiasporaAI.")
        api_key = st.text_input("Google AI key:", type="password", placeholder="AIza...")
    else:
        st.success("✅ DiasporaAI ready")

    EXAMPLES = [
        "Do I need to file FBAR if I send $15,000 to Kenya?",
        "How do I buy land in Kenya from the US?",
        "Can I keep my US citizenship if I get a Kenya passport?",
        "My mum needs surgery — how do I pay from here?",
    ]
    st.caption("**Try:** " + " · ".join(f"*{e}*" for e in EXAMPLES[:2]))

    if "dias_msgs" not in st.session_state:
        st.session_state.dias_msgs = []

    for role, msg in st.session_state.dias_msgs[-6:]:
        with st.chat_message(role):
            st.markdown(msg)

    q = st.chat_input("Ask about your US-Kenya life...")
    if q:
        st.session_state.dias_msgs.append(("user", q))
        with st.chat_message("user"): st.markdown(q)
        with st.chat_message("assistant"):
            if not api_key:
                ans = "Please add a Google AI key above."
            else:
                with st.spinner("Thinking..."):
                    try:
                        ans = _gemini(SYSTEM, q, api_key)
                    except urllib.error.HTTPError as e:
                        ans = "API key not recognised." if e.code == 403 else "Too many requests — please wait."
                    except Exception:
                        ans = "Something went wrong. Please try again."
            st.markdown(ans)
        st.session_state.dias_msgs.append(("assistant", ans))

st.divider()
st.caption("⚠️ General information only — not legal, tax, or financial advice. Always consult a licensed professional. © 2026 Gabriel Mahia · CC BY-NC-ND 4.0")
