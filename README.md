# CEFE Opportunity Intelligence — MVP

A cloud-ready starter application for CEFE Strategy & Advisory to register, discover, assess, and prepare for international tenders, consultancies, EOIs, and grants.

## Included now
- Streamlit dashboard and opportunity register
- SQLite for local testing; PostgreSQL via `DATABASE_URL` for cloud deployment
- RSS/Atom feed scanning (source URLs must be supplied)
- OpenAI Responses API assessment and application-planning brief
- CSV export
- Render deployment blueprint

## Not included yet
- Broad, verified catalogue of procurement sources
- Scheduled cloud discovery jobs
- Tender-document ingestion and full compliance checking
- CEFE verified-document knowledge base
- Portal-specific automated submission
- Automated legal declarations, signing, or financial commitments

## Run locally
1. Install Python 3.11 or 3.12.
2. Unzip the project and open a terminal in the project folder.
3. Create a virtual environment:
   - Windows PowerShell: `py -m venv .venv`
   - Activate: `.venv\\Scripts\\Activate.ps1`
4. Install packages: `pip install -r requirements.txt`
5. Copy `.env.example` to `.env` and add your OpenAI API key only if you want AI features.
6. Run: `streamlit run app.py`

Never commit `.env` or publish an API key.

## Deploy on Render
1. Push this folder to a private GitHub repository.
2. In Render, create a new Blueprint and connect that repository.
3. Review the proposed web service and PostgreSQL database before creating them.
4. Set `OPENAI_API_KEY` as a secret environment variable in Render. Do not put it in GitHub.
5. Deploy and test adding an opportunity, then test AI assessment.
6. Check plan pricing and database limits before selecting a production plan.

## AI model
The default `OPENAI_MODEL` is a configurable placeholder. Confirm the exact model name available in your OpenAI API project and set it in the environment before testing. API use is billed separately from ChatGPT.

## Security and operating rules
- Do not store tender portal passwords in the database.
- Verify every opportunity at its official source before applying.
- Treat AI scores as triage, not proof of eligibility.
- Keep human approval for legal declarations, signatures, pricing exceptions, and contractual commitments.
- Automated submission must be implemented separately for each portal and only where permitted.

## Next milestones
1. Confirm CEFE's verified profile and service priorities.
2. Add high-value official source connectors and scheduled discovery.
3. Parse official tender documents and create evidence-backed eligibility checks.
4. Build proposal generation from CEFE's approved knowledge base.
5. Add portal-specific submission adapters with audit logs and approval rules.
