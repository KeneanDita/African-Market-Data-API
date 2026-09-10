import type { Country } from "@/lib/api";
import { formatValue } from "@/lib/api";

export default function CountryCard({ country, onSelect, selected }: { country: Country; onSelect?: (iso2: string) => void; selected?: boolean }) {
  return (
    <button
      type="button"
      onClick={() => onSelect?.(country.iso2)}
      className={`card group w-full p-5 text-left transition hover:-translate-y-0.5 hover:border-ink ${selected ? "border-accent" : ""}`}
    >
      <div className="flex items-start justify-between">
        <span className="eyebrow">{country.region}</span>
        <span className="num text-2xl text-line transition group-hover:text-accent">{country.iso2}</span>
      </div>
      <h3 className="display mt-6 text-2xl">{country.name}</h3>
      <p className="mt-1 text-xs text-muted">{country.capital}</p>
      <dl className="mt-5 grid grid-cols-2 gap-3 border-t border-line pt-3">
        <div>
          <dt className="eyebrow">Population</dt>
          <dd className="num mt-1 text-lg">{formatValue(country.population, "people")}</dd>
        </div>
        <div>
          <dt className="eyebrow">Currency</dt>
          <dd className="num mt-1 text-lg">{country.currency_code ?? "—"}</dd>
        </div>
      </dl>
    </button>
  );
}
