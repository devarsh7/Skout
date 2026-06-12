# Meta App Review — Checklist for Skout

Goal: move the Skout-IG app (App ID `1280780000899542`, under Meta app
`1302397007955021`) from Development mode (testers only) to **Advanced
Access**, so any creator with an Instagram Professional account can connect.

Permissions we must get approved:

| Scope | Why we need it (use this wording in the review form) |
| --- | --- |
| `instagram_business_basic` | Read the creator's own profile (username, follower count, bio, profile photo) to pre-fill their Skout creator profile when they choose to connect their account during onboarding. |
| `instagram_business_manage_insights` | Read the creator's own media metrics (reach, views, saves, shares) to compute their true engagement rate, which Skout shows to the creator and uses for fair rate benchmarking. |

---

## 1. Prerequisites (do these before submitting)

- [ ] **Business Verification** — Advanced Access requires a verified
      business in Meta Business Manager (business.facebook.com → Security
      Centre → Start Verification). Needs a legal business name, address,
      and a document (incorporation, utility bill, etc.). This is usually
      the longest step — start it first.
- [ ] **Privacy Policy URL (real)** — the app currently points at
      `skout.com/privacy`, a domain we don't own. Must be a live page on a
      domain we control (e.g. `skoutmarketplace.com/privacy`) describing
      what Instagram data we collect (profile, media metrics), why, how
      long we keep it, and how users delete it.
- [ ] **Terms of Service URL (real)** — same as above for `/terms`.
- [ ] **App icon (1024×1024)** and category set in App Settings → Basic.
- [ ] **Production redirect URI** — a stable HTTPS callback
      (e.g. `https://api.skoutmarketplace.com/instagram/callback`)
      registered in Business Login settings. Reviewers will test against
      it; trycloudflare URLs are not acceptable for review.

## 2. Required endpoints (build before submitting)

- [ ] **Data Deletion Request callback** — Meta POSTs a signed request when
      a user asks Instagram to delete their data. We must implement
      `POST /instagram/data-deletion`: verify the `signed_request`
      (HMAC-SHA256 with the app secret), delete the creator's token, posts,
      and IG-derived fields, and respond with
      `{"url": "<status page>", "confirmation_code": "<id>"}`.
      Register the URL in Business Login settings → Data deletion request URL.
- [ ] **Deauthorize callback** (recommended) — same mechanism, fired when a
      user revokes the app in Instagram settings. Clear
      `instagram_access_token` / `instagram_token_expires_at` so we stop
      calling the API for them. Register in Business login settings.

## 3. The review submission itself

- [ ] **Screencast (the thing reviews live or die on)** — a single video
      showing the complete real flow on the production URL:
      1. Creator opens Skout onboarding and clicks "Connect Instagram".
      2. Instagram Business Login screen appears; the user logs in and
         sees/accepts the two requested permissions.
      3. Back in Skout: profile fields auto-fill (shows `instagram_business_basic`
         in use) and the engagement rate / reel stats appear (shows
         `instagram_business_manage_insights` in use).
      Narrate or caption each step. The reviewer must be able to map every
      requested permission to something visible in the product.
- [ ] **Step-by-step test instructions** for the reviewer, including a
      working test login for Skout itself (they bring their own IG account).
- [ ] **Per-permission usage descriptions** — paste the "why" column from
      the table above.
- [ ] Submit App Review → wait. Typical turnaround is a few days to a few
      weeks; rejections come with notes and you can resubmit.

## 4. After approval

- [ ] Switch the app from Development to **Live** mode.
- [ ] Verify a non-tester Instagram Professional account can connect.
- [ ] Rotate the Instagram app secret (it was used liberally during dev)
      and update the production `.env`.
- [ ] Keep the daily token-refresh job running (already implemented:
      `backend/services/instagram_maintenance.py`).

## Notes

- Standard Access (dev mode) keeps working for accounts with a role on the
  app — that's why testing with `crazyyspots` works today without review.
- If a future feature needs publishing or comment management
  (`instagram_business_content_publish`, `instagram_business_manage_comments`),
  each new permission needs its own review with its own screencast segment.
