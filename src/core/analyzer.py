
import collections
import streamlit as st
import logging
from src.core.nlp import SemanticSearchEngine
from collections import Counter
import re

logger = logging.getLogger(__name__)


from src.core.llm import get_llm_provider


from src.core.context import ContextManager

class AnalysisEngine:
    def __init__(self, chunks, api_key=None):
        """
        Args:
            chunks (List[Document]): LangChain documents with metadata
            api_key (str): Optional API Key for Generative AI
        """
        self.chunks = chunks
        self.raw_text_chunks = [doc.page_content for doc in chunks]
        
        # Initialize Context Manager
        self.context_manager = ContextManager()
        
        # Initialize Semantic Engine
        self.semantic_engine = SemanticSearchEngine()
        self.index_ready = self.semantic_engine.build_index(chunks)
        
        # Initialize LLM
        self.llm_provider = get_llm_provider(api_key)
        
        # Fallback Stats
        self.total_docs = len(chunks)

    def generate_summary(self, user_goal="General Reading"):
        """
        Generates a summary using LLM if available, otherwise heuristic.
        Adapts to user_goal (e.g., Exam Prep, Research) and User Context.
        """
        if not self.chunks:
            return "No content available."

        # Log Interaction
        self.context_manager.log_interaction("summary_generated", details={"goal": user_goal})

        # Context for Summary
        indices = [0, 1, len(self.chunks)//2, len(self.chunks)//2 + 1, -2, -1]
        context_docs = [self.chunks[i] for i in indices if i < len(self.chunks)]
        context_text = "\n\n".join([d.page_content for d in context_docs])
        
        # Adaptive Instruction
        adaptive_note = self.context_manager.get_adaptive_prompt_instruction()
        
        prompt = f"""
        {adaptive_note}
        You are an expert AI Book Summarizer. Your goal is to help a user with the goal: '{user_goal}'.
        
        Analyze the provided book context and generate a comprehensive response strictly following this structure:
        
        ## 📘 Book Overview
        (A concise high-level summary of what the book is about)

        ## 🔑 Key Themes
        - Theme 1
        - Theme 2
        
        ## 📖 Chapter-wise / Section Summary
        (Summarize the flow of arguments or chapters found in the text)

        ## 💡 Important Concepts Explained Simply
        (Explain complex ideas in simple terms, suitable for '{user_goal}')

        ## 🚀 Key Takeaways
        - Takeaway 1
        - Takeaway 2

        ## 🛠️ Use-Cases / Applications
        (Practical applications of the content)

        ## 📝 Quick Revision Notes
        (Bullet points for quick review)

        Tone: Professional, Friendly, Non-judgmental.
        Constraint: Do NOT hallucinate. Use only the provided text.
        
        Context:
        {context_text[:6000]}
        
        Summary:
        """
        
        return self.llm_provider.generate_text(prompt)

    def answer_question(self, question):
        """
        Answers a question using Semantic Search + LLM Synthesis + Context.
        """
        if not self.index_ready:
            return "Search index is not ready."

        # Log Interaction
        self.context_manager.log_interaction("question_asked", query=question)

        # 1. Retrieve relevant chunks (Semantic Search)
        results = self.semantic_engine.search(question, k=4)
        
        if not results:
            return "I couldn't find relevant information in the uploaded text."
            
        # 2. Prepare Context
        context_text = ""
        for i, doc in enumerate(results):
            page = doc.metadata.get('page', '?')
            context_text += f"[Page {page}]: {doc.page_content}\n\n"

        # Adaptive Instruction
        adaptive_note = self.context_manager.get_adaptive_prompt_instruction()

        # 3. Generate Answer via LLM
        prompt = f"""
        {adaptive_note}
        You are an expert academic tutor. Answer the student's question strictly based on the provided context.
        Cite the page numbers provided in the context.
        
        Context:
        {context_text}
        
        Question: {question}
        
        Answer (Academic & Citations):
        """
        
        return self.llm_provider.generate_text(prompt)

    def generate_questions(self):
        """Generates questions based on content analysis using LLM."""
        if not self.chunks:
            return []

        # Context (Random sample of chunks to catch different topics)
        indices = [0, len(self.chunks)//3, 2*len(self.chunks)//3, -1]
        context_docs = [self.chunks[i] for i in indices if i < len(self.chunks)]
        context_text = "\n\n".join([d.page_content for d in context_docs])

        prompt = f"""
        Based on the following text context, generate 5 thought-provoking discussion questions that test understanding of the key concepts.
        Return ONLY the questions, one per line.
        
        Context:
        {context_text[:4000]}
        
        Questions:
        """
        
        response = self.llm_provider.generate_text(prompt)
        
        # Parse response into list
        questions = [line.strip().lstrip('- ').lstrip('1234567890. ') for line in response.split('\n') if line.strip()]
        return questions[:10]  # Limit to reasonable number

    def generate_faqs(self):
        """Generates FAQs based on content using LLM."""
        if not self.chunks:
            return []

        # Context
        indices = [0, len(self.chunks)//2, -1]
        context_docs = [self.chunks[i] for i in indices if i < len(self.chunks)]
        context_text = "\n\n".join([d.page_content for d in context_docs])

        prompt = f"""
        Based on the text provided, generate 5 "Frequently Asked Questions" (FAQs) that a reader would likely ask.
        Provide clear, concise answers for each.
        
        Strict Output Format:
        Q: [Question Text]
        A: [Answer Text]
        
        Context:
        {context_text[:4000]}
        
        FAQs:
        """
        
        response = self.llm_provider.generate_text(prompt)
        
        # Parse Response
        faqs = []
        pairs = response.split("Q:")
        for pair in pairs:
            if "A:" in pair:
                parts = pair.split("A:")
                if len(parts) >= 2:
                    q = parts[0].strip()
                    a = parts[1].strip()
                    if q and a:
                        faqs.append((q, a))
                        
        if not faqs:
            # Fallback if parsing fails
            return [("Could not generate specific FAQs", "Please try again or check the document content.")]
            
        return faqs
