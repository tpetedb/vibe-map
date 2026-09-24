# Independent source review: galaxy-places-more

Reviewed on 2026-09-22 by `codex-audit-places-sources`, independently of the builder. Scope: criterion c5 only. This is not the work-order acceptance ruling and does not resolve c2 or certify the technical gates.

## Result

All 45 added or changed place sources were opened and their relevant content read. The sources support the organisation or city associations recorded below. No blocking c5 finding remains in the reviewed data. This judgment covers the TOML declarations, not a future renderer.

All 41 Earth places declare `generic-marker`. The three other changed abstract places also use that marker. `the-cloud` keeps its explicitly fictional `nebula`. None of those declarations names a logo, product, copied building, or asserted physical landmark. The generic `look` values select fictional kits. Docker now uses `tower`, removing the ambiguous container imagery. Bell Labs is unchanged and outside this review.

The source audit distinguishes location from historical origin. Modern mailing addresses and job listings establish a city association only. They do not establish where an earlier technology was invented. The new Heroku, Cursor and Dagster comments state that limitation. Cloudera, dbt and Snowflake use dated company announcements. Beda's interview is first-person primary testimony; Snowflake's wire copy explicitly identifies Snowflake Computing as the publisher. The IEEE milestone page is primary evidence for its own plaque and site. Nuenen remains a town-level marker; no private home address is reproduced.

## Retrieval details

The web reader returned the relevant content for most sources. Its extractor failed for Ecma, TU/e and FSF, and omitted relevant text for Google, SRI and Heroku. A separate declared Python urllib client retrieved those exact official URLs with HTTP 200 and exposed the relevant visible text. Princeton's footer was also checked in the official HTML. No source is accepted solely from the builder's research notes or a search-result snippet.

## Opened sources and coordinate checks

Coordinates were independently compared against fresh OpenStreetMap Nominatim structured city/state/country results on the same day. Requests ran sequentially at more than one second apart. The comparisons check the stated quarter-degree city tolerance, not precise historical building positions. Every Earth marker passes on both axes. The largest difference is Otaniemi's longitude, 0.1710° from Espoo's city reference; the campus source specifically identifies Otaniemi. PARC's primary source additionally prints coordinates within 0.001° of its marker.

| Place | Opened source | Supported claim and limits | Coordinate comparison |
|---|---|---|---|
| `a-data-centre` | [A data centre](https://datacenters.google/) | Google describes data centres as infrastructure and lists facilities across continents. This is an abstract marker, not one facility. | Not applicable: no Earth coordinates. |
| `airbnb-sf` | [Airbnb, San Francisco](https://news.airbnb.com/about-us/) | Airbnb places its beginning in a San Francisco home in 2007. The file only needs the city, not an office address. | 37.77, -122.403; maximum axis difference 0.0179° from San Francisco reference. |
| `amazon-seattle` | [Amazon, Seattle](https://www.aboutamazon.com/news/amazon-offices/amazon-headquarters-tour-seattle) | Amazon describes its Seattle headquarters campus and a tour in the Denny Triangle. | 47.622, -122.337; maximum axis difference 0.0182° from Seattle reference. |
| `anthropic-sf` | [Anthropic, San Francisco](https://www.anthropic.com/legal/privacy) | The contact section identifies Anthropic PBC with a registered address in San Francisco. | 37.79, -122.401; maximum axis difference 0.0065° from San Francisco reference. |
| `apple-cupertino` | [Apple, Cupertino](https://www.apple.com/contact/) | The corporate contact section locates Apple in Cupertino. | 37.335, -122.009; maximum axis difference 0.0233° from Cupertino reference. |
| `carnegie-mellon` | [Carnegie Mellon University, Pittsburgh](https://www.cmu.edu/about/) | CMU lists its Pittsburgh campus and Pittsburgh contact address. | 40.443, -79.944; maximum axis difference 0.0586° from Pittsburgh reference. |
| `cern` | [CERN, Geneva](https://home.cern/about) | CERN locates its laboratory on the Franco-Swiss border near Geneva and gives a Geneva postal address. | 46.234, 6.056; maximum axis difference 0.0906° from Geneva reference. |
| `cloudera-palo-alto` | [Cloudera, Palo Alto](https://www.cloudera.com/about/news-and-blogs/press-releases/2019-08-12-cloudera-and-carl-c-icahn-announce-agreement.html) | The company announcement is datelined Palo Alto on 12 August 2019. | 37.44, -122.14; maximum axis difference 0.0198° from Palo Alto reference. |
| `confluent-mountain-view` | [Confluent, Mountain View](https://www.confluent.io/about/) | The headquarters section explicitly names Mountain View. | 37.388, -122.083; maximum axis difference 0.0014° from Mountain View reference. |
| `cursor-sf` | [Cursor, San Francisco](https://cursor.com/careers) | The careers page lists numerous engineering positions in San Francisco. This establishes a city association, not an early office. | 37.78, -122.42; maximum axis difference 0.0125° from San Francisco reference. |
| `cwi-amsterdam` | [CWI, Amsterdam Science Park](https://www.cwi.nl/en/about/) | CWI explicitly places the institute at Amsterdam Science Park. | 52.356, 4.952; maximum axis difference 0.0595° from Amsterdam reference. |
| `dagster-sf` | [Dagster Labs, San Francisco](https://dagster.io/contact) | The contact page identifies a Dagster Labs office in San Francisco. | 37.78, -122.42; maximum axis difference 0.0125° from San Francisco reference. |
| `databricks-sf` | [Databricks, San Francisco](https://www.databricks.com/company/about-us) | The company page explicitly identifies San Francisco as its headquarters. | 37.791, -122.395; maximum axis difference 0.0125° from San Francisco reference. |
| `dbt-philadelphia` | [dbt Labs, Philadelphia](https://www.getdbt.com/blog/fishtown-analytics-rebrands-as-dbt-labs-closes-150m-to-develop-open-source-analytics-engineering-software) | The company release is datelined Philadelphia on 30 June 2021 and names the change from Fishtown Analytics to dbt Labs. | 39.95, -75.16; maximum axis difference 0.0035° from Philadelphia reference. |
| `docker-palo-alto` | [Docker, Palo Alto](https://www.docker.com/legal/docker-privacy-policy/) | The privacy contact section gives Docker a Palo Alto mailing address. It does not establish a historical development site. | 37.419, -122.129; maximum axis difference 0.0308° from Palo Alto reference. |
| `ecma-international` | [Ecma International, Geneva](https://ecma-international.org/) | The official homepage footer gives Ecma International a Geneva address. | 46.203, 6.154; maximum axis difference 0.0074° from Geneva reference. |
| `eindhoven-university` | [Eindhoven University of Technology](https://www.tue.nl/en/our-university) | The official university page names Eindhoven University of Technology and its founding in 1956. | 51.448, 5.487; maximum axis difference 0.0087° from Eindhoven reference. |
| `free-software-foundation` | [The Free Software Foundation, Boston](https://www.fsf.org/news/fsf40-hackathon/) | The FSF announcement is datelined Boston and explicitly says its headquarters are in Boston. | 42.357, -71.059; maximum axis difference 0.0018° from Boston reference. |
| `github-sf` | [GitHub, San Francisco](https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement) | The privacy contact section locates GitHub, Inc. in San Francisco. | 37.782, -122.392; maximum axis difference 0.0155° from San Francisco reference. |
| `google-kirkland` | [Google, Kirkland](https://thepodlets.io/episodes/006-joe-beda/) | In a first-person interview, Joe Beda identifies his Google office as Kirkland and corrects his preceding Seattle shorthand. | 47.68, -122.21; maximum axis difference 0.0035° from Kirkland reference. |
| `google-mountain-view` | [Google, Mountain View](https://policies.google.com/privacy) | The official privacy policy names Google LLC in Mountain View in the data-controller section. | 37.422, -122.084; maximum axis difference 0.0326° from Mountain View reference. |
| `helsinki-university-of-technology` | [Helsinki University of Technology, Otaniemi](https://www.aalto.fi/en/aalto-university) | Aalto identifies its Otaniemi campus and the 2010 merger that included Helsinki University of Technology. | 60.187, 24.827; maximum axis difference 0.1710° from Espoo reference. |
| `heroku-sf` | [Heroku, San Francisco](https://www.heroku.com/contact/) | The official contact page explicitly places the Heroku office in downtown San Francisco. This is stronger than relying on the Salesforce footer alone. | 37.78, -122.42; maximum axis difference 0.0125° from San Francisco reference. |
| `ibm-san-jose` | [IBM San Jose Research Lab](https://www.ibm.com/history/relational-database) | IBM explicitly identifies the San Jose Research Lab in San Jose, California. | 37.24, -121.796; maximum axis difference 0.0962° from San Jose reference. |
| `linkedin-mountain-view` | [LinkedIn, Mountain View](https://www.linkedin.com/blog/engineering/archive/come-linkedin-hear-talk-about-kafka-our-open-source-distributed-pub-sub-messaging-system) | The 21 July 2011 invitation identifies LinkedIn headquarters in Mountain View for a Kafka presentation. | 37.39, -122.08; maximum axis difference 0.0032° from Mountain View reference. |
| `meta-menlo-park` | [Facebook (Meta), Menlo Park](https://engineering.fb.com/2012/03/25/web/a-hack-of-epic-proportions-building-a-qr-code-on-the-roof/) | The March 2012 engineering article identifies the new Facebook headquarters in Menlo Park. | 37.48, -122.15; maximum axis difference 0.0280° from Menlo Park reference. |
| `microsoft-redmond` | [Microsoft, Redmond](https://news.microsoft.com/facts-about-microsoft/) | The corporate address is Redmond; the timeline also dates the campus move to 1986. | 47.64, -122.128; maximum axis difference 0.0294° from Redmond reference. |
| `mit` | [MIT, Cambridge](https://www.mit.edu/about/) | MIT explicitly lists Cambridge, Massachusetts as its campus location. | 42.36, -71.094; maximum axis difference 0.0100° from Cambridge reference. |
| `nuenen` | [Nuenen, the Netherlands](https://www.cs.utexas.edu/~EWD/transcriptions/EWD04xx/EWD447.html) | The archived first-person EWD 447 manuscript is signed from Nuenen on 30 August 1974. Only the town is relevant and retained here. | 51.47, 5.55; maximum axis difference 0.0160° from Nuenen reference. |
| `obsidian` | [Obsidian](https://obsidian.md/about) | The official about page identifies the Obsidian team. The file makes no Earth-location claim. | Not applicable: no Earth coordinates. |
| `openai-sf` | [OpenAI, San Francisco](https://openai.com/policies/communications-privacy-policy/) | The official policy identifies the registered office of OpenAI OpCo, LLC in San Francisco. The city marker does not claim an exact current address. | 37.762, -122.415; maximum axis difference 0.0259° from San Francisco reference. |
| `parc` | [PARC, Palo Alto](https://ethw.org/Milestones:The_Xerox_Alto_Establishes_Personal_Networked_Computing,_1972-1983) | The IEEE milestone record identifies PARC in Palo Alto and gives plaque-site coordinates of 37.402370, -122.148354. | 37.403, -122.148; maximum axis difference 0.0413° from Palo Alto reference. |
| `princeton-university` | [Princeton University](https://www.princeton.edu/meet-princeton) | The university page identifies Princeton University and gives its Princeton, New Jersey contact location. | 40.343, -74.655; maximum axis difference 0.0067° from Princeton reference. |
| `python-software-foundation` | [The Python Software Foundation](https://www.python.org/psf/about/) | The official page identifies the PSF and its role behind Python. The file makes no Earth-location claim. | Not applicable: no Earth coordinates. |
| `santa-clara` | [Santa Clara, California](https://us.pycon.org/2013/) | The official PyCon 2013 site title and travel links locate the conference in Santa Clara, California. | 37.35, -121.96; maximum axis difference 0.0048° from Santa Clara reference. |
| `snowflake-san-mateo` | [Snowflake, San Mateo](https://www.globenewswire.com/news-release/2015/06/23/1186853/0/en/Snowflake-Redefines-the-Data-Warehouse-for-the-Cloud-Era.html) | The company-issued release names Snowflake Computing as its source and is datelined San Mateo on 23 June 2015. | 37.56, -122.32; maximum axis difference 0.0053° from San Mateo reference. |
| `sri-menlo-park` | [SRI International, Menlo Park](https://www.sri.com/research/future-concepts-division/) | The official page footer gives SRI a Menlo Park contact location. The current page title concerns PARC, so this supports SRI location through the footer only. | 37.453, -122.182; maximum axis difference 0.0040° from Menlo Park reference. |
| `stanford-university` | [Stanford University](https://www.stanford.edu/about/) | The official page footer identifies Stanford, California. | 37.428, -122.17; maximum axis difference 0.0005° from Stanford reference. |
| `the-cloud` | [The cloud](https://csrc.nist.gov/pubs/sp/800/145/final) | NIST defines cloud computing as a computing-resource model. The nebula is explicitly fictional and has no Earth coordinates. | Not applicable: no Earth coordinates. |
| `twitter-sf` | [Twitter, San Francisco](https://blog.x.com/en_us/a/2012/our-new-nest) | The 11 June 2012 company post describes remaining in San Francisco and moving within the city. | 37.78, -122.42; maximum axis difference 0.0125° from San Francisco reference. |
| `uc-berkeley` | [University of California, Berkeley](https://www.berkeley.edu/about/) | The official university page identifies the Berkeley institution and campus. | 37.872, -122.258; maximum axis difference 0.0149° from Berkeley reference. |
| `uc-irvine` | [University of California, Irvine](https://uci.edu/about/) | The official page gives Irvine, California as the university location. | 33.641, -117.844; maximum axis difference 0.0447° from Irvine reference. |
| `uc-santa-barbara` | [UC Santa Barbara](https://www.ucsb.edu/) | The university homepage gives Santa Barbara, California as its contact location. | 34.415, -119.846; maximum axis difference 0.1433° from Santa Barbara reference. |
| `university-of-helsinki` | [University of Helsinki](https://www.helsinki.fi/en/about-us) | The official page identifies the University of Helsinki. No physical landmark is asserted. | 60.169, 24.95; maximum axis difference 0.0065° from Helsinki reference. |
| `usc-isi` | [USC Information Sciences Institute, Marina del Rey](https://www.isi.edu/about/) | ISI explicitly says it is based in Marina del Rey, California. | 33.98, -118.441; maximum axis difference 0.0076° from Marina del Rey reference. |

## Independent geographic references

These are the actual returned city reference points, not the builder's recorded coordinates. [Nominatim](https://nominatim.openstreetmap.org/) exposes OpenStreetMap geographic data. US queries included state and country; European queries included country. They are geographic checks, not evidence of an organisation's historical presence.

| City | Latitude | Longitude |
|---|---:|---:|
| San Francisco | 37.7879363 | -122.4075201 |
| Seattle | 47.6038321 | -122.330062 |
| Cupertino | 37.3228934 | -122.0322895 |
| Pittsburgh | 40.4406968 | -80.0025666 |
| Geneva | 46.2017559 | 6.1466014 |
| Mountain View | 37.3893889 | -122.0832101 |
| Amsterdam | 52.3730796 | 4.8924534 |
| Palo Alto | 37.4443293 | -122.1598465 |
| Eindhoven | 51.4392648 | 5.478633 |
| Boston | 42.3588336 | -71.0578303 |
| Espoo | 60.2049651 | 24.6559808 |
| San Jose | 37.3361663 | -121.890591 |
| Redmond | 47.6694141 | -122.1238767 |
| Cambridge | 42.3656347 | -71.1040018 |
| Princeton | 40.3496953 | -74.6597376 |
| Menlo Park | 37.4519671 | -122.177992 |
| Stanford | 37.427467 | -122.1702445 |
| Berkeley | 37.8708393 | -122.272863 |
| Irvine | 33.6856969 | -117.825981 |
| Santa Barbara | 34.4221319 | -119.702667 |
| Helsinki | 60.1666204 | 24.9435408 |
| Marina del Rey | 33.9776848 | -118.448647 |
| Philadelphia | 39.9527237 | -75.1635262 |
| Kirkland | 47.6765382 | -122.2070775 |
| Nuenen | 51.48603 | 5.544007 |
| Santa Clara | 37.3541132 | -121.955174 |
| San Mateo | 37.5629997 | -122.3253265 |

## Reviewed snapshot

Combined SHA-256 of sorted changed paths, a NUL separator and each file's exact bytes: `3c7775f1c048fa5b36ef849a8482cc0257836b1778fcaac0b4b0bd9fb6daf08e`. This covers the 45 TOMLs listed above. If those source URLs, claims, coordinates or landmark declarations change, recheck the affected rows.
