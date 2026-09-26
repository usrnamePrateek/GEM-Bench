import argparse
import os
from GemBench import AdLLMWorkflow
from GemBench import AdChatWorkflow
from GemBench import GemBench
from dotenv import load_dotenv
from functools import partial
from GemBench import LINEAR_WEIGHT, LOG_WEIGHT
from GemBench import PRODUCT_DATASET_PATH, TOPIC_DATASET_PATH
from utils import Timer

load_dotenv()

def _short_name(model_id: str) -> str:
    """Convert 'org/Model-Name' to 'model-name' for use in tags."""
    return model_id.split('/')[-1].lower()

if __name__ == '__main__':
    # ==================== CLI ====================
    parser = argparse.ArgumentParser(description="GEM-Bench: generate, evaluate, or run all")
    parser.add_argument("--mode", choices=["generate", "evaluate"], default=None,
                        help="'generate' for Stage 1, 'evaluate' for Stage 2+3, omit for full run")
    parser.add_argument("--results-path", type=str, default=None,
                        help="Path to results.json (required for evaluate mode)")
    args = parser.parse_args()

    # ==================== MODEL CONFIG ====================
    BASE_MODEL = "google/gemma-3-27b-it"
    JUDGE_MODEL = "nvidia/Llama-3.3-70B-Instruct-FP8"
    OUTPUT_BASE = "/home/gpuuser7/gpuuser7_a/prateek/GEM-Bench/GemBench/benchmarking/output"

    # Auto-generate tag and output dir based on mode
    base_short = _short_name(BASE_MODEL)
    judge_short = _short_name(JUDGE_MODEL)
    if args.mode == "generate":
        TAGS = f"base_{base_short}"
        OUTPUT_DIR = os.path.join(OUTPUT_BASE, "generate_results")
    elif args.mode == "evaluate":
        TAGS = f"judge_{judge_short}_base_{base_short}"
        OUTPUT_DIR = os.path.join(OUTPUT_BASE, "evaluate_results")
    else:
        TAGS = f"full_{base_short}_judge_{judge_short}"
        OUTPUT_DIR = OUTPUT_BASE

    # initialize the methods workflow
    chi_workflow = AdChatWorkflow(
            product_list_path=PRODUCT_DATASET_PATH,
            topic_list_path=TOPIC_DATASET_PATH,
            model_name=BASE_MODEL,
    )
    advocate_workflow = AdLLMWorkflow(
            product_list_path=PRODUCT_DATASET_PATH,
            # rag_model="text-embedding-3-small",
            rag_model="Sentence-Transformers/all-MiniLM-L6-v2",
            model_name=BASE_MODEL,
            score_func=LINEAR_WEIGHT,
            # score_func=LOG_WEIGHT,
    )
    # Example usage of the GemBench
    adv_bench = GemBench(
        # data_sets=["MT-Human"],
        # data_sets=["LM-Market"],
        # data_sets=["MT-Human", "LM-Market"],
        solutions={
                "Ad-Chat": 
                    partial(
                        chi_workflow.run,
                        solution_name="chi"
                    ),
                "GI-R": 
                    partial(
                        advocate_workflow.run,
                        query_type="QUERY_RESPONSE",
                        solution_name="BASIC_GEN_INSERT"
                    )
                ,
                "GI-P": 
                    partial(
                        advocate_workflow.run,
                        query_type="QUERY_PROMPT",
                        solution_name="BASIC_GEN_INSERT"
                    )
                ,
                "GIR-R": 
                    partial(
                        advocate_workflow.run,
                        query_type="QUERY_RESPONSE",
                        solution_name="REFINE_GEN_INSERT"
                    )
                ,
                "GIR-P": 
                    partial(
                        advocate_workflow.run,
                         query_type="QUERY_PROMPT",
                         solution_name="REFINE_GEN_INSERT"
                     )
                ,
        },
        best_product_selector={
            "Ad-Chat": 
                partial(
                    chi_workflow.get_best_product,
                    solution_name="chi"
                ),
            "GI-R": 
                partial(
                    advocate_workflow.run,
                    query_type="QUERY_RESPONSE",
                    solution_name="BASIC_GEN_INSERT"
                )
            ,
            "GI-P": 
                partial(
                    advocate_workflow.run,
                    query_type="QUERY_PROMPT",
                    solution_name="BASIC_GEN_INSERT"
                )
            ,
            "GIR-R": 
                partial(
                    advocate_workflow.run,
                    query_type="QUERY_RESPONSE",
                    solution_name="REFINE_GEN_INSERT"
                )
            ,
            "GIR-P": 
                partial(
                    advocate_workflow.run,
                        query_type="QUERY_PROMPT",
                        solution_name="REFINE_GEN_INSERT"
                    )
            ,
        },
        judge_model=JUDGE_MODEL,
        output_dir=OUTPUT_DIR,
        n_repeats=3,
        tags=TAGS
    )
    print(f"Mode: {args.mode or 'full'} | Tag: {TAGS}")

    timer = Timer()

    if args.mode == "generate":
        print("Starting generation phase...")
        with timer.track("generation"):
            gen_results, select_results = adv_bench.process_results()
        print("Generation complete! Check the output/ folder for results.json")

    elif args.mode == "evaluate":
        from GemBench.benchmarking.utils.struct import SolutionResult

        if not args.results_path:
            parser.error("--results-path is required when --mode is 'evaluate'")

        results_path = args.results_path
        if not os.path.isabs(results_path):
            results_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), results_path)

        print(f"Loading generated results from: {results_path}")
        results = SolutionResult.load(results_path)
        gen_results = results.query_result_by_attr(filters={"dataSet": ["MT-Human", "LM-Market"]})
        select_results = results.query_result_by_attr(filters={"dataSet": ["CA_Prod"]})

        print("Starting evaluation phase...")
        with timer.track("evaluation"):
            adv_bench.evaluate(gen_results, select_results)
        
        with timer.track("reporting"):
            adv_bench.report()
        print("Evaluation complete! Check the output/ folder for reports.")

    else:
        # Default: original behavior — generate + evaluate + report all at once
        print("Running full pipeline (generate + evaluate + report)...")
        with timer.track("full_pipeline"):
            adv_bench.run()
            
    timer.summary()