# Career Paths, Broadband Levels, and Score Ranges

Sources: `AcqDemo Factor Descriptors and Discriminators.pdf` (score ranges, Very High scores) and example pay pool business rules (Very High eligibility for NH). NJ and NK eligibility bands follow the same pattern (the top five points of the top level); confirm with your pay pool.

## Factor score ranges

| Career path | Level | Score range |
|---|---|---|
| NH | I | 0-29 |
| NH | II | 22-66 |
| NH | III | 61-83 |
| NH | IV | 79-100 |
| NJ | I | 0-29 |
| NJ | II | 22-51 |
| NJ | III | 43-66 |
| NJ | IV | 61-83 |
| NK | I | 0-29 |
| NK | II | 22-46 |
| NK | III | 38-61 |

Career path names: **NH** Business Management and Technical Management; **NJ** Technical Management Support; **NK** Administrative Support.

## Very High scores

Available only to employees in the top broadband level of their career path, and only when the employee's Expected Overall Contribution Score (EOCS) falls in the eligibility band. A Very High score must be justified in writing by showing how the employee exceeds the top level's descriptors.

| Career path | Top level | Very High scores | EOCS eligibility band |
|---|---|---|---|
| NH | IV | 105, 110, 115 | 96-100 |
| NJ | IV | 87, 91, 95 | 79-83 |
| NK | III | 64, 67, 70 | 57-61 |

Note: only the NH eligibility band (96-100) is stated in the source documents. The NJ (79-83) and NK (57-61) bands are inferred from the same pattern; verify them with your pay pool before relying on them.

## Categorical scores

Each factor also receives a categorical score made of the level number and a position within the level: L (low), M (mid), or H (high). Examples: 3H, 4M. Categorical scores stay consistent with the employee's broadband level.

## How descriptors are read

- Descriptors are written to the **high end** of each level.
- A level's descriptors are taken **as a group**. Contributions relate to them; they do not need to match every line.
- Ranges overlap between levels on purpose.
- One activity can support more than one factor, but each factor needs its own statement written in that factor's language.

## Target level

The profile field `target_level` controls calibration:
- **At or below expected:** write to the employee's current level descriptors.
- **Aiming above expected (the usual goal):** borrow language from the high end of the current level and, when the employee is not in the top level, from the next level up.
- **Top level:** borrow Very High language only when the EOCS is inside the eligibility band.
