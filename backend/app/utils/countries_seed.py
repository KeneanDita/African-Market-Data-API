"""Seed data for all 54 African Union member states.

Regions follow the five African Union geographic regions. Population is left null here and
filled in from the latest POPULATION_TOTAL data point after the World Bank scrape runs.
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.country import Country

REGIONS = ["North Africa", "West Africa", "East Africa", "Central Africa", "Southern Africa"]

# (iso2, iso3, name, region, capital, currency, currency_code, area_km2, languages)
COUNTRIES: list[tuple] = [
    # ---- North Africa (6)
    ("DZ", "DZA", "Algeria", "North Africa", "Algiers", "Algerian Dinar", "DZD", 2_381_741, ["Arabic", "Tamazight", "French"]),
    ("EG", "EGY", "Egypt", "North Africa", "Cairo", "Egyptian Pound", "EGP", 1_002_450, ["Arabic"]),
    ("LY", "LBY", "Libya", "North Africa", "Tripoli", "Libyan Dinar", "LYD", 1_759_540, ["Arabic"]),
    ("MA", "MAR", "Morocco", "North Africa", "Rabat", "Moroccan Dirham", "MAD", 446_550, ["Arabic", "Tamazight", "French"]),
    ("SD", "SDN", "Sudan", "North Africa", "Khartoum", "Sudanese Pound", "SDG", 1_861_484, ["Arabic", "English"]),
    ("TN", "TUN", "Tunisia", "North Africa", "Tunis", "Tunisian Dinar", "TND", 163_610, ["Arabic", "French"]),
    # ---- West Africa (16)
    ("BJ", "BEN", "Benin", "West Africa", "Porto-Novo", "West African CFA Franc", "XOF", 114_763, ["French"]),
    ("BF", "BFA", "Burkina Faso", "West Africa", "Ouagadougou", "West African CFA Franc", "XOF", 274_200, ["French", "Mooré", "Dioula"]),
    ("CV", "CPV", "Cabo Verde", "West Africa", "Praia", "Cape Verdean Escudo", "CVE", 4_033, ["Portuguese", "Cape Verdean Creole"]),
    ("CI", "CIV", "Côte d'Ivoire", "West Africa", "Yamoussoukro", "West African CFA Franc", "XOF", 322_463, ["French"]),
    ("GM", "GMB", "Gambia", "West Africa", "Banjul", "Gambian Dalasi", "GMD", 11_295, ["English", "Mandinka", "Wolof"]),
    ("GH", "GHA", "Ghana", "West Africa", "Accra", "Ghanaian Cedi", "GHS", 238_533, ["English", "Akan", "Ewe"]),
    ("GN", "GIN", "Guinea", "West Africa", "Conakry", "Guinean Franc", "GNF", 245_857, ["French", "Fula", "Malinké"]),
    ("GW", "GNB", "Guinea-Bissau", "West Africa", "Bissau", "West African CFA Franc", "XOF", 36_125, ["Portuguese", "Kriol"]),
    ("LR", "LBR", "Liberia", "West Africa", "Monrovia", "Liberian Dollar", "LRD", 111_369, ["English"]),
    ("ML", "MLI", "Mali", "West Africa", "Bamako", "West African CFA Franc", "XOF", 1_240_192, ["French", "Bambara"]),
    ("MR", "MRT", "Mauritania", "West Africa", "Nouakchott", "Mauritanian Ouguiya", "MRU", 1_030_700, ["Arabic", "French"]),
    ("NE", "NER", "Niger", "West Africa", "Niamey", "West African CFA Franc", "XOF", 1_267_000, ["French", "Hausa", "Zarma"]),
    ("NG", "NGA", "Nigeria", "West Africa", "Abuja", "Nigerian Naira", "NGN", 923_768, ["English", "Hausa", "Yoruba", "Igbo"]),
    ("SN", "SEN", "Senegal", "West Africa", "Dakar", "West African CFA Franc", "XOF", 196_722, ["French", "Wolof"]),
    ("SL", "SLE", "Sierra Leone", "West Africa", "Freetown", "Sierra Leonean Leone", "SLE", 71_740, ["English", "Krio"]),
    ("TG", "TGO", "Togo", "West Africa", "Lomé", "West African CFA Franc", "XOF", 56_785, ["French", "Ewe", "Kabiyé"]),
    # ---- East Africa (18)
    ("BI", "BDI", "Burundi", "East Africa", "Gitega", "Burundian Franc", "BIF", 27_834, ["Kirundi", "French", "English"]),
    ("KM", "COM", "Comoros", "East Africa", "Moroni", "Comorian Franc", "KMF", 1_862, ["Comorian", "Arabic", "French"]),
    ("DJ", "DJI", "Djibouti", "East Africa", "Djibouti", "Djiboutian Franc", "DJF", 23_200, ["French", "Arabic", "Somali", "Afar"]),
    ("ER", "ERI", "Eritrea", "East Africa", "Asmara", "Eritrean Nakfa", "ERN", 117_600, ["Tigrinya", "Arabic", "English"]),
    ("ET", "ETH", "Ethiopia", "East Africa", "Addis Ababa", "Ethiopian Birr", "ETB", 1_104_300, ["Amharic", "Oromo", "Tigrinya", "Somali", "Afar"]),
    ("KE", "KEN", "Kenya", "East Africa", "Nairobi", "Kenyan Shilling", "KES", 580_367, ["Swahili", "English"]),
    ("MG", "MDG", "Madagascar", "East Africa", "Antananarivo", "Malagasy Ariary", "MGA", 587_041, ["Malagasy", "French"]),
    ("MW", "MWI", "Malawi", "East Africa", "Lilongwe", "Malawian Kwacha", "MWK", 118_484, ["English", "Chichewa"]),
    ("MU", "MUS", "Mauritius", "East Africa", "Port Louis", "Mauritian Rupee", "MUR", 2_040, ["English", "French", "Mauritian Creole"]),
    ("MZ", "MOZ", "Mozambique", "East Africa", "Maputo", "Mozambican Metical", "MZN", 801_590, ["Portuguese"]),
    ("RW", "RWA", "Rwanda", "East Africa", "Kigali", "Rwandan Franc", "RWF", 26_338, ["Kinyarwanda", "English", "French", "Swahili"]),
    ("SC", "SYC", "Seychelles", "East Africa", "Victoria", "Seychellois Rupee", "SCR", 455, ["Seychellois Creole", "English", "French"]),
    ("SO", "SOM", "Somalia", "East Africa", "Mogadishu", "Somali Shilling", "SOS", 637_657, ["Somali", "Arabic"]),
    ("SS", "SSD", "South Sudan", "East Africa", "Juba", "South Sudanese Pound", "SSP", 644_329, ["English"]),
    ("TZ", "TZA", "Tanzania", "East Africa", "Dodoma", "Tanzanian Shilling", "TZS", 947_303, ["Swahili", "English"]),
    ("UG", "UGA", "Uganda", "East Africa", "Kampala", "Ugandan Shilling", "UGX", 241_550, ["English", "Swahili", "Luganda"]),
    ("ZM", "ZMB", "Zambia", "East Africa", "Lusaka", "Zambian Kwacha", "ZMW", 752_618, ["English", "Bemba", "Nyanja"]),
    ("ZW", "ZWE", "Zimbabwe", "East Africa", "Harare", "Zimbabwe Gold", "ZWG", 390_757, ["English", "Shona", "Ndebele"]),
    # ---- Central Africa (9)
    ("AO", "AGO", "Angola", "Central Africa", "Luanda", "Angolan Kwanza", "AOA", 1_246_700, ["Portuguese"]),
    ("CM", "CMR", "Cameroon", "Central Africa", "Yaoundé", "Central African CFA Franc", "XAF", 475_442, ["French", "English"]),
    ("CF", "CAF", "Central African Republic", "Central Africa", "Bangui", "Central African CFA Franc", "XAF", 622_984, ["French", "Sango"]),
    ("TD", "TCD", "Chad", "Central Africa", "N'Djamena", "Central African CFA Franc", "XAF", 1_284_000, ["French", "Arabic"]),
    ("CG", "COG", "Republic of the Congo", "Central Africa", "Brazzaville", "Central African CFA Franc", "XAF", 342_000, ["French", "Lingala", "Kituba"]),
    ("CD", "COD", "Democratic Republic of the Congo", "Central Africa", "Kinshasa", "Congolese Franc", "CDF", 2_344_858, ["French", "Lingala", "Swahili", "Kikongo", "Tshiluba"]),
    ("GQ", "GNQ", "Equatorial Guinea", "Central Africa", "Malabo", "Central African CFA Franc", "XAF", 28_051, ["Spanish", "French", "Portuguese"]),
    ("GA", "GAB", "Gabon", "Central Africa", "Libreville", "Central African CFA Franc", "XAF", 267_668, ["French"]),
    ("ST", "STP", "São Tomé and Príncipe", "Central Africa", "São Tomé", "São Tomé and Príncipe Dobra", "STN", 964, ["Portuguese"]),
    # ---- Southern Africa (5)
    ("BW", "BWA", "Botswana", "Southern Africa", "Gaborone", "Botswana Pula", "BWP", 581_730, ["English", "Setswana"]),
    ("SZ", "SWZ", "Eswatini", "Southern Africa", "Mbabane", "Swazi Lilangeni", "SZL", 17_364, ["Swazi", "English"]),
    ("LS", "LSO", "Lesotho", "Southern Africa", "Maseru", "Lesotho Loti", "LSL", 30_355, ["Sesotho", "English"]),
    ("NA", "NAM", "Namibia", "Southern Africa", "Windhoek", "Namibian Dollar", "NAD", 825_615, ["English", "Oshiwambo", "Afrikaans"]),
    ("ZA", "ZAF", "South Africa", "Southern Africa", "Pretoria", "South African Rand", "ZAR", 1_219_090, ["Zulu", "Xhosa", "Afrikaans", "English", "Sepedi", "Setswana", "Sesotho"]),
]

assert len(COUNTRIES) == 54, f"expected 54 countries, got {len(COUNTRIES)}"

AFRICAN_ISO2_CODES: list[str] = [c[0] for c in COUNTRIES]
AFRICAN_ISO3_CODES: list[str] = [c[1] for c in COUNTRIES]
ISO3_TO_ISO2: dict[str, str] = {c[1]: c[0] for c in COUNTRIES}


def seed_countries(db: Session) -> int:
    """Insert missing countries and refresh static metadata on existing ones. Returns rows created."""
    existing = {c.iso2: c for c in db.query(Country).all()}
    created = 0
    for iso2, iso3, name, region, capital, currency, currency_code, area, languages in COUNTRIES:
        row = existing.get(iso2)
        if row is None:
            row = Country(iso2=iso2, iso3=iso3)
            db.add(row)
            created += 1
        row.name = name
        row.region = region
        row.capital = capital
        row.currency = currency
        row.currency_code = currency_code
        row.area_km2 = area
        row.languages = languages
    db.commit()
    return created
