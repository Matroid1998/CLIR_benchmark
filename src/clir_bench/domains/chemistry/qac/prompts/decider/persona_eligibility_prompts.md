# Chemistry Jev eligibility prompt r7

The runtime eligibility request is assembled from `jev_eligibility.json` and
`eligibility_cases.json` by `clir_bench.domains.chemistry.qac.decider`. The JSON
instruction file defines the seven independent persona checks; the companion
file supplies bounded cases grouped by persona. The loader combines them by
`case_id` before sending the native Decisions API request. This file is an
index, not a second copy of the runtime prompt.
