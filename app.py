import os
import streamlit as st
from dotenv import load_dotenv
from cefe_app.db import init_db, list_opportunities, add_opportunity, update_opportunity, delete_opportunity
from cefe_app.ai import analyze_opportunity, draft_application_brief
from cefe_app.discovery import scan_rss_sources

load_dotenv()
st.set_page_config(page_title="CEFE Opportunity Intelligence", page_icon="🌍", layout="wide")
init_db()

st.title("🌍 CEFE Opportunity Intelligence")
st.caption("Cloud-ready MVP • Discover, assess, and prepare opportunities for CEFE Strategy & Advisory")

with st.sidebar:
    st.header("Workspace")
    page = st.radio("Navigate", ["Dashboard", "Add opportunity", "AI assessment", "Source discovery", "Settings & next steps"])
    st.divider()
    st.caption("Prototype mode: AI features require an OPENAI_API_KEY. Automatic tender submission is intentionally not enabled.")

items = list_opportunities()
total = len(items)
open_items = sum(1 for x in items if x["status"] not in ("Rejected", "Closed", "Won", "Lost"))
urgent = sum(1 for x in items if x.get("deadline_days") is not None and 0 <= x["deadline_days"] <= 7)
high_fit = sum(1 for x in items if (x.get("fit_score") or 0) >= 75)

if page == "Dashboard":
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Opportunities tracked", total)
    c2.metric("Active pipeline", open_items)
    c3.metric("Deadlines within 7 days", urgent)
    c4.metric("High-fit opportunities", high_fit)
    st.subheader("Opportunity pipeline")
    if items:
        st.dataframe(items, use_container_width=True, hide_index=True)
        st.download_button("Export opportunities as CSV", data=_csv_bytes(items), file_name="cefe_opportunities.csv", mime="text/csv")
    else:
        st.info("No opportunities yet. Add one manually or scan configured RSS feeds.")
    st.markdown("#### Recommended first workflow")
    st.markdown("1. Add or discover a real opportunity.  2. Run an AI assessment.  3. Verify eligibility against the official tender documents.  4. Prepare a draft application brief.")

elif page == "Add opportunity":
    st.subheader("Register an opportunity")
    with st.form("add_opp"):
        title = st.text_input("Opportunity title *")
        organization = st.text_input("Procuring organization")
        country = st.text_input("Country / region")
        sector = st.selectbox("Primary sector", ["Entrepreneurship & MSMEs", "Financial inclusion", "Market systems development", "Livelihoods & economic empowerment", "Fisheries & agribusiness", "Organizational development", "Training & capacity building", "Research & evaluation", "Other"])
        opp_type = st.selectbox("Opportunity type", ["Tender / RFP", "Expression of Interest", "Consultancy", "Grant / Call for Proposals", "Framework agreement", "Subcontracting", "Other"])
        deadline = st.date_input("Deadline (leave today's date if unknown)")
        url = st.text_input("Official source URL")
        summary = st.text_area("Summary / requirements")
        submitted = st.form_submit_button("Save opportunity")
        if submitted:
            if not title.strip():
                st.error("Please provide an opportunity title.")
            else:
                add_opportunity(title, organization, country, sector, opp_type, str(deadline), url, summary)
                st.success("Opportunity saved.")
                st.rerun()

elif page == "AI assessment":
    st.subheader("Assess and prepare an opportunity")
    if not items:
        st.info("Add an opportunity first.")
    else:
        labels = {f'{x["id"]} — {x["title"]}': x for x in items}
        selected_label = st.selectbox("Choose opportunity", list(labels.keys()))
        selected = labels[selected_label]
        st.write(f"**Source:** {selected.get('source_url') or 'Not provided'}")
        if st.button("Assess fit with OpenAI", type="primary"):
            with st.spinner("Assessing opportunity..."):
                result = analyze_opportunity(selected)
            if result.get("error"):
                st.error(result["error"])
            else:
                update_opportunity(selected["id"], fit_score=result.get("fit_score"), status="Assessed", ai_assessment=json.dumps(result, ensure_ascii=False))
                st.session_state["assessment_result"] = result
                st.session_state["assessment_opp_id"] = selected["id"]
        result = st.session_state.get("assessment_result")
        if result and st.session_state.get("assessment_opp_id") == selected["id"]:
            st.metric("Indicative fit score", f'{result.get("fit_score", "—")}/100')
            st.markdown("**Recommendation**")
            st.write(result.get("recommendation", ""))
            st.markdown("**Eligibility checks**")
            st.write(result.get("eligibility_checks", []))
            st.markdown("**Missing information / risks**")
            st.write(result.get("gaps_and_risks", []))
            st.markdown("**Suggested next steps**")
            st.write(result.get("next_steps", []))
            if st.button("Draft application brief"):
                with st.spinner("Drafting a first brief..."):
                    brief = draft_application_brief(selected, result)
                if brief.get("error"):
                    st.error(brief["error"])
                else:
                    st.session_state["application_brief"] = brief.get("brief", "")
            if st.session_state.get("application_brief"):
                st.text_area("Draft application brief — verify every claim before use", st.session_state["application_brief"], height=360)
                st.download_button("Download brief (.txt)", st.session_state["application_brief"], file_name="cefe_application_brief.txt")

elif page == "Source discovery":
    st.subheader("Discover opportunities from RSS feeds")
    st.write("Enter public RSS/Atom feed URLs from official procurement and funding sources. The system stores feed items as leads; official eligibility and deadlines must still be verified.")
    default_sources = os.getenv("RSS_FEEDS", "")
    feed_text = st.text_area("One feed URL per line", value=default_sources, height=140)
    if st.button("Scan feeds", type="primary"):
        urls = [u.strip() for u in feed_text.splitlines() if u.strip()]
        if not urls:
            st.warning("Add at least one RSS/Atom feed URL.")
        else:
            with st.spinner("Scanning feeds..."):
                found, errors = scan_rss_sources(urls)
            st.success(f"Scan complete. Added {found} new item(s).")
            if errors:
                st.warning("Some feeds could not be read:")
                for err in errors:
                    st.write(f"- {err}")
            st.rerun()
    st.caption("Next development milestone: add more official sources, source-specific connectors, deduplication, and scheduled cloud scans.")

elif page == "Settings & next steps":
    st.subheader("Configuration status")
    st.write("OpenAI API key:", "Configured" if os.getenv("OPENAI_API_KEY") else "Not configured")
    st.write("Database:", "PostgreSQL" if os.getenv("DATABASE_URL", "").startswith(("postgres://", "postgresql://")) else "Local SQLite fallback (development only)")
    st.markdown("""
**Development roadmap**
1. Configure OpenAI API credentials as a cloud secret.
2. Deploy the app and connect PostgreSQL.
3. Expand official-source discovery and scheduled scans.
4. Build document parsing and verified CEFE knowledge base.
5. Add proposal and financial-budget generation with compliance checks.
6. Add authorized submission integrations one portal at a time.

**Safety by design:** This version does not submit bids, sign declarations, or make financial commitments. Keep API keys and portal passwords out of source code.
""")

def _csv_bytes(rows):
    import csv, io
    if not rows:
        return b""
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue().encode("utf-8")
