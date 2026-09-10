# Privacy preference synchronization and focus

Reproduced a real cross-tab defect: after Decline in one tab, the other tab stored `no` but still displayed the choice banner. The storage listener had conflated a declined choice with no choice.

The component now reads a three-state preference: yes, no, or undecided. Both valid choices synchronize across tabs; invalid values become undecided on initial load and subsequent updates. Unrelated storage keys do not reset the preference. Clearing storage restores the prompt. Analytics still requires explicit yes and checks that value before sending.

Manually opening settings focuses Decline, including when the banner is already open. Saving a choice without a reload returns focus to the settings button. Revoking an existing Allow choice retains the existing full-page reload behavior; focus restoration across that reload is not claimed.

`python scripts/verify_privacy_browser.py` verified ten interactions in Chromium and WebKit at 320 pixels, including cross-tab Allow and Decline, reload persistence, invalid preferences, keyboard opening/saving, and revocation. Both document widths remained 320 pixels. The JSON retains the component hash and exact checks. TypeScript checking passed. All 87 application tests passed before the final one-line already-open focus correction; the complete browser check and TypeScript check passed afterward.

An automated UX reviewer identified the already-open focus issue and missing revocation test. Both were addressed. A pointer attempt on the footer settings button while the fixed banner was open was intercepted by the banner; the already-open activation test uses keyboard input. This is not a claim that fixed overlays cannot obscure footer content. Human screen-reader, real-device, broader overlay review, live provider ingestion, and production verification remain outstanding.

No production deployment or monetization setting changed.
