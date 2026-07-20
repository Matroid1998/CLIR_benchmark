"""
Licensing and attribution text, one block per data source.

This text is a licence condition, not documentation. The Google Patents block is
required on anything derived from that BigQuery data and is reproduced verbatim
from the version reviewed for the published datasets.

It is keyed by source deliberately. The old exporter attached the Google Patents
attribution to every dataset it published, including the EPO-derived ones, which
credited the wrong provider; here each source carries its own block and
publishing a source with no declared attribution raises rather than defaulting.
"""

from __future__ import annotations

GOOGLE_PATENTS = """
### Google Patents Public Data

- **Source dataset:** Patent text (titles, abstracts) in this dataset is derived from **Google Patents Public Data** on BigQuery (`patents-public-data.patents.publications`), provided by IFI CLAIMS Patent Services and Google. See [Marketplace](https://console.cloud.google.com/marketplace/product/google_patents_public_datasets/google-patents-public-data) and [announcement](https://cloud.google.com/blog/topics/public-datasets/google-patents-public-datasets-connecting-public-paid-and-private-patent-data).
- **License:** That source data is made available under [**CC BY 4.0**](https://creativecommons.org/licenses/by/4.0/) (Creative Commons Attribution 4.0).
- **This dataset:** The corpus, questions, and answers (including all Q&A pairs and translations) form a **derived/adapted dataset** based on that source.
- **No endorsement:** This dataset is not affiliated with, endorsed by, or officially connected with Google or IFI CLAIMS. Only the underlying patent publication text is from that source; the Q&A generation and benchmark design are independent.
- **Scope:** Attribution and license refer only to the patent dataset content (bibliographic and abstract text from the public BigQuery tables). They do not cover other Google services, products, or UI content.
""".strip()

EPO_BULK = """
### EPO bulk full-text data

- **Source dataset:** Patent text in this dataset is derived from **EPO full-text data for EP publications**, obtained through the European Patent Office's Bulk Data Distribution Service (BDDS).
- **Terms:** EPO bulk data is published for re-use subject to the EPO's terms and conditions for its data services. Users of this dataset should consult the [EPO's open data terms](https://www.epo.org/en/searching-for-patents/data) for the conditions attached to the underlying publication text.
- **This dataset:** The corpus, questions, and answers form a **derived dataset** built from that source; the Q&A generation and benchmark design are independent of the EPO.
- **No endorsement:** This dataset is not affiliated with, endorsed by, or officially connected with the European Patent Office.
- **Note:** The Google Patents / IFI CLAIMS attribution does **not** apply to this data, which does not originate from that source.
""".strip()

ATTRIBUTIONS = {
    "google_patents": GOOGLE_PATENTS,
    "epo": EPO_BULK,
}

__all__ = ["ATTRIBUTIONS", "EPO_BULK", "GOOGLE_PATENTS"]
