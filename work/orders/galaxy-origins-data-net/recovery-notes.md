# Historical attribution corrections

Builder: codex-audit-places-sources, 2026-09-22. Root performs the independent final review; this note does not accept the order.

- SOAP no longer assigns the undocumented location of its private 1998 development to Redmond. The selected echo is the public W3C SOAP 1.1 Note of 8 May 2000 at the abstract standards-body place. The [original Note](https://www.w3.org/TR/2000/NOTE-SOAP-20000508/) was opened: its heading supplies the date, abstract supplies the XML protocol claim, and status explicitly says discussion only, not W3C endorsement. The topic's separate history still retains the earlier design chronology and Don Box source.
- gRPC retains its 26 February 2015 milestone and [Google announcement](https://developers.googleblog.com/introducing-grpc-a-new-open-source-http2-rpc-framework/). The page was opened and read: it announces open source availability, HTTP/2 and APIs/microservices. The origin now explicitly represents the online announcement, not an inferred Mountain View development site.
- BigQuery retains its 14 November 2011 milestone and [Google announcement](https://developers.googleblog.com/google-bigquery-service-big-data-analytics-at-google-speed/). The opened page dates the broader preview, web interface and REST API improvements. The origin explicitly describes online publication and makes no Mountain View claim.
- Redshift keeps Seattle and 28 November 2012, backed by the [same-day Amazon press release](https://press.aboutamazon.com/2012/11/amazon-web-services-announces-amazon-redshift). The opened release has a Seattle dateline and the limited-preview announcement. The origin says precisely that, without implying all engineering happened in Seattle.

The existing actor test now recognizes the already-supported abstract internet place. Primary origins, fifteen total origins, unique places within each topic, year checks and all other content constraints remain unchanged. No acceptance criteria were relaxed. The broad data-shelf criterion still depends on the sibling data-engineering origin order.

## Focused verification

The first focused run reported two expected stale-output failures after the source edits: the injected game payload and generated tree no longer matched. After `just tree` and the established cookbook/template/fork/syllabus generators, `uv run pytest -q tests/test_origins_data_net.py tests/test_places.py tests/test_topics.py` passed all 64 collected cases. Ruff check and format passed for the adjusted test file. All six c4 generator checks passed, as did the style guard, sink guard and `git diff --check`.

No full suite, browser suite, commit, push or acceptance ruling was performed in this bounded correction. The original four primary origins and remaining historical content were preserved. The data-engineering dependency still needs integration for the broad c2 shelf check.
