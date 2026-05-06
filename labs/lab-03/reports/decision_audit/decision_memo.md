# Decision Memo - Live Race Use

**To:** Team Principal  
**From:** Carlos Orellana and Mattias Morales  
**Subject:** Whether to use the points tool for live strategy calls  
**Date:** April 2026

Do not use this tool to make live strategy calls during a race.

The tool is useful before the race. In the 2023 and 2024 seasons, it was off by 2.838 points per driver per race, while the simple grid-position lookup was off by 3.246 points. That is a 12.57% improvement over the simple option the team could already use.

That improvement does not solve the live-race problem. The tool has 0 live race inputs and 0 live refreshes. It does not see tire state, safety cars, damage, first-lap incidents, changing weather, or mechanical problems as they happen. It also has 0 named live-call owner in the current workflow.

At the action point we tested, the tool correctly caught 149 high-points cases, but it also created 43 bad action signals and missed 80 real ones. With our live-call cost rule, the bad action signals cost 86.0 and the missed opportunities cost 80.0. That means the mistakes lean slightly toward the more expensive side.

I do not recommend deploying this tool unless it is rebuilt with at least 1 live race input, at least 1 live refresh before the call window, and a retest showing bad action cost no higher than missed opportunity cost.

Use the tool in the pre-race briefing pack as a planning reference. Do not put it on the live strategy desk yet.
