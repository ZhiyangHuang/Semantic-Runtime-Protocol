# Provenance

This directory preserves machine-readable and human-readable provenance that is useful for release inspection but is not itself a live runtime dependency.

The release gate should treat this directory as an audit asset, not as a required historical archive boundary.

Current intent:

- preserve release provenance in a dedicated audit home
- keep archived historical material out of the live dependency graph
- avoid using `audit/provenance/docs_archive/` as an executable release requirement

