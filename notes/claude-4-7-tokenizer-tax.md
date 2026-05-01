# Claude 4.7's tokenizer tax

## Thesis

Claude 4.7 shipped a new tokenizer alongside a modest capability improvement. The per-token price held flat. The per-session bill did not. On authentic Claude Code workloads, the new tokenizer emitted roughly 1.325x more tokens for the same content, and an 80-turn session that cost about $6.65 on 4.6 cost $7.86 to $8.76 on 4.7. The instruction-following gain measured on IFEval strict was five percentage points on a twenty-prompt sample, with no measurable change on loose. The correct frame is not "is 4.7 better than 4.6" but "does the marginal capability gain exceed the 20 to 30 percent session cost uplift for the workloads you actually run." The right unit to measure is dollars per completed task, not dollars per token.

## The value side

What the 4.7 upgrade delivers:

- A measurable, if modest, improvement in strict instruction-following. The five-point jump on IFEval strict (85 to 90) sounds small in the abstract but is meaningful at the tail. For use cases where the pass rate has to cross a specific threshold (automated evaluation gates, compliance-adjacent workflows, any pipeline where a failed completion triggers a human review), moving pass rate from 85 to 90 reduces retries and human intervention by a third.
- No change on loose instruction-following, which is consistent with the theory that the improvements target edge-case obedience rather than core task competence.
- Better tokenization of some content types, though this is a double-edged sword. The same tokenizer change that makes the model more aware of sub-word structure is what inflates token counts for human-language content.
- A more graceful handling of unusual characters, diacritics, and mixed-language content, which the article gestures at but does not measure in detail.

The upgrade is real. It is not transformative. It is the kind of improvement that makes sense if you have a specific workload where the marginal capability matters.

## The cost side

The cost is not the sticker. The sticker held flat. The cost is what the tokenizer does to the same text.

- Weighted average expansion across authentic Claude Code workloads: 1.325x. This means that for every 1000 tokens on 4.6, 4.7 charges for about 1325.
- Technical documentation, the heaviest category measured, expanded 1.47x.
- CLAUDE.md files (the canonical Claude Code context file) expanded 1.445x.
- User prompts expanded 1.373x.
- Stack traces expanded 1.25x.
- JSON and CJK content expanded 1.01 to 1.13x.

On a realistic 80-turn Claude Code session, the article puts the cost delta at $6.65 → $7.86 low, $8.76 high. A 20 to 30 percent uplift at identical per-token pricing.

Cache economics complicate the picture. In Claude Code workflows, cache reads dominate cost. Tokens that are already cached are priced below uncached inputs, so the expansion hits twice: once on the new tokens emitted per turn, and again on the cache that has to be rebuilt at the new token boundaries the first time a file is seen. After the cache warms, the incremental cost of expansion is smaller but nonzero.

The subtler cost is predictability. A team that budgeted based on 4.6's session cost and the same sticker price will find its actual spend drifting upward by 20 to 30 percent without any change to its usage patterns. The bill moves. The invoice line items do not.

## Conditions under which the value exceeds the cost

Adopt 4.7 when:

1. **Strict instruction-following is a bottleneck.** If your evaluation harness scores 85 percent strict and you need 90 to pass a compliance gate or reduce human review load, the five-point gain pays for itself. The math is straightforward: if a failed completion costs you $X in human review, and 4.7 reduces failures by one third, then 4.7 is worth the session uplift as long as $X times the failure-reduction rate exceeds the session cost increase.
2. **Content is JSON-heavy or CJK-heavy.** These content types expand by 1 to 13 percent, near the bottom of the range. You pay the capability cost in pricing power (you're on the newer, more expensive model) but you do not pay the tokenization penalty to the same degree. The upgrade is cheaper for you than for the average customer.
3. **Volume is low and stakes are high.** If each prompt is high-value and low-volume (for example, legal drafts, regulatory filings, one-off research queries), a 20 percent cost uplift on a $7 session is trivial compared to the cost of a single bad output.

## Conditions under which the cost exceeds the value

Skip or defer 4.7 when:

1. **Workload is technical-documentation-heavy.** The 1.47x expansion on tech docs is the highest category measured. A team whose primary workload is generating or ingesting technical documentation is paying the full premium for a capability delta that does not obviously match the workload.
2. **Strict instruction-following is not on the critical path.** If your task surface does not map to IFEval strict (most creative, exploratory, or conversational workloads), the five-point gain is invisible to you. You pay more. You get nothing observable in return.
3. **Budget sensitivity is high.** 20 to 30 percent is not noise. For a team with a monthly Anthropic bill in the thousands, this is a real line item. Until you have measured the effective cost uplift on your own workload, the prudent default is to stay on 4.6.
4. **Evaluation discipline is immature.** If you do not currently measure dollars per completed task, you cannot tell whether the upgrade is worth it. You will feel the bill go up. You will not know what you got for it. Adopt measurement first, then adopt the upgrade.

## Alternatives

| Alternative | When it fits | Tradeoff |
|---|---|---|
| Stay on 4.6 | Workload is expansion-sensitive or capability gain is not on the critical path | Miss the modest instruction-following improvement; keep the old bill |
| Adopt 4.7 selectively | Some prompts need the strict-instruction improvement, others do not | Adds routing complexity; requires the team to classify prompts |
| Move cache-friendly workloads to 4.6, new-tokens-heavy workloads to 4.7 | Team runs a mix of batch and conversational workloads | Requires per-workload measurement; hard to maintain as workloads drift |
| Evaluate an open-source alternative (Qwen3, Llama, etc.) | Cost pressure is genuinely binding and in-house ops capacity exists | Operational overhead of self-hosting; capability ceiling may be lower |
| Prompt-engineer for strict compliance on 4.6 | The 5-point gap can be closed with better prompting | Prompt engineering has its own cost and fragility |

The underrated alternative is doing nothing. The upgrade is available. The upgrade is not mandatory. "Continue on 4.6 until the evaluation shows it is worth moving" is a valid position and often the right one.

## Decision framework

Before moving a workload to 4.7, answer:

1. What fraction of our monthly Anthropic spend comes from this workload?
2. What is the effective per-task cost on 4.6? (Not per-token. Per completed task.)
3. What is the measured capability ceiling on 4.6? (Failure rate, review rate, retry rate.)
4. Does the workload match IFEval strict? (If not, the headline capability gain does not apply.)
5. What is the content-type mix? (Tech docs, user prompts, JSON, stack traces. Each expands differently.)
6. What is the effective per-task cost on 4.7, extrapolated from the expansion data?
7. Is the capability delta worth the cost delta, given the answers above?

Answer all seven before moving. Teams that cannot answer three through six without measurement are not ready to decide. The right next step for those teams is measurement, not migration.

## Nuances that did not make the deck

**The N=20 sample on IFEval is small.** The article is honest about this. Five percentage points on twenty prompts is one prompt's difference. The confidence interval is wide. The headline "5-point gain" is probably directionally right but could easily be three or seven points with a proper sample. A responsible reader should treat the specific number as an estimate, not a benchmark.

**The expansion numbers are derived from Anthropic's own token counter.** The article uses Anthropic's public counting endpoint on real-world content. This is reasonable and auditable, but it does not substitute for running your own workload through both tokenizers and measuring the actual delta. Your content distribution may not match the article's sample.

**Cache economics are understated in the deck.** In a Claude Code session, cache reads dominate cost. The first few turns of a session are mostly cache writes (expensive). Subsequent turns are mostly cache reads (cheap). The tokenizer change affects both: more tokens to cache up front, more tokens to read on each subsequent turn, but the per-token cost of cache reads is low enough that the absolute dollar impact is diluted. The 20 to 30 percent session uplift in the article is an average over a full session; early turns feel the expansion more acutely, steady-state turns less.

**The HN thread framed this as evidence of diminishing returns on a logarithmic cost/performance curve.** That frame is larger than this single release. It is a thesis about LLMs in general: that each generational improvement delivers smaller incremental capability for higher incremental cost, and that the industry is approaching a regime where the marginal dollar buys less marginal intelligence. Whether 4.6 → 4.7 is evidence for that thesis depends on what reference class you compare against. Against a linear extrapolation of 4.0 → 4.5, the capability gain looks small. Against the theoretical ceiling of instruction-following (a plateau near 100 percent), closing half the gap to the ceiling is nontrivial. The deck stays on the specific release; the thesis is an interesting but separate conversation.

**Timing matters.** Anthropic has raised prices multiple times in 2024 and 2025. Some HN commenters framed the tokenizer change as another price rise in disguise, timed around an IPO. I did not include this framing in the deck because it is a motive claim and the measurement stands on its own regardless of intent. The cost went up. Why it went up is a separate conversation and a weaker claim to lead with.

**"Dollars per completed task" is harder to measure than it sounds.** What counts as "completed" varies by workload. For a coding agent, it might be a compiled build. For a content generator, it might be a human-accepted output. For an evaluation pipeline, it might be a passed gate. Each workload needs its own success definition. Teams that skip this step end up measuring dollars per response, which is closer to per-token than per-task and mostly reflects the pricing change.

**The tokenizer is not the only thing that changed.** Claude 4.7 is a new model with new weights and new behavior, not just a new tokenizer. The cost attribution in the deck is slightly simplified: the 20 to 30 percent uplift comes from more tokens emitted per turn, but some of that uplift is also because the model generates slightly longer responses in some cases. The article controls for the inbound expansion; controlling for output verbosity is harder. The number is right, but the allocation between "tokenizer" and "model behavior" is not fully clean.

## Notes on claim softening

No softening. Draft language matched final in all cases. Specific choices worth noting:

- The title evolved from "The tokenizer tax" (plan) to "Same sticker. Bigger bill." (final). The tax framing stays in the `pill` on slide 1 and the takeaway on slide 5, but the headline went with the parallel structure because it reads better as the LinkedIn feed preview.
- "Price the task, not the token" was the planned rule-of-thumb line. Replaced with "Tokens are the sticker. Tasks are the bill." to avoid the "not X, Y" construction per the writing style rule. Both phrasings say the same thing; the parallel form is cleaner.
- Slide 4 heading "The capability gain was modest" is the most editorialized line in the deck. "Modest" is a judgment call. The supporting data (5 points on one eval, N=20, no change on loose) justifies the word, but it is a stronger word than the article used. Left it in because the data supports it and because hedging the word to "small" or "limited" made the line weaker without adding accuracy.
