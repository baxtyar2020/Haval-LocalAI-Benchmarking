# Persona AI Workload and Response-Time Source Table

This source table defines 20 core personas across Consumer, Gaming, and Commercial businesses. Each persona has a Light, Balanced, and Heavy AI workload, along with a recommended maximum total completion time.

## Response-time interpretation

- **Light:** first token target within 2 seconds.
- **Balanced:** first token target within 4 seconds.
- **Heavy:** first token target within 8 seconds, with visible progress or streaming.
- The tolerance in each table cell is the recommended maximum time for the complete, usable answer—not merely time to first token.

| Business | Persona | Light workload | Balanced workload | Heavy workload |
|---|---|---|---|---|
| Consumer | Everyday Organizer | Convert notes into a short task list.<br>**Tolerance: ≤10 sec** | Create a three-day schedule from several constraints.<br>**Tolerance: ≤40 sec** | Build a complete weekly household, meal, appointment, and travel plan.<br>**Tolerance: ≤2 min** |
| Consumer | Student & Learner | Explain one difficult concept simply.<br>**Tolerance: ≤10 sec** | Summarize a chapter and create five quiz questions.<br>**Tolerance: ≤45 sec** | Analyze 10 pages and produce a study guide, key concepts, and practice exam.<br>**Tolerance: ≤3 min** |
| Consumer | Family Coordinator | Suggest a meal or children’s activity.<br>**Tolerance: ≤10 sec** | Build a weekly family meal and activity schedule.<br>**Tolerance: ≤45 sec** | Coordinate a multiweek family plan using school, travel, budget, and appointment information.<br>**Tolerance: ≤3 min** |
| Consumer | Researcher & Shopper | Compare two products using a few specifications.<br>**Tolerance: ≤12 sec** | Compare five products and recommend the best match.<br>**Tolerance: ≤60 sec** | Research a major purchase using multiple documents, requirements, and trade-offs.<br>**Tolerance: ≤4 min** |
| Consumer | Writer & Communicator | Rewrite a short message in a calmer tone.<br>**Tolerance: ≤7 sec** | Draft a polished email or one-page message.<br>**Tolerance: ≤30 sec** | Review and rewrite a long application, essay, or personal document.<br>**Tolerance: ≤2 min** |
| Consumer | Creative Prosumer | Generate titles, captions, or creative ideas.<br>**Tolerance: ≤12 sec** | Create a short script, outline, and storyboard.<br>**Tolerance: ≤60 sec** | Produce a complete content package with concept, script, captions, and publishing plan.<br>**Tolerance: ≤4 min** |
| Consumer | Personal Adviser | Suggest several options for a personal decision.<br>**Tolerance: ≤12 sec** | Build a structured personal plan with constraints and priorities.<br>**Tolerance: ≤60 sec** | Review extensive background information and produce options, risks, and a step-by-step plan.<br>**Tolerance: ≤3 min** |
| Consumer | Technical Hobbyist | Explain an error or provide one command.<br>**Tolerance: ≤10 sec** | Diagnose a PC or software problem from a short description.<br>**Tolerance: ≤60 sec** | Analyze logs, hardware details, and configuration information to create a complete repair plan.<br>**Tolerance: ≤4 min** |
| Gaming | Casual Gamer | Answer a quick gameplay or settings question.<br>**Tolerance: ≤7 sec** | Provide a walkthrough or solve a setup problem.<br>**Tolerance: ≤30 sec** | Recommend games and create a personalized setup and troubleshooting guide.<br>**Tolerance: ≤90 sec** |
| Gaming | Power Player | Recommend one performance or graphics setting.<br>**Tolerance: ≤10 sec** | Analyze PC specifications and recommend optimized game settings.<br>**Tolerance: ≤60 sec** | Analyze benchmarks, temperatures, logs, and game settings to produce a complete optimization plan.<br>**Tolerance: ≤3 min** |
| Gaming | Progressive Creator | Generate a title, caption, or hook for a clip.<br>**Tolerance: ≤10 sec** | Create a gameplay-video script and editing outline.<br>**Tolerance: ≤60 sec** | Turn gameplay notes or a transcript into a complete content and publishing package.<br>**Tolerance: ≤3 min** |
| Gaming | Rising Game Developer | Explain a short code snippet or engine concept.<br>**Tolerance: ≤12 sec** | Debug a small gameplay script and explain the correction.<br>**Tolerance: ≤90 sec** | Design and code a simple game feature with logic, documentation, and tests.<br>**Tolerance: ≤5 min** |
| Commercial | Executive & Decision Maker | Summarize one important email or update.<br>**Tolerance: ≤10 sec** | Convert a report into a one-page executive brief.<br>**Tolerance: ≤60 sec** | Analyze a 10-page business report and identify decisions, risks, options, and recommendations.<br>**Tolerance: ≤3 min** |
| Commercial | Project & Operations Manager | Extract owners and actions from meeting notes.<br>**Tolerance: ≤10 sec** | Create a project status report with risks and next steps.<br>**Tolerance: ≤60 sec** | Synthesize multiple project documents into a program plan with milestones, dependencies, risks, and owners.<br>**Tolerance: ≤3 min** |
| Commercial | Engineer & Software Developer | Explain an error or suggest a code correction.<br>**Tolerance: ≤12 sec** | Write or repair a function and generate unit tests.<br>**Tolerance: ≤90 sec** | Analyze a larger technical problem and produce implementation code, tests, and documentation.<br>**Tolerance: ≤5 min** |
| Commercial | Analyst & Finance Professional | Calculate a value or explain a spreadsheet formula.<br>**Tolerance: ≤10 sec** | Analyze a small dataset and identify important trends.<br>**Tolerance: ≤60 sec** | Analyze multiple tables and scenarios and produce a structured financial or business report.<br>**Tolerance: ≤4 min** |
| Commercial | Research & Product Professional | Summarize one article or customer comment.<br>**Tolerance: ≤10 sec** | Compare several competitors, features, or customer needs.<br>**Tolerance: ≤60 sec** | Synthesize multiple documents into market findings, product requirements, and recommendations.<br>**Tolerance: ≤4 min** |
| Commercial | Sales & Marketing Professional | Write a subject line, tagline, or short outreach message.<br>**Tolerance: ≤7 sec** | Draft personalized outreach or a short campaign concept.<br>**Tolerance: ≤45 sec** | Research an account and produce a proposal, campaign narrative, and supporting content.<br>**Tolerance: ≤3 min** |
| Commercial | Customer Support Specialist | Classify a ticket or rewrite a customer response.<br>**Tolerance: ≤7 sec** | Diagnose a case using a short description and knowledge-base content.<br>**Tolerance: ≤45 sec** | Analyze case history, logs, and documentation and produce a resolution plan and customer response.<br>**Tolerance: ≤2 min** |
| Commercial | People, Legal & Compliance Professional | Extract a date, obligation, person, or clause.<br>**Tolerance: ≤10 sec** | Compare policy language and identify important differences.<br>**Tolerance: ≤60 sec** | Review a long contract or policy and identify obligations, risks, conflicts, and required actions.<br>**Tolerance: ≤5 min** |

## Research basis

- [Response Time Limits — Nielsen Norman Group](https://www.nngroup.com/articles/response-times-3-important-limits/)
- [Mitigating Response Delays in Free-Form Conversations — ACM](https://dl.acm.org/doi/10.1145/3719160.3736636)
- [The Impact of Response Latency and Task Type on Human–LLM Interaction](https://arxiv.org/abs/2604.06183)
- [How to Evaluate LLMs — Microsoft Research](https://www.microsoft.com/en-us/research/articles/how-to-evaluate-llms-a-complete-metric-framework/)

These persona-specific completion thresholds are recommended benchmark-design values inferred from the research above. They are not published universal industry standards.
