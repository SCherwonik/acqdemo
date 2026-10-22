# Pay Pool Overlay

Values below are the example pay pool's defaults. Replace them with your pay pool's current business rules and guidance.

- pay_pool:
- business_rules_source:          # file name and year
- cycle_start: 10-01
- cycle_end: 09-30
- plan_due_days: 30
- plan_days_required: 90           # consecutive days on an approved plan before cycle end
- plan_change_lock_days: 90
- midpoint_window: Mar-Apr
- employee_due: 09-15
- supervisor_due: 09-30
- panels: Oct-Nov
- reconsideration_window: late Jan to mid Feb
- min_entries_annual: 3
- min_entries_midpoint: 1
- what_label: C                    # C (Contribution, current) or W (What, older guidance)
- min_plan_objectives_per_factor: 2   # a minimum, not a target; more are allowed
- plan_template:                    # optional: path to the pay pool's own plan template notes (option menus, intro statements, default KPOs)
- mandatory_paragraph_order:
  - JA: supervisory
  - MS: acquisition, dod-fm
- promotion_window_days: 150       # promotion within this many days of cycle end defaults to EOCS
- very_high_eocs_band: see references/levels.md
- char_limit: 3900
- supervisor_paql_prefix: "PAQL:"
- allow_phrases:                   # organization names allowed to repeat across factors and years
  -
- notes:

# Key Performance Objectives (acquisition-coded positions, FY27 onward)
- kpo_required: no            # yes for acquisition-coded positions from the FY27 cycle
- kpo_count: 2                # exact number of KPOs the plan carries
- kpo_labels: KPO1 Strategic Outcome; KPO2 Workforce Behavioral
- kpo_factor: MS              # factor the KPOs are written under, after its regular objectives
- plan_label_style: colon     # colon writes "JA1: ..."; parentheses writes "(JA1) ..."
