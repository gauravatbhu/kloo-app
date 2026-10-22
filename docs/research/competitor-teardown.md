# Competitor teardown: saved-reel and saved-post organisers

Owner: growth-research. All facts checked **2026-10-22** unless a different date is shown.
Method: desk research only (own website, help pages, privacy policy, App Store, Google Play, Chrome Web Store, launch pages, third-party reviews). No apps were installed.
"Not found" means we looked in the cited sources and the information was not there. It does not mean the feature is missing.
App Store pages often omit the year on dates. Where that happened we say "year not shown".

Sections 1 to 8 are **facts** with citations. Sections 9 and 10 are **our analysis and recommendations**.

---

## 1. Stasht (stasht.app), Stasht LLC, US

**Capture**
- Save one item: share a Reel or TikTok to Stasht from the share sheet. You can also stash pages from the iOS Safari extension. [organize-saved-reels](https://stasht.app/organize-saved-reels)
- Import existing saves: bulk import uses a Chrome extension (desktop) or a Safari extension (Mac/iPhone/iPad). You "log into the supported sites you want to import from, then bring those saves into Stasht". Old X bookmarks sync through Profile > Connected Accounts. [stasht.app](https://stasht.app/)
- **PRINCIPLES.md check:** the import relies on the user's logged-in browser session on Instagram or TikTok. That conflicts with principle 10 (no scraping, no logging into accounts). Kloo should not copy this.

**What it understands**
- Reads "the post's text, what's said, and what's shown on screen". It pulls out places, events, links and prices. [organize-saved-reels](https://stasht.app/organize-saved-reels)
- Frames: not named.
- Languages: "currently available in English only". [App Store](https://apps.apple.com/us/app/stasht-app-saves-that-work/id6756032175) No mention of Hindi or Hinglish.

**Where processing happens**
- Cloud. Data "may be transferred to and processed in the U.S.".
- Vendors named: AWS (hosting and media), OpenAI and Amazon Bedrock (AI and embeddings), Amazon OpenSearch, Google Maps Platform, and Google Calendar (optional). It also calls Meta, TikTok, X and YouTube APIs for metadata. No transcription vendor is named.
- Retention: "only as long as necessary". MCP logs are kept 14 days. Policy updated 2026-09-26. [privacy](https://stasht.app/privacy)
- App Store privacy label: Photos or Videos, contact info and usage are linked to the user. [App Store](https://apps.apple.com/us/app/stasht-app-saves-that-work/id6756032175)

**Answers and actions**
- Personal map of places, plus a public map of what other users saved.
- Events go to the calendar automatically. Reminders, tags, notes, search, collaborative collections, and a ChatGPT MCP connection.
- No chat-style Q&A inside the app was found.
- Sources: [Google Play](https://play.google.com/store/apps/details?id=app.stasht&hl=en_GB), [privacy](https://stasht.app/privacy)

**Platforms, pricing, traction**
- iOS, Android, desktop.
- Free ("we're early"). [organize-saved-reels](https://stasht.app/organize-saved-reels)
- iOS: 4.8 from 30 ratings. Earliest version shown is 5.2, Mar 29 (year not shown). [App Store](https://apps.apple.com/us/app/stasht-app-saves-that-work/id6756032175)
- Google Play: 1k+ downloads, 4.0 from 8 reviews, updated 2026-09-04. [Google Play](https://play.google.com/store/apps/details?id=app.stasht&hl=en_GB)
- Funding: not found.

**Top complaints**
1. "posts sent to stash do not parse and do not get added to the calendar" (Kyle Gerry, 2026-07-19). [Google Play](https://play.google.com/store/apps/details?id=app.stasht&hl=en_GB)
2. "setup instructions in-app are for iOS only" (M. R. Acuña, 2026-06-08). [Google Play](https://play.google.com/store/apps/details?id=app.stasht&hl=en_GB)
3. "I don't fully understand the purpose of collections" (sparky2708, Aug 8, year not shown). [App Store reviews](https://apps.apple.com/us/app/stasht-app-saves-that-work/id6756032175?see-all=reviews&platform=iphone)

---

## 2. Sorti (letitsorti.com), Sorti Inc., US

**Capture**
- Save one item: share a link, post, reel or screenshot from Instagram, TikTok, WhatsApp, Safari or Chrome. "Save It to Sorti" adds your latest screenshot. [letitsorti.com](https://letitsorti.com), [App Store](https://apps.apple.com/us/app/sorti-all-in-one-place/id6478935311)
- Import existing saves: not found. Siloe's comparison says Sorti is share-sheet only. [Siloe blog](https://siloe.app/blog/organize-saved-instagram-tiktok-posts/)

**What it understands**
- Identifies items in screenshots, tries to find the original link, and credits creators.
- Speech, on-screen text and frames of videos: not found. [App Store](https://apps.apple.com/us/app/sorti-all-in-one-place/id6478935311)
- Languages: the app is in English and Hebrew. No Hindi or Hinglish found.

**Where processing happens**
- Not stated. The privacy policy names no vendors (only "trusted service providers").
- Personal information is removed within 30 days of account deletion. Policy last modified January 2026. [privacy](https://letitsorti.com/privacy-policy)
- Google Play data safety: "may share" photos and videos, app activity and app info with third parties. [Google Play](https://play.google.com/store/apps/details?id=com.linoybargal.Sorti&hl=en_US)

**Answers and actions**
- Automatic categories and subcategories.
- Price comparison and price-drop alerts, map of places, lists (trips, shopping, gifts), reminders.
- Shareable cards, plus shared folders that update live.
- Q&A: not found.
- Accessibility: screen readers, larger text, reduced motion.
- Sources: [App Store](https://apps.apple.com/us/app/sorti-all-in-one-place/id6478935311), [letitsorti.com](https://letitsorti.com)

**Platforms, pricing, traction**
- iOS and Android.
- Free, with "no subscription, premium tier, or ads". [letitsorti.com](https://letitsorti.com)
- iOS: 4.7 from 45 ratings, version 1.1.41.
- Google Play: 1K+ downloads, 4.6 from 56 reviews, updated 2026-09-08.
- Affiliate partner (sovrn) linked in the site footer. [privacy](https://letitsorti.com/privacy-policy)
- Funding: not found.

**Top complaints**
1. "I really wish there were a way to turn off the automatic sorting" (sheeprus, Aug 12, year not shown). [App Store](https://apps.apple.com/us/app/sorti-all-in-one-place/id6478935311)
2. "doesn't work properly ... everything disappeared" (Kayla Auld, 2026-05-21). [Google Play](https://play.google.com/store/apps/details?id=com.linoybargal.Sorti&hl=en_US)
3. "The map is buggy right now" (nyaozi, Jun 14, year not shown). Another reviewer reports "lagging" (Ali Al-Ali, 2026-06-24). [App Store](https://apps.apple.com/us/app/sorti-all-in-one-place/id6478935311), [Google Play](https://play.google.com/store/apps/details?id=com.linoybargal.Sorti&hl=en_US)

---

## 3. Recall (getrecall.ai, now recall.it), Amsterdam

**Capture**
- Save one item: in Instagram or TikTok, tap Share > Recall (use "More" the first time), or paste the link into the app. Plus and Max users can paste up to 10 links at once. [Instagram doc](https://docs.recall.it/use-cases/content-type/social/instagram), [TikTok doc](https://docs.recall.it/use-cases/content-type/social/tiktok)
- Import existing Instagram saves: not found.
- Bulk import of up to 1,000 bookmarks is on Plus. [pricing](https://www.recall.it/pricing)

**What it understands**
- Reels are transcribed. For TikTok, it summarises spoken content "where available".
- For photo posts it reads text in each image and describes the image.
- On-screen text and frames for Reels: not found.
- Videos in a mixed photo-and-video carousel are not transcribed. [Instagram doc](https://docs.recall.it/use-cases/content-type/social/instagram)
- Languages: summaries translate into 10 languages. Hindi is not listed. [FAQ](https://www.recall.it/faq)

**Where processing happens**
- Hybrid. It calls itself "local-first"; queries and the database run locally. Backup and sync go to Google Cloud in Belgium. [FAQ](https://www.recall.it/faq)
- Policy names: Google Firebase, Google Analytics, PostHog, Sentry, and OpenAI (only via the MCP connector).
- Transcription vendor: not named. Saved content is kept until the user deletes it. Policy updated 2026-01-07. [privacy](https://www.recall.it/legal/privacy-policy)

**Answers and actions**
- Chat with your knowledge base (Plus), summaries, quizzes, Listen Mode, smart tags, augmented browsing, API and MCP.
- The Max plan lets you choose the AI model. [pricing](https://www.recall.it/pricing)
- Reminders: not found.

**Platforms, pricing, traction**
- iOS, Android, web, and Chrome, Firefox, Edge and Safari extensions. [about](https://www.recall.it/about)
- Free: 10 AI summaries a month. Plus: $10/month billed yearly. Max: $38/month billed yearly. USD only. [pricing](https://www.recall.it/pricing)
- More than 700,000 users (self-reported). Funded "within 24 hours" of a Hacker News post; amount not found. [about](https://www.recall.it/about)
- iOS: 4.4 from 117 ratings. Version 1.0 released 2023-11-15. [App Store](https://apps.apple.com/us/app/recall-summarize-save/id6445893722)
- Google Play downloads band: not found (the store page did not resolve).

**Top complaints**
1. "the 10 tokens provided are used up quickly" (enolip, 2025-08-28). [App Store](https://apps.apple.com/us/app/recall-summarize-save/id6445893722)
2. "plenty of bugs that make it tough to use continuously" (Dededevin, 2025-12-22). Same source.
3. "Sharing also has been difficult with certain apps" (Dededevin, 2025-12-22). Same source.

---

## 4. SavedThat (savedthat.app), operator based in the UAE

**Capture**
- Save one item: Android share menu > SavedThat; a Chrome extension (one click or Cmd+Shift+S); or paste a URL on the web. [savedthat.app](https://savedthat.app/)
- iPhone app: "on the way". [FAQ](https://savedthat.app/faq)
- Import: YouTube playlists and Watch Later through a Google Takeout ZIP (Pro+). No Instagram or TikTok import. [FAQ](https://savedthat.app/faq)
- **PRINCIPLES.md check:** for Instagram and TikTok, its server fetches the video from the link "to transcribe its speech and sample frames". It names ScrapeCreators, a scraping API, for "metadata, media links, or captions". [privacy](https://savedthat.app/privacy) This is server-side downloading from links, which conflicts with principle 10.

**What it understands**
- Full speech transcript, searchable by moment.
- Frames are sampled (Gemini describes them). Speech-free clips are indexed by what is on screen. [FAQ](https://savedthat.app/faq), [privacy](https://savedthat.app/privacy)
- Languages: search "in 100+ languages" via a multilingual model, including searching in one language to find speech in another. Hindi and Hinglish are not mentioned. [FAQ](https://savedthat.app/faq)

**Where processing happens**
- Cloud.
- Vendors named: Supadata (YouTube transcripts and metadata), a self-run Fly.io server (Instagram and TikTok transcription), ScrapeCreators, OpenAI (embeddings, answers, summaries), Google Gemini (frame and video descriptions), Supabase (US-West), Vercel, PostHog, Sentry, Stripe and RevenueCat.
- Video files are not stored. Transcripts are kept while the account is active and deleted within 30 days of account deletion, except transcripts other users also saved. Policy updated 2026-10-02. [privacy](https://savedthat.app/privacy)

**Answers and actions**
- AI Q&A over transcripts (unlimited on Power), summaries, jump to the matching moment, MCP for ChatGPT and Claude. [savedthat.app](https://savedthat.app/), [pricing](https://savedthat.app/pricing)
- Reminders and lists: not found.

**Platforms, pricing, traction**
- Web, Chrome, Android share. No iOS app.
- Free: first 5 videos. Pro: 300 saves a month. Power: unlimited (fair use).
- Prices: $16.99/month, $122/year, or $399 lifetime. The page also shows $9.99/month for Pro. 7-day trial with card required. [pricing](https://savedthat.app/pricing), [savedthat.app](https://savedthat.app/)
- Chrome extension: about 14 users, 5.0 from 2 ratings, updated 2026-10-17. [Chrome Web Store](https://chromewebstore.google.com/detail/abmmhcobkhdioddmejbjjplmfjegbbfh)
- Google Play listing, launch date and funding: not found.

**Top complaints:** not found (no written reviews in any source checked).

---

## 5. Siloe (siloe.app), developer David Coker Aizebioje

**Capture**
- Saves come in through import. You "log in to each platform through an in-app session", and Siloe uses that session locally to fetch saved posts from X, Reddit, TikTok, Instagram, LinkedIn and Bluesky. [siloe.app](https://siloe.app/), [blog](https://siloe.app/blog/organize-saved-instagram-tiktok-posts/)
- **PRINCIPLES.md check:** this is logging into users' Instagram and TikTok accounts. It conflicts with principle 10.

**What it understands**
- On-device OCR of text inside images and videos.
- Search covers captions, comments, "video transcripts", notes and in-media text.
- The description says it "reads bookmark media on-device" with no cloud upload required.
- Translates posts "from any language to English".
- Transcription engine and languages: not found. Hindi: not found.
- Sources: [App Store](https://apps.apple.com/us/app/siloe-save-organize/id6761395804), [blog](https://siloe.app/blog/organize-saved-instagram-tiktok-posts/)

**Where processing happens**
- Hybrid. Bookmarks and media stay on the device by default. Sync is optional and encrypted.
- On-device: Daily Picks and OCR. Cloud: Chat with Oppa, Smart Categorization, Semantic Search. [siloe.app](https://siloe.app/)
- No AI or hosting vendors named. Connected-AI request logs are kept 90 days. Platform credentials stay on the device. Policy updated 2026-10-08. [privacy](https://siloe.app/privacy)
- App Store label: email and device ID are used for "Developer's Advertising or Marketing". [App Store](https://apps.apple.com/us/app/siloe-save-organize/id6761395804)

**Answers and actions**
- "Chat with Oppa" Q&A and weekly summaries.
- Reminders (later today up to 12 years out), collections, share-as-image, download, exports (PDF/JSON/CSV), Notion and Sheets, App Lock, MCP. [siloe.app](https://siloe.app/), [pricing](https://siloe.app/pricing)

**Platforms, pricing, traction**
- iOS, Android, and Mac (running the iOS app).
- Free: unlimited bookmarks, 25 collections, 3 linked profiles, "limited" chat.
- Pro: $6.99/month, $49.99/year, or $199.99 lifetime. USD only. [pricing](https://siloe.app/pricing)
- iOS: 5.0 from 1 rating. Earliest version shown is 1.1.3, May 5 (year not shown). [App Store](https://apps.apple.com/us/app/siloe-save-organize/id6761395804)
- Google Play: 50+ downloads, updated 2026-10-12. [Google Play](https://play.google.com/store/apps/details?id=com.madebyelio.siloe&hl=en)
- Funding: not found.

**Top complaints:** not found (no written reviews).

---

## 6. Stashr (stashr.me), Australia. Assumed to be the "Stashr AI" on our list.

**Capture**
- Desktop browser extension only (Chrome, Firefox, Edge, Brave, Opera, Arc). You keep using each platform's own bookmark button and Stashr "is already listening". [stashr.me](https://stashr.me/), [docs](https://stashr.me/docs)
- Mobile apps: not found.
- Import: "One click" imports past saves. The policy says it "observes the data the platform's own app already loads". [privacy](https://stashr.me/privacy)
- **PRINCIPLES.md check:** capture reads the user's logged-in sessions on Instagram and TikTok. That is scraping-adjacent and conflicts with principle 10.

**What it understands**
- AI reads post text and images and captions images. Pro adds image and video search "by meaning".
- Transcription and on-screen text in video: not found. Languages: not found. [stashr.me](https://stashr.me/), [privacy](https://stashr.me/privacy)

**Where processing happens**
- Cloud. OpenAI handles tagging, captions and embeddings. Media is kept in cloud object storage. Polar, Resend and Cloudflare are also named.
- "No third-party advertising or analytics trackers."
- No set retention period. Policy updated 2026-09-26. [privacy](https://stashr.me/privacy)

**Answers and actions**
- Semantic search, smart collections, MCP, CLI and API.
- Chat Q&A inside the product, reminders and sharing: not found.

**Platforms, pricing, traction**
- Covers X, Reddit, Instagram, TikTok and GitHub. YouTube is "coming soon".
- 14-day trial. Hobby: $4.50/month. Pro: $7.50/month. [stashr.me](https://stashr.me/)
- Chrome extension: 4,000 users, no ratings, updated 2026-10-14. [Chrome Web Store](https://chromewebstore.google.com/detail/stashr-ai-bookmark-saver/mampphpkeibkmmdhdfenjdedpioklfmf)
- Product Hunt: not featured. [hunted.space](https://hunted.space/product/stashr)

**Top complaints:** not found.

---

## 7. TapFold (tapfold.com), developer Firdaosh Bano

**Capture**
- Save one item: share sheet > TapFold. A background pipeline then "scrapes the content, transcribes videos" using Apify for scraping. [tapfold.com](https://tapfold.com/), [maker page](https://mdsaban.com/projects/tapfold/)
- Import: not found.
- **PRINCIPLES.md check:** it scrapes from a link on the server, which conflicts with principle 10.

**What it understands**
- Transcripts, AI tags and a one-line summary.
- On-screen text and frames: not found. Languages: not found.
- Saves may come back without tags "if the source blocked the scraper" or there was "no clear audio". [support](https://tapfold.com/support)

**Where processing happens**
- Cloud. Groq and OpenAI per the maker. [maker page](https://mdsaban.com/projects/tapfold/)
- The policy names no vendors. Data is kept while the account is active, with deletion within 30 days of a request. Policy updated June 2026. [privacy](https://tapfold.com/privacy)

**Answers and actions**
- Search by meaning, collections.
- Chat, reminders and sharing: not found.

**Platforms, pricing, traction**
- iPhone live. The site says Android is on a waitlist, but the maker page and support page refer to Play Store builds, so this is unclear.
- Free: 50 saves. [support](https://tapfold.com/support)
- The App Store lists Pro at $4.99/month and $29.99/year. Support says nothing is buyable yet. [App Store](https://apps.apple.com/us/app/tapfold/id6784698559)
- No ratings. Earliest version shown is 1.1.3, Jul 16 (year not shown).

**Top complaints:** not found.

---

## 8. Ordo (ordoapp.online), developer Bhoomika Yadav, Lucknow, India

**Capture**
- Save one item: share a reel from Instagram, TikTok or YouTube Shorts. It saves "in the background without opening Ordo". [ScriptByAI, 2026-02-12](https://www.scriptbyai.com/organize-reels-shorts-ordo/), [ordoapp.online](https://ordoapp.online)
- There is also a Chrome extension. [Chrome Web Store](https://chromewebstore.google.com/detail/cmfppgcgooaojnollppbjmbbpafmfach)
- Import: not found.
- Stores "only references and metadata", not videos. [privacy](https://ordoapp.online/privacy-policy)

**What it understands**
- Categorises saves (Places, Food, Books, Film, Music, Workout, Product).
- Transcription, on-screen text and frames: not found. Languages: English only on the App Store. [App Store](https://apps.apple.com/us/app/ordo/id6757175332)

**Where processing happens**
- Servers. No vendors named. Retention is "as long as needed". Policy updated 2026-01-23. [privacy](https://ordoapp.online/privacy-policy)
- Marketed as "No account required", but the web portal and MCP need Google or Apple sign-in. [Chrome Web Store](https://chromewebstore.google.com/detail/cmfppgcgooaojnollppbjmbbpafmfach), [MCP](https://ordoapp.online/mcp)

**Answers and actions**
- "Ask Ordo" chat (added in v1.0.27, Apr 18). Shared collections.
- Read-only MCP for ChatGPT. [App Store](https://apps.apple.com/us/app/ordo/id6757175332), [MCP](https://ordoapp.online/mcp)
- Reminders: not found.

**Platforms, pricing, traction**
- iOS v1.0 released Feb 9, 2026 (copyright 2026). Android per the maker. Free.
- Product Hunt: 2026-03-24, 117 upvotes, #13 of the day. [hunted.space](https://hunted.space/product/ordo/launches/ordo-2)
- iOS: 1.0 from 1 rating. Google Play listing and downloads: not found.

**Top complaints**
1. "i try sending tiktoks to the app and it never shows that i saved anything" (ik_knight, Aug 2, year not shown). [App Store](https://apps.apple.com/us/app/ordo/id6757175332)
2. Not a user review: a reviewer saw categorisation errors, such as a restaurant food reel tagged "Place". [ScriptByAI](https://www.scriptbyai.com/organize-reels-shorts-ordo/)
3. Not found.

---

## Comparison table (facts; "?" = not found)

| | Stasht | Sorti | Recall | SavedThat | Siloe | Stashr | TapFold | Ordo |
|---|---|---|---|---|---|---|---|---|
| Save one reel by share sheet | Yes | Yes | Yes | Android only | ? (import) | No (desktop extension) | Yes | Yes |
| Imports old saves | Browser session | No | No (bookmarks only) | YouTube Takeout | In-app account login | Browser session | ? | ? |
| Conflicts with our principle 10 | Yes (import) | ? | ? | Yes (server fetch, scraper API) | Yes (login) | Yes (session capture) | Yes (Apify) | ? |
| Speech | Yes | ? | Yes | Yes | "transcripts" | ? | Yes | ? |
| On-screen text | Yes | Screenshots | Photos only | Speech-free clips | Yes, on-device | Images | ? | ? |
| Frames | ? | ? | ? | Yes (Gemini) | ? | Images | ? | ? |
| Hindi or Hinglish | No (English only) | ? | No | "100+ languages", Hindi not named | ? | ? | ? | ? |
| Processing | Cloud (OpenAI, Bedrock) | ? | Local DB plus cloud | Cloud (OpenAI, Gemini) | Device plus cloud AI | Cloud (OpenAI) | Cloud (Groq, OpenAI) | Server |
| Chat Q&A in app | ? | ? | Yes (paid) | Yes | Yes | ? | ? | Yes |
| Reminders | Yes | Yes | ? | ? | Yes | ? | ? | ? |
| Android | Yes | Yes | Yes | Share target | Yes | No | Unclear | Yes |
| Price | Free | Free | Free; $10/mo | $9.99–16.99/mo | Free; $6.99/mo | $4.50–7.50/mo | Free (50 saves) | Free |
| Traction | Play 1k+; iOS 30 ratings | Play 1K+; iOS 45 | 700k users (claimed) | about 14 extension users | Play 50+ | 4,000 extension users | 0 ratings | PH 117 upvotes |

---

## 9. Gaps Kloo can show in a demo (recommendation, backed by the facts above)

1. **Hindi and Hinglish reels.** No competitor claims Hindi or Hinglish.
   - Stasht is "English only". Recall's translation list has no Hindi. SavedThat claims "100+ languages" but names no Indic language or code-mixing. The others say nothing.
   - Demo: save a Hinglish cooking or finance reel, then ask in Hinglish ("isme kitna paneer dala tha?"). Show a grounded answer with a link to the reel.
   - Condition: only make this claim once our Hindi and Hinglish eval passes (`architecture.md` still says "evaluate larger for Hindi").
2. **Airplane-mode demo: the whole video read with nothing leaving the phone.**
   - Every competitor that reads video speech does it in the cloud: SavedThat (OpenAI, Gemini, its own server), Stasht (OpenAI, Bedrock), TapFold (Groq, OpenAI), and Recall (cloud backup, transcription vendor not named).
   - Siloe is the only one claiming on-device reading, and its chat and semantic search still go to the cloud.
   - Demo: turn on airplane mode, share a downloaded reel, then show transcript, on-screen text and answer.
   - This claim must be covered by `evals/privacy/` tests (principle 12).
3. **Speech, on-screen text and frames together, on mid-range Android.**
   - Only SavedThat claims all three, and it has no iOS app and fetches videos on its server.
   - Recall skips on-screen text for Reels. Siloe does not say it transcribes speech.
   - Sorti, Ordo and Stashr do not describe reading video at all.
   - Demo: a speech-free recipe reel with on-screen steps, and a talking-head reel. Answer from both.
4. **No account login, no scraping.**
   - Stasht, Siloe and Stashr import by riding the user's Instagram or TikTok session. SavedThat and TapFold use scraping APIs (ScrapeCreators, Apify).
   - This is mainly a trust story for the US privacy segment, but keep it factual. Do not name competitors in store copy.

## 10. Threats (what they do better than our plan)

1. **One-tap save from a link.**
   - Every share-sheet competitor saves from the link in one tap. Our plan only processes files the user downloaded (principle 10). That is extra steps, and not every reel can be downloaded.
   - This is our biggest friction risk. Onboarding has to make the "download, then share" path feel like one step, and we need to measure drop-off.
2. **Importing years of old saves.**
   - Stasht, Siloe and Stashr import existing saved tabs. Kloo starts from zero by design.
   - Users may judge every app by how full it is on day one. Mitigation (proposal): a guided "re-save your top 20" flow, and Instagram's official data download if it includes saved-post links (needs verification).
3. **Siloe already claims on-device.** It says media is read on-device with OCR, data is local by default, and sync is encrypted. Our "on-device" claim is not unique. We need to be precise: everything, including answers, stays on the device.
4. **Breadth of actions.** Stasht and Sorti have maps, calendar, price-drop alerts and shared folders. Siloe has reminders up to 12 years out, exports, and Notion integration. Several offer MCP connections to ChatGPT and Claude.
5. **Free and well funded.**
   - Sorti, Stasht and Ordo are free with no limits stated. Recall has 700k users (claimed) and a free tier.
   - All competitor pricing is in USD only. Indian rupee pricing is still open for us, but our free tier has to beat "free".
6. **An Indian maker is already in the space.** Ordo (Lucknow) is free, on both stores, and has chat. Its traction is small today.

## Decisions for the founders
- **Positioning:** lead with "Understands Hindi and Hinglish reels" plus "Nothing leaves your phone", not "on-device" alone. Siloe makes an on-device claim, so "on-device" by itself is not a differentiator.
- **Saving friction:** accept the download-first capture flow (principle 10) and invest in onboarding? Or ask architect and security-privacy to look for compliant ways to cut steps?
- **Day-one emptiness:** approve research into whether Instagram's official data export includes saved-post links, which could become a compliant import path.
