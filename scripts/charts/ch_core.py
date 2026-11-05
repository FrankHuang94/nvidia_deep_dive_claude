"""Core charts owned by the orchestrator (README / executive summary)."""
from style import Chart, NV, GEN_PAST, INK, load, register, sources_of, label_bars


@register
def revenue_by_fiscal_year():
    df = load("financials.csv")
    d = df[(df.metric == "revenue_total") & (df.period_type == "FY")].copy()
    d = d.sort_values("period_end")
    first, last = d.iloc[0], d.iloc[-1]
    mult = last.value / first.value
    c = Chart(
        id="00-nvidia-revenue-by-fiscal-year",
        title=f"NVIDIA revenue grew ~{mult:.0f}× in six fiscal years, from ${first.value:.1f}B to ${last.value:.0f}B",
        subtitle="Total revenue by fiscal year, US$ billions (NVIDIA's fiscal year ends in late January)",
        alt=(f"Bar chart of NVIDIA total revenue by fiscal year: ${first.value:.1f}B in {first.period} rising to "
             f"${last.value:.1f}B in {last.period}, roughly {mult:.0f} times higher, with the inflection in FY2024."),
        data=["financials.csv"], chapters=["00", "01", "13", "18"],
        source="NVIDIA 10-K and 8-K filings", source_ids=sources_of(d),
    )
    fig, ax = c.figure(width=10, height=5.6)
    colors = [GEN_PAST] * (len(d) - 1) + [NV]
    bars = ax.bar(d.period, d.value, color=colors, width=0.62)
    label_bars(ax, bars, fmt="${:,.1f}B")
    ax.set_ylim(0, d.value.max() * 1.15)
    ax.annotate("ChatGPT launch\n(Nov 2022) → FY2024\ninflection", xy=(4, d.value.iloc[4]), xytext=(2.2, d.value.max() * 0.55),
                fontsize=9, color=INK["text"], arrowprops=dict(arrowstyle="->", color=INK["muted"]))
    c.save(fig, ax, xlabel="Fiscal year", ylabel="Revenue (US$ B)")
