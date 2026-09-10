# Local integrated verification

Verified commit `78a42a2` with a clean worktree before this evidence note. This checkpoint includes the local forecast refresh, uncertainty wording, ratings sorting, smaller homepage and performance responses, sharing metadata, and conditional interval audit.

- `npm test`: 114 passed, zero failed or skipped.
- `python -m unittest discover -s tests -p 'test_*.py'`: 232 passed. Negative-path tests deliberately emit acquisition-failure and rejected-argument messages; the suite ends OK.
- `npm run build`: compilation and TypeScript completed; all 319 static pages generated.
- `npm audit --omit=dev --audit-level=high`: zero reported vulnerabilities.
- Frozen research SHA256 values remain unchanged: build_data.py `1137dbd0f57c6d0b913dc10439172b5a742d77c9cac0229a0d1fb7e26064bba5`; joint_scores.py `1279680b6e2df70f1a38a9bbb76962482a026f8f6f42c8790672af6b45e0a150`; evaluate_joint_scores.py `c8f9ecdbcea8f85561cab91c716b5b1b80a02a8e3819a748e67d643e3da727e0`.

These are local integration checks, not hosted deployment verification, prospective model validation, advertising approval, or commercial readiness. Browser evidence for the individual changes is recorded separately. No public forecast receipt was created by this run. The conditional interval audit remains descriptive and does not change the model.
