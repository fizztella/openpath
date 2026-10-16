# OpenPath User Testing Report

## 1. Purpose

This study evaluated whether first-time users could understand and use the OpenPath prototype without assistance. The test focused on:

- navigating the interface;
- filtering degree programs;
- understanding eligibility results;
- opening program details;
- building a shortlist;
- using the application timeline and checklist;
- changing the interface language;
- exporting data for later use.

The goal was not to prove that the prototype was complete. It was to identify usability problems, prioritize them, and improve the product using evidence from real users.

## 2. Method

Testing was conducted remotely with an early public version of the Streamlit application. Participants used their own computers and browsers. They explored the product and reported confusing behavior, errors, missing functionality, and an overall usability rating.

The first round included three participants. Feedback was anonymized as Tester 1, Tester 2, and Tester 3. No names, account information, or other identifying details were collected.

### Suggested task sequence

The following task sequence is used for subsequent tests so that results are easier to compare:

1. Change the interface language.
2. Enter an applicant profile and identify a matching program.
3. Open the program details and locate its fees and deadline.
4. Add at least one program to the shortlist.
5. Review the application timeline and checklist.
6. Mark one checklist task as complete.
7. Export the shortlist.
8. Change the visual theme.
9. Rate the overall experience from 1 to 5 and explain any difficulty.

## 3. Participants

| Participant | Device and operating system | Browser | Interface language | Rating |
|---|---|---|---|---:|
| Tester 1 | Desktop computer | Chrome and Yandex Browser | Russian | 4/5 |
| Tester 2 | Desktop, Windows 11 | Microsoft Edge | Russian; translation described as incomplete | Not provided |
| Tester 3 | Laptop, Windows | Yandex Browser | Russian | 3/5 |

The sample was small and based on convenience recruitment. It is useful for finding usability problems but is not statistically representative of all international applicants.

## 4. Findings from Round 1

| Priority | Finding | Evidence | Product response | Status |
|---|---|---|---|---|
| High | Parts of the timeline, checklist, tables, warnings, and program-detail interface remained in English after selecting another language. | Reported by Testers 2 and 3. | Extended localization across generated interface content, table labels, timeline actions, checklist tasks, warnings, and navigation. | Implemented |
| High | The CSV export opened in a single Excel column and was unclear to non-technical users. | Reported by Tester 3 with a screenshot. | Replaced CSV downloads with genuine `.xlsx` workbooks containing separate columns, filters, and frozen headers. | Implemented |
| High | Program details duplicated information and made the results page long and difficult to scan. | Reported by Tester 2; also visible during review. | Replaced expandable detail sections with compact result cards and a centered modal details window. | Implemented |
| Medium | The page selector was awkward and visually unclear. | Reported by Tester 3. | Replaced the page dropdown with Previous and Next buttons plus a page counter. | Implemented |
| Medium | A checklist section collapsed after marking a task complete. | Reported by Tester 3. | Replaced collapsing checklist groups with persistent bordered sections. | Implemented |
| Medium | The visual design used an overly bright orange accent and felt insufficiently formal. | Reported by Tester 1 and reinforced during design review. | Reworked the interface with a restrained blue accent, sharper corners, reduced decorative effects, and dark/light themes. | Implemented |
| Medium | Finding a specific program in the shortlist selector was difficult because unrelated countries and fields appeared together. | Identified during follow-up review. | Added country and field filters while preserving already selected programs and text search. | Implemented |
| Low | The content area left excessive unused space on some displays. | Reported by Tester 1. | Adjusted the maximum content width and later refined it to retain moderate side margins on large displays. | Implemented |
| Low | Users requested more countries, programs, languages, university reviews, currency selection, and theme control. | Reported across all three tests. | Added theme control. Dataset expansion and currency selection remain possible future work. Reviews were deferred because they require a reliable and ethically sourced data model. | Partially implemented |

## 5. Design Decisions

Not every suggestion was implemented literally. Feedback was evaluated according to user impact, reliability, project scope, and whether the requested feature could be supported with trustworthy data.

- University reviews were not added because unverified opinions could undermine the project's emphasis on reliable admissions information.
- The number of countries and programs was not expanded immediately. Improving data quality, citations, and usability was prioritized over increasing dataset size.
- Official university and program names remain in their original form. Source-derived admissions wording may also remain in English when translating it could change the meaning of an official requirement.
- Scholarship probability is not predicted because the prototype does not have reliable historical decision data.

## 6. Changes Delivered After Testing

The first testing round resulted in the following product iteration:

- broader localization across six interface languages;
- genuine Excel exports;
- compact cards with modal program details;
- clearer Previous and Next pagination;
- persistent checklist sections;
- a stricter visual system with blue accents and sharper corners;
- dark and light themes;
- improved large-screen width;
- shortlist filters for country and field;
- visual corrections for light-theme controls, dialogs, selected filter tags, and dropdown menus.

Automated tests were run after the implementation changes. The project currently has 51 passing tests covering filtering, data integrity, presentation, shortlist behavior, timeline generation, checklist generation, localization, Excel exports, and the main comparison workflows.

## 7. Round 2: Follow-up Validation

The second round tested the revised public prototype. Three additional participants used Windows computers with Yandex Browser or Microsoft Edge. This round included Russian, Spanish, and Ukrainian interfaces as well as both visual themes.

### Participant record

| Participant | Device and browser | Interface language | Reported understanding | Rating |
|---|---|---|---|---:|
| Tester 4 | Windows, Yandex Browser | Russian | Interface was usable; several presentation and workflow issues were identified | 4/5 |
| Tester 5 | Windows, Microsoft Edge | Russian and Spanish | Everything was understandable and the interface was described as pleasant | 4/5 |
| Tester 6 | Windows, Microsoft Edge | Ukrainian | Interface was described as intuitive | 5/5 |

### Follow-up task coverage

Participants explored filtering, result cards, compact tables, program details, the shortlist, the application timeline, localization, and visual themes. They reported their device and browser, selected language, unclear interactions, defects, suggestions, and an overall rating. Screenshots were supplied for the reproducible visual and localization problems.

### Round 2 observations

| Priority | Observation | Evidence | Decision | Status |
|---|---|---|---|---|
| High | Data tables remain dark in the light theme, producing a strong visual contrast. | Reported by Tester 6 and reproduced in the timeline screenshot. | Replaced fixed-theme data grids with theme-aware tables. | Implemented |
| High | Some source-derived notes in program details remain in English when Ukrainian is selected. | Reported by Tester 6 with a screenshot showing the academic-test note, aid note, and important note. | Localized the reported explanatory notes while preserving official names. | Implemented |
| High | The shortlist is lost after a browser refresh. | Reported by Tester 6. | Bound shortlist identifiers to URL query parameters so the selection survives refresh and can be shared. | Implemented |
| Medium | Selected filter tags display visually awkward square or cross-shaped removal controls. | Reported by Tester 4 with a screenshot. | Added browser-resistant sizing and transparent styling for tag removal icons. | Implemented |
| Medium | `Select all` remains in English in localized multi-select controls. | Reported by Tester 4 with a screenshot. | Disabled the framework-controlled command in every multi-select because Streamlit does not expose its text for localization. | Implemented |
| Medium | Rows generated by OpenPath in the application plan have no official-source URL, whereas official deadline rows do. | Reported by Tester 4 with a screenshot. | Generated milestones now show “Not applicable — OpenPath recommendation” instead of an empty source. | Implemented |
| Medium | Compact-table rows do not provide the same access to explanations as result cards. | Reported by Tester 5. | Replaced the compact grid with theme-aware rows that use the same details dialog as cards. | Implemented |
| Medium | Clearing active filters is not sufficiently obvious. | Suggested by Tester 5. | Added a localized reset-filters control. | Implemented |
| Low | The Sources and limitations section is visually overemphasized. | Reported by Tester 4. | Retained the disclosure as compact footer text without a large heading. | Implemented |
| Low | The separate program-selection and Details action adds an unnecessary step in one workflow. | Reported by Tester 4 with a screenshot. | Removed the separate selector; each compact result row now opens the same details dialog directly. | Implemented |
| Low | Country and other filter fields appear excessively wide on large screens. | Reported by Tester 6. | Constrained related filters into a narrower responsive column layout. | Implemented |

### Interpretation

Round 2 indicates that the main navigation and visual redesign improved perceived usability: all three participants rated the revised interface at least 4/5, and two explicitly described it as understandable or intuitive. The test also revealed a new class of problems that only became visible after adding themes and broader localization: component-level text that is controlled by the framework, theme-inconsistent tables, untranslated source notes, and non-persistent session state.

Some suggestions conflict and therefore require product judgement. One participant considered the separate Details action unnecessary, while another requested equal access to explanations from compact-table mode. The appropriate response is not to remove evidence entirely, but to reduce redundant steps and provide one consistent detail interaction from both result views.

## 8. Round 3: Post-release Review

One additional participant independently reviewed the published application after the `v1.0` release. Device, browser, and interface language were not recorded for this informal follow-up. The participant understood the purpose of the service, considered the project visually complete, and rated the experience **4/5**.

### Round 3 observations

| Priority | Observation | Evidence | Product response | Status |
|---|---|---|---|---|
| Critical | Adding a program through the comparison dropdown caused a `StreamlitWidgetAlreadyInstantiatedError`. | Reproduced from the participant's screenshot and traced to clearing widget state after widget creation. | Moved the state update into a callback and added an automated regression test covering the complete dropdown-add workflow. | Implemented in `v1.0.1` |
| High | Choosing programs for comparison through a separate dropdown was inconvenient. | Participant preferred adding a program directly while browsing search results. | Added comparison controls to both result cards and compact rows. The same control now adds or removes a program without requiring navigation to another tab. | Implemented in `v1.0.1–v1.0.3` |
| High | First-time visitors might not know where selected programs can be compared. | Participant could add a program but found the destination unclear. | Renamed the tab to **Compare & timeline** and added an in-page message directing users to it after a selection. | Implemented in `v1.0.2` |
| Medium | Filters occupied most of the initial viewport and pushed results below the fold. | Participant reported excessive scrolling before reaching results. | Moved advanced filters into a collapsible section while keeping search visible. | Implemented in `v1.0.1` |
| Medium | Program details were not sufficiently discoverable when only the title area was interactive. | Participant requested explicit actions. | Added separate **View details** and **Add to comparison** buttons at the bottom of every card. | Implemented in `v1.0.2` |
| Medium | Clickable program names disrupted alignment in compact-table mode. | Reproduced from the participant's screenshot. | Restored names as normal text and introduced dedicated Details and Compare action columns. | Implemented in `v1.0.2` |
| Low | The search field did not stand out enough. | Participant observation. | Increased its height and added a restrained accent border. | Implemented in `v1.0.1` |
| Low | Text in the light theme appeared too dark and visually harsh. | Participant observation with screenshots. | Softened the primary light-theme text and border colors while retaining readable contrast. | Implemented in `v1.0.2` |

### Interpretation

The post-release review confirmed that OpenPath's purpose and overall completeness were clear, but exposed friction in the central comparison workflow. The most valuable finding was the reproducible runtime error, which automated tests had not previously covered. The resulting regression tests now exercise comparison through both the dropdown and result cards. The remaining changes focused on discoverability and layout rather than expanding the project's scope.

## 9. Limitations

- The first two rounds involved three participants each; the post-release review added one participant, for a total of seven usability sessions.
- Participants were recruited from the developer's existing online network.
- The participants do not necessarily represent every target country, education system, language, or accessibility need.
- Early feedback was collected in a relatively informal format.
- Some findings concern data coverage rather than interface usability.
- Ratings were self-reported and the sessions were not moderated using timing or task-completion measurements.

Future testing should include applicants actively researching international education, mobile users, people using different interface languages, and at least one participant unfamiliar with the project or its developer.

## 10. Conclusion

The testing changed OpenPath substantially. Round 1 exposed problems that were not obvious during development, including incomplete localization, an unusable spreadsheet export, inefficient program-detail navigation, unstable checklist interaction, and difficulty finding shortlist options. Round 2 showed improved overall usability while identifying theme consistency, session persistence, component localization, and access-to-evidence issues for the next iteration.

The project therefore demonstrates more than implementation work. It shows an iterative process of identifying a real problem, building a prototype, testing it with users, evaluating evidence, making scoped product decisions, and validating the resulting changes. The post-release review also demonstrates maintenance discipline: a production error was reproduced, fixed, protected by regression tests, and delivered through scoped patch releases.
