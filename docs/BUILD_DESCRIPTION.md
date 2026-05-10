# Inbound Carrier Sales — Built for Acme Logistics

**Prepared by:** Ryan Haque · HappyRobot Consultant
**Date:** 9 May 2026

---

## What we built

An AI voice agent that answers your inbound carrier calls 24/7. When a carrier calls looking for a load, the agent verifies them with FMCSA, matches them to your available freight, negotiates the rate within parameters you set, and books the load — without a human on the line.

It's running today, deployed on the cloud with HTTPS, and integrated into the HappyRobot platform. Every call is captured and surfaced in a custom dashboard.

---

## What changes for Acme

| Before | After |
|---|---|
| One rep, one call. Peak hours = hold queues, dropped calls. | Every call answered instantly, in parallel. |
| FMCSA checks skipped under pressure. | Every carrier verified the same way, every time. |
| Margins drift between reps. | Negotiation stays inside your rate ceiling, automatically. |
| Reporting takes weeks. | Real-time dashboard. Every call captured, classified, searchable. |

---

## How a call goes

1. **Carrier calls** → agent answers as Acme Logistics.
2. **MC verification** → agent asks for the MC number, runs it through FMCSA. If the carrier isn't authorised or has no insurance on file, the agent politely ends the call.
3. **Load match** → agent asks the lane and trailer type, searches your loads, pitches the best match with full details (origin, destination, pickup/delivery, weight, commodity, miles, rate).
4. **Negotiation** → if the carrier counters, the agent negotiates up to 3 rounds, never going above your 10% ceiling.
5. **Booking** → if a price is agreed, the agent confirms and hands off to a human rep.
6. **Captured** → outcome is classified (booked / declined / not_qualified / no_match / transferred / dropped), key data is extracted (rate, sentiment, rounds), and everything appears on the dashboard within seconds.

---

## The dashboard

A single page Acme leadership opens to answer "how are we doing today?"

- **Volume** — total calls, by time range
- **Booking rate** — % of calls that turned into bookings
- **Pricing** — average agreed rate, margin vs. listed
- **Negotiation** — average rounds per call
- **Sentiment** — positive / neutral / negative breakdown
- **Outcomes** — donut chart of where calls landed
- **Drill-down** — click any call to see the full transcript and extracted data
- **Loads** — every load you're trying to cover, with status and call counts
- **Carriers** — every unique carrier the agent has spoken to, deduplicated by MC

Auto-refreshes every 30 seconds. Works on desktop and mobile. Light and dark themes.

---

## Why you can trust it

- **HTTPS** on every endpoint
- **API key authentication** so only your systems can talk to ours
- **FMCSA-backed verification** — the same federal source brokers are required to check before tendering freight
- **Containerised and reproducible** — full deployment instructions in the repo, can be redeployed in 10 minutes
- **Open code** — public repository, full commit history, automated tests covering every endpoint
- **Persistent storage** — every call recorded survives every deploy

---

## What's next (suggested phase 2)

- **Real warm transfer** to a sales rep with carrier context pre-populated
- **Live market rate intelligence** (DAT / Truckstop) so the agent can reference current spot rates during negotiation
- **Repeat carrier recognition** — recognise the carrier on call two, surface their last successful lane
- **TMS push** — booked loads flow directly into Transport Pro / McLeod, no manual re-entry

---

## Try it

| | |
|---|---|
| **Dashboard** | https://happyrobot-carrier-sales-production-95a3.up.railway.app/dashboard |
| **5-min walkthrough video** | https://youtu.be/kpDW6EkYlXc |
| **HappyRobot workflow** | https://platform.happyrobot.ai/fderyanhaque/workflows/t2b82xfysmjd |
| **Source code** | https://github.com/ryanhaqueIT/happyrobot-carrier-sales |

**Test it yourself:**
- MC `728261` → passes verification, lets you negotiate a load
- MC `728262` → real registered carrier, but FMCSA shows no insurance — agent politely rejects

API key for the dashboard: `acme-carrier-sales-2026`
