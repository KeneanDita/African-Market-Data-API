"""Seed data for the 87 indicators served by the API.

Each entry: (code, name, category, subcategory, unit, aggregation, source, source_code, description)
`source_code` is the identifier in the upstream system (World Bank WDI code, IMF WEO code, WHO GHO code).
A null source_code means no free machine-readable feed exists yet; the indicator is defined so it can
be populated later (e.g. from national statistics bureaus) without a schema change.
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.indicator import Indicator

WB = "World Bank"
IMF = "IMF"
WHO = "WHO"
UN = "UN Population Division"

INDICATORS: list[tuple] = [
    # ---------------- Economy (25)
    ("GDP_CURRENT_USD", "GDP (current US$)", "economy", "output", "USD", "sum", WB, "NY.GDP.MKTP.CD", "Gross domestic product at purchaser's prices in current US dollars."),
    ("GDP_PPP_USD", "GDP, PPP (current international $)", "economy", "output", "international_USD", "sum", WB, "NY.GDP.MKTP.PP.CD", "GDP converted to international dollars using purchasing power parity rates."),
    ("GDP_GROWTH_ANNUAL", "GDP growth (annual %)", "economy", "output", "percent", "mean", WB, "NY.GDP.MKTP.KD.ZG", "Annual percentage growth rate of GDP at market prices based on constant local currency."),
    ("GDP_PER_CAPITA_USD", "GDP per capita (current US$)", "economy", "output", "USD", "mean", WB, "NY.GDP.PCAP.CD", "Gross domestic product divided by midyear population."),
    ("GDP_PER_CAPITA_PPP", "GDP per capita, PPP (current international $)", "economy", "output", "international_USD", "mean", WB, "NY.GDP.PCAP.PP.CD", "GDP per capita based on purchasing power parity."),
    ("GNI_CURRENT_USD", "GNI (current US$)", "economy", "income", "USD", "sum", WB, "NY.GNP.MKTP.CD", "Gross national income in current US dollars."),
    ("GNI_PER_CAPITA_ATLAS", "GNI per capita, Atlas method (current US$)", "economy", "income", "USD", "mean", WB, "NY.GNP.PCAP.CD", "GNI per capita converted using the World Bank Atlas method."),
    ("INFLATION_ANNUAL", "Inflation, consumer prices (annual %)", "economy", "prices", "percent", "mean", WB, "FP.CPI.TOTL.ZG", "Annual percentage change in the cost to the average consumer of acquiring a basket of goods and services."),
    ("INFLATION_CONSUMER_PRICES", "Consumer price index (2010 = 100)", "economy", "prices", "index", "mean", WB, "FP.CPI.TOTL", "Consumer price index reflecting changes in the cost of a fixed basket of goods, 2010 = 100."),
    ("UNEMPLOYMENT_RATE", "Unemployment, total (% of labor force)", "economy", "labor", "percent", "mean", WB, "SL.UEM.TOTL.ZS", "Share of the labor force that is without work but available for and seeking employment (ILO modeled estimate)."),
    ("YOUTH_UNEMPLOYMENT", "Unemployment, youth total (% of labor force ages 15-24)", "economy", "labor", "percent", "mean", WB, "SL.UEM.1524.ZS", "Share of the labor force ages 15-24 without work but available for and seeking employment."),
    ("GOVERNMENT_DEBT_GDP", "General government gross debt (% of GDP)", "economy", "fiscal", "percent_gdp", "mean", IMF, "GGXWDG_NGDP", "Gross debt of the general government as a share of GDP (IMF World Economic Outlook)."),
    ("FISCAL_BALANCE_GDP", "General government net lending/borrowing (% of GDP)", "economy", "fiscal", "percent_gdp", "mean", IMF, "GGXCNL_NGDP", "Overall fiscal balance of the general government as a share of GDP."),
    ("CURRENT_ACCOUNT_BALANCE_GDP", "Current account balance (% of GDP)", "economy", "external", "percent_gdp", "mean", WB, "BN.CAB.XOKA.GD.ZS", "Sum of net exports of goods and services, net primary income, and net secondary income as a share of GDP."),
    ("FOREIGN_RESERVES_USD", "Total reserves (includes gold, current US$)", "economy", "external", "USD", "sum", WB, "FI.RES.TOTL.CD", "Holdings of monetary gold, SDRs, IMF reserve position, and foreign exchange under monetary authority control."),
    ("FOREIGN_INVESTMENT_NET", "Foreign direct investment, net inflows (BoP, current US$)", "economy", "investment", "USD", "sum", WB, "BX.KLT.DINV.CD.WD", "Net inflows of investment to acquire a lasting management interest in an enterprise operating in the economy."),
    ("FOREIGN_INVESTMENT_INFLOWS", "Foreign direct investment, net inflows (% of GDP)", "economy", "investment", "percent_gdp", "mean", WB, "BX.KLT.DINV.WD.GD.ZS", "FDI net inflows as a share of GDP."),
    ("REMITTANCES_INFLOWS_USD", "Personal remittances, received (current US$)", "economy", "external", "USD", "sum", WB, "BX.TRF.PWKR.CD.DT", "Personal transfers and compensation of employees received from abroad."),
    ("REMITTANCES_GDP_PCT", "Personal remittances, received (% of GDP)", "economy", "external", "percent_gdp", "mean", WB, "BX.TRF.PWKR.DT.GD.ZS", "Personal remittances received as a share of GDP."),
    ("EXPORTS_CURRENT_USD", "Exports of goods and services (current US$)", "economy", "trade", "USD", "sum", WB, "NE.EXP.GNFS.CD", "Value of all goods and market services provided to the rest of the world."),
    ("IMPORTS_CURRENT_USD", "Imports of goods and services (current US$)", "economy", "trade", "USD", "sum", WB, "NE.IMP.GNFS.CD", "Value of all goods and market services received from the rest of the world."),
    ("TRADE_BALANCE_USD", "External balance on goods and services (current US$)", "economy", "trade", "USD", "sum", WB, "NE.RSB.GNFS.CD", "Exports of goods and services minus imports of goods and services."),
    ("TRADE_GDP_PERCENT", "Trade (% of GDP)", "economy", "trade", "percent_gdp", "mean", WB, "NE.TRD.GNFS.ZS", "Sum of exports and imports of goods and services as a share of GDP."),
    ("GINI_INDEX", "Gini index", "economy", "inequality", "index", "mean", WB, "SI.POV.GINI", "Extent to which the distribution of income deviates from a perfectly equal distribution (0 = equality, 100 = inequality)."),
    ("POVERTY_RATE", "Poverty headcount ratio at national poverty lines (% of population)", "economy", "poverty", "percent", "mean", WB, "SI.POV.NAHC", "Percentage of the population living below the national poverty line."),
    # ---------------- Demographics (18)
    ("POPULATION_TOTAL", "Population, total", "demographics", "population", "people", "sum", WB, "SP.POP.TOTL", "Midyear estimate of all residents regardless of legal status or citizenship."),
    ("POPULATION_GROWTH", "Population growth (annual %)", "demographics", "population", "percent", "mean", WB, "SP.POP.GROW", "Exponential rate of growth of midyear population."),
    ("POPULATION_DENSITY", "Population density (people per sq. km of land area)", "demographics", "population", "people_per_km2", "mean", WB, "EN.POP.DNST", "Midyear population divided by land area in square kilometers."),
    ("URBAN_POPULATION", "Urban population", "demographics", "urbanization", "people", "sum", WB, "SP.URB.TOTL", "People living in urban areas as defined by national statistical offices."),
    ("URBAN_POPULATION_PCT", "Urban population (% of total population)", "demographics", "urbanization", "percent", "mean", WB, "SP.URB.TOTL.IN.ZS", "Share of the population living in urban areas."),
    ("RURAL_POPULATION", "Rural population", "demographics", "urbanization", "people", "sum", WB, "SP.RUR.TOTL", "Difference between total population and urban population."),
    ("MEDIAN_AGE", "Median age of population (years)", "demographics", "age_structure", "years", "mean", UN, "WPP:MedianAgePop", "Age that divides the population into two numerically equal groups (UN World Population Prospects)."),
    ("BIRTH_RATE", "Birth rate, crude (per 1,000 people)", "demographics", "vital_statistics", "per_1000", "mean", WB, "SP.DYN.CBRT.IN", "Number of live births occurring during the year per 1,000 midyear population."),
    ("DEATH_RATE", "Death rate, crude (per 1,000 people)", "demographics", "vital_statistics", "per_1000", "mean", WB, "SP.DYN.CDRT.IN", "Number of deaths occurring during the year per 1,000 midyear population."),
    ("FERTILITY_RATE", "Fertility rate, total (births per woman)", "demographics", "vital_statistics", "births_per_woman", "mean", WB, "SP.DYN.TFRT.IN", "Number of children that would be born to a woman if she lived to the end of her childbearing years."),
    ("INFANT_MORTALITY", "Mortality rate, infant (per 1,000 live births)", "demographics", "mortality", "per_1000_births", "mean", WB, "SP.DYN.IMRT.IN", "Number of infants dying before reaching one year of age per 1,000 live births."),
    ("UNDER5_MORTALITY", "Mortality rate, under-5 (per 1,000 live births)", "demographics", "mortality", "per_1000_births", "mean", WB, "SH.DYN.MORT", "Probability per 1,000 that a newborn will die before reaching age five."),
    ("LIFE_EXPECTANCY", "Life expectancy at birth, total (years)", "demographics", "mortality", "years", "mean", WB, "SP.DYN.LE00.IN", "Number of years a newborn would live if prevailing mortality patterns stayed the same."),
    ("LIFE_EXPECTANCY_MALE", "Life expectancy at birth, male (years)", "demographics", "mortality", "years", "mean", WB, "SP.DYN.LE00.MA.IN", "Life expectancy at birth for males."),
    ("LIFE_EXPECTANCY_FEMALE", "Life expectancy at birth, female (years)", "demographics", "mortality", "years", "mean", WB, "SP.DYN.LE00.FE.IN", "Life expectancy at birth for females."),
    ("NET_MIGRATION", "Net migration", "demographics", "migration", "people", "sum", WB, "SM.POP.NETM", "Total number of immigrants less the annual number of emigrants, including citizens and noncitizens."),
    ("DEPENDENCY_RATIO", "Age dependency ratio (% of working-age population)", "demographics", "age_structure", "percent", "mean", WB, "SP.POP.DPND", "Ratio of dependents (younger than 15 or older than 64) to the working-age population."),
    ("YOUTH_POPULATION_PCT", "Population ages 0-14 (% of total population)", "demographics", "age_structure", "percent", "mean", WB, "SP.POP.0014.TO.ZS", "Share of the population aged 0 to 14."),
    # ---------------- Health (15)
    ("HEALTH_EXPENDITURE_GDP", "Current health expenditure (% of GDP)", "health", "financing", "percent_gdp", "mean", WB, "SH.XPD.CHEX.GD.ZS", "Level of current health expenditure expressed as a percentage of GDP."),
    ("HEALTH_EXPENDITURE_PER_CAPITA", "Current health expenditure per capita (current US$)", "health", "financing", "USD", "mean", WB, "SH.XPD.CHEX.PC.CD", "Current expenditures on health per capita in current US dollars."),
    ("PHYSICIANS_PER_1000", "Physicians (per 1,000 people)", "health", "workforce", "per_1000", "mean", WB, "SH.MED.PHYS.ZS", "Generalist and specialist medical practitioners per 1,000 people."),
    ("HOSPITAL_BEDS_PER_1000", "Hospital beds (per 1,000 people)", "health", "infrastructure", "per_1000", "mean", WB, "SH.MED.BEDS.ZS", "Inpatient beds available in public, private, general, and specialized hospitals per 1,000 people."),
    ("IMMUNIZATION_DTP", "Immunization, DPT (% of children ages 12-23 months)", "health", "immunization", "percent", "mean", WB, "SH.IMM.IDPT", "Share of children ages 12-23 months who received DPT vaccinations."),
    ("IMMUNIZATION_MEASLES", "Immunization, measles (% of children ages 12-23 months)", "health", "immunization", "percent", "mean", WB, "SH.IMM.MEAS", "Share of children ages 12-23 months who received the measles vaccination."),
    ("HIV_PREVALENCE", "Prevalence of HIV, total (% of population ages 15-49)", "health", "disease", "percent", "mean", WB, "SH.DYN.AIDS.ZS", "Percentage of people ages 15-49 who are infected with HIV."),
    ("MALARIA_INCIDENCE", "Incidence of malaria (per 1,000 population at risk)", "health", "disease", "per_1000_at_risk", "mean", WB, "SH.MLR.INCD.P3", "Number of new malaria cases per 1,000 population at risk each year."),
    ("TUBERCULOSIS_INCIDENCE", "Incidence of tuberculosis (per 100,000 people)", "health", "disease", "per_100000", "mean", WB, "SH.TBS.INCD", "Estimated number of new and relapse tuberculosis cases per 100,000 population."),
    ("MATERNAL_MORTALITY", "Maternal mortality ratio (per 100,000 live births)", "health", "mortality", "per_100000_births", "mean", WB, "SH.STA.MMRT", "Number of women who die from pregnancy-related causes per 100,000 live births."),
    ("ACCESS_TO_SANITATION", "People using at least basic sanitation services (% of population)", "health", "wash", "percent", "mean", WB, "SH.STA.BASS.ZS", "Share of the population using improved sanitation facilities not shared with other households."),
    ("ACCESS_TO_WATER", "People using at least basic drinking water services (% of population)", "health", "wash", "percent", "mean", WB, "SH.H2O.BASW.ZS", "Share of the population drinking water from an improved source within a 30-minute round trip."),
    ("STUNTING_CHILDREN", "Prevalence of stunting, height for age (% of children under 5)", "health", "nutrition", "percent", "mean", WB, "SH.STA.STNT.ZS", "Share of children under 5 whose height for age is more than two standard deviations below the median."),
    ("WASTING_CHILDREN", "Prevalence of wasting, weight for height (% of children under 5)", "health", "nutrition", "percent", "mean", WB, "SH.STA.WAST.ZS", "Share of children under 5 whose weight for height is more than two standard deviations below the median."),
    ("OBESITY_ADULT", "Prevalence of obesity among adults, BMI >= 30 (age-standardized %)", "health", "nutrition", "percent", "mean", WHO, "NCD_BMI_30A", "Age-standardized share of adults (18+) with a body mass index of 30 or more (WHO Global Health Observatory)."),
    # ---------------- Education (12)
    ("LITERACY_RATE", "Literacy rate, adult total (% of people ages 15 and above)", "education", "literacy", "percent", "mean", WB, "SE.ADT.LITR.ZS", "Share of people ages 15 and above who can read and write a short simple statement about everyday life."),
    ("LITERACY_RATE_MALE", "Literacy rate, adult male (% of males ages 15 and above)", "education", "literacy", "percent", "mean", WB, "SE.ADT.LITR.MA.ZS", "Adult literacy rate for males."),
    ("LITERACY_RATE_FEMALE", "Literacy rate, adult female (% of females ages 15 and above)", "education", "literacy", "percent", "mean", WB, "SE.ADT.LITR.FE.ZS", "Adult literacy rate for females."),
    ("SCHOOL_ENROLLMENT_PRIMARY", "School enrollment, primary (% gross)", "education", "enrollment", "percent", "mean", WB, "SE.PRM.ENRR", "Total primary enrollment as a share of the population of official primary education age."),
    ("SCHOOL_ENROLLMENT_SECONDARY", "School enrollment, secondary (% gross)", "education", "enrollment", "percent", "mean", WB, "SE.SEC.ENRR", "Total secondary enrollment as a share of the population of official secondary education age."),
    ("SCHOOL_ENROLLMENT_TERTIARY", "School enrollment, tertiary (% gross)", "education", "enrollment", "percent", "mean", WB, "SE.TER.ENRR", "Total tertiary enrollment as a share of the five-year age group following secondary school leaving."),
    ("EDUCATION_EXPENDITURE_GDP", "Government expenditure on education, total (% of GDP)", "education", "financing", "percent_gdp", "mean", WB, "SE.XPD.TOTL.GD.ZS", "General government expenditure on education as a share of GDP."),
    ("PUPIL_TEACHER_RATIO_PRIMARY", "Pupil-teacher ratio, primary", "education", "quality", "ratio", "mean", WB, "SE.PRM.ENRL.TC.ZS", "Average number of pupils per teacher in primary school."),
    ("TRAINED_TEACHERS_PCT", "Trained teachers in primary education (% of total teachers)", "education", "quality", "percent", "mean", WB, "SE.PRM.TCAQ.ZS", "Share of primary school teachers who have received the minimum organized teacher training."),
    ("COMPLETION_RATE_PRIMARY", "Primary completion rate, total (% of relevant age group)", "education", "attainment", "percent", "mean", WB, "SE.PRM.CMPT.ZS", "Number of new entrants in the last grade of primary education as a share of the population at the entrance age."),
    ("COMPLETION_RATE_SECONDARY", "Lower secondary completion rate, total (% of relevant age group)", "education", "attainment", "percent", "mean", WB, "SE.SEC.CMPT.LO.ZS", "Number of new entrants in the last grade of lower secondary education as a share of the population at the entrance age."),
    ("OUT_OF_SCHOOL_CHILDREN", "Children out of school, primary", "education", "access", "children", "sum", WB, "SE.PRM.UNER", "Number of primary-school-age children not enrolled in primary or secondary school."),
    # ---------------- Infrastructure & Tech (10)
    ("ACCESS_TO_ELECTRICITY", "Access to electricity (% of population)", "infrastructure", "energy", "percent", "mean", WB, "EG.ELC.ACCS.ZS", "Share of the population with access to electricity."),
    ("RENEWABLE_ENERGY_PCT", "Renewable energy consumption (% of total final energy consumption)", "infrastructure", "energy", "percent", "mean", WB, "EG.FEC.RNEW.ZS", "Share of renewables in total final energy consumption."),
    ("INTERNET_USERS_PCT", "Individuals using the Internet (% of population)", "infrastructure", "digital", "percent", "mean", WB, "IT.NET.USER.ZS", "Share of individuals who have used the Internet from any location in the last three months."),
    ("MOBILE_SUBSCRIPTIONS", "Mobile cellular subscriptions (per 100 people)", "infrastructure", "digital", "per_100", "mean", WB, "IT.CEL.SETS.P2", "Subscriptions to a public mobile telephone service per 100 people."),
    ("BROADBAND_SUBSCRIPTIONS", "Fixed broadband subscriptions (per 100 people)", "infrastructure", "digital", "per_100", "mean", WB, "IT.NET.BBND.P2", "Fixed subscriptions to high-speed access to the public Internet per 100 people."),
    ("SECURE_INTERNET_SERVERS", "Secure Internet servers (per 1 million people)", "infrastructure", "digital", "per_million", "mean", WB, "IT.NET.SECR.P6", "Number of distinct, publicly-trusted TLS/SSL certificates per 1 million people."),
    ("ROAD_DENSITY", "Road density (km of road per 100 sq. km of land area)", "infrastructure", "transport", "km_per_100km2", "mean", WB, "IS.ROD.DNST.K2", "Ratio of the length of the country's total road network to the country's land area (legacy WDI series)."),
    ("RAIL_LINES_KM", "Rail lines (total route-km)", "infrastructure", "transport", "km", "sum", WB, "IS.RRS.TOTL.KM", "Length of railway route available for train service, irrespective of the number of parallel tracks."),
    ("AIR_TRANSPORT_PASSENGERS", "Air transport, passengers carried", "infrastructure", "transport", "passengers", "sum", WB, "IS.AIR.PSGR", "Domestic and international aircraft passengers of air carriers registered in the country."),
    ("CO2_EMISSIONS_PER_CAP", "CO2 emissions per capita (t CO2e/capita, excl. LULUCF)", "infrastructure", "environment", "tonnes_per_capita", "mean", WB, "EN.GHG.CO2.PC.CE.AR5", "Carbon dioxide emissions per person, excluding land use change and forestry."),
    # ---------------- Finance (7)
    ("BANK_ACCOUNTS_PCT", "Account ownership at a financial institution or mobile-money provider (% of population ages 15+)", "finance", "inclusion", "percent", "mean", WB, "FX.OWN.TOTL.ZS", "Share of adults who report having an account at a bank, another financial institution, or a mobile money service (Global Findex)."),
    ("MOBILE_MONEY_ACCOUNTS_PCT", "Mobile money account (% of population ages 15+)", "finance", "inclusion", "percent", "mean", "World Bank Global Findex", None, "Share of adults who report personally using a mobile money service in the past year (Global Findex; no WDI feed)."),
    ("DOMESTIC_CREDIT_GDP", "Domestic credit to private sector (% of GDP)", "finance", "credit", "percent_gdp", "mean", WB, "FS.AST.PRVT.GD.ZS", "Financial resources provided to the private sector by financial corporations as a share of GDP."),
    ("STOCK_MARKET_CAPITALIZATION_GDP", "Market capitalization of listed domestic companies (% of GDP)", "finance", "markets", "percent_gdp", "mean", WB, "CM.MKT.LCAP.GD.ZS", "Share price times the number of shares outstanding for listed domestic companies, as a share of GDP."),
    ("MICROFINANCE_BORROWERS", "Active microfinance borrowers", "finance", "inclusion", "people", "sum", "MIX Market", None, "Number of active borrowers reported by microfinance institutions (no free machine-readable feed; populated from national sources)."),
    ("INSURANCE_PENETRATION", "Insurance penetration (premiums % of GDP)", "finance", "insurance", "percent_gdp", "mean", "African Development Bank", None, "Total insurance premiums as a share of GDP (populated from AfDB / national regulators)."),
    ("INTEREST_RATE_LENDING", "Lending interest rate (%)", "finance", "rates", "percent", "mean", WB, "FR.INR.LEND", "Bank rate that usually meets the short- and medium-term financing needs of the private sector."),
]

assert len(INDICATORS) == 87, f"expected 87 indicators, got {len(INDICATORS)}"
assert len({i[0] for i in INDICATORS}) == 87, "duplicate indicator codes"

CATEGORIES = sorted({i[2] for i in INDICATORS})


def seed_indicators(db: Session) -> int:
    """Insert missing indicators and refresh metadata on existing ones. Returns rows created."""
    existing = {i.code: i for i in db.query(Indicator).all()}
    created = 0
    for code, name, category, subcategory, unit, aggregation, source, source_code, description in INDICATORS:
        row = existing.get(code)
        if row is None:
            row = Indicator(code=code)
            db.add(row)
            created += 1
        row.name = name
        row.category = category
        row.subcategory = subcategory
        row.unit = unit
        row.aggregation = aggregation
        row.source = source
        row.source_code = source_code
        row.description = description
    db.commit()
    return created
