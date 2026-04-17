# Car-wash prompt: fluency vs goal parsing

## Thesis

Fluency is a poor proxy for reasoning. When five AI tools received the same one-sentence question, four produced confident, well-structured answers to a problem that was never asked, and one produced the shortest response on the page with the only correct answer. The prompt is a goal-parsing trap. The surface features of the sentence (walk, drive, 50 meters, a preference to make) match the shape of a commute-efficiency question. Every model that read the surface answered as if the goal were commuting. Only the model that reasoned about the task (washing a car requires the car to be at the car wash) returned the correct answer.

## What the prompt is actually testing

The prompt: *I want to wash my car. The car wash is 50 meters away. Should I walk or drive?*

The surface pattern is: two transport verbs, a short distance, a preference to make. That pattern is everywhere in LLM training data. The implicit user intent in that pattern is "optimize for time, cost, or convenience over a short commute." Four tools answered that implicit intent.

The actual goal is different. Washing a car is an operation performed on a vehicle, at a location. The vehicle must be at the location for the operation to occur. The user is offering a choice (walk or drive) that appears symmetrical but is not: walking leaves the car at home, which fails the goal. Driving is the only option compatible with the stated intent.

This is a lateral-thinking puzzle, not a test of arithmetic or general knowledge. It rewards goal decomposition over pattern completion.

## Why four tools got it wrong

**ChatGPT** produced a cost-model response. Bullet points on fuel burn, wear, and edge cases. It treated the question as a micro-economics problem and walked through the factors of a commute decision. It arrived at "walk" through operational reasoning about a task that was never the real task.

**Claude Sonnet 4.6** produced one sentence: "Walk. It's 50 meters, that's basically your driveway." The response is confident and human. It is also wrong for the same reason as ChatGPT's: the model matched on walk-vs-drive and never queried whether the distance question was the right question.

**Claude Opus 4.7** produced a paragraph with three sentences. The prose is more polished than Sonnet's and weighs the tradeoffs with more nuance. The conclusion is identical. More fluency, same mistake.

**Grok** produced the longest response with the most personality. A bulleted list of reasons not to drive, a friendly summary, a walking-man emoji. It also flagged edge cases (rain, heavy equipment). The response is delightful to read and is still answering the wrong question.

The pattern across the four: the model recognized a template, generated a confident answer in that template, and never stopped to check whether the template matched the user's actual goal.

## Why Gemini 2.5 Pro got it right

Gemini returned two sentences. "You must drive. The vehicle requires physical presence at the facility for cleaning. Walking the 50 meters leaves the car at its current location."

The response decomposes the task. It names the vehicle as the object, the facility as the location, and cleaning as the operation that requires both to be co-located. The choice between walking and driving is then no longer a commute preference; it is a constraint problem with one valid answer.

What Gemini appears to have done differently is parse the clause "wash my car" before parsing "walk or drive." The models that answered wrong most likely fused the full sentence into a pattern and matched on the transport decision. Gemini treated the goal clause as the primary constraint, then evaluated the transport choice against it.

This is speculation. The models do not expose their intermediate reasoning on this prompt, and "why Gemini did it and others didn't" is not fully knowable from the outside. But the behavioral difference is real and reproducible.

## The broader implication

The failure mode visible in this prompt is the same failure mode that makes coding agents misdiagnose bugs, misread specs, and refactor the wrong function. An agent reads a request, matches it against a template from training, and generates a confident answer in that template. If the template is the right one, the answer is good. If the template is close but wrong, the answer is wrong in a way that looks competent from the outside.

Three places this shows up in agent workflows:

- A debugging request where the symptom matches a common bug pattern but the actual cause is different. The agent proposes the common fix. The fix does not resolve the issue.
- A refactoring request where the user asks to "clean up this function" and the agent rewrites surface style without touching the underlying semantic issue that prompted the request.
- A spec implementation where the spec is close to a common pattern but has an edge case. The agent implements the common pattern and misses the edge case.

The car-wash prompt is a toy version of this failure. The lesson is the same: fluency and confidence are not signals of goal alignment.

## Nuances that did not make the deck

**The prompt is charitably ambiguous.** A reasonable human could interpret "should I walk or drive" as a meta question about how to get the car washed, in which case walking is a nonsensical answer and the tools that said walk are clearly wrong. A less charitable reading treats "should I walk or drive" as a commute decision and assumes the user has some other plan for the car. Under that reading, the tools that said walk are answering the narrow question correctly. Gemini's response implicitly rejects the less charitable reading; the other four implicitly accept it. Which reading is "correct" is partly a judgment call. The thesis holds either way because the value of an AI answer is in parsing which reading the user intended, not in picking a reading at random.

**Sample size is one prompt.** This is a demonstration, not a benchmark. A single goal-parsing prompt does not prove that Gemini is generally better at goal parsing or that the other four are generally worse. It shows that on this specific prompt, four failed and one succeeded. The post frames it accordingly.

**Reproducibility varies.** LLM responses are non-deterministic. The same prompt run again will likely produce similar but not identical responses. The specific quotes in the carousel are from a single run each. A retry of Sonnet might produce "Drive. The car needs to go to the car wash" and a retry of Gemini might produce "Walk. The car wash is basically your driveway." The underlying distribution matters more than any one sample. The post treats the sample as representative; a rigorous version would run each prompt five or ten times and report the distribution.

**System prompts not controlled.** Each tool ships with a system prompt and tool-specific fine-tuning that shapes response style. ChatGPT's system prompt encourages structured helpful answers. Claude's encourages calibrated reasoning. Grok's encourages personality. Gemini's encourages directness. The differences in response style are partly a reflection of those system prompts, not pure reasoning ability. A fairer test would evaluate the same underlying model across different harnesses or evaluate the base model responses without system prompts.

**"Correct" is doing work.** Calling Gemini's answer "correct" and the others "wrong" assumes the user wanted the car washed. If the user wanted a walk and was rationalizing it as a car-washing errand, the other four are friendlier and more useful. The post does not acknowledge this reading because it dilutes the point, but it is a fair critique.

**The reveal is not novel.** The "LLMs pattern-match and miss the goal" observation is well-established in the alignment and eval literature. This post's contribution is a short, concrete, shareable demonstration of the phenomenon. It is not a new finding.

## Decision framework (for a reader who wants to use this pattern)

When evaluating an AI tool's answer to a non-trivial prompt, ask:

1. Did the tool parse the goal, or the surface form of the request?
2. Does the answer address the task the user is actually trying to accomplish, or a task-shaped thing that is close to it?
3. If the answer is confident and long, does that reflect genuine analysis or template completion?
4. Would the answer still be correct if the same goal were phrased with different surface vocabulary?

These questions are more useful than asking "does the answer sound right," which is exactly the failure mode the carousel illustrates.

## Notes on claim softening

Original framing: "Only Gemini Pro got it right. The others all failed." Softened to "Gemini parsed the goal. Four tools optimized for the verbs." Reason: the stronger framing invited a well-actually pile-on about the ambiguity of the prompt. The softer framing makes the point without committing to a reading of the prompt that some readers will dispute.

Original closing: "Articulate is not accurate." Replaced with "Reasoning beats fluency." Reason: the writing style rule against "X is not Y" aphorisms. The replacement is weaker as a slogan but consistent with the style.

Original slide 9 heading: "Pattern matching is not goal parsing." Replaced with "The prompt looks like a commute question." Reason: same rule. The replacement reads less punchy but avoids the prohibited construction.
