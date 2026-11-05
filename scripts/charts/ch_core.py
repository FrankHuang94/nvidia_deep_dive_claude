"""Core charts owned by the orchestrator (README / executive summary)."""
from style import Chart, NV, GEN_PAST, INK, load, register, sources_of, label_bars


@register
def revenue_by_fiscal_year():
    df = load("financials.csv")
    d = df[(df.metric == "revenue_total") & (df.period_type == "FY")].copy()
    d = d.sort_values("period_end")
    d = d.drop_duplicates("period", keep="last").reset_index(drop=True)
    first, last = d.iloc[0], d.iloc[-1]
    mult = last.value / first.value
    nyears = len(d) - 1
    words = {6: "six", 7: "seven", 8: "eight", 9: "nine", 10: "ten", 11: "eleven"}
    c = Chart(
        id="00-nvidia-revenue-by-fiscal-year",
        title=f"NVIDIA revenue grew ~{mult:.0f}× in {words.get(nyears, nyears)} fiscal years, from ${first.value:.1f}B to ${last.value:.0f}B",
        subtitle="Total revenue by fiscal year, US$ billions (NVIDIA's fiscal year ends in late January)",
        alt=(f"Bar chart of NVIDIA total revenue by fiscal year: ${first.value:.1f}B in {first.period} rising to "
             f"${last.value:.1f}B in {last.period}, roughly {mult:.0f} times higher, with the inflection in FY2024."),
        data=["financials.csv"], chapters=["00", "01", "13", "18"],
        source="NVIDIA 10-K and 8-K filings", source_ids=sources_of(d),
    )
    fig, ax = c.figure(width=10, height=5.6)
    colors = [GEN_PAST] * (len(d) - 1) + [NV]
    labels = [p.replace("FY20", "FY") for p in d.period]
    bars = ax.bar(labels, d.value, color=colors, width=0.62)
    label_bars(ax, bars, fmt="${:,.1f}B", fontsize=8)
    ax.set_ylim(0, d.value.max() * 1.15)
    if "FY2024" in set(d.period):  # annotate the AI inflection wherever it sits in the series
        i24 = int(d.index[d.period == "FY2024"][0])
        ax.annotate("ChatGPT launch\n(Nov 2022) → FY2024\ninflection", xy=(i24, d.value.iloc[i24]),
                    xytext=(max(i24 - 3.2, 0), d.value.max() * 0.55), fontsize=9, color=INK["text"],
                    arrowprops=dict(arrowstyle="->", color=INK["muted"]))
    ax.set_axisbelow(True)
    c.save(fig, ax, xlabel="Fiscal year", ylabel="Revenue (US$ B)")
