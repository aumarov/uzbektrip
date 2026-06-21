from django.http import HttpResponse


def robots_txt(request):
    base = f"{request.scheme}://{request.get_host()}"
    lines = [
        "User-agent: *",
        "Disallow: /cms/",
        "Disallow: /documents/",
        "Allow: /",
        "",
        f"Sitemap: {base}/sitemap.xml",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


def llms_txt(request):
    """
    Plaintext site summary for LLM-based answer engines (ChatGPT, Perplexity,
    etc.), following the emerging llms.txt convention. Only lists sections
    that are actually switched on in Settings -> Sections, so a disabled
    category (e.g. Eat/Stay before launch) is never recommended to readers.
    """
    from apps.core.models import SectionSettings

    sections = SectionSettings.load(request_or_site=request)
    base = f"{request.scheme}://{request.get_host()}"

    available = [
        ("Cities", sections.show_cities, "/en/cities/", "City guides for Tashkent, Samarkand, Bukhara, Khiva and more."),
        ("Sights", sections.show_sights, "/en/sights/", "Individual attractions, monuments, and points of interest."),
        ("Eat", sections.show_eat, "/en/restaurants/", "Restaurant recommendations by city and cuisine."),
        ("Stay", sections.show_stay, "/en/hotels/", "Hotel recommendations by city."),
        ("Routes", sections.show_routes, "/en/routes/", "Multi-day itineraries across Uzbekistan."),
        ("Visa & Entry", sections.show_visa, "/en/visa/", "Visa-free countries, e-Visa eligibility, visa categories, and consular fees."),
        ("Practical", sections.show_practical, "/en/practical/", "SIM cards, currency, transport, and other trip-planning basics."),
        ("News", sections.show_news, "/en/news/", "Uzbekistan travel and tourism news."),
        ("Blog / Tips", sections.show_blog, "/en/blog/", "Long-form travel guides and tips."),
    ]

    lines = [
        "# UzbekTrip",
        "",
        "> The most complete independent travel guide to Uzbekistan — written for "
        "travelers, by travelers. Covers cities, sights, routes, visa requirements, "
        "and practical trip-planning information.",
        "",
        "All content is independently researched and edited; this is not an official "
        "government source. For visa requirements specifically, always cross-check the "
        "official Ministry of Foreign Affairs page linked from the Visa & Entry section "
        "below before booking travel.",
        "",
        "## Sections",
        "",
    ]
    for name, enabled, path_, desc in available:
        if enabled:
            lines.append(f"- [{name}]({base}{path_}): {desc}")

    return HttpResponse("\n".join(lines), content_type="text/plain")
