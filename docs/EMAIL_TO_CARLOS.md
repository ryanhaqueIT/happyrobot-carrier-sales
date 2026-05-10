# Email to Carlos Becker

**To:** c.becker@happyrobot.ai
**CC:** [your recruiter's email]
**Subject:** FDE Technical Challenge — Inbound Carrier Sales build, ahead of our meeting

---

Hi Carlos,

Ahead of our meeting, I wanted to share where I've landed on the inbound carrier sales build. The proof of concept is live: an AI voice agent that takes inbound carrier calls, runs FMCSA eligibility checks, matches carriers to available loads from a Dockerised backend I deployed on Railway, negotiates rate over up to three rounds, and books the load — all surfaced in a custom dashboard for Acme leadership.

A few links so you can have a look beforehand:

- **Dashboard:** https://happyrobot-carrier-sales-production-95a3.up.railway.app/dashboard
- **5-min walkthrough video:** https://youtu.be/kpDW6EkYlXc
- **HappyRobot workflow:** https://platform.happyrobot.ai/fderyanhaque/workflows/t2b82xfysmjd
- **Source code (public):** https://github.com/ryanhaqueIT/happyrobot-carrier-sales
- **Build description for Acme Logistics:** https://github.com/ryanhaqueIT/happyrobot-carrier-sales/blob/master/docs/BUILD_DESCRIPTION.md

If you want to test the verification flow yourself, MC `728261` will pass and let you negotiate a load. MC `728262` is a real registered carrier with no insurance on file, so the agent will reject the call — that demos the eligibility check end-to-end.

Looking forward to walking you through it.

Best,
Ryan Haque
