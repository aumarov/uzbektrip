"""
Populates the singleton Visa & Entry page with content sourced from the
Ministry of Foreign Affairs of the Republic of Uzbekistan
(https://gov.uz/en/mfa/activity_page/o-zbekiston-respublikasi-vizasi).

Idempotent — safe to re-run; always overwrites with the latest copy below.
Run after `setup_site` has created the page:
    python manage.py seed_visa_page
"""
from django.core.management.base import BaseCommand

MFA_SOURCE_URL = "https://gov.uz/en/mfa/activity_page/o-zbekiston-respublikasi-vizasi"

CIS_UNLIMITED = [
    "Azerbaijan", "Armenia", "Belarus", "Georgia", "Kazakhstan",
    "Moldova", "Russia", "Ukraine",
]
SIXTY_DAYS = ["Kyrgyzstan"]
THIRTY_DAYS = [
    "Tajikistan", "Australia", "Austria", "Argentina", "Bosnia and Herzegovina",
    "Vatican City", "Luxembourg", "Hungary", "Brunei", "Israel", "Greece",
    "Ireland", "Iceland", "Italy", "Canada", "Andorra", "Liechtenstein",
    "Monaco", "Belgium", "Denmark", "Spain", "Netherlands", "Norway", "Sweden",
    "Latvia", "Lithuania", "Malaysia", "Mauritius", "New Zealand",
    "United Arab Emirates", "Portugal", "Bulgaria", "Indonesia", "Cyprus",
    "South Korea", "Malta", "Poland", "San Marino", "Serbia", "Slovenia",
    "Croatia", "Chile", "Romania", "Singapore", "Slovakia", "United Kingdom",
    "Turkey", "Brazil", "Germany", "Finland", "France", "Montenegro",
    "Czech Republic", "Switzerland", "Estonia", "Japan", "Antigua and Barbuda",
    "Barbados", "Belize", "Grenada", "Dominican Republic", "Mexico",
    "Guatemala", "Honduras", "Costa Rica", "Cuba", "Nicaragua", "Panama",
    "Trinidad and Tobago", "El Salvador", "Saint Vincent and the Grenadines",
    "Saint Lucia", "Bahamas", "Dominica", "Saint Kitts and Nevis", "Jamaica",
    "Qatar",
]
TEN_DAYS = ["Bahrain", "Kuwait", "Oman", "China (incl. Hong Kong & Macao)"]
EVISA_COUNTRIES = [
    "Algeria", "Egypt", "Venezuela", "Uruguay", "Gabon", "Qatar", "Kuwait",
    "Sri Lanka", "Jordan", "Iran", "China (incl. Hong Kong)", "Guyana",
    "North Korea", "Bahrain", "Bhutan", "Cambodia", "Morocco", "Saudi Arabia",
    "Thailand", "Tonga", "Laos", "Lebanon", "Maldives", "Bolivia",
    "Bangladesh", "Samoa", "Albania", "Angola", "Vanuatu", "Ghana", "India",
    "Cabo Verde", "Cameroon", "Kiribati", "Colombia", "Côte d'Ivoire",
    "Mauritius", "North Macedonia", "Marshall Islands", "Nauru", "Palau",
    "Paraguay", "Peru", "Seychelles", "Senegal", "Suriname", "Fiji",
    "Philippines", "Ecuador", "United States", "Solomon Islands", "Vietnam",
    "Oman", "Tunisia", "Nepal", "Micronesia",
]
TRANSIT_5DAY = [
    "Albania", "Algeria", "Antigua and Barbuda", "Bahamas", "Barbados",
    "Belize", "Bhutan", "Venezuela", "Vietnam", "Gabon", "Guyana",
    "Guatemala", "Grenada", "Dominica", "Dominican Republic", "India",
    "Colombia", "Costa Rica", "Lebanon", "Mauritius", "North Macedonia",
    "Maldives", "Morocco", "Mexico", "Nauru", "Palau", "Panama", "Peru",
    "Saudi Arabia", "Seychelles", "Saint Vincent and the Grenadines",
    "Saint Kitts and Nevis", "Saint Lucia", "United States", "Suriname",
    "Thailand", "Trinidad and Tobago", "Tunisia", "Turkmenistan", "Uruguay",
    "Fiji", "Philippines", "Sri Lanka", "Ecuador", "Equatorial Guinea",
    "South Africa", "Jamaica",
]

FEE_TABLE_ROWS = [
    ["Visa type", "Duration", "Fee (per person)"],
    ["Single-entry", "Up to 7 days", "$40"],
    ["Single-entry", "Up to 15 days", "$50"],
    ["Single-entry", "Up to 30 days", "$60"],
    ["Single-entry", "Up to 3 months", "$80"],
    ["Single-entry", "Up to 6 months", "$120"],
    ["Single-entry", "Up to 1 year", "$160"],
    ["Multiple-entry", "Up to 6 months", "$150"],
    ["Multiple-entry", "Up to 1 year", "$250"],
    ["Multiple-entry", "Up to 2 years", "$300"],
    ["Multiple-entry", "Up to 3 years", "$350"],
    ["Transit", "Up to 72 hours", "$40"],
    ["Transit", "Double transit", "$50"],
    ["Tourist (T)", "Up to 30 days", "$40"],
    ["Group tourist (5+ people)", "Up to 15 days", "$15 / person"],
    ["Group tourist (5+ people)", "Up to 30 days", "$25 / person"],
    ["e-Visa", "Single-entry", "$20"],
    ["e-Visa", "Double-entry, up to 30 days", "$35"],
    ["e-Visa", "Multiple-entry, up to 30 days", "$50"],
    ["e-Visa", "Group, up to 30 days", "from $20 / person"],
]

VISA_CATEGORY_GROUPS = [
    (
        "Tourist & pilgrimage (most travelers use one of these)",
        "<ul>"
        "<li><strong>T</strong> — Tourist visa, up to 30 days</li>"
        "<li><strong>TG</strong> — Group Tourist visa, up to 30 days (groups of 5+)</li>"
        "<li><strong>PLG</strong> — Pilgrimage visa, up to 2 months</li>"
        "</ul>",
    ),
    (
        "Transit & exit",
        "<ul>"
        "<li><strong>TRAN</strong> — Transit visa, up to 72 hours</li>"
        "<li><strong>EXIT</strong> — Exit visa for travelers whose entry visa has overstayed, up to 1 month</li>"
        "</ul>",
    ),
    (
        "Business & investment",
        "<ul>"
        "<li><strong>B-1</strong> — Accredited representative of a foreign company or bank</li>"
        "<li><strong>B-2</strong> — Business visa, up to 1 year</li>"
        "<li><strong>INV</strong> — Multiple-entry Investment visa, up to 3 years</li>"
        "</ul>",
    ),
    (
        "Work, study & academic",
        "<ul>"
        "<li><strong>IS</strong> — Work visa, based on a foreign labour migration licence</li>"
        "<li><strong>STD</strong> — Student exchange visa, up to 1 year</li>"
        "<li><strong>A-1</strong> — Student visa, full programme, up to 1 year</li>"
        "<li><strong>A-2</strong> — Teacher visa, up to 1 year</li>"
        "<li><strong>A-3</strong> — Academic / research visa, 3 months–2 years</li>"
        "</ul>",
    ),
    (
        "Family & visitor",
        "<ul>"
        "<li><strong>PV-1</strong> — Visitor invited by a citizen of Uzbekistan, up to 1 year</li>"
        "<li><strong>PV-2</strong> — Visitor invited by a foreign resident of Uzbekistan, up to 1 year</li>"
        "<li><strong>VTD</strong> — Compatriot visa for those born in Uzbekistan and relatives, up to 2 years</li>"
        "</ul>",
    ),
    (
        "Diplomatic & official",
        "<ul>"
        "<li><strong>D-1 / D-2</strong> — Diplomatic visa (permanent / temporary accreditation)</li>"
        "<li><strong>DT</strong> — Diplomatic tourist visa, up to 1 month</li>"
        "<li><strong>S-1 / S-2 / S-3</strong> — Service visa for foreign government and NGO staff</li>"
        "<li><strong>O</strong> — Official visa for state and official visits</li>"
        "</ul>",
    ),
    (
        "Press",
        "<ul>"
        "<li><strong>J-1 / J-2</strong> — Foreign media accreditation (permanent / temporary)</li>"
        "</ul>",
    ),
    (
        "Medical & transport crew",
        "<ul>"
        "<li><strong>C</strong> — Medical treatment visa, up to 3 months</li>"
        "<li><strong>C-1</strong> — Aircraft / railway crew visa, up to 1 year</li>"
        "<li><strong>C-2</strong> — Freight vehicle driver visa, up to 1 year</li>"
        "</ul>",
    ),
]

FAQ_ITEMS = [
    (
        "Do I need a visa to visit Uzbekistan?",
        "It depends on your nationality. Citizens of 90+ countries can enter visa-free "
        "(see the tiers below), and around 55 more qualify for a simplified e-Visa. If your "
        "country isn't on either list, you'll need a visa from an Uzbek embassy or consulate "
        "before you travel.",
    ),
    (
        "How long can I stay without a visa?",
        "Anywhere from 10 days to unlimited, depending on your nationality — find your country "
        "in the visa-free tiers below. If you need to stay longer, you can apply for a "
        "longer-duration visa or extend your stay at a local immigration office.",
    ),
    (
        "What is an e-Visa and how do I apply?",
        "An e-Visa is an online-only visa for citizens of around 55 countries (see the list "
        "below). Apply at e-visa.gov.uz, upload your passport and a photo, and pay the fee "
        "online — approval typically takes a few business days.",
    ),
    (
        "My country isn't visa-free or e-Visa eligible — what now?",
        "You'll need to apply at the nearest Uzbek embassy or consulate. If your country has "
        "none, a visa can be arranged on arrival at Tashkent International Airport, but only if "
        "your host (an individual or organization in Uzbekistan) requests MFA confirmation in "
        "advance and sends it to you before you fly.",
    ),
    (
        "Can visa rules, fees, or durations change without notice?",
        "Yes — Uzbekistan has updated its visa-free list and e-Visa rules several times in "
        "recent years. Always check the official MFA visa page or e-visa.gov.uz before booking "
        "flights or finalizing your trip.",
    ),
    (
        "Can I get a visa on arrival in Uzbekistan?",
        "Only if your country has no Uzbek diplomatic mission. In that case, your host in "
        "Uzbekistan must apply to the Ministry of Foreign Affairs in advance and send you a "
        "confirmation stamp, which you present at the visa service sector of Tashkent "
        "International Airport.",
    ),
]


def _country_tag(label, countries):
    return {
        "title": f"{label} — {len(countries)} countr{'y' if len(countries) == 1 else 'ies'}",
        "content": f"<p>{', '.join(countries)}</p>",
    }


class Command(BaseCommand):
    help = "Seed the Visa & Entry page with content sourced from the Uzbek MFA"

    def handle(self, *args, **options):
        from apps.visa.models import VisaIndexPage

        page = VisaIndexPage.objects.first()
        if page is None:
            self.stderr.write(
                "No VisaIndexPage found — run `python manage.py setup_site` first."
            )
            return

        page.intro = (
            "<p>Most travelers can enter Uzbekistan visa-free or apply for a simple e-Visa "
            "online. This page summarizes Uzbekistan's visa system — visa-free durations by "
            "country, e-Visa eligibility, the official visa categories, and consular fees — "
            "based on information published by the Ministry of Foreign Affairs of the "
            f'Republic of Uzbekistan (<a href="{MFA_SOURCE_URL}">gov.uz/en/mfa</a>).</p>'
        )
        page.visa_free_note = (
            "<p>More than <strong>90 countries</strong> can enter Uzbekistan without a visa, "
            "with durations ranging from 10 days to unlimited depending on nationality. Below "
            "is the headline 30-day tier most international travelers fall into — see the full "
            "breakdown by duration further down this page.</p>"
        )
        page.visa_free_countries = ", ".join(THIRTY_DAYS)

        page.body = [
            {
                "type": "quote",
                "value": {
                    "quote": (
                        "Foreign citizens and stateless persons may enter Uzbekistan and "
                        "transit through its territory only if they have entry visas in "
                        "accordance with the legislation of the Republic of Uzbekistan, with "
                        "the exception of citizens of countries for which a visa-free entry "
                        "regime is established by bilateral international treaties and "
                        "Decrees of the President of the Republic of Uzbekistan."
                    ),
                    "attribution": "Ministry of Foreign Affairs of the Republic of Uzbekistan",
                    "attribution_role": "gov.uz/en/mfa",
                },
            },
            {
                "type": "alert",
                "value": {
                    "style": "warning",
                    "heading": "Always verify before you travel",
                    "text": (
                        "<p>Visa-free durations, e-Visa eligibility, visa categories and "
                        "consular fees can change without notice. This page is based on "
                        "information published by Uzbekistan's Ministry of Foreign Affairs "
                        "and is provided as a starting point for trip planning only — always "
                        f'confirm your specific requirements on the official <a href="{MFA_SOURCE_URL}">'
                        'MFA visa page</a> or <a href="https://e-visa.gov.uz">e-visa.gov.uz</a> '
                        "before booking flights or finalizing your travel plans.</p>"
                    ),
                },
            },
            {
                "type": "rich_text",
                "value": (
                    "<h2>How Uzbekistan's visa system works</h2>"
                    "<p>Uzbekistan uses three main routes for foreign visitors:</p>"
                    "<ul>"
                    "<li><strong>Visa-free entry</strong> — citizens of 90+ countries can enter "
                    "without applying for anything in advance, for a set number of days that "
                    "depends on nationality.</li>"
                    "<li><strong>e-Visa</strong> — citizens of around 55 additional countries "
                    'can apply online at <a href="https://e-visa.gov.uz">e-visa.gov.uz</a>, '
                    "usually approved within a few business days, without visiting an "
                    "embassy.</li>"
                    "<li><strong>Embassy or consulate visa</strong> — everyone else applies in "
                    "person (or via an inviting organization or individual) at an Uzbek "
                    "diplomatic mission, or, if none exists in their country, through the visa "
                    "service sector at Tashkent International Airport with prior MFA "
                    "confirmation.</li>"
                    "</ul>"
                    "<p>Independent travelers will almost always use one of four simplified "
                    "categories: <strong>T</strong> (Tourist, up to 30 days), <strong>TG</strong> "
                    "(Group Tourist), <strong>PLG</strong> (Pilgrimage, up to 2 months), or "
                    "<strong>TRAN</strong> (Transit, up to 72 hours). The categories further "
                    "down this page cover business, diplomatic, work, study and family "
                    "visits.</p>"
                ),
            },
            {
                "type": "table",
                "value": {
                    "table_caption": (
                        "Official consular fees, Ministry of Foreign Affairs of the Republic of "
                        "Uzbekistan. Single- and multiple-entry rates increase by $10 per "
                        "additional entry."
                    ),
                    "first_row_is_table_header": True,
                    "first_col_is_header": False,
                    "data": FEE_TABLE_ROWS,
                },
            },
            {
                "type": "accordion",
                "value": {
                    "heading": "Visa-free & extended-stay tiers, by country",
                    "items": [
                        _country_tag("Unlimited duration", CIS_UNLIMITED),
                        _country_tag("Up to 60 days", SIXTY_DAYS),
                        _country_tag("Up to 30 days", THIRTY_DAYS),
                        _country_tag("Up to 10 days (return ticket required)", TEN_DAYS),
                        _country_tag(
                            "5-day visa-free airport transit (with onward ticket on Uzbekistan Airways)",
                            TRANSIT_5DAY,
                        ),
                    ],
                },
            },
            {
                "type": "accordion",
                "value": {
                    "heading": "e-Visa eligible countries",
                    "items": [_country_tag("Apply at e-visa.gov.uz", EVISA_COUNTRIES)],
                },
            },
            {
                "type": "accordion",
                "value": {
                    "heading": "Visa categories at a glance (28 official types)",
                    "items": [
                        {"title": label, "content": html}
                        for label, html in VISA_CATEGORY_GROUPS
                    ],
                },
            },
        ]

        page.faq_items = [
            {"type": "item", "value": {"question": q, "answer": f"<p>{a}</p>"}}
            for q, a in FAQ_ITEMS
        ]

        page.save()
        rev = page.save_revision()
        rev.publish()

        self.stdout.write(self.style.SUCCESS(f"✓ Seeded Visa & Entry page ({page.url})"))
