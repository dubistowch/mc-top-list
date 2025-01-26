# ADR 0006: Data Scraping Policy

## Status
Accepted

## Context
As part of the "Minecraft 插件模組爬蟲" project, we aim to scrape data from various websites that provide Minecraft plugins and mods. However, some platforms explicitly prohibit data scraping in their Terms of Service (ToS) or End User License Agreement (EULA). To ensure compliance with legal and ethical guidelines, we need to decide whether to proceed with scraping these sites.

The following websites were reviewed for their scraping policies:
- **SpigotMC**: Prohibits data scraping.
- **BuiltByBit (formerly MC-Market)**: Prohibits data scraping but provides an API for automation under specific conditions.
- **Polymart**: No explicit mention of scraping in the ToS.
- **CurseForge**: No explicit mention of scraping in the ToS.
- **Modrinth**: No explicit mention of scraping in the ToS.
- **Planet Minecraft**: No explicit mention of scraping in the ToS.
- **Hangar (PaperMC)**: No explicit mention of scraping in the ToS.
- **Bukkit**: No explicit mention of scraping in the ToS.

## Decision
We will **not** scrape websites that explicitly prohibit data scraping in their Terms of Service (ToS) or End User License Agreement (EULA). For sites without explicit policies, we will assess their scraping stance by:
1. Reviewing their publicly available documentation or terms.
2. Contacting site administrators for clarification, if necessary.

**Implementation Guidelines:**
- SpigotMC: Excluded from scraping due to explicit prohibition.
- BuiltByBit: Excluded from scraping unless the official API is used under proper authorization.
- Other Sites (Polymart, CurseForge, Modrinth, Planet Minecraft, Hangar, Bukkit): Tentatively included in scraping, pending further clarification or review of their policies.

## Consequences
- This decision ensures legal and ethical compliance, reducing risks of project disruption due to ToS violations.
- Some potentially valuable data sources (e.g., SpigotMC and BuiltByBit) will not be included in the scraping pipeline unless alternative solutions (e.g., API usage) are implemented.
- Additional time and effort may be required to clarify the policies of sites with ambiguous terms.

## Related ADRs
- None at this time.

## Date
January 26, 2025
