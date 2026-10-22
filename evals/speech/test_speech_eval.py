"""Unit tests for the speech normaliser and runner. Stdlib only, offline.

Run: python3 -m unittest discover -s evals/speech -v
"""
import io
import json
import os
import struct
import sys
import tempfile
import unittest
import wave
from contextlib import redirect_stderr, redirect_stdout

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))  # evals/, for run_evals

import run_evals  # noqa: E402
import run_speech_eval as rse  # noqa: E402
from speech_normalise import (  # noqa: E402
    hinglish_normalise, hinglish_skeleton, load_lexicon, romanise_devanagari,
    script_profile, strict_normalise,
)

EXAMPLE = os.path.join(HERE, "example")
LEXICON = load_lexicon(os.path.join(HERE, "translit_lexicon.tsv"))


def read_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def read_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def run_quiet(argv):
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        code = rse.main(argv)
    return code, out.getvalue(), err.getvalue()


class StrictNormaliseTest(unittest.TestCase):
    def test_lowercase_and_punctuation(self):
        self.assertEqual(strict_normalise("Hello, World! Pour-over?"), "hello world pour over")

    def test_apostrophes_join(self):
        self.assertEqual(strict_normalise("Don't  stop — it’s fine"), "dont stop its fine")

    def test_danda_and_devanagari_digits(self):
        self.assertEqual(strict_normalise("कुल १०० रुपये।"), "कुल 100 रुपये")

    def test_numbers_currency_percent(self):
        self.assertEqual(strict_normalise("Save 20% — ₹10,000 of Rs. 1,00,000"),
                         "save 20 percent 10000 rupees of 100000 rupees")
        self.assertEqual(strict_normalise("years 5"), "years 5")

    def test_zero_width_chars_do_not_split_words(self):
        # ZWJ/ZWNJ would otherwise be split by run_evals.norm_words
        self.assertEqual(strict_normalise("क्‍ष‌त्र"), "क्षत्र")

    def test_nukta_folded_except_dd_rh(self):
        self.assertEqual(strict_normalise("ज़्यादा"), strict_normalise("ज्यादा"))
        self.assertEqual(strict_normalise("फ़िर"), "फिर")
        self.assertNotEqual(strict_normalise("गुड़"), strict_normalise("गुड"))
        self.assertNotEqual(strict_normalise("पढ़"), strict_normalise("पढ"))

    def test_chandrabindu_folds_to_anusvara(self):
        self.assertEqual(strict_normalise("हाँ"), strict_normalise("हां"))

    def test_bracketed_non_speech_removed(self):
        self.assertEqual(strict_normalise("[Music] hi (applause) [संगीत] there [BLANK_AUDIO]"), "hi there")

    def test_idempotent_and_stable_under_run_evals(self):
        for text in ("ये cafe इंदिरानगर में है।", "Don't stop", "हाँ, ज़रूर!"):
            once = strict_normalise(text)
            self.assertEqual(strict_normalise(once), once)
            self.assertEqual(" ".join(run_evals.norm_words(once)), once)


class RomaniserTest(unittest.TestCase):
    def test_common_words(self):
        cases = {"बहुत": "bahut", "कमल": "kamal", "करना": "karnaa", "समझना": "samajhnaa",
                 "है": "hai", "में": "men", "फिर": "phir", "लड़का": "ladkaa", "पढ़ना": "padhnaa"}
        for dev, lat in cases.items():
            self.assertEqual(romanise_devanagari(strict_normalise(dev)), lat, dev)

    def test_passes_through_latin(self):
        self.assertEqual(romanise_devanagari("cafe"), "cafe")


class SkeletonTest(unittest.TestCase):
    def assertSame(self, *words):
        sk = {hinglish_skeleton(w) for w in words}
        self.assertEqual(len(sk), 1, f"{words} -> {sk}")

    def test_romanisation_variants_collapse(self):
        self.assertSame("accha", "acha", "achchha")
        self.assertSame("mein", "me")
        self.assertSame("hai", "hain", "he")
        self.assertSame("zyada", "jyada", "zyaada")
        self.assertSame("phir", "fir")
        self.assertSame("aur", "or")
        self.assertSame("theek", "thik")

    def test_distinct_words_stay_distinct(self):
        for a, b in (("pani", "puri"), ("kal", "kab"), ("roti", "rota"), ("protein", "protin shake")):
            self.assertNotEqual(hinglish_skeleton(a), hinglish_skeleton(b))

    def test_non_ascii_passthrough(self):
        self.assertEqual(hinglish_skeleton("ہر"), "ہر")


class HinglishNormaliseTest(unittest.TestCase):
    def test_script_agnostic_match(self):
        dev = "ये cafe इंदिरानगर में है और बहुत अच्छा है।"
        rom = "ye cafe indiranagar mein hai aur bahut accha hai"
        self.assertEqual(hinglish_normalise(dev, LEXICON), hinglish_normalise(rom, LEXICON))

    def test_lexicon_maps_english_loanwords(self):
        self.assertEqual(hinglish_normalise("कैफ़े", LEXICON), hinglish_normalise("cafe", LEXICON))
        self.assertEqual(hinglish_normalise("प्रोटीन शेक", LEXICON).split()[0],
                         hinglish_normalise("protein", LEXICON))

    def test_without_lexicon_loanword_mismatches(self):
        self.assertNotEqual(hinglish_normalise("कैफे"), hinglish_normalise("cafe"))

    def test_translit_hook_is_used(self):
        calls = []

        def hook(tok):
            calls.append(tok)
            return "X"

        self.assertEqual(hinglish_normalise("नमस्ते dost", translit=hook), "x dost")
        self.assertEqual(calls, ["नमस्ते"])

    def test_output_is_run_evals_stable(self):
        out = hinglish_normalise("रोज़ सुबह 10 minute stretching करो, फिर protein shake लो।", LEXICON)
        self.assertEqual(" ".join(run_evals.norm_words(out)), out)
        self.assertTrue(out.isascii())


class ScriptProfileTest(unittest.TestCase):
    def test_profiles(self):
        self.assertEqual(script_profile("abc")["latn"], 1.0)
        self.assertEqual(script_profile("नमस्ते")["deva"], 1.0)
        self.assertGreater(script_profile("ہر مہینے")["arab"], 0.9)
        self.assertEqual(script_profile("")["latn"], 0.0)


class HypothesisCleaningTest(unittest.TestCase):
    def test_whisper_cpp_timestamps(self):
        raw = "[00:00:00.000 --> 00:00:05.000]   hello there\n[00:00:05.000 --> 00:00:09.000]  again\n"
        self.assertEqual(rse.clean_hypothesis(raw), "hello there again")

    def test_srt_and_vtt(self):
        srt = "1\n00:00:00,000 --> 00:00:04,200\nhello\n\n2\n00:00:04,200 --> 00:00:06,000\nworld\n"
        vtt = "WEBVTT\n\n00:00.000 --> 00:04.200\nhello\n\n00:04.200 --> 00:06.000\nworld\n"
        self.assertEqual(rse.clean_hypothesis(srt), "hello world")
        self.assertEqual(rse.clean_hypothesis(vtt), "hello world")

    def test_plain_numbers_in_speech_survive_inline(self):
        self.assertEqual(rse.clean_hypothesis("add 2 cups"), "add 2 cups")


class ScoringTest(unittest.TestCase):
    def test_edit_ops(self):
        dist, s, d, i = rse.edit_ops("a b c d".split(), "a x c d e".split())
        self.assertEqual((dist, s, d, i), (2, 1, 0, 1))
        self.assertEqual(rse.edit_ops([], ["a"])[0], 1)
        self.assertEqual(rse.edit_ops(["a"], [])[2], 1)


def _write_wav(path, seconds, rate=16000, channels=1):
    with wave.open(path, "wb") as w:
        w.setnchannels(channels)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(struct.pack("<h", 0) * int(seconds * rate) * channels)


class AudioCheckTest(unittest.TestCase):
    def test_audio_rules(self):
        with tempfile.TemporaryDirectory() as d:
            good = os.path.join(d, "good.wav")
            _write_wav(good, 20)
            self.assertEqual(rse.check_audio(good), [])
            short = os.path.join(d, "short.wav")
            _write_wav(short, 1)
            self.assertTrue(any("outside" in p for p in rse.check_audio(short)))
            stereo = os.path.join(d, "stereo.wav")
            _write_wav(stereo, 20, rate=44100, channels=2)
            self.assertTrue(any("mono 16 kHz" in p for p in rse.check_audio(stereo)))
            self.assertTrue(rse.check_audio(os.path.join(d, "nope.wav")))
            self.assertTrue(any("sha256" in p for p in rse.check_audio(good, "00" * 32)))


class EndToEndTest(unittest.TestCase):
    def test_example_runs_and_matches_run_evals(self):
        with tempfile.TemporaryDirectory() as d:
            out, summ = os.path.join(d, "r.jsonl"), os.path.join(d, "s.json")
            code, _, err = run_quiet(["--golden", EXAMPLE, "--hyps", os.path.join(EXAMPLE, "hyps"),
                                      "--out", out, "--summary", summ, "--engine", "synthetic"])
            self.assertEqual(code, 0, err)
            rows = read_jsonl(out)
            self.assertEqual(len(rows), 6)
            for r in rows:
                self.assertEqual(r["suite"], "speech")
                self.assertIn(r["lang"], ("en", "hi"))
            metrics, _ = run_evals.compute(rows)
            groups = read_json(summ)["groups"]
            for lang in ("en", "hi"):
                self.assertAlmostEqual(metrics[f"speech.wer_{lang}"], groups[f"lang={lang}"]["wer"], places=4)
            # Romanised and Devanagari Hinglish hypotheses are not penalised for script
            fit = next(r for r in rows if r["id"] == "hi-fitness-003")
            self.assertEqual(fit["scores"]["official"]["word_errors"], 0)
            self.assertGreater(fit["scores"]["strict"]["word_errors"], 0)
            # Urdu-script output is flagged and scored as errors
            self.assertEqual(groups["lang=hi/condition=music"]["wrong_script_clips"], 1)
            # Injection clip is transcribed verbatim, not obeyed or dropped
            inj = next(r for r in rows if r["injection"])
            self.assertIn("ignore your previous instructions", inj["hypothesis"])

    def test_missing_hypothesis(self):
        with tempfile.TemporaryDirectory() as d:
            out = os.path.join(d, "r.jsonl")
            code, _, err = run_quiet(["--golden", EXAMPLE, "--hyps", d, "--out", out])
            self.assertEqual(code, 2)
            self.assertIn("missing hypothesis", err)
            code, _, _ = run_quiet(["--golden", EXAMPLE, "--hyps", d, "--out", out, "--missing", "empty"])
            self.assertEqual(code, 0)
            rows = read_jsonl(out)
            self.assertTrue(all(r["missing_hypothesis"] for r in rows))
            self.assertEqual(run_evals.compute(rows)[0]["speech.wer_en"], 1.0)

    def test_check_audio_flags_missing_audio(self):
        with tempfile.TemporaryDirectory() as d:
            code, _, err = run_quiet(["--golden", EXAMPLE, "--hyps", os.path.join(EXAMPLE, "hyps"),
                                      "--out", os.path.join(d, "r.jsonl"), "--check-audio"])
            self.assertEqual(code, 2)
            self.assertIn("missing audio", err)

    def test_bad_manifest(self):
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, "refs"))
            with open(os.path.join(d, "manifest.jsonl"), "w", encoding="utf-8") as f:
                f.write('{"id":"x","lang":"fr"}\n{"id":"y","lang":"hi","variety":"english"}\n')
            with open(os.path.join(d, "refs", "y.txt"), "w", encoding="utf-8") as f:
                f.write("नमस्ते")
            code, _, err = run_quiet(["--golden", d, "--hyps", d, "--out", os.path.join(d, "r.jsonl"),
                                      "--missing", "empty"])
            self.assertEqual(code, 2)
            self.assertIn("lang", err)
            self.assertIn("variety", err)


if __name__ == "__main__":
    unittest.main()
