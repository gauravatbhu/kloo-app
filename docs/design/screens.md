# Kloo screens, v1

There is one section per approved screen. Components are specified in
`components.md`, copy rules in `copy-guide.md`, and tokens in `tokens.json`.
The copy below is final unless it is marked **[open]**.

Every screen works in dark (default) and light mode, scales to accessibility
text sizes, and keeps 44 pt / 48 dp targets. The only screen with an ad is Home.

---

## 1. Welcome

**Purpose:** say what Kloo does and set the privacy promise in one glance.

**Components:** display headline, body, privacy panel, primary button,
secondary button.

**Copy**
- Label: `KLOO`
- Headline (default): "Every reel you saved, ready when you ask."
- Headline (India, Hinglish, see copy guide): "Jo reel save ki thi, bas pooch lo."
- Body: "Save from Instagram, TikTok and YouTube. Kloo reads them on your
  phone and finds them when you ask."
- Privacy panel (teal): "Your saves never leave your phone."
- Primary: "Get started"
- Secondary: "Restore from backup"

**Accessibility:** the headline is a heading, and the label is read as "Kloo".

**[open]** There is no age gate in the designs (PRINCIPLES 14: 18+ in India,
13+ in the US). A neutral step is needed after Welcome, for example "What
year were you born?" with no default value.

## 2. How your saves get here

**Purpose:** show the two ways saves arrive, per platform, before asking for
any permission.

**Components:** title, three platform rows with status labels, privacy line,
primary button.

**Copy**
- Title: "How your saves get here"
- YouTube row:
  - status `AUTOMATIC`
  - "Share a YouTube link and Kloo does the rest."
  - **[open]** See the founder questions below. This must say exactly what
    "automatic" fetches.
- Instagram row:
  - status `DOWNLOAD, THEN SHARE`
  - "Tap Download in Instagram, then share the video to Kloo."
- TikTok row:
  - status `DOWNLOAD, THEN SHARE`
  - "Tap Save video in TikTok, then share it to Kloo."
- Privacy line: "Kloo never asks for your Instagram or TikTok password."
- Primary: "Next"

**Accessibility:** each row is one element, for example "Instagram. Download,
then share. Tap Download in Instagram, then share the video to Kloo."

## 3. Download is your new Save button

**Purpose:** the photo-access permission explainer (limited access), so
downloaded reels arrive without a share step.

**Components:** permission explainer (headline, one sentence, primary,
secondary).

**Copy**
- Headline: "Download is your new Save button"
- Sentence: "Kloo only checks for new videos you download, so your saved reels
  show up here without sharing each one."
- Primary: "Continue" (this opens the OS prompt)
- Secondary: "Not now"
- Footnote (`caption`, `text.muted`): "You can always share reels to Kloo
  yourself."

**Note:** after reading a reel, Kloo offers "Remove the video from Photos?",
with the buttons "Remove" / "Keep" (docs/architecture.md, step 6).

## 4. Home

**Purpose:** ask, browse and rediscover. This is the only screen with an ad.

**Components:** title, ask bar, chip row, resurfaced card (plum), ad card,
collection tiles, toast.

**Copy**
- Title: "Your saves"
- Ask bar placeholder: "Ask your saves…". The mic is labelled "Ask by voice".
- Chips: "Recipes", "Travel", "Fitness", "Money", "Shopping"
- Resurfaced card:
  - label `FROM 3 WEEKS AGO`
  - title: the save's title
  - line: "You saved this. Still want to try it?"
  - actions: "Open" / "Not now"
- Ad card:
  - label `AD`
  - ad content
  - "About this ad", which opens: "This ad isn't based on your saves. Ads in
    Kloo aren't personalised."
- Collections heading: "Collections". Tile count in mono, for example `24 SAVES`.
- Empty state:
  - title "Nothing saved yet"
  - body "Download a reel, then share it to Kloo. It shows up here."
  - primary "How to save"

**Placement rules:** the ad is never the first card and never sits directly
under the ask bar. Pro users see no ad.

## 5. Ask

**Purpose:** answer a question using only the user's saves, with the reels
that support the answer.

**Components:** question header, answer text (`bodyLarge`), reel result
cards, privacy footer, ask bar (follow-up), empty state.

**Copy**
- Answer footer (teal, `label` style): `ANSWERED ON THIS PHONE`
- Section above the cards: "From your saves"
- Each card has: "Open in Instagram" / "Open in TikTok" / "Open in YouTube"
- No match:
  - "I couldn't find that in your saves."
  - "Try other words, or save a reel about it."
- Older phones (result cards only, with no written answer): "Here are the
  saves that match." Don't imply a written answer.

**Rules:** no ads. Answers never use outside knowledge (PRINCIPLES 13).

**Accessibility:** when the answer is ready, announce it politely: "Answer
ready, 3 saves".

## 6. Act (grocery list)

**Purpose:** turn saves into something usable, such as a shopping list built
from saved recipes.

**Components:** title, source line, checklist rows (checkbox with a
`line.control` border), primary button, secondary button, toast.

**Copy**
- Title: "Grocery list"
- Source line: "From 3 recipes you saved". Each item can show "From
  @handle" in `caption`.
- Primary: "Copy list"
- Secondary: "Share list"
- Toast: "List copied"
- Empty: "No ingredients found in these saves."

**Rules:** no ads. Sharing is started by the user. Don't add a privacy claim
here, because the user is choosing to send content out.

**Accessibility:** each row is a checkbox with the item as its label; state
is announced as checked or unchecked.

## 7. Save sheet (over Instagram)

**Purpose:** confirm a save, get the video when only a link came through, and
show what Kloo found.

**Components:** save sheet (link-only, reading, found and error states),
findability meter, chips, buttons.

**Copy**
- Link-only state:
  - Title: "Link saved"
  - Row: "Add the video so I can read it."
    - The designs say "watch it". **Changed**, because Kloo transcribes
      audio and reads a few frames; it doesn't watch (PRINCIPLES 12).
  - Helper: "Tap Download in Instagram, then share the video here. It's read
    on your phone."
  - Primary: "Add the video"
  - Secondary: "Keep link only"
- Reading state:
  - Title: "Reading the video…"
  - Steps: "Listening", "Reading text on screen", "Filing"
  - Secondary: "Close"
- Found state:
  - Title: "What I found in the video"
  - Content: the title, category chip and up to 3 key points
  - Findability label: `FINDABILITY` with HARD / OKAY / EASY
  - Hint when Hard or Okay: "Add a note to make it easier to find."
  - Primary: "Done"
  - Ghost: "Add a note"
  - Link: "Open in Instagram"
- Error state: see copy guide errors. The save is kept as a link.

**Rules:** no ads. Clipboard is never read automatically (PRINCIPLES 5).

## 8. Help me file these

**Purpose:** batch-file unsorted saves into collections, with suggestions the
user confirms.

**Components:** title, count, suggestion rows (save plus suggested collection
chip, with "Move" and "Skip" ghost buttons), primary button, secondary button.

**Copy**
- Title: "Help me file these"
- Body: "{n} saves aren't in a collection yet. Here's where I'd put them."
- Row actions: "Move" / "Skip"
- Primary: "File all {n}"
- Secondary: "Review one by one"
- Done toast: "Filed {n} saves". Action: "Undo".

**Accessibility:** each row label is "{title}. Suggested: Recipes." Its
actions are separate buttons, and also custom actions on iOS.

## 9. Free backup and Pro

**Purpose:** offer free encrypted backup, and explain Pro honestly. Never
pressure the user.

**Components:** headline, privacy panel, two option blocks, primary button,
secondary button, and an equal "Not now" button.

**Copy**
- Headline: "Keep your saves safe"
- Free backup block:
  - Title: "Free encrypted backup"
  - Body: "Your backup is encrypted on this phone before it's uploaded. Only
    you can unlock it."
  - Detail: "You'll get a recovery key. Keep it in your password manager. We
    can't reset it for you."
- Pro block:
  - Title: "Pro"
  - Benefits: **[open]** this list needs a decision.
  - Line: "Your saves are always yours. Pro never locks what you've
    already saved."
  - Price is shown in full, with renewal terms, before the button.
- Primary: "Turn on free backup"
- Secondary: "Try Pro"
- Secondary (same size, below both): "Not now"

**Rules:** don't preselect a plan, don't use countdown timers, and don't use
a fake "most popular" badge. Never paywall existing saves (PRINCIPLES 9).

**Accessibility:** the price and renewal are read before the Pro button. The
recovery key screen allows copying the key and saving it to the password
manager. Never show the key only as an image.

---

## Open questions for the founders

1. **YouTube "Automatic":** what does Kloo fetch, and from where? Fetching
   the video or captions from YouTube may break PRINCIPLES 10 (no scraping or
   downloaders). It also sends the video ID from the phone to Google, so
   "Your saves never leave your phone" would need careful wording.
2. **Age gate:** it isn't in the designs (PRINCIPLES 14). Where does it go,
   and what does it ask?
3. **Error colour:** the designs have none. Tokens add a soft red
   (`error.*`). Is that OK, or should errors use neutral text only?
4. **Pro benefits and the free backup limit:** what is in each? The copy
   can't be finalised without this.
5. **"I" voice:** do we keep Kloo speaking as "I" in the Save sheet and Ask
   only (as proposed), or everywhere?
6. **Hinglish rollout:** does it turn on by region (India, English UI), or
   only when the user picks Hindi?
