# Data-engineering origins research

The historical-attribution corrections below supersede the original Earth-location
choices and registry requests. Earlier entries remain as an audit trail, not final claims.

Read on 2026-09-22. Builder: codex-origins-data-engineering.

These are dated milestones, not claims to have found the invention of a whole field. The existing registry supplies an organisation's location; the event page supplies its actor and date. Online releases and a public specification commit use the internet because those are publication events.

| Topic | Event and source checked |
| --- | --- |
| airflow | Maxime Beauchemin starts Airflow at Airbnb in October 2014. [Primary source](https://airflow.apache.org/docs/apache-airflow/2.10.3/project.html) |
| arrow | The Apache Software Foundation announces Arrow as a top-level project on 17 February 2016. [Primary source](https://news.apache.org/foundation/entry/the_apache_software_foundation_announces87) |
| csv | RFC 4180 documents the CSV format and registers its text/csv media type in October 2005. [Primary source](https://www.rfc-editor.org/rfc/rfc4180.txt) |
| dagster | The Dagster team announces version 1.0 online on 5 August 2022, with stable software-defined assets. [Primary source](https://dagster.io/blog/dagster-1-0-hello) |
| datamap | Airbnb publicly announces Airflow in June 2015. [Primary source](https://airflow.apache.org/docs/apache-airflow/2.10.3/project.html) |
| dlt | Marcin Rudolf announces dlt 1.0.0 online on 16 September 2024, bringing database, file and REST API sources into the core library. [Primary source](https://dlthub.com/blog/dlt-v1) |
| duckdblab | Hannes Muehleisen and Mark Raasveldt create DuckDB at CWI Amsterdam in 2018. [Primary source](https://duckdb.foundation/) |
| iceberg | Apache Iceberg graduates from the Apache Incubator on 20 May 2020. [Primary source](https://incubator.apache.org/projects/iceberg.html) |
| jsonl | Ian Ward numbers the three JSON Lines requirements in the public website repository on 10 October 2013. [Primary source](https://github.com/wardi/jsonlines/commit/92c32d4496d1f0b789cc4840e6cd65e11ef51e94) |
| medallion | Databricks publishes guidance for Bronze, Silver and Gold data layers on 24 June 2022. [Primary source](https://www.databricks.com/blog/2022/06/24/data-warehousing-modeling-techniques-and-their-implementation-on-the-databricks-lakehouse-platform.html) |
| parquet | The Apache Software Foundation announces Parquet as a top-level project on 27 April 2015. [Primary source](https://news.apache.org/foundation/entry/the_apache_software_foundation_announces75) |
| polars | Ritchie Vink announces the Python Polars 1.0 release online on 1 July 2024. [Primary source](https://pola.rs/posts/announcing-polars-1/) |
| schemas | The Iceberg table specification moves to git and the Apache Software Foundation website on 23 June 2019. [Primary source](https://incubator.apache.org/projects/iceberg.html) |

## Missing registry entries

- `dbt-philadelphia`: [dbt's own press release](https://www.getdbt.com/blog/fishtown-analytics-rebrands-as-dbt-labs-closes-150m-to-develop-open-source-analytics-engineering-software) has the Philadelphia dateline. [Tristan Handy's account](https://www.getdbt.com/blog/whats-in-a-name) explicitly dates his and Drew's full-time work on dbt/Fishtown Analytics to July 2016. Use this event for `dbt`. [His later account](https://www.getdbt.com/blog/our-biggest-launch-event-yet) says dbt shipped data quality features in 2016; use that narrower event for `dataquality`.
- `linkedin-mountain-view`: [LinkedIn's July 2011 event announcement](https://www.linkedin.com/blog/engineering/archive/come-linkedin-hear-talk-about-kafka-our-open-source-distributed-pub-sub-messaging-system) explicitly locates its then headquarters at 2027 Stierlin Court, Mountain View. [Jun Rao's 11 January 2011 announcement](https://www.linkedin.com/blog/member/archive/open-source-linkedin-kafka) dates the open-sourcing of Kafka developed at LinkedIn. Do not pin it to Confluent, a different organisation.

## Access and interpretation

- Every linked page was opened. JSON Lines commit HTML failed through the web reader; `gh api repos/wardi/jsonlines/commits/92c32d4496d1f0b789cc4840e6cd65e11ef51e94` opened the same primary commit, showing Ian Ward, 2013-10-10, and the added numbered requirements. This is a specification edit, not a claimed invention date.
- Medallion: attempted 2020 Databricks URLs did not open. The 24 June 2022 Databricks article did open and explicitly describes the three layers. The origin says publication of guidance, not invention in 2022.
- DuckDB Foundation explicitly names both co-creators, CWI Amsterdam and 2018.
- Dagster, dlt and Polars milestones are actual online release announcements, with no unsupported historical office location.
- The Airflow origins distinguish its start in October 2014 from its public announcement in June 2015. `datamap` uses the public milestone of an orchestration tool featured in that lesson.
- Schema evolution uses the dated migration of Iceberg's table specification to Apache's website. No date for the invention of schema evolution is implied.

## Validation

- Initial new acceptance tests: 17 failed, 1 passed. All sixteen missing origins failed individually.
- After thirteen sourced additions: 14 passed, 4 failed. Remaining failures are dbt, dataquality, kafka and aggregate validation, all awaiting the two requested place files.
- No browser/full gate started: parent owns browser capacity and is resolving baseline issue 175.

## Accuracy finding corrected

The existing medallion summary universally called Bronze append-only and never edited. The opened Databricks article explicitly permits updates to Bronze for CDC. Parent authorized a focused correction within the owned topic: this camp keeps Bronze append-only for replay, while the broader architecture can apply CDC updates. The exercise, hands-on check and pipeline semantics stay the same. Issue 88 had no existing comments when checked through the paginated API on 2026-09-22.

Latest acceptance attempt: c1/c2/c3 fail only the missing three origins (seven new assertions); c3 completed in 153.7 seconds with no other failed tests. Its c4 overlapped the authorized copy edit and saw stale output. After regeneration, a fresh `just generated` passed every generator. No full browser gate, commit or PR yet.

Remaining exact events, once the requested registry IDs exist:

- `dbt`, `dbt-philadelphia`, 2016: Tristan Handy and Drew begin working full-time on dbt and Fishtown Analytics in July 2016. Source: https://www.getdbt.com/blog/whats-in-a-name
- `dataquality`, `dbt-philadelphia`, 2016: dbt ships data quality features in 2016. Source: https://www.getdbt.com/blog/our-biggest-launch-event-yet
- `kafka`, `linkedin-mountain-view`, 2011: LinkedIn open-sources Kafka on 11 January 2011. Source: https://www.linkedin.com/blog/member/archive/open-source-linkedin-kafka

The places builder independently opened both location sources and agreed the IDs. Final three origins are now written against the declared `galaxy-places-more` dependency. Do not claim acceptance until those registry files are integrated, generated outputs rebuilt and checks rerun.

## Combined dependency validation

Parent authorized one disposable combined validation after the stop hook refused
an incomplete handoff. Source branch remains unchanged by registry work.

- Scratch: `/var/folders/7w/kds2b3j97zl470x5dqm47gkw0000gn/T/vibe-data-engineering-combined-am9ewphd`.
- Registry snapshot: `/tmp/galaxy-places-more-registry.tar.gz`.
- SHA-256: `81b5ba0ace5522723a950a58acdd1cb66830eaf285efd56a5b68134f8e46919d`.
- Overlay contains registry files plus places.py/topics.py, not updated tests.
- Used this worktree's Python with `PYTHONPATH` pointing to scratch, verified
  `vibemap.__file__` resolved within scratch, and invoked pytest with `python -m`.
- Removed 57 macOS AppleDouble archive metadata files (`._*`) from scratch only;
  otherwise the place loader attempted to decode them as TOML.
- All five generation commands succeeded after removing archive metadata.
- Targeted suite: 89 passed, 1 failed. All new data-engineering assertions passed.
  Only failure is existing `tests/test_places.py` line 308, which explicitly
  assumes data-engineering has unsourced topics. Reported to its places-more owner
  to replace with a controlled missing-origin fixture.
- `places.problems(packs=['data-engineering'])` returned `[]` in scratch.
- This proves dependency compatibility; it is not branch acceptance or delivery.

Places-more subsequently supplied its already-reproduced fixture correction in
snapshot SHA-256 `a2d28708cb8ba27f25a16f7ad9f6c72c47016156d38cec30d37a434bcc9aacaf`.
Overlaying that updated snapshot corrected the missing-origin fixture. Its new
place-link test then failed because the snapshot omits its matching tools/checks.py
change: 97 tests passed and 1 failed. No dependency files entered this branch.

With the places owner's explicit approval, copied its matching tools/checks.py
into scratch only (SHA-256
`3454f6d6bcd98bbc26c0cf5d30abc936818cb2a9c831f216581d83760fd9f597`).
Fresh combined targeted result: all 98 tests passed, exit 0. This closes the
snapshot completeness issue, not branch acceptance. Await integration train,
final generation/checks, full verification, commit and independent review.


## Historical-attribution corrections (2026-09-22)

Read the independent historical-attribution review and tightened TOPICS rule.
A later office address cannot supply an earlier event location. All six findings
are accepted; no private development claim was merely moved to the internet.

| Topic | Final event | Opened primary evidence |
| --- | --- | --- |
| airflow | Maxime Beauchemin announces the open-sourcing of Airflow on the Airbnb engineering blog on 2 June 2015. | [Event source](https://medium.com/airbnb-engineering/airflow-a-workflow-management-platform-46318b977fd8?responsesOpen=true&sortBy=REVERSE_CHRON) |
| datamap | Airbnb publishes its Airflow workflow-management announcement online on 2 June 2015. | [Event source](https://medium.com/airbnb-engineering/airflow-a-workflow-management-platform-46318b977fd8?responsesOpen=true&sortBy=REVERSE_CHRON) |
| dbt | The dbt team announces online that dbt Core 1.0.0 is available on 3 December 2021. | [Event source](https://discourse.getdbt.com/t/release-dbt-core-v1-0-w-e-b-du-bois/3180) |
| dataquality | The dbt Core 1.0 online release announcement in 2021 renames schema tests to generic tests and data tests to singular tests. | [Event source](https://discourse.getdbt.com/t/release-dbt-core-v1-0-w-e-b-du-bois/3180) |
| kafka | LinkedIn advertises a Kafka talk by Neha Narkhede at its Mountain View headquarters, scheduled for 27 July 2011. | [Event source](https://www.linkedin.com/blog/engineering/archive/come-linkedin-hear-talk-about-kafka-our-open-source-distributed-pub-sub-messaging-system) |
| medallion | Databricks publishes online guidance for Bronze, Silver and Gold data layers on 24 June 2022. | [Dated publication](https://www.databricks.com/blog/2022/06/24/data-warehousing-modeling-techniques-and-their-implementation-on-the-databricks-lakehouse-platform.html) |

- Airbnb's original engineering article explicitly says it is announcing open-sourcing, dates the post 2 June 2015, and identifies its original publication at nerds.airbnb.com. Its bare Medium URL failed, but the linked query-string variant opened the complete article. Both Airflow topics now describe that publication, not private work in October 2014.
- The dbt maintainer's forum post is from 2021; its dated updates explicitly say the final 1.0.0 release was available 3 December. Its test-renaming section directly supports the data-quality lesson's narrower terminology milestone. Neither claims to locate 2016 development in Philadelphia.
- The Kafka page is a 21 July invitation for a 27 July talk. Wording deliberately says advertised and scheduled; the invitation alone does not prove the talk happened. It directly identifies Neha Narkhede, LinkedIn headquarters, Mountain View and the scheduled date. It no longer borrows that location for January's release.
- Databricks' article supports online guidance publication, not historical author geography. Its current footer is not evidence.
- DuckDB remains CWI Amsterdam, 2018, exactly as the Foundation explicitly documents. Existing reviewer-notes.md was preserved unchanged for the independent reviewer to update.

Correction verification: new historical-location regression failed against the
previous scratch topic data at airflow/airbnb-sf, then passed after copying the
corrected owned topics. All 99 targeted tests passed in the complete combined
scratch; pack defects remained `[]`; all five generators succeeded there. The
branch's topic generators were refreshed. Its built game still awaits integration
of the registry dependency. No full/browser suite or commit was run.
