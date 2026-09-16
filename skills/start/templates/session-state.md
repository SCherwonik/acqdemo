# Session State
Written before every message that waits on the user, so a closed window loses nothing.
- step:                   # 0 load, 1 gate, 2 harvest, 3 dump, 3b sweeps, 4 deep-dive, 5 allocate, 6 draft, 7 review, 8 finalize
- current_entry:          # ledger id in progress, for example L-002, or none
- round:                  # question round number within the current step or entry
- pending_questions:      # the numbered questions just asked and not yet answered, copied verbatim
  -
- next_action:            # the exact next move when the user returns
- open_questions:         # unknowns parked for later (never block on these)
  -
- updated:               # YYYY-MM-DD HH:MM
