# CLAUDE.md

GEM-Bench (KDD '26): benchmark for **ad-injected response (AIR)** generation in Generative Engine Marketing. Solutions inject product ads into LLM answers; evaluators score them with quantitative metrics and LLM-as-a-judge (LAAJ) agents.

The detailed workflow guide lives in `skills/gembench/SKILL.md` (CLI, pricing, adding solutions, validation commands) — read it before CLI or solution work rather than rediscovering.

## Layout

End-to-end flow diagram (generate → evaluate → report, plus Ad-LLM internals): `docs/pipeline.html`. Update it when the pipeline changes.

- `paper.py` — main experiment runner. `--mode generate|evaluate` (omit for full run), `--results-path` (evaluate mode), `--identifiability-only`. Model config (`BASE_MODEL`, `JUDGE_MODEL`, `OUTPUT_BASE`) is hardcoded at the top.
- `paper_rebuttal.py` — RAG-AdChat-only run for the rebuttal.
- `utils/__init__.py` — top-level `Timer` used by `paper.py` (not part of the `GemBench` package).
- `GemBench/benchmarking/GemBench.py` — orchestrator: `process_results()` (Stage 1, generation) → `evaluate()` (Stage 2) → `report()` (xlsx).
- `GemBench/benchmarking/evaluator/`
  - `quantitative_evaluator/` — `has_ad`, `local_flow`, `global_coherence`, `ad_transition_similarity`, `ad_content_alignment`, `in_token`, `out_token`, `price`.
  - `laaj_evaluator/` — one agent + one prompt per qualitative metric: accuracy, naturalness, personality, trust, notice_products, click_products, **identifiability**. Agents parse `[[CATEGORY]]` from judge output and map to 0/33/66/100.
  - `selector_evaluator/` — `product_selection_accuracy` for the CA_Prod search task.
- `GemBench/benchmarking/dataset/` — MT-Human, LM-Market (chat), CA_Prod (search/selection), plus `product/` ad library.
- `GemBench/solutions/src/` — `AdChat` (system-prompt ads), `AdLLM` (GI-R / GI-P / GIR-R / GIR-P via `query_type` ∈ {`QUERY_RESPONSE`, `QUERY_PROMPT`} × `solution_name` ∈ {`BASIC_GEN_INSERT`, `REFINE_GEN_INSERT`}), `RAGAdChat`.
- `GemBench/cli/` — `gembench` CLI (`python -m GemBench.cli ...`). Metric names are mirrored in `cli/constants.py`.
- `analysis/*.ipynb` — result analysis notebooks (evaluation, GI-P, identifiability).
- `vllm_scripts/` — launch scripts for self-hosted base/judge models (vLLM OpenAI-compatible server on port 8000).

## Adding or changing a LAAJ metric

Touch all of: `laaj_evaluator/prompts/<name>_prompt.py`, `laaj_evaluator/agents/<name>_agent.py` (copy an existing agent), `agents/__init__.py`, `ANALYSIS_MATRIXES` + `evaluation_methods` in `laaj_qualitative_evaluator.py`, and `GemBench/cli/constants.py`. When revising a prompt, keep the old version as `<name>_prompt_v1.py` (as done for identifiability) so results stay reproducible.

## Running

- Install: `pip install -e .` (Python 3.12; `uv.lock` also present).
- Config via `.env` (template: `.env.u-should-make`): `OPENAI_API_KEY`/`BASE_URL` for the generator, optional `JUDGE_*` and `EMBEDDING_*` overrides. With vLLM, point `BASE_URL` at `http://localhost:8000/v1`.
- Experiments are expensive (n_repeats × datasets × solutions × 7 judge metrics). Prefer `--mode evaluate --results-path <results.json>` to re-judge existing generations, and `--identifiability-only` when iterating on that metric.
- Outputs: `<output_dir>/output/<YYYYmmdd_HHMMSS>_<tags>/` containing `results.json`, per-metric `*_evaluation.xlsx`, `evaluation_result.json`, and `evaluation_result*.xlsx`. Don't commit outputs.

## Gotchas

- **LLM call cache**: `ExperimentCache` stores responses in `./.cache/` relative to the CWD (diskcache). Identical prompts return cached answers — clear or change CWD if a fresh judge run is intended.
- `paper.py` `OUTPUT_BASE` and the vLLM scripts use absolute paths from the GPU server (`/home/gpuuser7/gpuuser7_a/prateek/...`), not this machine. Adjust before running locally; don't "fix" them silently in commits.
- `BaseAgent.answer()` references `self.model.model_name`, but `Oracle` only has `.model` — the error path would raise `AttributeError`.
- Category parsing falls back to the lowest category (e.g. `NOT_IDENTIFIABLE` → 0) when the judge output has no valid `[[...]]` tag, so malformed judge output silently lowers scores. Check the `Evaluation` column in the per-metric xlsx when numbers look off.
- No test suite. Validate with `python -m compileall GemBench paper.py` and the CLI smoke checks in `skills/gembench/SKILL.md`; say explicitly when API-backed runs were not performed.
