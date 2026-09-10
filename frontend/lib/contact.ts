export const CONTACT = {
  name: "Kenean Dita Meleta",
  email: "Keneansufa@gmail.com",
  phone: "+251923759696",
  phoneDisplay: "+251 923 759 696",
  telegram: "KeneanDita",
  website: "https://keneandita.me",
  github: "https://github.com/KeneanDita/African-Market-Data-API",
} as const;

export const CONTACT_LINKS = {
  email: (subject?: string) => `mailto:${CONTACT.email}${subject ? `?subject=${encodeURIComponent(subject)}` : ""}`,
  telegram: `https://t.me/${CONTACT.telegram}`,
  whatsapp: (text?: string) => `https://wa.me/${CONTACT.phone.replace("+", "")}${text ? `?text=${encodeURIComponent(text)}` : ""}`,
};

export const SOURCES = [
  { name: "World Bank WDI", href: "https://data.worldbank.org/indicator" },
  { name: "IMF World Economic Outlook", href: "https://www.imf.org/external/datamapper/datasets/WEO" },
  { name: "WHO Global Health Observatory", href: "https://www.who.int/data/gho" },
  { name: "UN Population Division", href: "https://population.un.org/dataportal/" },
];
