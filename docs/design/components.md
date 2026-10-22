# Kloo components, v1

Token names refer to `docs/design/tokens.json`. Every spec works in both
themes, because each colour is a role (for example `text.muted`), not a hex value.

## Rules for every component

- **Touch targets:** at least 44 x 44 pt on iOS and 48 x 48 dp on Android. If
  something looks smaller (a chip or an icon button), extend its hit area
  with invisible padding.
- **Real controls:** use native buttons, toggles and text fields (`Button`,
  `TextField`, Compose `Button`, `OutlinedTextField`). Don't use tappable
  `Text` or `View`/`Box` elements.
- **Text scaling:** sizes follow Dynamic Type and font scale. Heights are
  minimums, never fixed values. At accessibility sizes, side-by-side buttons
  stack vertically and keep the same order.
- **Focus:** a 2 pt `focus.ring` outline, offset 2 pt, follows the
  component's radius. It shows for keyboard, switch control and Android
  D-pad focus. Never remove it.
- **Pressed state:** a colour change. Scale 0.98 is allowed only when
  reduced motion is off.
- **Disabled state:** the control stays visible and readable (text still
  passes 4.5:1). VoiceOver announces it as "dimmed" and TalkBack as
  "disabled". Where possible, say why it is disabled in nearby helper text.
- **No colour-only meaning:** every status, category or level also has a word
  or an icon.
- **Elevation:** none. Use surface colour steps and 1 pt lines.

---

## 1. Buttons

| | Primary | Secondary | Ghost |
|---|---|---|---|
| Use | The one main action on a screen | An equal alternative, including "Not now" on decision screens | Low-stakes inline actions ("Add a note", "See all") |
| Min height | 56 (designs allow 54–58) | 56 | 48 dp / 44 pt |
| Radius | `lg` 18 | `lg` 18 | `lg` 18 (focus ring shape) |
| Fill | `accent.fill` | `surface.3` | none |
| Border | none | 1 pt `line.strong` | none |
| Label | `button`, `accent.onFill` | `button`, `text.primary` | `button`, `accent.text` or `text.primary` |
| Width | Full width in onboarding and sheets | Same width as the primary next to it | Fits its content |

**States**

| State | Primary | Secondary | Ghost |
|---|---|---|---|
| Default | as above | as above | as above |
| Pressed | `accent.pressed` (7.99:1 with ink) | fill `surface.2`, border `line.control` | `surface.2` background behind label |
| Disabled | fill `surface.3`, label `text.faint` | fill `surface.2`, label `text.faint` | label `text.faint` |
| Focus | 2 pt `focus.ring` outside the button | same | same |
| Loading | label replaced by a spinner plus the same text read aloud ("Saving"). The button keeps its width. | same | n/a |

**Accessibility**
- Role: button. The accessibility label is the visible text. Don't add
  "button" to the label, because the OS already says it.
- Only one primary button per screen.
- **Equal-clarity rule (no dark patterns):** on any decision screen
  (permissions, backup, Pro), the decline option ("Not now") is a
  **secondary** button. It has the same height and width as the primary,
  sits directly below it, uses `text.primary`, and is never a ghost button,
  faint text, a small link or an "x". It must be visible without scrolling
  at default text size.

## 2. Chips

Filter and category chips on Home ("Recipes", "Travel"), and topic chips in
the Save sheet.

- Visual height 36, hit height 48. Radius `lg` 18, so the chip is fully
  rounded. Horizontal padding 14.
- Label: `body` at weight 600.
- **Unselected:** fill `surface.2`, 1 pt `line.subtle` border, label `text.primary`.
- **Selected:** fill is the category tint (`category.*.bg`), label is the
  category ink, and a leading check icon appears. Chips without a category
  use `accent.fill` with `accent.onFill`.
- **Pressed:** fill `surface.3`.
- **Disabled:** label `text.faint`. Rarely needed; hide the chip if it can't
  be used.
- **Focus:** ring.
- **Accessibility:** filter chips have the button role plus a selected state
  (iOS `.isSelected` trait, Compose `FilterChip` with `selected`). The label
  is the category name. Counts are included ("Recipes, 24 saves"). A chip
  row scrolls horizontally at default size and wraps onto more lines at
  accessibility sizes.

## 3. Ask bar

The text field on Home that opens Ask.

- Min height 56, radius `lg` 18, fill `surface.2`, 1 pt **`line.control`**
  border. (The designs used a subtle line, which is 1.29:1. Inputs need 3:1;
  see tokens contrastAudit.)
- Leading search icon (`icon.subtle`, decorative and hidden from
  accessibility). Placeholder in `text.muted`: "Ask your saves…"
- Trailing mic button: 44/48 hit area. Accessibility label "Ask by voice".
  It appears only if the device supports on-device speech-to-text.
- **Focused:** border becomes 2 pt `focus.ring`, and the keyboard opens.
- **Typing:** a trailing "Clear" icon button appears (label "Clear question").
- **Disabled** (the model is still downloading): placeholder "Getting ready
  to answer…" in `text.faint`. The field can still be focused, so the
  helper text below can be read.
- **Accessibility:** search field role, label "Ask your saves". Pressing
  Return submits. The placeholder is not the label.

## 4. Reel result card

Used in Ask answers, collections and search.

- Fill `surface.1`, 1 pt `line.subtle` border, radius `xl` 20, padding 12.
- Layout: a 9:16 thumbnail (radius `xs` 8, 64 pt wide) on the left. On the
  right:
  - Source row: the platform icon and `@handle` in `label` style, `text.muted`.
  - Title: `cardTitle`, `text.primary`, up to 2 lines.
  - Why it matched: `caption`, `text.muted`, 1 line. For example "Mentions
    'paneer' at 0:42".
  - Category tag (optional): `label` style in the tint colours.
- A trailing "Open in Instagram/TikTok/YouTube" ghost link is always present
  (PRINCIPLES.md 11).
- **Pressed:** fill `surface.2`. **Focus:** ring around the whole card.
- **Accessibility:** one focus stop for the card (button role, opens
  details), plus a separate stop for "Open in Instagram". Combined label:
  "{title}. Reel from @{handle}, saved {relative date}. {why it matched}."
  The thumbnail is decorative. Thumbnails never autoplay.

## 5. Findability meter

Shown in the Save sheet after Kloo has read a video. It tells the user how
easy the save will be to find later.

- Three segments in a row, each 1/3 of the width, 6 pt tall, 4 pt gaps,
  radius 3. Filled segments use `accent.fill`; empty ones use `surface.3`
  with a 1 pt `line.control` edge.
- The word is always shown next to the bar in `label` style: **HARD**
  (1 segment), **OKAY** (2) or **EASY** (3). The colour never changes by
  level (no red/green), so the word carries the meaning.
- When the level is Hard or Okay, a ghost button underneath gives one
  fix: "Add a note" or "Add the video".
- Motion: segments fill over `slow`. With reduced motion, the final state
  shows at once.
- **Accessibility:** a single element. On iOS it is a static text element
  with the value; on Android, `progressBarRangeInfo` set to 1–3 plus a
  content description. Label: "Findability: Okay. Adding a note makes it
  easier to find." Don't use an adjustable role, because users can't change it.
- **Honesty:** the level must come from a real measure (for example: has a
  transcript, has on-screen text, has a title and topic), defined by
  ml-engineer and tested. It must not be decoration.

## 6. Status labels

Used on "How your saves get here", for example "Automatic" and "Download,
then share".

- Height 24 (not interactive, so no touch-target rule applies). Radius `sm`
  12, horizontal padding 10. Text in `label` style (DM Mono 11, uppercase,
  0.12em).
- **AUTOMATIC:** fill `privacy.bg`, border `privacy.border`, ink `privacy.ink`.
- **DOWNLOAD, THEN SHARE:** fill `surface.3`, border `line.strong`, ink
  `text.primary`. It is a neutral instruction, not a warning.
- **Accessibility:** read as part of the row: "YouTube. Automatic." or
  "Instagram. Download, then share." The accessibility text is in sentence
  case.

## 7. Save sheet

A bottom sheet. It appears over Instagram/TikTok/YouTube from the Share
Extension or share target, and inside the app.

- Fill `surface.3`, top radius `3xl` 28, 1 pt `line.strong` top edge,
  `scrim` behind. A grabber (36 x 4, `line.strong`) is decorative; the sheet
  also has a "Close" button (44/48) so swiping is never the only way to
  dismiss it.
- Padding 20. It sizes to its content and becomes full height at
  accessibility text sizes, with scrolling.
- **States**
  1. **Link only:** the link was shared without the video. The title is
     "Link saved". There is an explainer row and an "Add the video" primary
     button. The secondary button is "Keep link only".
  2. **Reading:** a determinate progress bar if available, otherwise stepped
     text ("Listening…", "Reading text on screen…"). The user can close the
     sheet; the work continues in the app. The secondary button is "Close".
  3. **Found:** the title is "What I found in the video". It shows the title,
     category chip, up to 3 key points, the findability meter, and the
     "Open in Instagram" link. Primary button "Done", ghost button "Add a note".
  4. **Error:** see the copy guide error messages. The secondary button is
     "Close", and the save is kept as a link.
- **Accessibility:** on open, focus moves to the sheet title. The sheet is
  modal (`accessibilityViewIsModal` / Compose `ModalBottomSheet`). The
  Escape / two-finger scrub gesture closes it. State changes are announced
  politely ("Done reading. Findability: Easy.").
- **No ads, ever** (PRINCIPLES.md 7).

## 8. Ad card

The only ad surface in the app. It appears once, on Home only.

- Fill `surface.1`, 1 pt `line.strong` border, radius `xl` 20, padding 16.
- **"AD"** label at top left in `label` style, `text.muted`. It is always
  visible and never truncated or hidden.
- It must not look like a save:
  - no 9:16 thumbnail
  - no platform icon or `@handle`
  - no category tint or plum resurfacing colours
  - no "saved" date
  - never placed directly under the ask bar or between a resurfaced card
    and its content
- Placement: after the resurfaced card and before Collections, or after
  Collections. It is never the first card on Home.
- A trailing "About this ad" ghost button opens a sheet: "This ad isn't
  based on your saves. Ads in Kloo aren't personalised." Pro users see no
  ad card.
- **Accessibility:** a container whose first element is announced as "Ad".
  Ad content follows. The ad's own call to action is a real button.
- **Never:** "watch an ad to unlock", ads in Ask, answers, lists, the Save
  sheet or onboarding, or the blocked categories (PRINCIPLES.md 6–8).

## 9. Toast

Short, non-blocking confirmations, such as "Saved to Recipes" or "List copied".

- Fill `surface.3`, 1 pt `line.strong`, radius `sm` 12. It sits above the
  bottom safe area and tab bar. Text is `body` in `text.primary`.
- Optional single action ("Undo"), as an accent.text ghost button with a
  48 dp hit area.
- **Duration:** 4 s without an action, 8 s with one. When VoiceOver or
  TalkBack is on, a toast with an action stays until it is dismissed.
- Motion: fades and rises 8 pt over `base`. With reduced motion it only
  fades.
- **Accessibility:** announced politely (iOS `UIAccessibility.post
  .announcement`, Android live region polite). Never use a toast for errors
  that need action; use inline errors instead.

## 10. Empty states

- Centred in the content area, with `screenGutter` padding. An optional
  simple line illustration in `icon.subtle` is decorative.
- Title in `titleSmall`, `text.primary`. One sentence of body in `text.muted`.
  At most one primary action.
- Variants (copy is in `copy-guide.md`):
  - Home with no saves
  - Collection with no saves
  - Ask with no match (PRINCIPLES.md 13: say nothing matched; never guess)
  - Act with no list items
- **Accessibility:** the title is a heading.

## 11. Permission explainer

A pre-prompt shown **before** every OS permission dialog (photos,
notifications, microphone).

- A full-screen step in onboarding, or a sheet elsewhere.
- Layout:
  - Icon at the top (decorative).
  - Title in `headline` or `titleSmall`.
  - **One sentence** of explanation in `bodyLarge`, `text.primary`.
  - Optional privacy line in a `privacy` panel (radius `2xl`), only if it
    is literally true and tested.
- Buttons, stacked:
  - Primary: "Continue". It triggers the OS dialog.
  - Secondary: "Not now". Same size, directly below.
- "Not now" skips without calling the OS prompt, so the one-time OS prompt
  is kept for later. Kloo asks again only when the user starts the related
  feature. It never nags on launch.
- If the user previously denied the permission, the primary becomes "Open
  Settings" and the sentence explains how to turn it on.
- **Accessibility:** the title is a heading, and focus starts on it. Button
  order matches the visual order.
