"""
Enhanced Prompt RAG Application - Phase 2 (Updated)
==================================================

Architecture Overview:
1. Prompt Categorization (Gemini API)
2. Knowledge Base Retrieval (Vector Search)
3. Prompt Enhancement (Gemini API)

This module implements the core RAG logic for enhancing user prompts
using "The Prompt Report" knowledge base.

UPDATE: Migrated from local Ollama TinyLlama to Gemini API for
prompt enhancement, providing better quality and consistency.
"""

import logging
import os
import pickle
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

import faiss
import google.generativeai as genai
from google.generativeai.types import HarmBlockThreshold, HarmCategory
from sentence_transformers import SentenceTransformer

# Import our knowledge base
from PromptReportKnowledgeBase import (
    TEXT_BASED_TECHNIQUES,
    get_technique_by_name,
)


# Configuration
@dataclass
class RAGConfig:
    """Configuration for the RAG application"""

    gemini_api_key: str
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    vector_store_path: str = "knowledge_base_vectors"
    max_retrieval_results: int = 3
    temperature: float = 0.7
    debug: bool = False


# Abstract Base Classes for Flexibility
class PromptCategorizer(ABC):
    """Abstract base class for prompt categorization"""

    @abstractmethod
    def categorize_prompt(self, user_prompt: str) -> str:
        """Categorize the user prompt and return the most relevant technique name"""
        pass


class KnowledgeRetriever(ABC):
    """Abstract base class for knowledge retrieval"""

    @abstractmethod
    def retrieve_technique_info(self, technique_name: str) -> Dict:
        """Retrieve detailed information about a specific technique"""
        pass

    @abstractmethod
    def search_knowledge(self, query: str, top_k: int = 3) -> List[Dict]:
        """Search the knowledge base using semantic similarity"""
        pass


class PromptSafetyChecker(ABC):
    """Abstract base class for prompt safety checking and sanitization"""

    @abstractmethod
    def check_and_sanitize_prompt(self, user_prompt: str) -> Dict:
        """
        Check if prompt is safe and sanitize if needed
        
        Returns:
            Dict with keys:
            - is_safe: bool
            - sanitized_prompt: str (original or sanitized version)
            - safety_issues: List[str] (list of issues found)
            - modifications_made: bool
        """
        pass


class PromptEnhancer(ABC):
    """Abstract base class for prompt enhancement"""

    @abstractmethod
    def enhance_prompt(self, original_prompt: str, context: Dict) -> str:
        """Enhance the original prompt using retrieved context"""
        pass


# Main RAG Application Class
class EnhancedPromptRAG:
    """
    Main RAG application that orchestrates the four-step process:
    1. Categorization -> 2. Safety Check -> 3. Retrieval -> 4. Enhancement
    """

    def __init__(self, config: RAGConfig):
        self.config = config
        self.setup_logging()

        # Components (will be initialized based on chosen implementations)
        self.categorizer: Optional[PromptCategorizer] = None
        self.safety_checker: Optional[PromptSafetyChecker] = None
        self.retriever: Optional[KnowledgeRetriever] = None
        self.enhancer: Optional[PromptEnhancer] = None

    def setup_logging(self):
        """Setup logging configuration"""
        level = logging.DEBUG if self.config.debug else logging.INFO
        logging.basicConfig(level=level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        self.logger = logging.getLogger(__name__)

    def initialize_components(
        self, categorizer: PromptCategorizer, safety_checker: PromptSafetyChecker, 
        retriever: KnowledgeRetriever, enhancer: PromptEnhancer
    ):
        """Initialize the RAG components"""
        self.categorizer = categorizer
        self.safety_checker = safety_checker
        self.retriever = retriever
        self.enhancer = enhancer
        self.logger.info("RAG components initialized successfully")

    def process_prompt(self, user_prompt: str) -> Dict:
        """
        Main method that processes a user prompt through the RAG pipeline

        Args:
            user_prompt: The original user prompt to enhance

        Returns:
            Dict containing the enhanced prompt and metadata
        """
        if not all([self.categorizer, self.safety_checker, self.retriever, self.enhancer]):
            raise ValueError("RAG components not properly initialized")

        try:
            self.logger.info(f"Processing user prompt: {user_prompt[:100]}...")

            # Step 1: Categorization
            self.logger.debug("Step 1: Categorizing prompt...")
            relevant_technique = self.categorizer.categorize_prompt(user_prompt)
            self.logger.info(f"Identified technique: {relevant_technique}")

            # Step 2: Safety Check and Sanitization
            self.logger.debug("Step 2: Checking prompt safety...")
            safety_result = self.safety_checker.check_and_sanitize_prompt(user_prompt)
            
            if not safety_result["is_safe"]:
                self.logger.warning(f"Unsafe prompt detected. Issues: {safety_result['safety_issues']}")
                if safety_result["modifications_made"]:
                    self.logger.info("Prompt has been sanitized for safety")
                    prompt_to_enhance = safety_result["sanitized_prompt"]
                else:
                    self.logger.error("Could not sanitize unsafe prompt")
                    return {
                        "original_prompt": user_prompt,
                        "enhanced_prompt": user_prompt,
                        "error": f"Unsafe prompt could not be sanitized: {safety_result['safety_issues']}",
                        "success": False,
                    }
            else:
                self.logger.info("Prompt passed safety check")
                prompt_to_enhance = user_prompt

            # Step 3: Retrieval
            self.logger.debug("Step 3: Retrieving knowledge...")
            technique_info = self.retriever.retrieve_technique_info(relevant_technique)
            additional_context = self.retriever.search_knowledge(prompt_to_enhance)

            context = {
                "technique": technique_info,
                "additional_context": additional_context,
                "original_prompt": user_prompt,
                "sanitized_prompt": prompt_to_enhance,
                "safety_result": safety_result,
            }

            # Step 4: Enhancement
            self.logger.debug("Step 4: Enhancing prompt...")
            enhanced_prompt = self.enhancer.enhance_prompt(prompt_to_enhance, context)

            result = {
                "original_prompt": user_prompt,
                "sanitized_prompt": prompt_to_enhance,
                "identified_technique": relevant_technique,
                "enhanced_prompt": enhanced_prompt,
                "safety_result": safety_result,
                "context_used": context,
                "success": True,
            }

            self.logger.info("Prompt enhancement completed successfully")
            return result

        except Exception as e:
            self.logger.error(f"Error processing prompt: {str(e)}")
            return {
                "original_prompt": user_prompt,
                "enhanced_prompt": user_prompt,  # Fallback to original
                "error": str(e),
                "success": False,
            }


# Production Implementation Classes
class GeminiCategorizer(PromptCategorizer):
    """Production categorizer using Gemini API"""

    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.5-flash")
        self.logger = logging.getLogger(__name__)

        # Prepare technique descriptions for categorization
        self.technique_descriptions = self._prepare_technique_descriptions()

    def _prepare_technique_descriptions(self) -> str:
        """Prepare concise descriptions of all techniques for Gemini"""
        descriptions = []
        for technique in TEXT_BASED_TECHNIQUES:
            desc = f"- {technique.technique_name}: {technique.description[:150]}..."
            descriptions.append(desc)
        return "\n".join(descriptions)

    def categorize_prompt(self, user_prompt: str) -> str:
        """Use Gemini to categorize the user prompt"""
        categorization_prompt = f"""
You are an expert prompt engineering analyst. Your task is to analyze a user's prompt and identify the most relevant prompting technique from "The Prompt Report" taxonomy.

Available Techniques:
{self.technique_descriptions}

User Prompt to Analyze:
"{user_prompt}"

Instructions:
1. Analyze the user's prompt for its intent, complexity, and structure
2. Determine which prompting technique would be most beneficial
3. Return ONLY the exact technique name from the list above
4. If multiple techniques could apply, choose the most impactful one

Response Format: Return only the technique name, nothing else.
"""

        try:
            response = self.model.generate_content(categorization_prompt)
            technique_name = response.text.strip()

            # Validate the response is a real technique
            if get_technique_by_name(technique_name):
                self.logger.info(f"Gemini categorized prompt as: {technique_name}")
                return technique_name
            else:
                # Fallback: try to find a close match
                self.logger.warning(f"Gemini returned unknown technique: {technique_name}")
                return self._find_closest_technique(technique_name)

        except Exception as e:
            self.logger.error(f"Gemini categorization failed: {e}")
            return "Zero-Shot Prompting"  # Safe fallback

    def _find_closest_technique(self, partial_name: str) -> str:
        """Find the closest matching technique name"""
        for technique in TEXT_BASED_TECHNIQUES:
            if partial_name.lower() in technique.technique_name.lower():
                return technique.technique_name
        return "Zero-Shot Prompting"  # Ultimate fallback


class GeminiSafetyChecker(PromptSafetyChecker):
    """Production safety checker using Gemini API"""

    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.5-flash")
        self.logger = logging.getLogger(__name__)
        self.logger.info("Gemini safety checker initialized successfully")

    def check_and_sanitize_prompt(self, user_prompt: str) -> Dict:
        """Check if prompt is safe and sanitize if needed using Gemini"""
        
        # First, do a quick safety assessment
        safety_check_prompt = f"""
You are a content safety analyst. Analyze the following user prompt for any potential safety issues.

User Prompt: "{user_prompt}"

Check for:
1. Harmful, toxic, or inappropriate content
2. Requests for illegal activities
3. Hate speech or harassment
4. Violence or dangerous content
5. Explicit sexual content
6. Privacy violations
7. Misinformation requests

Respond in this exact format:
SAFE: [YES/NO]
ISSUES: [list any issues found, separated by commas, or "none"]
SEVERITY: [LOW/MEDIUM/HIGH or "none"]

If the prompt has issues but can be made safe, suggest how to sanitize it while preserving the core intent.
"""

        try:
            self.logger.debug("Checking prompt safety with Gemini...")
            
            # Call Gemini for safety assessment
            response = self.model.generate_content(
                safety_check_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.1, top_p=0.8, max_output_tokens=300
                ),
                safety_settings=[
                    {
                        "category": HarmCategory.HARM_CATEGORY_HARASSMENT,
                        "threshold": HarmBlockThreshold.BLOCK_NONE,
                    },
                    {
                        "category": HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                        "threshold": HarmBlockThreshold.BLOCK_NONE,
                    },
                    {
                        "category": HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                        "threshold": HarmBlockThreshold.BLOCK_NONE,
                    },
                    {
                        "category": HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                        "threshold": HarmBlockThreshold.BLOCK_NONE,
                    },
                ],
            )

            # Check if response was blocked by safety filters (same fix as enhancer)
            if not response or not hasattr(response, "candidates") or not response.candidates:
                self.logger.warning("Gemini safety check returned no candidates - assuming safe for innocent prompts")
                return self._create_safe_result(user_prompt)

            candidate = response.candidates[0]
            
            # Check finish reason first
            if hasattr(candidate, "finish_reason"):
                finish_reason = candidate.finish_reason
                finish_reason_str = str(finish_reason)
                
                # Handle different finish reasons
                if finish_reason_str in ["2", "SAFETY"]:  # Safety block
                    self.logger.warning(f"Safety check itself was blocked by safety filter: {finish_reason_str}")
                    self.logger.info(f"Prompt that triggered safety filter in safety check: '{user_prompt}'")
                    return self._create_safe_result(user_prompt)
                elif finish_reason_str in ["3", "RECITATION"]:  # Recitation block
                    self.logger.warning(f"Safety check blocked due to recitation: {finish_reason_str}")
                    return self._create_safe_result(user_prompt)
                elif finish_reason_str in ["4", "OTHER"]:  # Other issues
                    self.logger.warning(f"Safety check blocked for other reasons: {finish_reason_str}")
                    return self._create_safe_result(user_prompt)

            # Check if we have valid content before accessing response.text
            if not hasattr(candidate, "content") or not candidate.content:
                self.logger.warning("Gemini safety check candidate has no content - assuming safe")
                return self._create_safe_result(user_prompt)

            # Safely access the text content
            try:
                safety_response_text = response.text.strip()
            except (AttributeError, ValueError) as text_error:
                self.logger.warning(f"Could not access safety check response.text: {text_error}")
                return self._create_safe_result(user_prompt)

            # Parse Gemini's safety assessment
            safety_analysis = self._parse_safety_response(safety_response_text)
            
            if safety_analysis["is_safe"]:
                self.logger.info("Prompt passed safety check")
                return {
                    "is_safe": True,
                    "sanitized_prompt": user_prompt,
                    "safety_issues": [],
                    "modifications_made": False,
                    "analysis": safety_analysis
                }
            else:
                # Attempt to sanitize the prompt
                self.logger.warning(f"Unsafe prompt detected: {safety_analysis['issues']}")
                sanitized_result = self._sanitize_prompt(user_prompt, safety_analysis)
                return sanitized_result

        except Exception as e:
            self.logger.error(f"Safety check failed: {e}")
            # Conservative fallback - assume safe for innocent-looking prompts
            if len(user_prompt) < 500 and not any(word in user_prompt.lower() for word in 
                ['hack', 'attack', 'violence', 'kill', 'bomb', 'weapon', 'drug', 'illegal']):
                self.logger.info("Safety check failed, but prompt appears innocent - allowing")
                return {
                    "is_safe": True,
                    "sanitized_prompt": user_prompt,
                    "safety_issues": ["safety_check_failed"],
                    "modifications_made": False,
                    "analysis": {"error": str(e)}
                }
            else:
                self.logger.warning("Safety check failed and prompt may be risky - blocking")
                return {
                    "is_safe": False,
                    "sanitized_prompt": user_prompt,
                    "safety_issues": ["safety_check_failed", "potentially_risky"],
                    "modifications_made": False,
                    "analysis": {"error": str(e)}
                }

    def _create_safe_result(self, user_prompt: str) -> Dict:
        """Create a safe result when safety check fails but prompt appears innocent"""
        return {
            "is_safe": True,
            "sanitized_prompt": user_prompt,
            "safety_issues": ["safety_check_system_blocked"],
            "modifications_made": False,
            "analysis": {"note": "Safety check system was blocked, but prompt appears safe"}
        }

    def _parse_safety_response(self, response_text: str) -> Dict:
        """Parse Gemini's safety assessment response"""
        try:
            lines = response_text.strip().split('\n')
            is_safe = False
            issues = []
            severity = "none"
            
            for line in lines:
                line = line.strip()
                if line.startswith("SAFE:"):
                    is_safe = "YES" in line.upper()
                elif line.startswith("ISSUES:"):
                    issues_text = line.split(":", 1)[1].strip()
                    if issues_text.lower() != "none":
                        issues = [issue.strip() for issue in issues_text.split(",")]
                elif line.startswith("SEVERITY:"):
                    severity = line.split(":", 1)[1].strip().lower()
            
            return {
                "is_safe": is_safe,
                "issues": issues,
                "severity": severity,
                "raw_response": response_text
            }
            
        except Exception as e:
            self.logger.error(f"Failed to parse safety response: {e}")
            return {
                "is_safe": False,
                "issues": ["parse_error"],
                "severity": "unknown",
                "raw_response": response_text
            }

    def _sanitize_prompt(self, user_prompt: str, safety_analysis: Dict) -> Dict:
        """Attempt to sanitize an unsafe prompt while preserving intent"""
        
        sanitization_prompt = f"""
You are a content moderator. The following prompt has been flagged for safety issues.

Original Prompt: "{user_prompt}"
Safety Issues: {safety_analysis['issues']}
Severity: {safety_analysis['severity']}

Please rewrite this prompt to make it safe while preserving the user's core legitimate intent. 

Guidelines:
1. Remove any harmful, toxic, or inappropriate elements
2. Keep the constructive educational or creative intent
3. Make it suitable for general audiences
4. If the prompt cannot be made safe, respond with "CANNOT_SANITIZE"

Sanitized Prompt:
"""

        try:
            self.logger.debug("Attempting to sanitize unsafe prompt...")
            
            response = self.model.generate_content(
                sanitization_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3, top_p=0.8, max_output_tokens=300
                ),
                safety_settings=[
                    {
                        "category": HarmCategory.HARM_CATEGORY_HARASSMENT,
                        "threshold": HarmBlockThreshold.BLOCK_NONE,
                    },
                    {
                        "category": HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                        "threshold": HarmBlockThreshold.BLOCK_NONE,
                    },
                    {
                        "category": HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                        "threshold": HarmBlockThreshold.BLOCK_NONE,
                    },
                    {
                        "category": HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                        "threshold": HarmBlockThreshold.BLOCK_NONE,
                    },
                ],
            )

            # Check if response was blocked by safety filters
            if not response or not hasattr(response, "candidates") or not response.candidates:
                self.logger.warning("Gemini sanitization returned no candidates")
                return {
                    "is_safe": False,
                    "sanitized_prompt": user_prompt,
                    "safety_issues": safety_analysis['issues'] + ["sanitization_system_blocked"],
                    "modifications_made": False,
                    "analysis": safety_analysis
                }

            candidate = response.candidates[0]
            
            # Check finish reason first
            if hasattr(candidate, "finish_reason"):
                finish_reason = candidate.finish_reason
                finish_reason_str = str(finish_reason)
                
                if finish_reason_str in ["2", "SAFETY", "3", "RECITATION", "4", "OTHER"]:
                    self.logger.warning(f"Sanitization blocked by safety filter: {finish_reason_str}")
                    return {
                        "is_safe": False,
                        "sanitized_prompt": user_prompt,
                        "safety_issues": safety_analysis['issues'] + ["sanitization_blocked"],
                        "modifications_made": False,
                        "analysis": safety_analysis
                    }

            # Check if we have valid content before accessing response.text
            if not hasattr(candidate, "content") or not candidate.content:
                self.logger.warning("Gemini sanitization candidate has no content")
                return {
                    "is_safe": False,
                    "sanitized_prompt": user_prompt,
                    "safety_issues": safety_analysis['issues'] + ["sanitization_no_content"],
                    "modifications_made": False,
                    "analysis": safety_analysis
                }

            # Safely access the text content
            try:
                sanitized_prompt = response.text.strip()
            except (AttributeError, ValueError) as text_error:
                self.logger.warning(f"Could not access sanitization response.text: {text_error}")
                return {
                    "is_safe": False,
                    "sanitized_prompt": user_prompt,
                    "safety_issues": safety_analysis['issues'] + ["sanitization_text_access_failed"],
                    "modifications_made": False,
                    "analysis": safety_analysis
                }
            
            if "CANNOT_SANITIZE" in sanitized_prompt:
                self.logger.warning("Prompt cannot be sanitized safely")
                return {
                    "is_safe": False,
                    "sanitized_prompt": user_prompt,
                    "safety_issues": safety_analysis['issues'],
                    "modifications_made": False,
                    "analysis": safety_analysis
                }
            else:
                self.logger.info("Successfully sanitized unsafe prompt")
                return {
                    "is_safe": True,
                    "sanitized_prompt": sanitized_prompt,
                    "safety_issues": safety_analysis['issues'],
                    "modifications_made": True,
                    "analysis": safety_analysis
                }

        except Exception as e:
            self.logger.error(f"Sanitization failed: {e}")
            return {
                "is_safe": False,
                "sanitized_prompt": user_prompt,
                "safety_issues": safety_analysis['issues'] + ["sanitization_failed"],
                "modifications_made": False,
                "analysis": safety_analysis
            }


class FAISSRetriever(KnowledgeRetriever):
    """Production retriever using FAISS vector database"""

    def __init__(self, config: RAGConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Initialize embedding model
        self.embedding_model = SentenceTransformer(config.embedding_model)
        self.embedding_dim = self.embedding_model.get_sentence_embedding_dimension()

        # FAISS index and metadata
        self.index = None
        self.technique_metadata = []
        self.knowledge_chunks = []

        # Initialize or load vector store
        self.vector_store_path = Path(config.vector_store_path)
        self._setup_vector_store()

    def _setup_vector_store(self):
        """Setup or load the FAISS vector store"""
        index_file = self.vector_store_path / "faiss_index.bin"
        metadata_file = self.vector_store_path / "metadata.pkl"

        if index_file.exists() and metadata_file.exists():
            self.logger.info("Loading existing FAISS index...")
            self._load_vector_store()
        else:
            self.logger.info("Creating new FAISS index...")
            self._create_vector_store()

    def _create_vector_store(self):
        """Create FAISS index from knowledge base"""
        self.vector_store_path.mkdir(exist_ok=True)

        # Prepare text chunks for embedding
        texts = []
        metadata = []

        for technique in TEXT_BASED_TECHNIQUES:
            # Create comprehensive text representation
            technique_text = f"""
            Technique: {technique.technique_name}
            Category: {technique.category.value}
            Description: {technique.description}
            How to Apply: {technique.how_to_apply}
            Benefits: {technique.benefits}
            Prerequisites: {technique.prerequisites_or_inputs}
            Related: {technique.related_techniques}
            """

            texts.append(technique_text.strip())
            metadata.append(
                {"technique_name": technique.technique_name, "category": technique.category.value, "type": "technique"}
            )

        # Generate embeddings
        self.logger.info("Generating embeddings...")
        embeddings = self.embedding_model.encode(texts, show_progress_bar=True)

        # Create FAISS index
        self.index = faiss.IndexFlatIP(self.embedding_dim)  # Inner product for cosine similarity

        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(embeddings)
        self.index.add(embeddings.astype("float32"))

        # Store metadata
        self.technique_metadata = metadata
        self.knowledge_chunks = texts

        # Save to disk
        self._save_vector_store()
        self.logger.info(f"Created FAISS index with {len(texts)} techniques")

    def _save_vector_store(self):
        """Save FAISS index and metadata to disk"""
        faiss.write_index(self.index, str(self.vector_store_path / "faiss_index.bin"))
        with open(self.vector_store_path / "metadata.pkl", "wb") as f:
            pickle.dump({"metadata": self.technique_metadata, "chunks": self.knowledge_chunks}, f)

    def _load_vector_store(self):
        """Load FAISS index and metadata from disk"""
        self.index = faiss.read_index(str(self.vector_store_path / "faiss_index.bin"))
        with open(self.vector_store_path / "metadata.pkl", "rb") as f:
            data = pickle.load(f)
            self.technique_metadata = data["metadata"]
            self.knowledge_chunks = data["chunks"]

    def retrieve_technique_info(self, technique_name: str) -> Dict:
        """Retrieve detailed information about a specific technique"""
        technique = get_technique_by_name(technique_name)
        if technique:
            return {
                "technique_name": technique.technique_name,
                "category": technique.category.value,
                "description": technique.description,
                "how_to_apply": technique.how_to_apply,
                "benefits": technique.benefits,
                "prerequisites_or_inputs": technique.prerequisites_or_inputs,
                "related_techniques": technique.related_techniques,
            }
        return {}

    def search_knowledge(self, query: str, top_k: int = 3) -> List[Dict]:
        """Search knowledge base using semantic similarity"""
        if not self.index:
            return []

        # Generate query embedding
        query_embedding = self.embedding_model.encode([query])
        faiss.normalize_L2(query_embedding)

        # Search FAISS index
        scores, indices = self.index.search(query_embedding.astype("float32"), top_k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(self.technique_metadata):
                result = self.technique_metadata[idx].copy()
                result["similarity_score"] = float(score)
                result["content"] = self.knowledge_chunks[idx]
                results.append(result)

        return results


class GeminiEnhancer(PromptEnhancer):
    """Production enhancer using Gemini API"""

    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.5-flash")
        self.logger = logging.getLogger(__name__)
        self.logger.info("Gemini enhancer initialized successfully")

    def enhance_prompt(self, original_prompt: str, context: Dict) -> str:
        """Enhance prompt using Gemini API with retrieved context"""
        technique_info = context.get("technique", {})
        additional_context = context.get("additional_context", [])

        # Get the primary identified technique name
        identified_primary_technique = technique_info.get("technique_name", "Unknown")
        self.logger.info(f"Enhancing prompt with technique: {identified_primary_technique}")

        # Filter related techniques if the primary is Zero-Shot Prompting
        if identified_primary_technique == "Zero-Shot Prompting":
            technique_info["technique_name"] = "Direct Instruction Following"
            self.logger.debug("Zero-Shot Prompting detected. Filtering ICL-based related techniques.")
            # Zero-Shot should not be 'enhanced' by adding example-based techniques (ICL)
            filtered_additional_context = [
                t
                for t in additional_context
                if t.get("category") != "In-Context Learning"  # Ensure 'category' is used correctly from retrieval
                and t.get("technique_name") != "Unified Demonstration Retrieval (UDR)"
                and t.get("technique_name") != "Self-Generated In-Context Learning (SG-ICL)"
                # Add other ICL-based techniques if present in your knowledge base
            ]
        else:
            filtered_additional_context = additional_context

        # Prepare additional context information
        context_info = ""
        if filtered_additional_context:
            context_info = "\n\nAdditional Related Techniques:"
            for ctx in filtered_additional_context[:2]:  # Limit to top 2 for clarity
                context_info += f"\n- {ctx.get('technique_name', 'Unknown')}: {ctx.get('content', '')[:200]}..."

        # Construct enhancement prompt for Gemini - Using safer template
        enhancement_prompt = f"""
You are a helpful writing assistant. Please help improve the clarity and effectiveness of the following request.

Original Request: "{original_prompt}"

Suggested Improvement Approach: {technique_info.get('technique_name', 'Unknown')}

Description: {technique_info.get('description', 'No description available')}

Guidance: {technique_info.get('how_to_apply', 'No specific guidance available')}

Please provide an improved version of the original request that is clearer and more specific while maintaining the same intent.

Improved Request:
"""

        try:
            self.logger.debug("Sending enhancement request to Gemini...")
            self.logger.debug(f"Enhancement prompt length: {len(enhancement_prompt)} characters")

            # Call Gemini API to enhance the prompt
            response = self.model.generate_content(
                enhancement_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7, top_p=0.9, max_output_tokens=500, candidate_count=1
                ),
                safety_settings=[
                    {
                        "category": HarmCategory.HARM_CATEGORY_HARASSMENT,
                        "threshold": HarmBlockThreshold.BLOCK_NONE,
                    },
                    {
                        "category": HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                        "threshold": HarmBlockThreshold.BLOCK_NONE,
                    },
                    {
                        "category": HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                        "threshold": HarmBlockThreshold.BLOCK_NONE,
                    },
                    {
                        "category": HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                        "threshold": HarmBlockThreshold.BLOCK_NONE,
                    },
                ],
            )

            # Comprehensive safety filter and response validation
            if not response or not hasattr(response, "candidates") or not response.candidates:
                self.logger.warning("Gemini returned no candidates, using fallback")
                return self._fallback_enhancement(original_prompt, technique_info)

            candidate = response.candidates[0]
            
            # Check finish reason first (this is where the error was happening)
            if hasattr(candidate, "finish_reason"):
                finish_reason = candidate.finish_reason
                finish_reason_str = str(finish_reason)
                
                # Handle different finish reasons
                if finish_reason_str in ["2", "SAFETY"]:  # Safety block
                    self.logger.warning(f"Response blocked by safety filter: {finish_reason_str}")
                    if hasattr(candidate, "safety_ratings"):
                        self.logger.warning(f"Safety ratings: {candidate.safety_ratings}")
                    self.logger.info(f"Original prompt that triggered safety filter: '{original_prompt}'")
                    return self._fallback_enhancement(original_prompt, technique_info)
                elif finish_reason_str in ["3", "RECITATION"]:  # Recitation block
                    self.logger.warning(f"Response blocked due to recitation: {finish_reason_str}")
                    return self._fallback_enhancement(original_prompt, technique_info)
                elif finish_reason_str in ["4", "OTHER"]:  # Other issues
                    self.logger.warning(f"Response blocked for other reasons: {finish_reason_str}")
                    return self._fallback_enhancement(original_prompt, technique_info)

            # Check if we have valid content before accessing response.text
            if not hasattr(candidate, "content") or not candidate.content:
                self.logger.warning("Gemini candidate has no content, using fallback")
                return self._fallback_enhancement(original_prompt, technique_info)

            # Safely access the text content
            try:
                enhanced_prompt = response.text.strip()
            except (AttributeError, ValueError) as text_error:
                self.logger.warning(f"Could not access response.text: {text_error}")
                return self._fallback_enhancement(original_prompt, technique_info)

            # Basic validation that we got a meaningful response
            if enhanced_prompt and len(enhanced_prompt) > 10:
                self.logger.info("Successfully enhanced prompt with Gemini")
                self.logger.debug(f"Enhanced prompt length: {len(enhanced_prompt)} characters")
                return enhanced_prompt
            else:
                self.logger.warning("Gemini returned empty or very short response, using fallback")
                return self._fallback_enhancement(original_prompt, technique_info)

        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"Gemini enhancement failed: {error_msg}")

            # Log detailed error information for safety issues
            if any(
                keyword in error_msg.lower() for keyword in ["safety", "blocked", "policy", "harmful", "inappropriate"]
            ):
                self.logger.error(f"SAFETY ISSUE DETECTED: {error_msg}")
                self.logger.error(f"Original prompt: {original_prompt}")
                self.logger.error(f"Identified technique: {technique_info.get('technique_name', 'Unknown')}")

            return self._fallback_enhancement(original_prompt, technique_info)

    def _fallback_enhancement(self, original_prompt: str, technique_info: Dict) -> str:
        """Fallback enhancement using template-based approach"""
        technique_name = technique_info.get("technique_name", "")
        how_to_apply = technique_info.get("how_to_apply", "")

        self.logger.info(f"Using fallback enhancement for technique: {technique_name}")

        # More sophisticated fallback based on technique categories
        if "Chain-of-Thought" in technique_name or "CoT" in technique_name:
            return f"{original_prompt}\n\nPlease think through this step-by-step and explain your reasoning:"
        elif "Role Prompting" in technique_name or "Role Playing" in technique_name:
            return f"You are an expert in this domain with extensive knowledge and experience. {original_prompt}"
        elif "Few-Shot" in technique_name:
            return f"{original_prompt}\n\nPlease provide a detailed response with examples if applicable:"
        elif "Zero-Shot" in technique_name:
            return f"{original_prompt}\n\nPlease provide a comprehensive and detailed response:"
        elif "Instruction Following" in technique_name:
            return f"Please follow these instructions carefully:\n\n{original_prompt}"
        elif "Self-Consistency" in technique_name:
            return f"{original_prompt}\n\nPlease think about this from multiple angles and provide a well-reasoned response:"
        elif "Generated Knowledge" in technique_name:
            return f"First, consider what background knowledge is relevant to this task, then:\n\n{original_prompt}"
        else:
            # Generic enhancement using the how_to_apply information
            if how_to_apply and how_to_apply != "No specific instructions available":
                return f"{original_prompt}\n\n{how_to_apply}"
            else:
                return f"{original_prompt}\n\nPlease provide a detailed and well-structured response:"


# Factory function for production setup
def create_production_rag(gemini_api_key: str) -> EnhancedPromptRAG:
    """Create a production-ready RAG system using Gemini for categorization, safety, and enhancement"""

    # Create configuration
    config = RAGConfig(
        gemini_api_key=gemini_api_key,
        embedding_model="sentence-transformers/all-MiniLM-L6-v2",
        vector_store_path="knowledge_base_vectors",
        debug=True,
    )

    # Initialize components - now all using Gemini
    categorizer = GeminiCategorizer(gemini_api_key)
    safety_checker = GeminiSafetyChecker(gemini_api_key)  # New safety checker
    retriever = FAISSRetriever(config)
    enhancer = GeminiEnhancer(gemini_api_key)  # Using Gemini for enhancement

    # Create and initialize RAG system
    rag = EnhancedPromptRAG(config)
    rag.initialize_components(categorizer, safety_checker, retriever, enhancer)

    return rag


# Implementation Options Discussion
class ImplementationOptions:
    """
    Class to document and discuss different implementation options
    """

    CATEGORIZER_OPTIONS = {
        "gemini_api": {
            "description": "Use Google Gemini API for categorization",
            "pros": ["High accuracy", "Latest model capabilities", "Good reasoning"],
            "cons": ["Requires API key", "Network dependency", "API costs"],
            "dependencies": ["google-generativeai"],
        },
        "classifier_model": {
            "description": "Fine-tuned classification model",
            "pros": ["Fast", "Deterministic", "Low resource"],
            "cons": ["Requires training", "Less flexible", "Limited to predefined categories"],
            "dependencies": ["transformers", "torch"],
        },
    }

    RETRIEVER_OPTIONS = {
        "faiss_vector": {
            "description": "FAISS vector store with embeddings",
            "pros": ["Fast similarity search", "Scalable", "Local storage"],
            "cons": ["Setup complexity", "Memory usage", "Index management"],
            "dependencies": ["faiss-cpu", "sentence-transformers"],
        },
        "chroma_db": {
            "description": "ChromaDB vector database",
            "pros": ["Easy setup", "Built-in persistence", "Good documentation"],
            "cons": ["Newer project", "Less proven at scale"],
            "dependencies": ["chromadb"],
        },
        "simple_search": {
            "description": "Simple text-based search in knowledge base",
            "pros": ["Simple", "Fast setup", "No dependencies"],
            "cons": ["Lower accuracy", "No semantic understanding"],
            "dependencies": [],
        },
    }

    ENHANCER_OPTIONS = {
        "gemini_api": {
            "description": "Google Gemini API for prompt enhancement (CURRENT)",
            "pros": ["High quality", "Advanced reasoning", "Consistent results", "No local setup required"],
            "cons": ["API costs", "Network dependency", "Rate limits"],
            "dependencies": ["google-generativeai"],
        },
        "openai_api": {
            "description": "OpenAI GPT models",
            "pros": ["High quality", "Easy integration", "Reliable"],
            "cons": ["API costs", "Network dependency", "Privacy concerns"],
            "dependencies": ["openai"],
        },
        "template_based": {
            "description": "Template-based enhancement using retrieved patterns",
            "pros": ["Fast", "Deterministic", "No AI dependency"],
            "cons": ["Less flexible", "Limited creativity", "Rule-based"],
            "dependencies": [],
        },
    }


# Utility Functions
def load_config_from_env() -> RAGConfig:
    """Load configuration from environment variables"""
    return RAGConfig(
        gemini_api_key=os.getenv("GEMINI_API_KEY", ""),
        embedding_model=os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"),
        debug=os.getenv("DEBUG", "false").lower() == "true",
    )


def create_sample_config() -> RAGConfig:
    """Create a sample configuration for testing"""
    return RAGConfig(
        gemini_api_key="your_gemini_api_key_here", embedding_model="sentence-transformers/all-MiniLM-L6-v2", debug=True
    )


if __name__ == "__main__":
    print("Enhanced Prompt RAG Application - Phase 2")
    print("=" * 50)

    # Check if we want to run production test
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "test":
        print("\n🚀 PRODUCTION TEST MODE")
        print("-" * 30)

        # Test with your API key
        GEMINI_API_KEY = "AIzaSyAWvHgMe_CpVbJI1yZ3Os9pwRV05tRztb8"

        try:
            print("Creating production RAG system...")
            rag = create_production_rag(GEMINI_API_KEY)

            # Test prompts
            test_prompts = [
                "Write a summary about machine learning",
                "Solve this math problem: What is 15 * 23?",
                "Help me write a professional email",
                "Explain quantum computing to a 10-year old",
            ]

            print("\nTesting with sample prompts:")
            print("=" * 40)

            for i, prompt in enumerate(test_prompts, 1):
                print(f"\n🔵 Test {i}: {prompt}")
                print("-" * 50)

                result = rag.process_prompt(prompt)

                if result["success"]:
                    print(f"✅ Identified Technique: {result['identified_technique']}")
                    print(f"📝 Enhanced Prompt: {result['enhanced_prompt']}")
                else:
                    print(f"❌ Error: {result.get('error', 'Unknown error')}")

                print()

        except Exception as e:
            print(f"❌ Production test failed: {e}")
            print("\nPlease install dependencies first:")
            print("pip install -r requirements.txt")
            print("\nAnd ensure you have a valid Gemini API key")
    else:
        print()
        print("Implementation Update:")
        print("-" * 30)

        options = ImplementationOptions()

        print("✅ CURRENT PRODUCTION SETUP:")
        print("   • Categorizer: Gemini API (High accuracy)")
        print("   • Safety Checker: Gemini API (Content safety & sanitization)")
        print("   • Retriever: FAISS Vector Database (Best performance)")
        print("   • Enhancer: Gemini API (High quality, consistent)")
        print()

        print("🔄 MIGRATION COMPLETED:")
        print("   • Migrated from local Ollama TinyLlama to Gemini API")
        print("   • Added intelligent safety checking and sanitization")
        print("   • Better prompt enhancement quality and consistency")
        print("   • Simplified deployment (no local LLM required)")
        print("   • Unified Gemini API approach for all AI operations")
        print()

        print("📦 Required Dependencies:")
        print("   • google-generativeai (Gemini API)")
        print("   • faiss-cpu (Vector database)")
        print("   • sentence-transformers (Embeddings)")
        print("   • numpy (Numerical operations)")
        print("   Note: Fully powered by Gemini API - no local LLM setup required")
        print()

        print("🚀 Setup Instructions:")
        print("   1. Install dependencies: pip install -r requirements.txt")
        print("   2. Set your Gemini API key")
        print("   3. Run production test: python EnhancedPrompt.py test")
        print()

        print("🔧 Enhanced Features:")
        print("   • 4-step RAG pipeline: Categorization → Safety → Retrieval → Enhancement")
        print("   • Intelligent content safety checking and sanitization")
        print("   • FAISS vector search with semantic similarity")
        print("   • Automatic vector store creation and persistence")
        print("   • Gemini-powered intelligent categorization")
        print("   • Gemini-powered advanced prompt enhancement")
        print("   • Comprehensive fallback logic for reliability")
        print("   • Production-ready architecture")
        print("   • Better error handling and logging")
