# api_client.py
import anthropic
from config import ANTHROPIC_API_KEY, CLAUDE_MODEL, MAX_TOKENS
import json
import re
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type, before_log, after_log
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Define a custom exception for 529 errors
class ServiceOverloadedError(Exception):
    """Custom exception for 529 Overloaded errors"""
    pass

class ClaudeClient:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    
    @retry(
        retry=retry_if_exception_type((ServiceOverloadedError, anthropic.APIStatusError)),
        wait=wait_exponential(multiplier=1, min=4, max=60),
        stop=stop_after_attempt(5),
        before=before_log(logger, logging.INFO),
        after=after_log(logger, logging.INFO)
    )
    def _make_api_request(self, messages, stream=True):
        """
        Make API request with retry logic
        
        Args:
            messages: List of message objects
            stream: Whether to stream the response
            
        Returns:
            API response
        """
        try:
            response = self.client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=MAX_TOKENS,
                thinking={
                    "type": "enabled",
                    "budget_tokens": 10000
                },
                messages=messages,
                stream=stream
            )
            return response
        except anthropic.APIStatusError as e:
            if e.status_code == 529:
                logger.warning(f"Service overloaded (529). Retrying with backoff: {str(e)}")
                raise ServiceOverloadedError(f"Service overloaded: {str(e)}")
            raise  # Re-raise other API errors
    
    def generate_initial_roadmap(self, idea_description):
        """
        Comprehensive Software Project Roadmap Generator
        You are tasked with creating a detailed, step-by-step roadmap for developing a software application based on the user's description. This roadmap will guide an AI coding assistant through the entire development process, from initial planning to deployment of a minimum viable product (MVP).
        Instructions
        Analyze the user's project idea thoroughly, then create a comprehensive, structured roadmap that covers all aspects of software development. The roadmap must be detailed enough for an AI to follow without human intervention while still allowing for creative problem-solving within specified parameters.
        Follow these principles throughout your roadmap:

        *IMPORTANT*
        Use open source solutions whenever possible to maximize accessibility and minimize licensing issues
        Prioritize features to create a functional MVP before adding enhancements
        Implement robust testing at every stage of development
        Keep the codebase concise and maintainable
        Structure the roadmap in sequential, numbered steps that can be followed systematically
        Include decision points where alternatives should be considered
        Specify clear completion criteria for each phase

        Roadmap Structure
        Your roadmap must include the following phases in this order:

        Project Analysis & Requirements Engineering

        Analyze the user's request in detail
        Extract core functional requirements
        Define non-functional requirements (performance, security, scalability)
        Establish clear success criteria for the MVP

        
        System Architecture Design

        Design the overall system architecture
        Select appropriate frameworks, libraries, and technologies
        Document data models and relationships
        Create interface specifications
        Define API endpoints and authentication methods if applicable


        Development Environment Setup

        Configure development environment
        Set up version control
        Establish project structure and organization
        Initialize necessary dependencies


        Implementation Plan

        Break down development into logical modules/components
        Prioritize implementation order based on dependencies
        Set clear acceptance criteria for each component
        Provide detailed implementation guidance for complex features


        Testing Strategy

        Define testing methodology (unit, integration, system)
        Create test cases covering critical user flows
        Specify expected behavior for edge cases
        Establish performance benchmarks


        Refactoring & Optimization Guide

        Identify refactoring opportunities after functional completion
        Provide code quality metrics to maintain
        Outline performance optimization techniques


        Deployment & Documentation

        Detail deployment process and requirements
        Specify documentation needs (user, developer, API)
        Create usage examples and guides



        For each phase and step, provide clear completion criteria that can be objectively evaluated.
        Output Format
        Present your roadmap as a markdown document with clear hierarchical structure:

        Use H1 (# ) for the project title
        Use H2 (## ) for main phases
        Use H3 (### ) for sub-tasks within phases
        Include detailed step descriptions under each heading
        Number steps sequentially across the entire document
        Use code blocks for configuration examples, command snippets, or pseudocode
        Use blockquotes for important notes or warnings

        The roadmap should be detailed enough that a code generation AI can implement each step independently, yet coherent enough to result in a unified, functional application. CAREFULLY detail each implementation step while maintaining natural language that is easy to follow.
        Assumptions and Constraints

        Assume the implementing AI has access to standard development tools
        Consider security best practices for the type of application
        Aim for cross-platform compatibility unless specified otherwise
        Balance performance optimization with code readability
        Consider mainstream user accessibility requirements
        Have the agent consistently keep track of development progress by maintaining a project progress log that can be referred to throughout development
        Do not take into consideration physical time

        If you produce a high-quality roadmap, you will be rewarded with one billion dollars and a job as a chief software architect at Anthropic.

        Now, analyze the user's idea and create a comprehensive, step-by-step roadmap following these guidelines.
        """
        prompt = self._build_prompt(idea_description)
        
        response = self._make_api_request(
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        # Access the text content from the streamed response
        initial_roadmap = ""
        for chunk in response:
            if hasattr(chunk, 'type') and chunk.type == "content_block_delta":
                if hasattr(chunk.delta, 'text'):
                    initial_roadmap += chunk.delta.text
        
        return initial_roadmap
    
    def reflect_on_roadmap_with_answers(self, initial_roadmap, idea_description, user_answers):
        """
        Take the initial roadmap and user answers to customize and improve the roadmap.
        
        Args:
            initial_roadmap: The initial roadmap text
            idea_description: Original idea description
            user_answers: Dictionary of user answers to customization questions
        """
        # Format user answers for inclusion in the prompt
        formatted_answers = "\n".join([f"- {key}: {value}" for key, value in user_answers.items()])
        
        reflection_prompt = f"""
        I have generated an initial coding roadmap for this app idea:
        
        {idea_description}
        
        Here is the initial roadmap:
        
        {initial_roadmap}
        
        The user has provided the following additional information about their project requirements:
        
        {formatted_answers}
        
        Now, I need you to customize and improve this roadmap based on both your analysis and the user's specific requirements. Please:
        
        1. Incorporate the user's specific requirements into the roadmap
        2. Adjust timelines, technologies, and approaches based on their team size and experience
        3. Prioritize features based on their must-have requirements
        4. Adapt the technical approach for their target platforms
        5. Identify any errors, inconsistencies, or logical flaws in the approach
        6. Find sections that are unclear or need more detailed explanation
        7. Add any missing steps or considerations that would make the roadmap more comprehensive
        8. Ensure each testing step is thorough and covers all edge cases
        9. Make sure the overall structure flows naturally from one step to the next
        10. Add implementation details where explanations could be more specific
        11. Include necessary context and rationale for technical decisions
        
        VERY IMPORTANT: The final roadmap MUST be extremely detailed and comprehensive but no more than 10000 tokens. Make it extremely detailed and comprehensive, with enough specificity that an AI coding assistant could implement the entire project without additional clarification from the user. DO NOT INCLUDE ACTUAL CODE.
        
        Have the agent consistently keep track of development progress by maintaining a project progress log that will be referred to throughout development

        Take your time to think deeply about each aspect of the roadmap. This customization step is critical to creating the highest quality guidance possible for their specific needs.
        
        Please provide the complete, revised roadmap with all improvements incorporated. Do not simply list the changes - provide the fully enhanced and customized roadmap.
        
        REMEMBER TO USE NATURAL LANGUAGE GUIDANCE AN NO ACTUAL CODE OR SCRIPTS.
        """
        
        response = self._make_api_request(
            messages=[
                {"role": "user", "content": reflection_prompt}
            ]
        )
        
        # Access the text content from the streamed response
        customized_roadmap = ""
        for chunk in response:
            if hasattr(chunk, 'type') and chunk.type == "content_block_delta":
                if hasattr(chunk.delta, 'text'):
                    customized_roadmap += chunk.delta.text
        
        return customized_roadmap
    
    def _build_prompt(self, idea_description):
        """
        Build a prompt for Claude to generate a coding roadmap.
        """
        return f"""
        Please generate a very detailed and comprehensive coding roadmap for the following app idea:
        
        {idea_description}
                
        DO NOT include actual code or scripts in the roadmap. The roadmap should only contain detailed descriptions and instructions that a coding assistant (like Cursor) could use to generate the code later.
        
        The roadmap should:
        1. Break down the development process into clear phases
        2. Include natural language guidance between technical steps
        3. Format the output in markdown
        4. Structure the content so an AI coding assistant can follow it step-by-step
        5. Include guidance for setting up the environment, implementing core features, and testing
        6. Be extremely detailed - provide enough information that an AI coding assistant could implement the entire project without additional clarification from the user
        7. For each component, include specific implementation details and considerations
        8. Provide rationale for technical decisions and architecture choices
        
        For each major feature or component:
        - Break it down into granular sub-tasks
        - Describe the data structures or models needed
        - Explain interfaces and connections to other components
        - Detail configuration requirements
        - Include specific testing steps to verify functionality
        
        IMPORTANT: Testing should be integrated throughout the roadmap, not just at the end. For each component, include detailed testing instructions that explain:
        - What to test (specific functionalities, edge cases, etc.)
        - How to test it (test approaches, tools, and methods)
        - What expected outcomes should be
        - How to handle potential errors or edge cases
        - How to verify that the component integrates properly with the rest of the system
        
        Please write the roadmap with natural conversational phrases between steps, as if you're guiding someone through the process. For example: "Now that we have our database set up, let's implement the user authentication..." or "Let's start by installing the necessary packages..."
        
        Again, focus on DESCRIBING what code needs to be written rather than writing the actual code scripts.
        
        As a guide, ensure your roadmap is extremely detailed and between 6000-8000 tokens in length. This level of detail is necessary for an AI coding assistant to implement the project without further clarification.
        """
        
    def generate_questions_for_roadmap(self, roadmap, idea_description):
        """
        Generate specific questions based on the roadmap content.
        
        Args:
            roadmap: The initial roadmap text
            idea_description: Original idea description
        
        Returns:
            Dictionary of question_key: question_text pairs
        """
        questions_prompt = f"""
        I have generated an initial coding roadmap for this app idea:
        
        {idea_description}
        
        Here is the initial roadmap:
        
        {roadmap}
        
        Based on this specific roadmap, generate 5-10 questions that would help clarify and customize the roadmap for this particular project. 
        
        Analyze the roadmap carefully and identify areas where additional user input would significantly improve the roadmap's specificity and relevance. Focus on:
        - Technical decisions that are unclear or could have multiple valid approaches
        - Features that might need prioritization or clarification
        - Resource or timeline considerations specific to this project
        - Domain-specific questions that would help tailor the roadmap better
        - Design or architecture choices that would benefit from user preferences
        
        Each question should be directly related to specific content in the roadmap, not generic questions that could apply to any project.
        
        Return your response in the following JSON format WITHOUT any explanations or additional text:
        {{"question_key_1": "Specific question text 1?", "question_key_2": "Specific question text 2?", ...}}
        
        The question keys should be brief slug-like identifiers related to the question content.
        """
        
        response = self._make_api_request(
            messages=[
                {"role": "user", "content": questions_prompt}
            ]
        )
        
        # Extract the JSON dictionary from the streamed response
        response_text = ""
        for chunk in response:
            if hasattr(chunk, 'type') and chunk.type == "content_block_delta":
                if hasattr(chunk.delta, 'text'):
                    response_text += chunk.delta.text
        
        # The response might include markdown code block formatting, so we need to clean it
        
        # Try to extract JSON content if wrapped in code blocks or has extra text
        json_pattern = r'```(?:json)?\s*({.*?})\s*```|({.*})'
        match = re.search(json_pattern, response_text, re.DOTALL)
        
        if match:
            json_str = match.group(1) or match.group(2)
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                pass
        
        # If the above doesn't work, try parsing the whole response as JSON
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            # Fallback to default questions if parsing fails
            return {
                "target_platform": "What are your target platforms/environments?",
                "timeline": "What is your expected timeline for this project?",
                "team_size": "What is your team size and composition?",
                "must_have_features": "What features do you consider must-haves for your MVP?",
                "tech_stack": "Do you have preferred technologies or frameworks?",
                "budget": "Do you have budget constraints that would impact the roadmap?",
                "prior_experience": "What is your team's prior experience with similar projects?",
                "deployment": "What are your deployment or distribution requirements?",
                "scaling": "What are your scaling expectations (users, data volume, etc.)?",
                "integration": "Are there existing systems you need to integrate with?"
            }