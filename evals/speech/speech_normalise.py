"""Text normalisation for Kloo's speech eval (English, Hindi, Hinglish).

Two levels, both deterministic and stdlib-only:

strict_normalise(text)
    Unicode NFC, drop zero-width characters, lowercase, Devanagari digits to
    ASCII, fold nukta and chandrabindu, delete apostrophes, "1,000" -> "1000",
    "%" -> "percent", "₹500" / "Rs. 500" -> "500 rupees", turn all other
    punctuation and symbols into spaces, drop bracketed non-speech tags such as
    "[Music]" or "(संगीत)". Script is preserved. Used for English scoring and as
    the "strict" Hindi diagnostic.

hinglish_normalise(text, lexicon=None, translit=None)
    strict_normalise, then every Devanagari token is converted to Latin
    (lexicon lookup first, then the transliteration hook, default: the built-in
    rule-based romaniser), then every token is reduced to a Hinglish spelling
    skeleton so that common romanisation variants compare equal
    ("accha" / "acha" / "अच्छा", "mein" / "me" / "में", "zyada" / "ज़्यादा").
    Used for the official Hindi/Hinglish WER, so engines are not punished for
    choosing Devanagari or Roman script.

The skeleton is deliberately lenient (it forgives vowel-length and schwa
differences). That is the right trade for Kloo, where transcripts feed search
and filing, but it means our numbers are NOT comparable with published FLEURS
figures. Always report the strict number next to it.

Version string NORMALISER_VERSION is written into every result line; bump it
whenever behaviour changes, because scores across versions are not comparable.
"""
import re
import unicodedata

NORMALISER_VERSION = "kloo-speech-norm-1"
PHONETIC_VERSION = "kloo-speech-phon-1"

_ZERO_WIDTH = dict.fromkeys(map(ord, "​‌‍⁠﻿­"), None)
_DEVANAGARI_DIGITS = {ord(c): str(i) for i, c in enumerate("०१२३४५६७८९")}
_APOSTROPHES = dict.fromkeys(map(ord, "'‘’ʼ`"), None)
# Bracketed non-speech tags that engines emit: [Music], (applause), [BLANK_AUDIO], [संगीत]
_DIGIT_COMMA = re.compile(r"(?<=\d),(?=\d)")
_RUPEE = re.compile(r"(?:₹|\brs\.?)\s*(\d+(?:\.\d+)?)")
_BRACKETED = re.compile(r"\[[^\]]*\]|\([^)]*\)|\{[^}]*\}|<[^>]*>|♪[^♪]*♪")

# Nukta letters folded to their base letter. ड़ and ढ़ are distinct Hindi
# letters (not loan sounds), so they are kept.
_NUKTA_FOLD = {
    "क़": "क", "ख़": "ख", "ग़": "ग", "ज़": "ज", "फ़": "फ", "य़": "य",
}
_NUKTA = "़"
_KEEP_NUKTA_BASES = {"ड", "ढ"}


def _fold_nukta(text):
    # Precomposed forms first (NFC keeps क़ etc. decomposed, but be safe).
    for k, v in _NUKTA_FOLD.items():
        text = text.replace(k, v)
    out = []
    for ch in text:
        if ch == _NUKTA and out and out[-1] not in _KEEP_NUKTA_BASES:
            continue
        out.append(ch)
    return "".join(out)


def strict_normalise(text):
    """Script-preserving normalisation. Returns a space-joined string."""
    text = unicodedata.normalize("NFC", text or "")
    text = text.translate(_ZERO_WIDTH)
    text = _BRACKETED.sub(" ", text)
    text = text.lower()
    text = text.translate(_DEVANAGARI_DIGITS)
    text = _fold_nukta(unicodedata.normalize("NFD", text))
    text = text.replace("ँ", "ं")  # chandrabindu -> anusvara
    text = unicodedata.normalize("NFC", text)
    text = text.translate(_APOSTROPHES)
    text = _DIGIT_COMMA.sub("", text)                 # 1,000 / 1,00,000 -> 1000 / 100000
    text = _RUPEE.sub(r" \1 rupees ", text)           # ₹500 -> 500 rupees (as spoken)
    text = text.replace("%", " percent ")
    out = []
    for ch in text:
        cat = unicodedata.category(ch)
        out.append(ch if cat[0] in ("L", "N", "M") else " ")
    return " ".join("".join(out).split())


# ---------------------------------------------------------------------------
# Devanagari -> Latin romaniser (Hindi conventions, Hinglish-friendly spelling)
# ---------------------------------------------------------------------------
_CONSONANTS = {
    "क": "k", "ख": "kh", "ग": "g", "घ": "gh", "ङ": "n",
    "च": "ch", "छ": "chh", "ज": "j", "झ": "jh", "ञ": "n",
    "ट": "t", "ठ": "th", "ड": "d", "ढ": "dh", "ण": "n",
    "त": "t", "थ": "th", "द": "d", "ध": "dh", "न": "n",
    "प": "p", "फ": "ph", "ब": "b", "भ": "bh", "म": "m",
    "य": "y", "र": "r", "ल": "l", "ळ": "l", "व": "v",
    "श": "sh", "ष": "sh", "स": "s", "ह": "h",
}
# Consonant + nukta (after the nukta fold only ड़ / ढ़ remain, but keep all).
_NUKTA_CONSONANTS = {"ड": "d", "ढ": "dh", "क": "q", "ख": "kh", "ग": "g",
                     "ज": "z", "फ": "f", "य": "y"}
_INDEPENDENT_VOWELS = {
    "अ": "a", "आ": "aa", "इ": "i", "ई": "ee", "उ": "u", "ऊ": "oo",
    "ऋ": "ri", "ए": "e", "ऐ": "ai", "ओ": "o", "औ": "au", "ऑ": "o", "ऍ": "e",
}
_MATRAS = {
    "ा": "aa", "ि": "i", "ी": "ee", "ु": "u", "ू": "oo",
    "ृ": "ri", "े": "e", "ै": "ai", "ो": "o", "ौ": "au",
    "ॉ": "o", "ॅ": "e",
}
_VIRAMA = "्"
_ANUSVARA = "ं"
_CHANDRABINDU = "ँ"
_VISARGA = "ः"


def is_devanagari(token):
    return any("ऀ" <= ch <= "ॿ" for ch in token)


def romanise_devanagari(word):
    """Rule-based Hindi romanisation with simple schwa deletion.

    Not a linguistic transliterator: it aims to land close to how people type
    Hinglish, so that after skeleton folding it matches romanised references.
    Non-Devanagari characters pass through unchanged.
    """
    word = unicodedata.normalize("NFD", word)
    # Build syllables: [consonant_latin, vowel_latin_or_None(inherent), explicit?]
    units = []  # each: dict(kind, text, vowel, inherent)
    i = 0
    while i < len(word):
        ch = word[i]
        nxt = word[i + 1] if i + 1 < len(word) else ""
        if ch in _CONSONANTS:
            lat = _CONSONANTS[ch]
            if nxt == _NUKTA:
                lat = _NUKTA_CONSONANTS.get(ch, lat)
                i += 1
                nxt = word[i + 1] if i + 1 < len(word) else ""
            unit = {"kind": "C", "text": lat, "vowel": "a", "inherent": True}
            if nxt == _VIRAMA:
                unit["vowel"], unit["inherent"] = "", False
                i += 1
            elif nxt in _MATRAS:
                unit["vowel"], unit["inherent"] = _MATRAS[nxt], False
                i += 1
            units.append(unit)
        elif ch in _INDEPENDENT_VOWELS:
            units.append({"kind": "V", "text": _INDEPENDENT_VOWELS[ch], "vowel": "", "inherent": False})
        elif ch in (_ANUSVARA, _CHANDRABINDU):
            units.append({"kind": "N", "text": "n", "vowel": "", "inherent": False})
        elif ch == _VISARGA:
            units.append({"kind": "N", "text": "h", "vowel": "", "inherent": False})
        elif ch == _NUKTA or ch == _VIRAMA:
            pass
        else:
            units.append({"kind": "X", "text": ch, "vowel": "", "inherent": False})
        i += 1

    def has_vowel(u):
        return u["kind"] == "V" or (u["kind"] == "C" and u["vowel"] != "")

    # Schwa deletion: word-final inherent 'a' (if the word has >1 unit), then
    # medial inherent 'a' in V C(a) C V context, scanning right to left.
    cons_idx = [k for k, u in enumerate(units) if u["kind"] == "C"]
    if len(units) > 1 and units and units[-1]["kind"] == "C" and units[-1]["inherent"]:
        units[-1]["vowel"] = ""
    for k in reversed(cons_idx):
        u = units[k]
        if not u["inherent"] or u["vowel"] == "" or k == 0 or k == len(units) - 1:
            continue
        prev, nxt_u = units[k - 1], units[k + 1]
        if has_vowel(prev) and nxt_u["kind"] == "C" and has_vowel(nxt_u):
            u["vowel"] = ""
    return "".join(u["text"] + u["vowel"] for u in units)


# ---------------------------------------------------------------------------
# Hinglish spelling skeleton (applied to Latin tokens, both sides)
# ---------------------------------------------------------------------------
_LATIN_SUBS = [("ph", "f"), ("w", "v"), ("z", "j"), ("q", "k"), ("chh", "ch")]


def hinglish_skeleton(token):
    """Collapse common romanisation variants. Non-ASCII tokens pass through."""
    t = token.lower()
    if not t.isascii():
        return t
    for a, b in _LATIN_SUBS:
        t = t.replace(a, b)
    t = t.replace("ee", "i").replace("oo", "u")
    t = re.sub(r"(.)\1+", r"\1", t)          # accha -> acha, aa -> a
    t = re.sub(r"(ch)(?:ch)+", r"\1", t)    # achcha -> acha
    t = t.replace("ai", "e").replace("ei", "e").replace("au", "o")
    if len(t) > 2:
        t = re.sub(r"(?<=[aeiou])n$", "", t)  # hain/hai, mein/me
    t = t[:1] + t[1:].replace("a", "") if t else t  # drop non-initial 'a' (schwa)
    return t or token.lower()


def load_lexicon(path):
    """TSV: Devanagari spelling <TAB> Latin spelling. '#' starts a comment."""
    lex = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.split("#", 1)[0].strip()
            if not line:
                continue
            parts = line.split("\t")
            if len(parts) < 2:
                continue
            key = strict_normalise(parts[0])
            val = strict_normalise(parts[1])
            if key and val:
                lex[key] = val
    return lex


def hinglish_normalise(text, lexicon=None, translit=None):
    """Script-agnostic normalisation for Hindi and Hinglish scoring.

    translit: optional callable(token) -> str used instead of the built-in
    romaniser for Devanagari tokens (the "transliteration hook").
    """
    lexicon = lexicon or {}
    romanise = translit or romanise_devanagari
    out = []
    for tok in strict_normalise(text).split():
        if is_devanagari(tok):
            lat = lexicon.get(tok)
            if lat is None:
                lat = strict_normalise(romanise(tok))
            out.extend(lat.split())
        else:
            out.append(tok)
    return " ".join(s for s in (hinglish_skeleton(t) for t in out) if s)


def script_profile(text):
    """Share of letters by script: {'deva':..,'latn':..,'arab':..,'other':..}."""
    counts = {"deva": 0, "latn": 0, "arab": 0, "other": 0}
    for ch in unicodedata.normalize("NFC", text or ""):
        if not unicodedata.category(ch).startswith("L"):
            continue
        if "ऀ" <= ch <= "ॿ":
            counts["deva"] += 1
        elif ch.isascii() or "À" <= ch <= "ɏ":
            counts["latn"] += 1
        elif "؀" <= ch <= "ۿ" or "ݐ" <= ch <= "ݿ":
            counts["arab"] += 1
        else:
            counts["other"] += 1
    total = sum(counts.values())
    return {k: (v / total if total else 0.0) for k, v in counts.items()}


# ---------------------------------------------------------------- phonetic key
# Diagnostic only (WERph), never the official score. Hinglish engines write the
# same English loanword in either script ("file" / "फाइल" -> "fel"), and
# Devanagari romanisation cannot recover English spelling. A consonant key makes
# such pairs match: file -> fl, फाइल -> fl, box -> bks, बॉक्स -> bks.
# It is lenient by design (it ignores vowels), so it shows how much of a gap is
# script and spelling rather than wrong words. Always report it next to WER.
_PH_RULES = (
    ("ck", "k"), ("ce", "s"), ("ci", "s"), ("cy", "s"), ("ch", "\x01"), ("c", "k"),
    ("\x01", "ch"), ("x", "ks"), ("q", "k"), ("ph", "f"), ("w", "v"), ("z", "j"),
)


def phonetic_key(token):
    t = token.lower()
    if not t.isascii() or not t.isalpha():
        return t
    for a, b in _PH_RULES:
        t = t.replace(a, b)
    head, rest = t[0], t[1:]
    rest = re.sub(r"[aeiouy]", "", rest)
    rest = re.sub(r"(?<=[^aeiou])h", "", rest) if len(rest) > 1 else rest
    key = re.sub(r"(.)\1+", r"\1", head + rest)
    return key


def phonetic_normalise(skeleton_text):
    """Map an already-normalised (Hinglish skeleton) string to phonetic keys."""
    return " ".join(phonetic_key(w) for w in skeleton_text.split())
