# Denver leave-behinds — STACK DEMO + STACK CONVERT

**New folder for FedEx:** keep these piles separate from Stack A and Stack B.

Live: https://nathanplatteruser.github.io/settleup-booth-kit/denver-leavebehinds/

Exclusively **SettleUp Collections** for Brainstorm 2026 Denver (never Marketplace, never Dell).

## DEMO vs CONVERT

| | **STACK DEMO** | **STACK CONVERT** |
|---|---|---|
| Purpose | Re-open the Nathan · Olga · Ralph Dispute Queue demo | After the demo: traffic + conversations with Nathan |
| Cover | STACK DEMO — Dispute Queue (Nathan · Olga · Ralph) | STACK CONVERT — SettleUp Collections · after the demo |
| Screenshots | Remediation + ops console (large) | Same remediation/console (recall) |
| QRs | Letter demo · GitHub repo · Pages home · walkthrough · demo screen | Calendly (PRIMARY) · SettleUp home · pricing · audit · everything · risk-scan · qr · brainstorm · demo recall · waitlist |
| Sales CTAs | **None** (no Calendly, pricing, site marketing, waitlist, book-me) | **Yes** - book 20 min / intro / product. No list prices. |
| FedEx notes | `FEDEX-DEMO-ONLY.md` | `FEDEX-CONVERT.md` |
| Full PDF | `SettleUp-DisputeQueue-Demo-ONLY.pdf` | `SettleUp-Collections-Conversion-Leavebehind.pdf` |
| 2-up PDF | `SettleUp-DisputeQueue-Demo-ONLY-2up.pdf` | `SettleUp-Collections-Conversion-Leavebehind-2up.pdf` |
| Screen page | `demo-only.html` | `convert.html` |

## Proof lines (both packs)

- Refuse over hallucinate
- Model **$1,000** vs ledger **$20,370.53**
- Run **300 / 20 / 19 / 1** · letter `LTR-300-REFUSED`
- Console `/app?booth=1` · Remediation tab

## Credits

- **Nathan Platter** — SettleUp / Platter Analytics (drives refuse-letter UI)
- **Olga Mironova** — CCMR3 (ops / capacity / exam)
- **Ralph Hall** — GVH (setup / deterministic automation)

## Screen / HTML

| Page | Live URL |
|---|---|
| Folder index (this README on Pages) | https://nathanplatteruser.github.io/settleup-booth-kit/denver-leavebehinds/ |
| Demo QR wall | https://nathanplatteruser.github.io/settleup-booth-kit/denver-leavebehinds/demo-only.html |
| Convert QR wall | https://nathanplatteruser.github.io/settleup-booth-kit/denver-leavebehinds/convert.html |
| Session walkthrough | https://nathanplatteruser.github.io/settleup-booth-kit/denver-leavebehinds/walkthrough.html |
| Public letter demo | https://nathanplatteruser.github.io/dispute-agent-demo/DEMO-OUTPUT.html |

## Absolute paths (workspace)

- `/workspace/denver-outreach/booth-kit/denver-leavebehinds/SettleUp-DisputeQueue-Demo-ONLY.pdf`
- `/workspace/denver-outreach/booth-kit/denver-leavebehinds/SettleUp-DisputeQueue-Demo-ONLY-2up.pdf`
- `/workspace/denver-outreach/booth-kit/denver-leavebehinds/SettleUp-Collections-Conversion-Leavebehind.pdf`
- `/workspace/denver-outreach/booth-kit/denver-leavebehinds/SettleUp-Collections-Conversion-Leavebehind-2up.pdf`

## Rebuild

```bash
python3 build_leavebehinds.py
```

Requires `reportlab`, `qrcode`, `Pillow`.
