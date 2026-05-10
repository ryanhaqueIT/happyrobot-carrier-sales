# Inbound Carrier Sales Automation
## Build Description — Prepared for Acme Logistics

**Prepared by:** Ryan Haque
**Platform:** HappyRobot AI
**Date:** 9 May 2026
**Status:** Production-ready proof of concept

---

## Executive summary

Acme Logistics has deployed a HappyRobot voice AI agent to automate inbound carrier sales. When a carrier calls in looking for a load, the agent **verifies** them against the federal FMCSA database, **matches** them to viable freight, **negotiates** the rate over up to three rounds, and **books** the load — without a human on the line. Every call is captured, classified, and surfaced in a custom dashboard so operations and leadership have real-time visibility into agent performance.

The system is live, containerised, deployed to Railway with HTTPS, and integrated into the HappyRobot platform via tool webhooks. It is ready for pilot use and to be expanded with additional capabilities.

---

## The problem we solved

Until now, every inbound call from a carrier was answered by a human sales rep. That meant:

- **Capacity ceiling.** A rep can only handle one call at a time. Peak hours create hold queues. Calls roll to voicemail. Carriers go to competitors.
- **Inconsistent vetting.** Verifying a carrier's authority and insurance with FMCSA is slow and easy to skip when the rep is busy.
- **Variable negotiation quality.** Different reps give different rates. Margins drift.
- **Limited visibility.** Hard to answer "How are we performing?" without weeks of manual reporting.

This solution removes those bottlenecks. The AI agent answers every call instantly, verifies every carrier the same way every time, negotiates within tight rate parameters, and writes a complete audit trail to the dashboard.

---

## The solution

A two-part system:

**1. Voice agent on the HappyRobot platform.** Configured with a prompt, two tool integrations (carrier verification and load search), and post-call AI nodes that classify the outcome and extract structured data.

**2. Custom backend and dashboard.** A FastAPI service that holds Acme's loads, exposes them to the agent over HTTPS, runs FMCSA-backed eligibility checks, captures every completed call, and renders a real-time dashboard.

```
                         Carrier dials in
                              │
                              ▼
                    ┌────────────────────┐
                    │  HappyRobot        │
                    │  Voice Agent       │
                    └─┬───────────────┬──┘
                      │               │
            verify_carrier      find_available_loads
                      │               │
                      ▼               ▼
            ┌─────────────────────────────────┐
            │   Acme Logistics backend        │
            │                                 │
            │   /verify-mc  ──▶  FMCSA API    │
            │   /loads      ──▶  Loads DB     │
            │   /call-record ──▶ Calls DB     │
            │   /metrics    ──▶  Dashboard    │
            └─────────────────────────────────┘
```

---

## How it works on every call

1. **Greeting.** Agent answers as Acme Logistics within the first ring.
2. **Carrier qualification.** Agent asks for the MC number, then queries FMCSA in real time. Three checks run: active operating authority, no Unsatisfactory safety rating, and required liability insurance on file. Failed checks end the call politely with a specific reason ("our records show your liability insurance isn't on file with FMCSA"). No freight is tendered to ineligible carriers.
3. **Load matching.** Once verified, the agent asks the carrier where they're running and what trailer type, then searches the loads database for matches. The 13 spec-required fields are pitched: origin, destination, pickup and delivery datetimes, equipment type, weight, commodity, miles, dimensions, number of pieces, notes, and rate.
4. **Rate negotiation.** If the carrier counters, the agent negotiates monotonically: round one at 4% above the listed rate, round two at 7%, round three at 10% as the absolute ceiling. Each counter is higher than the last — no awkward price decreases. If three rounds pass without agreement, the agent thanks them and ends the call.
5. **Booking handoff.** When a price is agreed, the agent confirms the deal and announces a transfer to a human rep to finalise the rate confirmation.
6. **Post-call processing.** AI Classify tags the outcome (booked / declined / not_qualified / no_match / transferred / dropped). AI Extract pulls structured data: MC number, carrier name, equipment type, load ID, offered and agreed rates, negotiation rounds, and carrier sentiment. Everything is posted to Acme's backend and rendered on the dashboard within seconds.

---

## The metrics dashboard

A custom-built dashboard, not platform analytics, designed around what an operations leader needs to see in the morning:

- **Volume** — total inbound calls, broken down by time range
- **Conversion** — booking rate (% of calls that resulted in a booked load), surfaced in the hero KPI card with a 14-day sparkline trend
- **Pricing** — average agreed rate, margin vs. listed rate, automatic flagging of above-market deals
- **Negotiation efficiency** — average number of rounds per call
- **Sentiment** — positive / neutral / negative breakdown of how carriers reacted on the call, with a net sentiment score
- **Outcome distribution** — donut chart showing where calls landed (booked, declined, not qualified, etc.)
- **Drill-downs** — recent calls table with click-through to a detail drawer showing the full transcript, matched load, extracted fields, and audio playback hook
- **Loads view** — board of all available freight, status (open / covered / expired), calls received per load, lane-level analytics
- **Carriers view** — every unique carrier the agent has spoken to, deduplicated by MC number, with fleet size, FMCSA status, booking rate, and total revenue contributed
- **Issues chip** — a single number in the header that aggregates expired uncovered loads, FMCSA-flagged carriers, and dropped calls — a quick triage signal

The dashboard auto-refreshes every 30 seconds. Light and dark themes. Works on desktop and mobile.

---

## Security and deployment posture

| Concern | How we handled it |
|---|---|
| **Transport encryption** | HTTPS enforced on every endpoint via Railway's auto-provisioned Let's Encrypt certificates |
| **API authentication** | All sensitive endpoints require an `X-API-Key` header. Keys are environment variables, never in code or git history |
| **Secrets management** | FMCSA WebKey, API key, and HappyRobot credentials live in Railway environment variables. The `.env` file is gitignored |
| **Data persistence** | SQLite database on a Railway-attached volume — survives every deploy and rebuild |
| **Carrier eligibility** | Federally-compliant — uses the FMCSA QCMobile API (the same source brokers are required to check before tendering freight) |
| **Reproducibility** | Containerised with Docker. The README documents the full deploy process from scratch — Railway sign-up to live URL in under 10 minutes |
| **Source code** | Public repository with full commit history, automated test suite (16 tests covering all endpoints), and CI-ready Dockerfile |

---

## What this means for Acme

- **24/7 coverage.** Every inbound call is answered immediately, no matter the hour. No more rolling to voicemail at 2 AM when a driver in another timezone is looking for a load.
- **Consistent vetting.** Every carrier is checked against FMCSA the same way. Ineligible carriers are turned away politely without consuming rep time.
- **Margin discipline.** Negotiations happen within parameters that ops sets. The agent will never quietly approve a $3,000 deal on a $1,650 load because someone wore them down.
- **Total auditability.** Every call has a transcript, a recording hook, a classified outcome, and structured data — searchable and exportable.
- **Capacity to grow.** The agent runs many concurrent calls. Adding more carriers doesn't require hiring more reps.

---

## What's next

Recommended phase-2 capabilities, in priority order:

1. **Booking confirmation handoff.** Replace the mocked transfer with a real warm transfer to the on-duty sales rep, with carrier context (MC, load, agreed rate) pushed via SIP UUI headers so the rep doesn't have to re-ask.
2. **Rate intelligence.** Integrate DAT or Truckstop rate data so the agent can reference real-time market rates ("DAT is showing $2.45 on this lane — I'm at $2.50") and adjust negotiation parameters dynamically.
3. **Memory / contact intelligence.** Recognise repeat carriers, surface their last successful lane, greet them by company name on the second call.
4. **Outbound workflow.** When new loads are posted, automatically dial the carriers most likely to take them based on historical lane preferences.
5. **Multi-channel.** Add SMS and email versions of the same agent so carriers can text-in a load reference and get a rate quote without picking up the phone.
6. **TMS integration.** Push booked loads directly into Acme's TMS (Transport Pro, McLeod, etc.) so reps don't have to manually re-enter the rate confirmation.

---

## Live access

| Resource | URL |
|---|---|
| Dashboard | https://happyrobot-carrier-sales-production-95a3.up.railway.app/dashboard |
| API base | https://happyrobot-carrier-sales-production-95a3.up.railway.app |
| Code repository | https://github.com/ryanhaqueIT/happyrobot-carrier-sales |
| HappyRobot workflow | https://platform.happyrobot.ai/fderyanhaque/workflows/t2b82xfysmjd |
| 5-min walkthrough video | _(YouTube link)_ |

API key for evaluation: `acme-carrier-sales-2026`

To verify the FMCSA eligibility flow:
- MC `728261` — passes verification (KING SIZED TRUCKING)
- MC `728262` — fails for missing insurance (DIANE BARBER, registered carrier but FMCSA flags her as uninsured)

---

## Appendix — built capabilities checklist

| Spec requirement | Built |
|---|---|
| Inbound agent on HappyRobot platform | ✅ |
| Loads API with all 13 fields | ✅ |
| MC number verification via FMCSA | ✅ |
| Search loads and pitch details | ✅ |
| Ask if interested in accepting | ✅ |
| Up to 3 rounds of negotiation | ✅ |
| Mock transfer when price agreed | ✅ |
| Extract relevant call data | ✅ |
| Classify call outcome | ✅ |
| Classify carrier sentiment | ✅ |
| Custom metrics dashboard | ✅ |
| Containerised with Docker | ✅ |
| HTTPS | ✅ |
| API key authentication | ✅ |
| Cloud deployment with reproducible setup | ✅ |
| Web call trigger (no phone number purchased) | ✅ |
