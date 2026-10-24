#!/usr/bin/env python3
"""Apply only the approved contact/navigation edits to the Vercel snapshot.

Usage: python3 scripts/apply-approved-content.py [destination]
       python3 scripts/apply-approved-content.py --self-test

The default destination is current-site. All ten files are validated before
writing. An already patched or partially patched input fails clearly; this is
intentional so source drift cannot silently acquire a second set of edits.
Stylesheets, script tags, hero markup, image references and layout are untouched.
"""

import argparse
from html.parser import HTMLParser
from pathlib import Path
import re
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[1]
PAGES = (
    "index", "company", "briefing", "solutions", "training", "platform",
    "creator-social", "marketing-investment", "online-conversion",
)
FILES = tuple(page + ".html" for page in PAGES) + ("revision-enquiry.js",)
CONTACT_PAGES = {"index", "company", "briefing", "solutions", "platform"}
EMAIL = '<a class="contact-email" href="mailto:randy@aicatalyst.biz">randy@aicatalyst.biz</a>'
PHONE = '<a class="contact-phone" href="tel:+14162700132">416-270-0132</a>'
LINKEDIN = 'https://www.linkedin.com/company/catalystretailsolutions/'
ADVISORS = (
    ("randyweyersberg", "Randy Weyersberg"),
    ("nickbobrow", "Nick Bobrow"),
    ("billlanglois", "Bill Langlois"),
    ("andrewryder", "Andrew Ryder"),
    ("adun-abiodun-664550138", "Adun Abiodun"),
    ("megan-page-ba627013", "Megan Page"),
)


class ContentError(ValueError):
    """An input differs from the precise, unmodified content expected here."""


class Copy(HTMLParser):
    def __init__(self):
        super().__init__()
        self.words = []
        self.hidden = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.hidden += 1

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self.hidden -= 1

    def handle_data(self, value):
        if not self.hidden and value.strip():
            self.words.append(re.sub(r"\s+", " ", value.strip()))


def words(source):
    parser = Copy()
    parser.feed(source.decode("utf-8"))
    return parser.words


def reference(revision, filename):
    return subprocess.check_output(
        ["git", "show", f"{revision}:current-site/{filename}"], cwd=ROOT
    )


def replace_once(source, before, after, filename, label):
    before, after = before.encode("utf-8"), after.encode("utf-8")
    count = source.count(before)
    if count != 1:
        raise ContentError(
            f"{filename}: {label}: expected one original occurrence, found {count}. "
            "Input may already be patched or may differ from the Vercel snapshot; "
            "no files were written."
        )
    return source.replace(before, after, 1)


def patch(source, filename):
    def change(before, after, label):
        nonlocal source
        source = replace_once(source, before, after, filename, label)

    if filename == "revision-enquiry.js":
        change(
            "Enquiry delivery is not connected. Please contact AI Catalyst on LinkedIn. Your message has not been sent.",
            "Enquiry delivery is not connected. Email randy@aicatalyst.biz or call 416-270-0132. Your message has not been sent.",
            "unconfigured enquiry fallback",
        )
        return source

    page = Path(filename).stem
    menu_before = '<li><a href="solutions.html">How We Work</a></li><li><a href="briefing.html">Start a conversation</a></li>'
    menu_after = '<li><a href="solutions.html">How We Work</a></li><li><a href="training.html">Training and adoption</a></li><li><a href="briefing.html">Start a conversation</a></li>'
    change(menu_before, menu_after, "expanded-menu Training after How We Work")
    change(
        f'<a href="{LINKEDIN}" target="_blank" rel="noopener noreferrer">LinkedIn <span aria-hidden="true">↗</span></a>',
        EMAIL,
        "footer LinkedIn route",
    )
    if page in CONTACT_PAGES:
        change("<address>" + PHONE, "<address>" + EMAIL + PHONE,
               "visible email beside existing phone and Toronto")
    if page == "index":
        change(
            f'<a class="contact-primary" href="{LINKEDIN}" target="_blank" rel="noopener noreferrer">Start a conversation <span aria-hidden="true">↗</span></a>',
            '<a class="contact-primary" href="mailto:randy@aicatalyst.biz">Email Randy <span aria-hidden="true">↗</span></a>',
            "homepage contact action",
        )
    elif page in CONTACT_PAGES:
        change(
            '<p>Call us or start a conversation on LinkedIn.</p>'
            f'<a class="text-link" href="{LINKEDIN}" target="_blank" rel="noopener noreferrer">Contact AI Catalyst <span aria-hidden="true">↗</span></a>',
            '<p>Email or call to start a conversation.</p>',
            "contact LinkedIn wording and action",
        )
    if page == "company":
        for slug, name in ADVISORS:
            change(
                f'<a class="advisor-profile" href="https://www.linkedin.com/in/{slug}/" target="_blank" rel="noopener noreferrer" aria-label="{name} on LinkedIn">LinkedIn ↗</a>',
                "",
                f"{name} LinkedIn profile",
            )
    return source


def validate_result(source, filename):
    if re.search(rb"linkedin|catalyst\s*retail\s*solutions", source, re.I):
        raise ContentError(f"{filename}: a retired contact reference remains")
    if filename.endswith(".html"):
        if words(source) != words(reference("9bc79bd", filename)):
            raise ContentError(f"{filename}: copy differs from the approved content revision 9bc79bd")
        page = Path(filename).stem
        email_count = 3 if page == "index" else 2 if page in CONTACT_PAGES else 1
        if source.count(b'href="mailto:randy@aicatalyst.biz"') != email_count:
            raise ContentError(f"{filename}: unexpected email route count")
        phone_count = 2 if page in CONTACT_PAGES else 1
        if source.count(b'href="tel:+14162700132"') != phone_count:
            raise ContentError(f"{filename}: the existing phone routes changed")
        if b"Toronto, Canada" not in source:
            raise ContentError(f"{filename}: the existing location is absent")
    elif source != reference("9bc79bd", filename):
        raise ContentError(f"{filename}: differs from the approved enquiry fallback revision")


def apply(destination):
    planned = []
    for filename in FILES:
        target = destination / filename
        if not target.is_file():
            raise ContentError(f"Missing input {target}; no files were written")
        source = patch(target.read_bytes(), filename)
        validate_result(source, filename)
        planned.append((target, source))
    for target, source in planned:
        target.write_bytes(source)
    return len(planned)


def protected_markup(source):
    tags = re.findall(rb'<script\b[\s\S]*?</script>|<link\b[^>]*>|<style\b[\s\S]*?</style>', source)
    hero = re.search(rb'<section\b[^>]*class="(?:hero|page-hero)[^\"]*"[\s\S]*?</section>', source)
    if hero is None:
        raise AssertionError("Expected one original hero section")
    return tags, hero.group(0)


def self_test():
    originals = {filename: reference("68dbb96", filename) for filename in FILES}
    with tempfile.TemporaryDirectory(prefix="ai-catalyst-content-only-") as folder:
        destination = Path(folder)
        for filename, source in originals.items():
            (destination / filename).write_bytes(source)
        assert apply(destination) == 10
        for filename in FILES:
            after = (destination / filename).read_bytes()
            validate_result(after, filename)
            if filename.endswith(".html"):
                assert protected_markup(after) == protected_markup(originals[filename]), filename
        before_retry = {name: (destination / name).read_bytes() for name in FILES}
        try:
            apply(destination)
        except ContentError as error:
            assert "already be patched" in str(error)
        else:
            raise AssertionError("An already patched destination must fail clearly")
        assert all((destination / name).read_bytes() == value for name, value in before_retry.items())
        # An unexpected occurrence in the last file must not partially patch
        # any of the preceding nine files.
        for filename, source in originals.items():
            (destination / filename).write_bytes(source)
        script = destination / "revision-enquiry.js"
        script.write_bytes(script.read_bytes().replace(b"Please contact AI Catalyst on LinkedIn.", b"Unexpected fallback."))
        try:
            apply(destination)
        except ContentError:
            pass
        else:
            raise AssertionError("Unexpected source must fail preflight")
        assert all((destination / (page + ".html")).read_bytes() == originals[page + ".html"] for page in PAGES)
    print("PASS: all 9 page texts match 9bc79bd; style/script tags and hero markup are byte-identical to Vercel; retry/drift fail without partial writes.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", nargs="?", type=Path, default=ROOT / "current-site")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    try:
        if args.self_test:
            self_test()
        else:
            count = apply(args.destination.resolve())
            print(f"Applied only approved contact/navigation edits to {count} files in {args.destination.resolve()}")
    except (ContentError, OSError, subprocess.CalledProcessError) as error:
        parser.exit(1, f"FAIL: {error}\n")


if __name__ == "__main__":
    main()
