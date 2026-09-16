# Getting Your Documents from CAS2Net

> Platform note. This copy is for an agent with no file system. Where the text below names a
> workspace file or folder such as `profile.md`, `paypool.md`, `roster.md`, `ledger.md`, or
> `FY<yy>/evidence/`, read it as a block of text kept in the conversation: the assistant
> re-emits those blocks at the end of every round and the user keeps them in a document of
> their own. Source documents are uploaded in the chat rather than saved into folders. Field
> names, allowed values, and every rule below are unchanged.

CAS2Net is the DoD web system that holds AcqDemo contribution plans, midpoint and annual assessments, closeouts, and salary appraisals. A user can export their own documents from it and hand them straight to this toolkit. These steps were observed in CAS2Net 2.0 (version 2.33.0). Labels move between releases; if a menu does not match, describe what is on screen and the user can point at the nearest equivalent.

Walk this with the user only when they say they cannot find a document. If they already have the file, take it and move on.

## What to pull, by task

Pull the **salary appraisal for the last completed cycle first**, with every section checked. It is one file that already contains that cycle's employee assessment, the supervisor assessment, the midpoint, the closeout, the contribution plan it ran under, and the scores. Pulling the individual reports for that same cycle afterwards adds nothing.

| Writing this | Pull these |
|---|---|
| **Annual assessment** | 1. Last completed cycle: **Salary Appraisal**, Check All. 2. Current cycle: **Midpoint Assessment**, **Contribution Plan**, and the **Closeout Assessment** if a supervisor or position changed. |
| **Midpoint assessment** | 1. Last completed cycle: **Salary Appraisal**, Check All. 2. Current cycle: **Contribution Plan**, and any **Closeout Assessment** already written. |
| **Contribution plan** | The Position Requirements Document (PRD), which does not live in CAS2Net, plus the prior cycle's **Contribution Plan** (inside the salary appraisal) and the last **Annual Assessment** for the language that scored well. |
| **Closeout assessment** | This cycle's **Contribution Plan**, and any **Midpoint Assessment** already written this cycle. |

A first-cycle employee has none of the prior-cycle documents. Pull this cycle's contribution plan and stop; the intake asks a few position questions instead.

If the salary appraisal for the last completed cycle is unavailable, fall back to the individual reports for that fiscal year: **Annual Assessment** with both the employee and supervisor sections, then **Midpoint Assessment**, then **Closeout Assessment**.


## Fiscal Year Based Reports

This is the path that produces a document for any plan or assessment, current or past.

1. Sign in to CAS2Net and stay on the home page long enough to read the banner. The session expires after about **15 minutes** of inactivity, so plan to pull everything in one sitting.
2. In the left menu, open the **Employee** group. It holds Contribution Plan, Midpoint Assessment, Annual Assessment, Additional Feedback, Closeout Assessment, Salary Appraisal, Archived Appraisals, and Reports.
3. Choose **Employee > Reports**. The page is titled **Employee Reports** and contains a section called **Fiscal Year Based Reports**.
4. Set the **Fiscal Year** picker to the cycle wanted. The previous cycle's annual is filed under the fiscal year that cycle ended, not the year it is being read in.
5. Choose the report type: **Contribution Plan**, **Midpoint Assessment**, **Annual Assessment**, or **Closeout Assessment**.
6. A dialog opens, **Select ACDP Assessment Form Sections**, with a **Check All** option and these choices: **Part 1: ACDP Assessment Details**, **include Compensation Detail**, **Supervisor Assessment**, and **include Employee Assessment**. Tick what is needed, then **Continue**; **Cancel** backs out without producing anything.
7. Save the document the system produces, then repeat from step 4 for the next fiscal year or report type.

What the section checkboxes mean, in plain words:

- **include Employee Assessment** is the user's own submitted text. This is the one that matters most; without it the toolkit cannot check for repeats or build the delta.
- **Supervisor Assessment** is the narrative someone else wrote about them. Worth including on a previous cycle's annual, because it shows the vocabulary the pay pool rewards and what the supervisor saw as the high points.
- **Part 1: ACDP Assessment Details** is the header block: career path, broadband level, rating period, objectives, and scores. Include it.
- **include Compensation Detail** carries salary. Leave it unchecked unless the user actually needs pay figures, and never paste it into a draft.

Which to tick for each purpose:

| Purpose | Tick |
|---|---|
| Previous cycle's annual, for repeat checks and supervisor vocabulary | Part 1: ACDP Assessment Details, Supervisor Assessment, include Employee Assessment |
| This cycle's midpoint, as the jump point for the annual | Part 1: ACDP Assessment Details, include Employee Assessment |
| This cycle's contribution plan, for objective labels and duty tiebacks | Part 1: ACDP Assessment Details |
| A closeout a losing supervisor wrote | Part 1: ACDP Assessment Details, Supervisor Assessment, include Employee Assessment |

**Check All** is fine when the user would rather pull everything once, as long as they know the result then contains salary and is not something to upload whole.

## Salary appraisal and archived appraisals

1. **Employee > Salary Appraisal** shows the current cycle's appraisal.
2. **Employee > Archived Appraisals** lists earlier ones, one per completed cycle. Open the cycle wanted and save it.
3. A dialog opens, **Select Salary Appraisal Form Sections**, offering **Check All** and these sections: **Part I CCAS Salary Appraisal** (always included), **include Compensation Detail**, **Part II Supervisor Assessment**, **include Employee Assessment**, **Midpoint Assessment**, and **Closeout Assessment**. Take **Check All** unless the user objects to pay figures being in the file, then **Continue**.

Exported files are named for what they hold, for example EmployeeSalaryAppraisal_<year>_<name>.pdf, EmployeeAnnualReview_<year>.pdf, EmployeeMidpointReview_<year>.pdf, EmployeeContributionPlan_<year>.pdf, and EmployeeCloseoutReview_<year>.pdf. The salary appraisal runs several times longer than the others because it contains them.

That document is the single richest source for the profile. It usually holds the prior assessments, the scores awarded, the expected contribution score (EOCS) for the broadband level, the value of position, and often the contribution plan that cycle ran under. It also carries pay figures, so the file itself is sensitive.

## What to do with each file

| File | Where it goes |
|---|---|
| Previous cycle's annual, or a salary appraisal | Extract the text; employee assessment text into `prior/FY<yy>/`, split per factor; scores, EOCS, and value of position into `profile.md` |
| This cycle's midpoint | `FY<yy>/midpoint/final/`, one file per factor |
| A closeout | `FY<yy>/closeout-<date>/final/` |
| This cycle's contribution plan | `FY<yy>/plan/` |

Upload whatever comes down (pdf, docx, pptx, txt, or md) in the chat. A long export is easier to work through a section at a time, so say which pages matter if asked.

The rule for the source file: these exports are normally marked CUI, and any of them may carry salary if Compensation Detail was included. Upload only the pages the drafting actually needs, and keep the rest of the export out of the conversation. CAS2Net itself is authorized only up to CUI, so nothing classified belongs in these documents or in the conversation about them.

The full list of what to ask for and what each item buys is in `intake-checklist.md`; do not repeat it here.

## While you are in there

Two blocks on the CAS2Net home page answer intake questions faster than asking the user to remember:

- **Points of Contact** names the pay pool manager, the sub-panel manager, the supervisors, and the administrator. That is the supervisor of record and the pay pool chain the profile asks for, spelled the way the system spells them.
- **User Notifications** is a dated event list: contribution plan updates, a closeout created by a supervisor, an annual assessment released or returned. Those dates settle questions the intake asks anyway, such as when the plan was approved (which drives the 90-day eligibility check) and whether a closeout exists for a mid-cycle supervisor change.

Ask the user to read those two blocks off the screen while they are signed in, rather than signing back in later.

## When CAS2Net is out of reach

Plenty of users are on a network that cannot reach it, or are between accounts after a move. That is not a blocker:

- Take a paste instead. Any text the user can copy out of an email, a saved copy, or a supervisor's forwarded document works the same as an export.
- Take a screenshot's text, or let them read numbers aloud.
- Take nothing at all and start with the position questions and the memory sweep; anything found later can be dropped in and folded back.

Whatever the route, keep the sitting short. The session expires after about **15 minutes** of inactivity, so a user who stops to read a long assessment in the browser may have to sign in again. Download first, read afterward.
