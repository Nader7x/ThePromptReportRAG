"""
The Prompt Report Knowledge Base
Systematically extracted from "The Prompt Report" to build a comprehensive knowledge base
for a RAG application designed to categorize and enhance user prompts.

Phase 1: Data Extraction - Building the Knowledge Base
"""

import json
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Dict, List, Optional

# ================================================================================
# A. FUNDAMENTAL PROMPT COMPONENTS [1.2.1, 19-25]
# ================================================================================


@dataclass
class PromptComponent:
    component_name: str
    description: str
    usage_notes: Optional[str] = None
    template_example: Optional[str] = None
    design_decisions: Optional[List[Dict[str, str]]] = None


# Fundamental Components based on sections/vocabulary/components.tex
FUNDAMENTAL_COMPONENTS = [
    PromptComponent(
        component_name="Directive",
        description="The core intent or instruction of the prompt, which can be explicit (e.g., a question or instruction) or implicit (e.g., in one-shot cases like translation). Sometimes simply called the 'intent'.",
        usage_notes="How it guides GenAI output. Can be explicit instructions or implicit demonstrations.",
        template_example="Tell me five good books to read.",
    ),
    PromptComponent(
        component_name="Examples (Exemplars/Shots)",
        description="Demonstrations provided to guide the GenAI to accomplish a task, also known as exemplars or shots.",
        usage_notes="Act as demonstrations that guide the GenAI. The number and quality significantly affects performance.",
        template_example="Night: Noche \\ Morning:",
        design_decisions=[
            {
                "name": "Quantity",
                "description": "General improvement with more exemplars, diminishing returns beyond 20 for some models, continued increase for long-context LLMs.",
                "details": "Increasing quantity generally improves performance, particularly in larger models. Benefits may diminish beyond 20 exemplars in some cases, but long context LLMs continue to benefit from additional exemplars.",
            },
            {
                "name": "Ordering",
                "description": "Affects model behavior, can cause significant accuracy variation (sub-50% to 90%+).",
                "details": "The order of exemplars affects model behavior significantly. On some tasks, exemplar order can cause accuracy to vary from sub-50% to 90%+.",
            },
            {
                "name": "Label Distribution",
                "description": "Needs to be balanced to avoid bias.",
                "details": "The distribution of exemplar labels affects behavior. If 10 exemplars from one class and 2 from another are included, this may cause bias toward the first class.",
            },
            {
                "name": "Label Quality",
                "description": "Unclear necessity for strict validity; some work suggests irrelevance, while others show significant impact; larger models handle incorrect labels better.",
                "details": "Despite general benefit of multiple exemplars, necessity of strictly valid demonstrations is unclear. Some work suggests label accuracy is irrelevant, while other settings show significant impact. Larger models are often better at handling incorrect or unrelated labels.",
            },
            {
                "name": "Format",
                "description": "'Q: {input}, A: {label}' is common, but optimal may vary; common formats in training data tend to perform better.",
                "details": "One of the most common formats is 'Q: {input}, A: {label}', but optimal format may vary across tasks. Evidence suggests formats that occur commonly in training data lead to better performance.",
            },
            {
                "name": "Similarity",
                "description": "Generally beneficial to select exemplars similar to the test sample, though diverse ones can also improve performance.",
                "details": "Selecting exemplars similar to the test sample is generally beneficial for performance. However, in some cases, selecting more diverse exemplars can improve performance.",
            },
        ],
    ),
    PromptComponent(
        component_name="Output Formatting",
        description="Instructions for the desired output structure (e.g., CSV, Markdown, XML, JSON, custom formats).",
        usage_notes="Can sometimes reduce performance, but other sources suggest improvement when done properly.",
        template_example="{PARAGRAPH} Summarize this into a CSV.",
    ),
    PromptComponent(
        component_name="Style Instructions",
        description="Used to modify the output stylistically rather than structurally.",
        usage_notes="Different from output formatting as it focuses on style rather than structure.",
        template_example="Write a clear and curt paragraph about llamas.",
    ),
    PromptComponent(
        component_name="Role",
        description="Assigns a specific persona to the GenAI, influencing writing and style. Also known as 'persona'.",
        usage_notes="Can create more desirable outputs for open-ended tasks and sometimes improve accuracy.",
        template_example="Pretend you are a shepherd and write a limerick about llamas.",
    ),
    PromptComponent(
        component_name="Additional Information",
        description="Any other context needed in the prompt (e.g., name, position for an email). Sometimes referred to as 'context', though the report discourages this due to ambiguity.",
        usage_notes="Often necessary to include for proper task completion. Term 'context' is discouraged due to overloaded meanings in prompting space.",
        template_example="Information such as your name and position for email writing.",
    ),
]

# ================================================================================
# B. TEXT-BASED PROMPTING TECHNIQUES TAXONOMY [2.2, 35, Figure 2.2]
# ================================================================================


class TechniqueCategory(Enum):
    IN_CONTEXT_LEARNING = "In-Context Learning"
    ZERO_SHOT = "Zero-Shot"
    THOUGHT_GENERATION = "Thought Generation"
    DECOMPOSITION = "Decomposition"
    ENSEMBLING = "Ensembling"
    SELF_CRITICISM = "Self-Criticism"


@dataclass
class PromptingTechnique:
    technique_name: str
    category: TechniqueCategory
    sub_category: Optional[str] = None
    description: str = ""
    how_to_apply: str = ""
    benefits: str = ""
    prerequisites_or_inputs: str = ""
    related_techniques: List[str] = None

    def __post_init__(self):
        if self.related_techniques is None:
            self.related_techniques = []


# Text-Based Prompting Techniques (58 total from Figure 2.2)
TEXT_BASED_TECHNIQUES = [
    # ========== IN-CONTEXT LEARNING ==========
    PromptingTechnique(
        technique_name="Few-Shot Prompting",
        category=TechniqueCategory.IN_CONTEXT_LEARNING,
        description="The paradigm where the GenAI learns to complete a task with only a few examples (exemplars). A special case of Few-Shot Learning (FSL) but does not require updating model parameters.",
        how_to_apply="Include multiple input-output exemplars in the prompt following formats like 'Q: {input}, A: {label}'. Consider the six design decisions: quantity, ordering, label distribution, label quality, format, and similarity.",
        benefits="Enables models to learn new tasks without parameter updates. Performance generally improves with more exemplars, especially in larger models.",
        prerequisites_or_inputs="Training dataset with input-output pairs to use as exemplars",
        related_techniques=["Zero-Shot Prompting", "Chain-of-Thought", "In-Context Learning"],
    ),
    PromptingTechnique(
        technique_name="K-Nearest Neighbor (KNN)",
        category=TechniqueCategory.IN_CONTEXT_LEARNING,
        sub_category="Exemplar Selection",
        description="Selects exemplars similar to the test input to boost performance as part of few-shot prompting.",
        how_to_apply="Use similarity metrics to select exemplars from training data that are most similar to the test input.",
        benefits="Effective for improving performance by providing relevant demonstrations.",
        prerequisites_or_inputs="Training dataset and similarity metric (e.g., embedding-based)",
        related_techniques=["Few-Shot Prompting", "Vote-K", "Exemplar Selection"],
    ),
    PromptingTechnique(
        technique_name="Vote-K",
        category=TechniqueCategory.IN_CONTEXT_LEARNING,
        sub_category="Exemplar Selection",
        description="Method to select similar exemplars to test sample in two stages: model proposes unlabeled candidates for annotation, then uses labeled pool for Few-Shot Prompting.",
        how_to_apply="Stage 1: Use model to propose useful unlabeled candidate exemplars for human annotation. Stage 2: Use labeled pool for Few-Shot Prompting, ensuring new exemplars are sufficiently different to increase diversity.",
        benefits="Ensures diversity and representativeness of exemplars while maintaining similarity to test samples.",
        prerequisites_or_inputs="Unlabeled candidate pool and human annotators",
        related_techniques=["KNN", "Few-Shot Prompting", "Exemplar Selection"],
    ),
    PromptingTechnique(
        technique_name="Self-Generated In-Context Learning (SG-ICL)",
        category=TechniqueCategory.IN_CONTEXT_LEARNING,
        sub_category="Exemplar Generation",
        description="Leverages a GenAI to automatically generate exemplars when training data is unavailable.",
        how_to_apply="Prompt the GenAI to generate input-output examples for the target task, then use these generated examples as few-shot exemplars.",
        benefits="Better than zero-shot scenarios when training data is unavailable, though not as effective as actual data.",
        prerequisites_or_inputs="Target task description, no training data required",
        related_techniques=["Few-Shot Prompting", "Zero-Shot Prompting"],
    ),
    # ========== ZERO-SHOT ==========
    PromptingTechnique(
        technique_name="Role Prompting",
        category=TechniqueCategory.ZERO_SHOT,
        description="Assigns a specific role to the GenAI in the prompt, also known as persona prompting. Creates more desirable outputs for open-ended tasks and may improve accuracy on benchmarks.",
        how_to_apply="Include role assignment in prompt such as 'Act like Madonna' or 'You are a travel writer'. Specify the persona before the main instruction.",
        benefits="Creates more desirable outputs for open-ended tasks and in some cases may improve accuracy on benchmarks.",
        prerequisites_or_inputs="Definition of desired role or persona",
        related_techniques=["Style Prompting", "Persona Prompting"],
    ),
    PromptingTechnique(
        technique_name="Style Prompting",
        category=TechniqueCategory.ZERO_SHOT,
        description="Involves specifying the desired style, tone, or genre in the prompt to shape the output of a GenAI. Similar effect can be achieved using role prompting.",
        how_to_apply="Include style specifications in the prompt such as 'Write in a formal tone', 'Use casual language', or 'Write in the style of a news article'.",
        benefits="Shapes output to match desired style, tone, or genre requirements.",
        prerequisites_or_inputs="Definition of desired style characteristics",
        related_techniques=["Role Prompting", "Style Instructions"],
    ),
    PromptingTechnique(
        technique_name="Emotion Prompting",
        category=TechniqueCategory.ZERO_SHOT,
        description="Incorporates phrases of psychological relevance to humans (e.g., 'This is important to my career') into the prompt, which may lead to improved LLM performance on benchmarks and open-ended text generation.",
        how_to_apply="Add emotionally relevant phrases to prompts such as 'This is important to my career', 'Take your time', or 'This will help many people'.",
        benefits="May lead to improved LLM performance on benchmarks and open-ended text generation.",
        prerequisites_or_inputs="Understanding of psychologically relevant phrases",
        related_techniques=["Role Prompting", "Style Prompting"],
    ),
    PromptingTechnique(
        technique_name="System 2 Attention (S2A)",
        category=TechniqueCategory.ZERO_SHOT,
        description="First asks an LLM to rewrite the prompt and remove any information unrelated to the question therein. Then, it passes this new prompt into an LLM to retrieve a final response.",
        how_to_apply="Step 1: Prompt LLM to rewrite and remove irrelevant information. Step 2: Use the cleaned prompt for the actual task.",
        benefits="Helps eliminate effect of irrelevant information in the prompt, improving focus on core question.",
        prerequisites_or_inputs="Original prompt that may contain irrelevant information",
        related_techniques=["SimToM", "Two-step prompting"],
    ),
    PromptingTechnique(
        technique_name="SimToM",
        category=TechniqueCategory.ZERO_SHOT,
        description="Deals with complicated questions involving multiple people or objects. Attempts to establish the set of facts one person knows, then answer based only on those facts.",
        how_to_apply="Step 1: Establish what facts one person in the scenario knows. Step 2: Answer the question based only on those established facts. This is a two prompt process.",
        benefits="Helps eliminate effect of irrelevant information in prompts involving multiple entities.",
        prerequisites_or_inputs="Complex scenario with multiple people or objects",
        related_techniques=["S2A", "Two-step prompting"],
    ),
    PromptingTechnique(
        technique_name="Rephrase and Respond (RaR)",
        category=TechniqueCategory.ZERO_SHOT,
        description="Instructs the LLM to rephrase and expand the question before generating the final answer.",
        how_to_apply="Add phrase to question such as 'Rephrase and expand the question, and respond'. Can be done in single pass or pass new question separately.",
        benefits="Has demonstrated improvements on multiple benchmarks by encouraging better understanding of the question.",
        prerequisites_or_inputs="Original question or prompt",
        related_techniques=["Re-reading", "Question reformulation"],
    ),
    PromptingTechnique(
        technique_name="Re-reading (RE2)",
        category=TechniqueCategory.ZERO_SHOT,
        description="Adds the phrase 'Read the question again:' to the prompt in addition to repeating the question.",
        how_to_apply="Add 'Read the question again:' followed by repeating the original question.",
        benefits="Simple technique that has shown improvement in reasoning benchmarks, especially with complex questions.",
        prerequisites_or_inputs="Original question",
        related_techniques=["RaR", "Question repetition"],
    ),
    PromptingTechnique(
        technique_name="Self-Ask",
        category=TechniqueCategory.ZERO_SHOT,
        description="Prompts the model to ask itself follow-up questions to decompose complex problems.",
        how_to_apply="Instruct the model to ask follow-up questions and answer them step by step before providing final answer.",
        benefits="Helps break down complex problems into manageable sub-questions.",
        prerequisites_or_inputs="Complex question that can benefit from decomposition",
        related_techniques=["Decomposition techniques", "Question generation"],
    ),
    # ========== THOUGHT GENERATION ==========
    PromptingTechnique(
        technique_name="Chain-of-Thought (CoT) Prompting",
        category=TechniqueCategory.THOUGHT_GENERATION,
        description="Leverages few-shot prompting to encourage the LLM to express its thought process before delivering its final answer. Significantly enhances performance in mathematics and reasoning tasks.",
        how_to_apply="Include exemplars that feature a question, a reasoning path, and the correct answer. Show the model how to think step by step through examples.",
        benefits="Significantly enhances the LLM's performance in mathematics and reasoning tasks.",
        prerequisites_or_inputs="Exemplars with reasoning paths",
        related_techniques=["Zero-Shot CoT", "Few-Shot CoT", "Auto-CoT"],
    ),
    PromptingTechnique(
        technique_name="Zero-Shot CoT",
        category=TechniqueCategory.THOUGHT_GENERATION,
        sub_category="Chain-of-Thought (CoT)",
        description="A straightforward version of Chain-of-Thought (CoT) that encourages the LLM to express its thought process without requiring any exemplars.",
        how_to_apply="Append a thought-inducing phrase to the prompt. Examples: 'Let's think step by step.', 'First, let's think about this logically.', 'Let's work this out in a step by step way to be sure we have the right answer'.",
        benefits="Enhances LLM performance in mathematics and reasoning tasks; attractive as it doesn't require exemplars and is generally task agnostic.",
        prerequisites_or_inputs="N/A (zero exemplars needed)",
        related_techniques=[
            "Chain-of-Thought (CoT)",
            "Analogical Prompting",
            "Step-Back Prompting",
            "Thread-of-Thought (ThoT)",
            "Tabular Chain-of-Thought (Tab-CoT)",
        ],
    ),
    PromptingTechnique(
        technique_name="Step-Back Prompting",
        category=TechniqueCategory.THOUGHT_GENERATION,
        sub_category="Chain-of-Thought (CoT)",
        description="A modification of CoT where the LLM is first asked a generic, high-level question about relevant concepts or facts before delving into reasoning.",
        how_to_apply="Step 1: Ask a high-level, generic question about relevant concepts. Step 2: Use that information for detailed reasoning on the original question.",
        benefits="Has improved performance significantly on multiple reasoning benchmarks for both PaLM-2L and GPT-4.",
        prerequisites_or_inputs="Complex reasoning question that can benefit from high-level concept review",
        related_techniques=["Zero-Shot CoT", "Analogical Prompting"],
    ),
    PromptingTechnique(
        technique_name="Thread-of-Thought (ThoT) Prompting",
        category=TechniqueCategory.THOUGHT_GENERATION,
        sub_category="Chain-of-Thought (CoT)",
        description="Consists of an improved thought inducer for CoT reasoning. Uses more sophisticated prompting than simple 'Let's think step by step.'",
        how_to_apply="Instead of 'Let's think step by step,' use 'Walk me through this context in manageable parts step by step, summarizing and analyzing as we go.'",
        benefits="Works well in question-answering and retrieval settings, especially when dealing with large, complex contexts.",
        prerequisites_or_inputs="Complex contexts or lengthy materials to analyze",
        related_techniques=["Zero-Shot CoT", "Chain-of-Thought"],
    ),
    PromptingTechnique(
        technique_name="Tabular Chain-of-Thought (Tab-CoT)",
        category=TechniqueCategory.THOUGHT_GENERATION,
        sub_category="Chain-of-Thought (CoT)",
        description="Consists of a Zero-Shot CoT prompt that makes the LLM output reasoning as a markdown table.",
        how_to_apply="Use Zero-Shot CoT prompting but instruct the model to format its reasoning steps as a markdown table.",
        benefits="Tabular design enables the LLM to improve the structure and thus the reasoning of its output.",
        prerequisites_or_inputs="Tasks that can benefit from structured reasoning presentation",
        related_techniques=["Zero-Shot CoT", "Structured reasoning"],
    ),
    PromptingTechnique(
        technique_name="Analogical Prompting",
        category=TechniqueCategory.THOUGHT_GENERATION,
        sub_category="Chain-of-Thought (CoT)",
        description="Similar to SG-ICL, automatically generates exemplars that include CoTs (Chain of Thoughts).",
        how_to_apply="Automatically generate exemplars that include reasoning chains similar to the target problem, using analogies to guide the reasoning process.",
        benefits="Has demonstrated improvements in mathematical reasoning and code generation tasks.",
        prerequisites_or_inputs="Target problem that can benefit from analogical reasoning",
        related_techniques=["SG-ICL", "Auto-CoT", "Chain-of-Thought"],
    ),
    PromptingTechnique(
        technique_name="Few-Shot CoT",
        category=TechniqueCategory.THOUGHT_GENERATION,
        sub_category="Chain-of-Thought (CoT)",
        description="Presents the LLM with multiple exemplars which include chains-of-thought. Can significantly enhance performance.",
        how_to_apply="Include multiple exemplars in the prompt, each showing question, reasoning chain, and answer. Also referred to as Manual-CoT or Golden CoT.",
        benefits="Can significantly enhance performance compared to Zero-Shot CoT.",
        prerequisites_or_inputs="Multiple exemplars with high-quality reasoning chains",
        related_techniques=["Chain-of-Thought", "Auto-CoT", "Contrastive CoT"],
    ),
    PromptingTechnique(
        technique_name="Contrastive CoT Prompting",
        category=TechniqueCategory.THOUGHT_GENERATION,
        sub_category="Chain-of-Thought (CoT)",
        description="Adds both exemplars with incorrect and correct explanations to the CoT prompt in order to show the LLM how not to reason.",
        how_to_apply="Include both positive examples (correct reasoning) and negative examples (incorrect reasoning) in the prompt to contrast good and bad reasoning approaches.",
        benefits="Has shown significant improvement in areas like Arithmetic Reasoning and Factual QA.",
        prerequisites_or_inputs="Examples of both correct and incorrect reasoning for the task",
        related_techniques=["Few-Shot CoT", "Chain-of-Thought"],
    ),
    PromptingTechnique(
        technique_name="Uncertainty-Routed CoT Prompting",
        category=TechniqueCategory.THOUGHT_GENERATION,
        sub_category="Chain-of-Thought (CoT)",
        description="Samples multiple CoT reasoning paths, then selects the majority if above a certain threshold, otherwise samples greedily.",
        how_to_apply="Sample multiple reasoning paths, calculate agreement threshold based on validation data. If majority exceeds threshold, use majority vote; otherwise, use greedy sampling.",
        benefits="Demonstrates improvement on MMLU benchmark for both GPT-4 and Gemini Ultra models.",
        prerequisites_or_inputs="Validation data to calculate thresholds",
        related_techniques=["Self-Consistency", "CoT Prompting"],
    ),
    PromptingTechnique(
        technique_name="Complexity-based Prompting",
        category=TechniqueCategory.THOUGHT_GENERATION,
        sub_category="Chain-of-Thought (CoT)",
        description="Involves selecting complex examples for annotation and using majority vote among chains exceeding length threshold during inference.",
        how_to_apply="Step 1: Select complex examples based on factors like question length or reasoning steps. Step 2: During inference, sample multiple reasoning chains and use majority vote among chains exceeding certain length threshold.",
        benefits="Has shown improvements on three mathematical reasoning datasets.",
        prerequisites_or_inputs="Complex examples and length thresholds for reasoning chains",
        related_techniques=["CoT Prompting", "Complexity analysis"],
    ),
    PromptingTechnique(
        technique_name="Active Prompting",
        category=TechniqueCategory.THOUGHT_GENERATION,
        sub_category="Chain-of-Thought (CoT)",
        description="Starts with training questions/exemplars, asks LLM to solve them, calculates uncertainty (disagreement), then asks human annotators to rewrite highest uncertainty exemplars.",
        how_to_apply="Step 1: Use LLM to solve training exemplars. Step 2: Calculate uncertainty/disagreement. Step 3: Have humans rewrite exemplars with highest uncertainty.",
        benefits="Improves quality of exemplars through human feedback on uncertain cases.",
        prerequisites_or_inputs="Training exemplars and human annotators",
        related_techniques=["Few-Shot CoT", "Human-in-the-loop"],
    ),
    PromptingTechnique(
        technique_name="Automatic Chain-of-Thought (Auto-CoT) Prompting",
        category=TechniqueCategory.THOUGHT_GENERATION,
        sub_category="Chain-of-Thought (CoT)",
        description="Uses Zero-Shot prompt to automatically generate chains of thought, which are then used to build a Few-Shot CoT prompt for test sample.",
        how_to_apply="Step 1: Use Zero-Shot CoT to generate reasoning chains for training examples. Step 2: Use these generated chains as exemplars in Few-Shot CoT prompt for test sample.",
        benefits="Automates the creation of reasoning exemplars without manual annotation.",
        prerequisites_or_inputs="Training examples for chain generation",
        related_techniques=["Zero-Shot CoT", "Few-Shot CoT"],
    ),
    PromptingTechnique(
        technique_name="Memory-of-Thought Prompting",
        category=TechniqueCategory.THOUGHT_GENERATION,
        sub_category="Chain-of-Thought (CoT)",
        description="Leverages unlabeled training exemplars to build Few-Shot CoT prompts at test time by performing inference on unlabeled training exemplars with CoT.",
        how_to_apply="Step 1: Perform CoT inference on unlabeled training exemplars. Step 2: At test time, retrieve similar instances to test sample and use as few-shot exemplars.",
        benefits="Has shown substantial improvements in benchmarks like Arithmetic, commonsense, and factual reasoning.",
        prerequisites_or_inputs="Unlabeled training exemplars",
        related_techniques=["Few-Shot CoT", "Retrieval-based prompting"],
    ),
    # ========== DECOMPOSITION ==========
    PromptingTechnique(
        technique_name="Least-to-Most Prompting",
        category=TechniqueCategory.DECOMPOSITION,
        description="Starts by prompting a LLM to break a given problem into sub-problems without solving them. Then, it solves them sequentially, appending model responses to the prompt each time.",
        how_to_apply="Step 1: Prompt LLM to break problem into sub-problems. Step 2: Solve sub-problems sequentially, appending each response to prompt for context.",
        benefits="Has shown significant improvements in tasks involving symbolic manipulation, compositional generalization, and mathematical reasoning.",
        prerequisites_or_inputs="Complex problems that can be decomposed into sub-problems",
        related_techniques=["Decomposed Prompting", "Sub-question generation"],
    ),
    PromptingTechnique(
        technique_name="Decomposed Prompting (DECOMP)",
        category=TechniqueCategory.DECOMPOSITION,
        description="Few-Shot prompts a LLM to show it how to use certain functions. The LLM breaks down its original problem into sub-problems which it sends to different functions.",
        how_to_apply="Show LLM how to use functions (string splitting, internet searching, etc.) through few-shot examples. LLM then decomposes problems and sends sub-problems to appropriate functions.",
        benefits="Has shown improved performance over Least-to-Most prompting on some tasks.",
        prerequisites_or_inputs="Set of available functions and few-shot examples of their usage",
        related_techniques=["Least-to-Most Prompting", "Tool use"],
    ),
    PromptingTechnique(
        technique_name="Plan-and-Solve Prompting",
        category=TechniqueCategory.DECOMPOSITION,
        description="Consists of an improved Zero-Shot CoT prompt that focuses on planning before execution.",
        how_to_apply="Use the prompt: 'Let's first understand the problem and devise a plan to solve it. Then, let's carry out the plan and solve the problem step by step'.",
        benefits="Generates more robust reasoning processes than standard Zero-Shot-CoT on multiple reasoning datasets.",
        prerequisites_or_inputs="Complex reasoning problems that benefit from planning",
        related_techniques=["Zero-Shot CoT", "Planning-based approaches"],
    ),
    PromptingTechnique(
        technique_name="Recursion-of-Thought",
        category=TechniqueCategory.DECOMPOSITION,
        description="Similar to regular CoT, but sends complicated sub-problems encountered during reasoning to another prompt/LLM call, then inserts the answer back into original prompt.",
        how_to_apply="During reasoning chain, when encountering complex sub-problem, send it to separate LLM call, then insert result back into original reasoning chain.",
        benefits="Can recursively solve complex problems, including ones which might exceed maximum context length. Has shown improvements on arithmetic and algorithmic tasks.",
        prerequisites_or_inputs="Complex problems with sub-problems that exceed context limits",
        related_techniques=["Chain-of-Thought", "Recursive problem solving"],
    ),
    PromptingTechnique(
        technique_name="Program-of-Thoughts",
        category=TechniqueCategory.DECOMPOSITION,
        description="Generates code to solve reasoning problems instead of natural language reasoning chains.",
        how_to_apply="Instead of generating natural language reasoning, prompt the model to write and execute code that solves the problem.",
        benefits="Can leverage computational tools and precise logic for problem solving.",
        prerequisites_or_inputs="Problems that can be solved programmatically",
        related_techniques=["Code generation", "Tool use"],
    ),
    PromptingTechnique(
        technique_name="Skeleton-of-Thought",
        category=TechniqueCategory.DECOMPOSITION,
        description="Focuses on accelerating answer speed through parallelization by creating a skeleton of the answer as sub-problems to be solved in parallel.",
        how_to_apply="Step 1: Prompt LLM to create skeleton/outline of answer as sub-problems. Step 2: Send sub-problems to LLM in parallel. Step 3: Concatenate outputs for final response.",
        benefits="Accelerates answer generation through parallelization.",
        prerequisites_or_inputs="Problems that can be decomposed into parallel sub-tasks",
        related_techniques=["Parallel processing", "Decomposition"],
    ),
    PromptingTechnique(
        technique_name="Metacognitive Prompting",
        category=TechniqueCategory.DECOMPOSITION,
        description="Attempts to make the LLM mirror human metacognitive processes with a five-part prompt chain.",
        how_to_apply="Use five-step process: 1) Clarifying the question, 2) Preliminary judgement, 3) Evaluation of response, 4) Decision confirmation, 5) Confidence assessment.",
        benefits="Mirrors human metacognitive processes for improved understanding.",
        prerequisites_or_inputs="Complex problems requiring metacognitive analysis",
        related_techniques=["Multi-step reasoning", "Self-evaluation"],
    ),
    # ========== ENSEMBLING ==========
    PromptingTechnique(
        technique_name="Self-Consistency",
        category=TechniqueCategory.ENSEMBLING,
        description="Samples multiple reasoning paths and selects the most consistent answer through majority voting.",
        how_to_apply="Generate multiple reasoning paths for the same problem (typically with temperature > 0), then select the answer that appears most frequently across the paths.",
        benefits="Improves reliability and accuracy by leveraging multiple reasoning attempts.",
        prerequisites_or_inputs="Problem that can be solved multiple ways",
        related_techniques=["Chain-of-Thought", "Majority voting"],
    ),
    PromptingTechnique(
        technique_name="Mixture of Reasoning Experts (MoRE)",
        category=TechniqueCategory.ENSEMBLING,
        description="Creates a set of diverse reasoning experts using different specialized prompts for different reasoning types, then selects best answer based on agreement score.",
        how_to_apply="Create specialized prompts for different reasoning types (retrieval augmentation for factual, CoT for multi-hop math, generated knowledge for commonsense). Select best answer based on agreement score.",
        benefits="Leverages specialized reasoning approaches for different problem types.",
        prerequisites_or_inputs="Problems that can benefit from different reasoning approaches",
        related_techniques=["Specialized prompting", "Expert systems"],
    ),
    PromptingTechnique(
        technique_name="Max Mutual Information Method",
        category=TechniqueCategory.ENSEMBLING,
        description="Creates multiple prompt templates with varied styles and exemplars, then selects the optimal template as the one that maximizes mutual information between prompt and LLM outputs.",
        how_to_apply="Create multiple prompt variations with different styles and exemplars. Select template that maximizes mutual information between prompt and model outputs.",
        benefits="Systematically selects optimal prompt variation based on information theory.",
        prerequisites_or_inputs="Multiple prompt template variations",
        related_techniques=["Prompt optimization", "Information theory"],
    ),
    PromptingTechnique(
        technique_name="DiVeRSe",
        category=TechniqueCategory.ENSEMBLING,
        description="Creates multiple prompts for a given problem then performs Self-Consistency for each, generating multiple reasoning paths. Scores reasoning paths based on each step.",
        how_to_apply="Step 1: Create multiple prompts for same problem. Step 2: Perform Self-Consistency for each prompt. Step 3: Score reasoning paths based on individual steps. Step 4: Select final response.",
        benefits="Combines multiple prompt variations with consistency checking.",
        prerequisites_or_inputs="Problem amenable to multiple prompt formulations",
        related_techniques=["Self-Consistency", "Multiple prompts"],
    ),
    PromptingTechnique(
        technique_name="Consistency-based Self-adaptive Prompting (COSP)",
        category=TechniqueCategory.ENSEMBLING,
        description="Constructs Few-Shot CoT prompts by running Zero-Shot CoT with Self-Consistency on examples, then selecting high agreement subset for final prompt exemplars.",
        how_to_apply="Step 1: Run Zero-Shot CoT with Self-Consistency on example set. Step 2: Select subset with high agreement. Step 3: Use as exemplars in Few-Shot CoT prompt. Step 4: Apply Self-Consistency again.",
        benefits="Automatically selects high-quality exemplars based on consistency.",
        prerequisites_or_inputs="Example set for exemplar generation",
        related_techniques=["Self-Consistency", "Auto-CoT"],
    ),
    PromptingTechnique(
        technique_name="Universal Self-Adaptive Prompting (USP)",
        category=TechniqueCategory.ENSEMBLING,
        description="Builds upon COSP, aiming to make it generalizable to all tasks. Uses unlabeled data to generate exemplars and more complicated scoring function.",
        how_to_apply="Use unlabeled data to generate exemplars with more sophisticated scoring function than COSP. Does not use Self-Consistency in final step.",
        benefits="Generalizable approach that works across different task types.",
        prerequisites_or_inputs="Unlabeled data for exemplar generation",
        related_techniques=["COSP", "Task-agnostic prompting"],
    ),
    # ========== SELF-CRITICISM ==========
    PromptingTechnique(
        technique_name="Self-Calibration",
        category=TechniqueCategory.SELF_CRITICISM,
        description="First prompts an LLM to answer a question, then builds a new prompt asking whether the answer is correct for gauging confidence levels.",
        how_to_apply="Step 1: Prompt LLM to answer question. Step 2: Create new prompt with question, LLM's answer, and instruction asking if answer is correct.",
        benefits="Useful for gauging confidence levels when applying LLMs and deciding when to accept or revise original answer.",
        prerequisites_or_inputs="Initial question and model response",
        related_techniques=["Self-evaluation", "Confidence estimation"],
    ),
    PromptingTechnique(
        technique_name="Self-Refine",
        category=TechniqueCategory.SELF_CRITICISM,
        description="Iterative framework where LLM provides feedback on its own answer, then improves the answer based on the feedback until stopping condition is met.",
        how_to_apply="Step 1: Get initial answer from LLM. Step 2: Prompt same LLM to provide feedback. Step 3: Prompt LLM to improve answer based on feedback. Step 4: Repeat until stopping condition (e.g., max steps).",
        benefits="Has demonstrated improvement across a range of reasoning, coding, and generation tasks.",
        prerequisites_or_inputs="Initial response and stopping criteria",
        related_techniques=["Iterative improvement", "Self-feedback"],
    ),
    PromptingTechnique(
        technique_name="Reversing Chain-of-Thought (RCoT)",
        category=TechniqueCategory.SELF_CRITICISM,
        description="First prompts LLMs to reconstruct the problem based on generated answer, then generates fine-grained comparisons between original and reconstructed problem.",
        how_to_apply="Step 1: Generate answer to original problem. Step 2: Prompt LLM to reconstruct problem from answer. Step 3: Compare original and reconstructed problems for inconsistencies.",
        benefits="Helps check for inconsistencies and errors in reasoning.",
        prerequisites_or_inputs="Original problem and generated answer",
        related_techniques=["Consistency checking", "Reverse reasoning"],
    ),
    PromptingTechnique(
        technique_name="Cumulative Reasoning",
        category=TechniqueCategory.SELF_CRITICISM,
        description="Generates several potential steps in answering the question. It then has a LLM evaluate them, deciding to either accept or reject these steps. Finally, it checks whether it has arrived at the final answer.  If so, it terminates the process, but otherwise it repeats it. This method has demonstrated improvements in logical inference tasks and mathematical problem.",
        how_to_apply="Step 1: Generate potential reasoning steps. Step 2: Have LLM evaluate each step (accept/reject). Step 3: Check if final answer reached. Step 4: If not, repeat process.",
        benefits="Has demonstrated improvements in logical inference tasks and mathematical problems.",
        prerequisites_or_inputs="Multi-step problems amenable to incremental solving",
        related_techniques=["Step-by-step evaluation", "Incremental reasoning"],
    ),
    PromptingTechnique(
        technique_name="Chain-of-Verification (COVE)",
        category=TechniqueCategory.SELF_CRITICISM,
        description="First uses an LLM to generate an answer to a given question. Then, it creates a list of related questions that would help verify the correctness of the answer. Each question is answered by the LLM, then all the information is given to the LLM to produce the final revised answer.",
        how_to_apply="Step 1: Generate initial answer. Step 2: Create verification questions. Step 3: Answer verification questions. Step 4: Use all information to produce final revised answer.",
        benefits="Has shown improvements in various question-answering and text-generation tasks.",
        prerequisites_or_inputs="Initial question and response requiring verification",
        related_techniques=["Self-verification", "Question generation"],
    ),
    PromptingTechnique(
        technique_name="Self-Verification",
        category=TechniqueCategory.SELF_CRITICISM,
        description="Generates multiple candidate solutions with Chain-of-Thought (CoT). It then scores each solution by masking certain parts of the original question and asking an LLM to predict them based on the rest of the question and the generated solution.",
        how_to_apply="Step 1: Generate multiple CoT solutions. Step 2: Mask parts of original question. Step 3: Score solutions by predicting masked parts. Step 4: Select best solution.",
        benefits="Has shown improvement on eight reasoning datasets.",
        prerequisites_or_inputs="Questions amenable to masking and reconstruction",
        related_techniques=["Chain-of-Thought", "Self-consistency"],
    ),
    # Additional THOUGHT GENERATION techniques
    PromptingTechnique(
        technique_name="Tree-of-Thought (ToT)",
        category=TechniqueCategory.DECOMPOSITION,
        description="Creates a tree-like search problem by starting with an initial problem then generating multiple possible steps in the form of thoughts. It evaluates the progress each step makes towards solving the problem and decides which steps to continue with.",
        how_to_apply="Step 1: Start with initial problem. Step 2: Generate multiple possible thought steps. Step 3: Evaluate progress of each step. Step 4: Continue with promising steps, creating tree-like search.",
        benefits="Particularly effective for tasks that require search and planning.",
        prerequisites_or_inputs="Complex problems requiring search and planning",
        related_techniques=["Chain-of-Thought", "Search algorithms"],
    ),
    PromptingTechnique(
        technique_name="Faithful Chain-of-Thought",
        category=TechniqueCategory.DECOMPOSITION,
        description="Generates a CoT that has both natural language and symbolic language (e.g. Python) reasoning. Makes use of different types of symbolic languages in a task-dependent fashion.",
        how_to_apply="Generate reasoning chain combining natural language explanations with symbolic/programming language expressions appropriate for the task domain.",
        benefits="Combines benefits of natural language reasoning with symbolic precision.",
        prerequisites_or_inputs="Tasks that can benefit from symbolic reasoning",
        related_techniques=["Program-of-Thoughts", "Chain-of-Thought"],
    ),
    # Additional ENSEMBLING techniques
    PromptingTechnique(
        technique_name="Universal Self-Consistency",
        category=TechniqueCategory.ENSEMBLING,
        description="Similar to universal Self-Consistency; it first generates multiple reasoning chains (but not necessarily final answers) for a given problem. Next, it inserts all of these chains in a single prompt template then generates a final answer from them.",
        how_to_apply="Step 1: Generate multiple reasoning chains for problem. Step 2: Insert all chains into single prompt template. Step 3: Generate final answer from combined chains.",
        benefits="Leverages multiple reasoning paths without requiring final answers from each.",
        prerequisites_or_inputs="Problems amenable to multiple reasoning approaches",
        related_techniques=["Self-Consistency", "Multiple reasoning chains"],
    ),
    # Additional IN-CONTEXT LEARNING techniques
    PromptingTechnique(
        technique_name="Prompt Mining",
        category=TechniqueCategory.IN_CONTEXT_LEARNING,
        sub_category="Exemplar Selection",
        description="The process of discovering optimal 'middle words' in prompts through large corpus analysis. These middle words are effectively prompt templates.",
        how_to_apply="Analyze large corpus to find frequently occurring prompt formats. Use formats that occur more often in corpus for better performance instead of common formats like 'Q: A:'.",
        benefits="Formats which occur more often in the corpus will likely lead to improved prompt performance.",
        prerequisites_or_inputs="Large corpus for analysis",
        related_techniques=["Few-Shot Prompting", "Template optimization"],
    ),
    PromptingTechnique(
        technique_name="LENS",
        category=TechniqueCategory.IN_CONTEXT_LEARNING,
        sub_category="Exemplar Selection",
        description="More complicated technique that leverages iterative filtering for exemplar selection.",
        how_to_apply="Use iterative filtering process to select optimal exemplars for few-shot prompting.",
        benefits="Improved exemplar selection through systematic filtering.",
        prerequisites_or_inputs="Pool of candidate exemplars",
        related_techniques=["Few-Shot Prompting", "Active Example Selection"],
    ),
    PromptingTechnique(
        technique_name="UDR (Unified Demonstration Retrieval)",
        category=TechniqueCategory.IN_CONTEXT_LEARNING,
        sub_category="Exemplar Selection",
        description="More complicated technique that leverages embedding and retrieval for exemplar selection.",
        how_to_apply="Use embedding-based retrieval to select most relevant exemplars for the target task.",
        benefits="Improved exemplar relevance through semantic similarity.",
        prerequisites_or_inputs="Embedding model and exemplar database",
        related_techniques=["KNN", "Embedding-based retrieval"],
    ),
    PromptingTechnique(
        technique_name="Active Example Selection",
        category=TechniqueCategory.IN_CONTEXT_LEARNING,
        sub_category="Exemplar Selection",
        description="More complicated technique that leverages reinforcement learning for exemplar selection.",
        how_to_apply="Use reinforcement learning to learn optimal exemplar selection strategy.",
        benefits="Learned selection strategy adapted to specific tasks.",
        prerequisites_or_inputs="Training data and RL framework",
        related_techniques=["Reinforcement learning", "Few-Shot Prompting"],
    ),
    # Final missing techniques to complete 58 total
    PromptingTechnique(
        technique_name="Exemplar Ordering",
        category=TechniqueCategory.IN_CONTEXT_LEARNING,
        sub_category="Exemplar Selection",
        description="The order of exemplars affects model behavior. On some tasks, exemplar order can cause accuracy to vary from sub-50% to 90%+.",
        how_to_apply="Carefully arrange the order of exemplars in the prompt, considering that different orderings can significantly impact performance.",
        benefits="Can dramatically improve performance by optimizing exemplar sequence.",
        prerequisites_or_inputs="Multiple exemplars that can be reordered",
        related_techniques=["Few-Shot Prompting", "Exemplar Selection"],
    ),
    PromptingTechnique(
        technique_name="Instruction Selection",
        category=TechniqueCategory.IN_CONTEXT_LEARNING,
        sub_category="Few-Shot Instructions",
        description="While instructions are required for zero-shot prompts, in few-shot prompts generic task-agnostic instructions often improve classification and QA accuracy over task-specific ones.",
        how_to_apply="Use generic instructions like 'Complete the following task:' rather than task-specific instructions. Instruction-following abilities can be achieved via exemplars alone.",
        benefits="Improves classification and question answering accuracy. Instructions can still guide auxiliary output attributes like writing style.",
        prerequisites_or_inputs="Few-shot prompts that can benefit from optimized instruction selection",
        related_techniques=["Few-Shot Prompting", "Zero-Shot Prompting"],
    ),
    PromptingTechnique(
        technique_name="AutoDiCoT (Automatic Directed Chain-of-Thought)",
        category=TechniqueCategory.THOUGHT_GENERATION,
        sub_category="Chain-of-Thought (CoT)",
        description="Automatically directs the CoT process to reason in a particular way. Combines automatic generation of CoTs with showing the LLM examples of bad reasoning (contrastive approach).",
        how_to_apply="Step 1: Label training examples. Step 2: For incorrect labels, prompt 'It is actually [correct label], please explain why.' Step 3: Use generated reasoning as exemplars showing what NOT to do.",
        benefits="Combines automatic CoT generation with contrastive learning to improve reasoning quality.",
        prerequisites_or_inputs="Training examples with labels for generating contrastive reasoning examples",
        related_techniques=["Auto-CoT", "Contrastive CoT", "Chain-of-Thought"],
    ),
    PromptingTechnique(
        technique_name="DENSE (Demonstration Ensembling)",
        category=TechniqueCategory.ENSEMBLING,
        description="Creates multiple few-shot prompts, each containing a distinct subset of exemplars from the training set. Next, it aggregates over their outputs to generate a final response.",
        how_to_apply="Step 1: Create multiple few-shot prompts with different exemplar subsets. Step 2: Run each prompt separately. Step 3: Aggregate outputs (usually via majority vote) for final response.",
        benefits="Reduces variance and often improves accuracy by leveraging diverse exemplar subsets.",
        prerequisites_or_inputs="Training set with multiple exemplars that can be divided into subsets",
        related_techniques=["Few-Shot Prompting", "Ensembling", "Self-Consistency"],
    ),
    PromptingTechnique(
        technique_name="Meta-CoT (Meta-Reasoning over Multiple CoTs)",
        category=TechniqueCategory.ENSEMBLING,
        description="Similar to Universal Self-Consistency; first generates multiple reasoning chains (but not necessarily final answers) for a given problem. Next, inserts all chains in a single prompt template then generates a final answer.",
        how_to_apply="Step 1: Generate multiple reasoning chains for the problem. Step 2: Insert all reasoning chains into a single prompt template. Step 3: Generate final answer from the combined chains.",
        benefits="Leverages multiple reasoning paths without requiring final answers from each chain.",
        prerequisites_or_inputs="Problems amenable to multiple reasoning approaches",
        related_techniques=["Universal Self-Consistency", "Chain-of-Thought", "Ensembling"],
    ),
    PromptingTechnique(
        technique_name="Prompt Paraphrasing",
        category=TechniqueCategory.ENSEMBLING,
        description="Transforms an original prompt by changing some of the wording, while still maintaining the overall meaning. Effectively a data augmentation technique that can be used to generate prompts for an ensemble.",
        how_to_apply="Create multiple variations of the original prompt by paraphrasing while preserving meaning. Use these variations in an ensemble approach with majority voting.",
        benefits="Provides prompt diversity for ensembling while maintaining semantic meaning.",
        prerequisites_or_inputs="Original prompt that can be paraphrased in multiple ways",
        related_techniques=["Ensembling", "Prompt Engineering", "Data Augmentation"],
    ),
    # 58th technique - Zero-Shot Prompting as the foundational technique
    PromptingTechnique(
        technique_name="Zero-Shot Prompting",
        category=TechniqueCategory.ZERO_SHOT,
        description="The foundational prompting paradigm that uses zero exemplars and relies only on instructions to guide the GenAI's response.",
        how_to_apply="Provide clear instructions without any examples. Use natural language instructions that specify the desired task and output format.",
        benefits="Simple, fast, and doesn't require examples. Often serves as baseline for comparison with other techniques.",
        prerequisites_or_inputs="Clear task description and instructions",
        related_techniques=["Few-Shot Prompting", "Chain-of-Thought", "Role Prompting"],
    ),
]

# ================================================================================
# C. EXTENSIONS OF PROMPTING [4, 116, Figures 4.1, 4.2]
# ================================================================================


@dataclass
class AgentType:
    type_name: str
    description: str
    example_techniques: List[str]
    how_it_works_example: str


AGENT_TYPES = [
    AgentType(
        type_name="Tool Use Agents",
        description="LLMs making API calls to use external tools (symbolic like calculators or neural like other LLMs).",
        example_techniques=["MRKL System", "CRITIC"],
        how_it_works_example="For MRKL, LLM router provides access to multiple tools, combines info for final response. For CRITIC, LLM generates response, criticizes it, then uses tools to verify/amend.",
    ),
    AgentType(
        type_name="Code-Generation Agents",
        description="Agents that write and execute code.",
        example_techniques=["PAL", "ToRA", "TaskWeaver"],
        how_it_works_example="PAL translates problems directly into code for interpreter; ToRA interleaves code/reasoning; TaskWeaver uses user-defined plugins.",
    ),
    AgentType(
        type_name="Observation-Based Agents",
        description="Agents designed to solve problems by interacting with toy environments, receiving observations in their prompts.",
        example_techniques=["ReAct", "Reflexion", "Voyager", "Ghost in the Minecraft (GITM)"],
        how_it_works_example="ReAct generates thought, takes action, receives observation repeatedly, with all info in prompt as memory. Reflexion adds introspection and reflection on success/failure.",
    ),
    AgentType(
        type_name="Retrieval Augmented Generation (RAG)",
        description="Paradigm where information is retrieved from an external source and inserted into the prompt to enhance performance in knowledge-intensive tasks.",
        example_techniques=[
            "Verify-and-Edit",
            "Demonstrate-Search-Predict (DSP)",
            "Interleaved Retrieval guided by Chain-of-Thought (IRCoT)",
            "Iterative Retrieval Augmentation (FLARE, IRP)",
        ],
        how_it_works_example="For Verify-and-Edit, multiple CoT chains are generated, some selected for editing by retrieving relevant external info. For Iterative RAG, an iterative three-step process: generate temp sentence, retrieve knowledge, inject knowledge.",
    ),
]


@dataclass
class EvaluationTechnique:
    technique_name: str
    description: str
    category: str = "Prompting Techniques"


@dataclass
class EvaluationFormat:
    format_type: str
    description: str = ""


@dataclass
class EvaluationFramework:
    framework_name: str
    description: str = ""


EVALUATION_TECHNIQUES = [
    EvaluationTechnique(
        technique_name="In-Context Learning for Evaluation",
        description="Frequently used in evaluation prompts, much in the same way it is used in other applications.",
        category="Prompting Techniques",
    ),
    EvaluationTechnique(
        technique_name="Role-based Evaluation",
        description="Improves and diversifies evaluations by assigning different roles. Creates prompts with same instructions but different roles for diverse evaluations.",
        category="Prompting Techniques",
    ),
    EvaluationTechnique(
        technique_name="Chain-of-Thought for Evaluation",
        description="Further improves evaluation performance by having models reason through their evaluations step by step.",
        category="Prompting Techniques",
    ),
    EvaluationTechnique(
        technique_name="Model-Generated Guidelines",
        description="Prompts LLM to generate evaluation guidelines, reducing insufficient prompting problems.",
        category="Prompting Techniques",
    ),
]

EVALUATION_FORMATS = [
    EvaluationFormat(
        format_type="Styling (XML, JSON)", description="Structured output formats for evaluation results."
    ),
    EvaluationFormat(
        format_type="Linear Scale (e.g., 1-5, 1-10, 0-1)",
        description="Numerical scales for rating quality or performance.",
    ),
    EvaluationFormat(
        format_type="Binary Score (Yes/No, True/False)", description="Simple binary judgments for evaluation."
    ),
    EvaluationFormat(
        format_type="Likert Scale",
        description="Structured scales with qualitative descriptors (Poor, Acceptable, Good, Very Good, Incredible).",
    ),
]

EVALUATION_FRAMEWORKS = [
    EvaluationFramework(
        framework_name="LLM-EVAL",
        description="One of the simplest evaluation frameworks. Uses a single prompt that contains a schema of variables to evaluate (e.g. grammar, relevance, etc.), an instruction telling the model to output scores for each variable within a certain range, and the content to evaluate.",
    ),
    EvaluationFramework(
        framework_name="G-EVAL (includes AutoCoT steps)",
        description="Similar to LLM-EVAL, but includes an AutoCoT steps in the prompt itself. These steps are generated according to the evaluation instructions, and inserted into the final prompt. These weight answers according to token probabilities.",
    ),
    EvaluationFramework(
        framework_name="ChatEval (multi-agent debate framework)",
        description="Uses a multi-agent debate framework with each agent having a separate role.",
    ),
]

# ================================================================================
# D. PROMPT ENGINEERING TECHNIQUES (for Automatic Optimization) [2.4, 82-90]
# ================================================================================


@dataclass
class PromptEngineeringTechnique:
    technique_name: str
    description: str
    template_example: Optional[str] = None
    process_steps: Optional[List[str]] = None
    notes: Optional[str] = None


PROMPT_ENGINEERING_TECHNIQUES = [
    PromptEngineeringTechnique(
        technique_name="Meta Prompting",
        description="Prompting an LLM to generate or improve a prompt or prompt template.",
        template_example="Improve the following prompt: {PROMPT}.",
        notes="Can be simple or complex with multiple iterations and scoring.",
    ),
    PromptEngineeringTechnique(
        technique_name="Automatic Prompt Engineer (APE)",
        description="Uses exemplars to generate a Zero-Shot instruction prompt, generates multiple prompts, scores them, and creates variations.",
        process_steps=[
            "Generate initial prompts from exemplars",
            "Score generated prompts",
            "Create variations (e.g., via prompt paraphrasing)",
            "Iterate until desiderata reached",
        ],
    ),
    PromptEngineeringTechnique(
        technique_name="Gradientfree Instructional Prompt Search (GrIPS)",
        description="Similar to APE, but uses a more complex set of operations (deletion, addition, swapping, paraphrasing) to create prompt variations.",
    ),
    PromptEngineeringTechnique(
        technique_name="Prompt Optimization with Textual Gradients (ProTeGi)",
        description="Improves prompt templates through a multi-step process involving LLM criticism of the original prompt.",
        process_steps=[
            "Pass batch of inputs through template",
            "Pass output, ground truth, and prompt into criticism prompt",
            "Generate new prompts from criticisms",
            "Use bandit algorithm to select one",
        ],
    ),
    PromptEngineeringTechnique(
        technique_name="RLPrompt",
        description="Uses a frozen LLM with an unfrozen module to generate prompt templates, scores them, and updates the module using reinforcement learning.",
        notes="Often selects grammatically nonsensical text as optimal prompt template.",
    ),
    PromptEngineeringTechnique(
        technique_name="Dialogue-comprised Policy-gradient-based Discrete Prompt Optimization (DP2O)",
        description="Complex technique involving reinforcement learning, a custom scoring function, and conversations with an LLM to construct the prompt.",
        notes="Perhaps the most complicated prompt engineering technique.",
    ),
]

# ================================================================================
# E. MULTILINGUAL AND MULTIMODAL PROMPTING [3, 96, Figures 3.1, 3.2]
# ================================================================================


@dataclass
class MultilingualTechnique:
    technique_name: str
    description: str
    area: str = "Multilingual"
    example_process: Optional[str] = None
    notes: Optional[str] = None


@dataclass
class MultimodalTechnique:
    technique_name: str
    description: str
    modality: str
    area: str = "Multimodal"


MULTILINGUAL_TECHNIQUES = [
    MultilingualTechnique(
        technique_name="Translate First Prompting",
        description="Translates non-English input examples into English first to leverage the model's English strengths.",
    ),
    MultilingualTechnique(
        technique_name="Cross-Lingual CoT (XLT, CLSP)",
        description="Extends CoT to multilingual settings, including constructing reasoning paths in different languages.",
    ),
    MultilingualTechnique(
        technique_name="In-Context Learning (X-InSTA, In-CLT, PARC)",
        description="Extends ICL to multilingual settings, often involving alignment of in-context examples (semantic, task-based) or retrieval from high-resource languages.",
    ),
    MultilingualTechnique(
        technique_name="Prompt Template Language Selection",
        description="Discussion on whether English or the task language is more effective for prompt templates.",
        notes="English templates often more effective due to pre-training data predominance; task language prompts used for specific cases, human-translated superior to machine-translated.",
    ),
    MultilingualTechnique(
        technique_name="Prompting for Machine Translation (MAPS, CoD, DiPMT, DecoMT)",
        description="Leveraging GenAI for accurate and nuanced translation.",
        example_process="MAPS mimics human translation with knowledge mining, multiple translations, and selection. CoD/DiPMT prepend dictionary phrases. DecoMT divides text into chunks for independent translation.",
    ),
]

MULTIMODAL_TECHNIQUES = [
    # Image Prompting
    MultimodalTechnique(
        technique_name="Prompt Modifiers",
        description="Words appended to change resultant image (e.g., 'on canvas', 'a well lit scene').",
        modality="Image",
    ),
    MultimodalTechnique(
        technique_name="Negative Prompting",
        description="Numerically weights terms so model considers them more/less heavily (e.g., negatively weighting 'bad hands').",
        modality="Image",
    ),
    MultimodalTechnique(
        technique_name="Paired-Image Prompting (Multimodal ICL)",
        description="Shows two images (before/after transformation) then a new image for the demonstrated conversion.",
        modality="Image",
    ),
    MultimodalTechnique(
        technique_name="Image-as-Text Prompting (Multimodal ICL)",
        description="Generates textual description of an image for inclusion in a text-based prompt.",
        modality="Image",
    ),
    MultimodalTechnique(
        technique_name="Multimodal Chain-of-Thought (DDCoT, Multimodal GoT, CoI)",
        description="Extends CoT to image domain, e.g., image of math problem with 'Solve this step by step'. DDCoT extends Least-to-Most. CoI generates images as part of thought process with 'Let's think image by image'.",
        modality="Image",
    ),
    # Audio Prompting
    MultimodalTechnique(
        technique_name="Audio Prompting",
        description="Prompting extended to audio modality, still in early stages.",
        modality="Audio",
    ),
    # Video Prompting
    MultimodalTechnique(
        technique_name="Video Prompting",
        description="Prompting extended to video modality for text-to-video generation, editing, video-to-text.",
        modality="Video",
    ),
    # Segmentation Prompting
    MultimodalTechnique(
        technique_name="Segmentation Prompting",
        description="Prompting used for segmentation tasks (e.g., semantic segmentation).",
        modality="Segmentation",
    ),
    # 3D Prompting
    MultimodalTechnique(
        technique_name="3D Prompting",
        description="Prompting used in 3D modalities (e.g., 3D object synthesis, texturing, 4D scene generation).",
        modality="3D",
    ),
]

# ================================================================================
# KNOWLEDGE BASE EXPORT FUNCTIONS
# ================================================================================


def export_knowledge_base():
    """Export the complete knowledge base as structured data."""

    def convert_technique(tech):
        """Convert technique to dict with enum values as strings."""
        tech_dict = asdict(tech)
        tech_dict["category"] = tech.category.value
        return tech_dict

    knowledge_base = {
        "fundamental_components": [asdict(comp) for comp in FUNDAMENTAL_COMPONENTS],
        "text_based_techniques": [convert_technique(tech) for tech in TEXT_BASED_TECHNIQUES],
        "agent_types": [asdict(agent) for agent in AGENT_TYPES],
        "evaluation_techniques": [asdict(eval_tech) for eval_tech in EVALUATION_TECHNIQUES],
        "evaluation_formats": [asdict(eval_format) for eval_format in EVALUATION_FORMATS],
        "evaluation_frameworks": [asdict(framework) for framework in EVALUATION_FRAMEWORKS],
        "prompt_engineering_techniques": [asdict(pe_tech) for pe_tech in PROMPT_ENGINEERING_TECHNIQUES],
        "multilingual_techniques": [asdict(ml_tech) for ml_tech in MULTILINGUAL_TECHNIQUES],
        "multimodal_techniques": [asdict(mm_tech) for mm_tech in MULTIMODAL_TECHNIQUES],
    }
    return knowledge_base


def save_knowledge_base_json(filename="prompt_report_knowledge_base.json"):
    """Save the knowledge base to a JSON file."""
    kb = export_knowledge_base()
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(kb, f, indent=2, ensure_ascii=False)
    print(f"Knowledge base saved to {filename}")


def get_technique_by_name(technique_name: str) -> Optional[PromptingTechnique]:
    """Retrieve a specific technique by name."""
    for technique in TEXT_BASED_TECHNIQUES:
        if technique.technique_name.lower() == technique_name.lower():
            return technique
    return None


def get_techniques_by_category(category: TechniqueCategory) -> List[PromptingTechnique]:
    """Retrieve all techniques in a specific category."""
    return [tech for tech in TEXT_BASED_TECHNIQUES if tech.category == category]


def search_techniques_by_keyword(keyword: str) -> List[PromptingTechnique]:
    """Search techniques by keyword in name, description, or benefits."""
    keyword = keyword.lower()
    results = []
    for tech in TEXT_BASED_TECHNIQUES:
        if (
            keyword in tech.technique_name.lower()
            or keyword in tech.description.lower()
            or keyword in tech.benefits.lower()
            or keyword in tech.how_to_apply.lower()
        ):
            results.append(tech)
    return results


# ================================================================================
# MAIN EXECUTION
# ================================================================================

if __name__ == "__main__":
    # Export and save the knowledge base
    print("Building The Prompt Report Knowledge Base...")
    print(f"Total Fundamental Components: {len(FUNDAMENTAL_COMPONENTS)}")
    print(f"Total Text-Based Techniques: {len(TEXT_BASED_TECHNIQUES)}")
    print(f"Total Agent Types: {len(AGENT_TYPES)}")
    print(f"Total Evaluation Techniques: {len(EVALUATION_TECHNIQUES)}")
    print(f"Total Prompt Engineering Techniques: {len(PROMPT_ENGINEERING_TECHNIQUES)}")
    print(f"Total Multilingual Techniques: {len(MULTILINGUAL_TECHNIQUES)}")
    print(f"Total Multimodal Techniques: {len(MULTIMODAL_TECHNIQUES)}")

    # Save the knowledge base
    save_knowledge_base_json()

    # Example usage
    print("\n" + "=" * 50)
    print("EXAMPLE QUERIES:")
    print("=" * 50)

    # Example 1: Get a specific technique
    cot_technique = get_technique_by_name("Chain-of-Thought (CoT) Prompting")
    if cot_technique:
        print(f"\nTechnique: {cot_technique.technique_name}")
        print(f"Category: {cot_technique.category.value}")
        print(f"Description: {cot_technique.description}")
        print(f"How to Apply: {cot_technique.how_to_apply}")

    # Example 2: Get techniques by category
    thought_techniques = get_techniques_by_category(TechniqueCategory.THOUGHT_GENERATION)
    print(f"\nThought Generation Techniques ({len(thought_techniques)}):")
    for tech in thought_techniques[:3]:  # Show first 3
        print(f"- {tech.technique_name}")

    # Example 3: Search by keyword
    reasoning_techniques = search_techniques_by_keyword("reasoning")
    print(f"\nTechniques related to 'reasoning' ({len(reasoning_techniques)}):")
    for tech in reasoning_techniques[:3]:  # Show first 3
        print(f"- {tech.technique_name}")
