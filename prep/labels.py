"""Shared labels and groupings, so every chart names things the same way.

Charts 7, 8 and 9 all show field of study. If each script invented its own
labels, the same field could appear as "Management and Commerce" in one chart
and "Business" in another. Everything that names a field, a region or a
university group comes from here.
"""

# ---------------------------------------------------------------- fields
# The Department's 12 broad fields, regrouped for display. Two corrections
# matter:
#   * English-language courses (ELICOS) are officially filed under "Society
#     and Culture > Language and Literature". Left alone, half of "Society &
#     Culture" would be English courses, so ELICOS gets its own group.
#   * School students and foundation programs sit in "Mixed Field Programmes",
#     which isn't a field of study at all. They become "School & other".
# The three smallest academic fields are merged so the Marimekko columns
# stay wide enough to read.
FIELD_GROUP = {
    "Management and Commerce": "Business & Commerce",
    "Society and Culture": "Society & Culture",
    "Information Technology": "IT",
    "Engineering and Related Technologies": "Engineering",
    "Education": "Education",
    "Health": "Health",
    "Food, Hospitality and Personal Services": "Hospitality & Services",
    "Architecture and Building": "Architecture & Building",
    "Natural and Physical Sciences": "Sciences, Arts & Agriculture",
    "Creative Arts": "Sciences, Arts & Agriculture",
    "Agriculture, Environmental and Related Studies": "Sciences, Arts & Agriculture",
    "Mixed Field Programmes": "School & other",
    "_Dual Qualification": "School & other",
}
ELICOS_GROUP = "English language"
SCHOOL_GROUP = "School & other"

# Fixed display order, used by every field chart. Roughly by size, with
# "School & other" last because it isn't a real field.
FIELD_ORDER = [
    "Business & Commerce",
    "IT",
    "English language",
    "Society & Culture",
    "Engineering",
    "Education",
    "Health",
    "Hospitality & Services",
    "Architecture & Building",
    "Sciences, Arts & Agriculture",
    "School & other",
]

# Higher-education data uses the same field names, but some only make sense
# individually there. Used by the dumbbell (chart 8).
HE_FIELD_LABEL = {
    "Management and Commerce": "Business & Commerce",
    "Information Technology": "IT",
    "Engineering and Related Technologies": "Engineering",
    "Health": "Health",
    "Society and Culture": "Society & Culture",
    "Education": "Education",
    "Natural and Physical Sciences": "Sciences",
    "Creative Arts": "Creative Arts",
    "Architecture and Building": "Architecture & Building",
    "Agriculture, Environmental and Related Studies": "Agriculture & Environment",
}

# --------------------------------------------------------------- sectors
SECTOR_ORDER = ["Higher Education", "VET", "ELICOS", "Schools", "Non-award"]

# --------------------------------------------------------------- regions
# The Department's 9 regions (+ Unknown), merged to 3 colour classes plus a
# grey "Rest of world" for Maps 1 and 3. On a map every colour sits beside
# every other, and only about three hues stay distinguishable under colour-
# blindness that way (validated with the dataviz palette checker,
# --pairs all). The three groups are also the story: South Asia rising,
# East/South-East Asia established, Latin America arriving.
REGION_GROUP = {
    "Southern and Central Asia": "South & Central Asia",
    "North-East Asia": "East & South-East Asia",
    "South-East Asia": "East & South-East Asia",
    "Americas": "Americas",
    "Sub-Saharan Africa": "Rest of world",
    "North-West Europe": "Rest of world",
    "Southern and Eastern Europe": "Rest of world",
    "North Africa and the Middle East": "Rest of world",
    "Oceania and Antarctica": "Rest of world",
    "Unknown": "Rest of world",
}
REGION_ORDER = ["South & Central Asia", "East & South-East Asia", "Americas", "Rest of world"]

# ---------------------------------------------------------------- states
STATE_ABBR = {
    "New South Wales": "NSW", "Victoria": "VIC", "Queensland": "QLD",
    "Western Australia": "WA", "South Australia": "SA", "Tasmania": "TAS",
    "Australian Capital Territory": "ACT", "Northern Territory": "NT",
}

# ---------------------------------------------------- university groups
GO8 = {
    "The Australian National University", "The University of Sydney",
    "University of New South Wales", "The University of Queensland",
    "The University of Adelaide", "The University of Melbourne",
    "Monash University", "The University of Western Australia",
}
PRIVATE_UNIS = {
    "Bond University", "Torrens University Australia",
    "Carnegie Mellon University Australia", "The University of Notre Dame Australia",
    "Avondale University", "University of Divinity",
}
# Aggregate rows in the higher-education data. They're buckets of many
# small providers, not institutions, so they're left out of per-provider charts.
HE_BUCKETS = {
    "Non-University Higher Education Providers",
    "Private Universities and Non-University Higher Education Providers",
}
# Australian Catholic University reports all enrolments as "Multi-State".
# For the state filter on Map 4 it's assigned to its head-office state.
HOME_STATE_OVERRIDE = {"Australian Catholic University": "NSW"}


def short_uni(name: str) -> str:
    """'The University of Sydney' -> 'Sydney'; for tight chart labels."""
    special = {
        "The Australian National University": "ANU",
        "University of New South Wales": "UNSW",
        "University of Technology Sydney": "UTS",
        "Queensland University of Technology": "QUT",
        "RMIT University": "RMIT",
        "CQUniversity": "CQU",
        "Australian Catholic University": "ACU",
        "Batchelor Institute of Indigenous Tertiary Education": "Batchelor Institute",
        "The University of Notre Dame Australia": "Notre Dame",
        "Carnegie Mellon University Australia": "Carnegie Mellon Aus.",
        "Swinburne University of Technology": "Swinburne",
        "University of Southern Queensland": "UniSQ",
        "University of the Sunshine Coast": "UniSC",
        "University of South Australia": "UniSA",
    }
    if name in special:
        return special[name]
    s = name
    for prefix in ("The University of ", "University of "):
        if s.startswith(prefix):
            s = s[len(prefix):]
    for suffix in (" University Australia", " University"):
        if s.endswith(suffix):
            s = s[: -len(suffix)]
    return s
