# roadmap_generator.py
from api_client import ClaudeClient, ServiceOverloadedError
import time
import argparse
from loading_animation import LoadingAnimation, AnimationType
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def generate_roadmap(idea_description, status_callback=None):
    """
    Generate a coding roadmap based on the user's idea description.
    
    Args:
        idea_description: Description of the app idea
        status_callback: Optional callback function to update UI about current progress
    """
    client = ClaudeClient()
    
    # Don't send standard generation messages via status_callback
    # The animation will handle these messages
    
    try:
        initial_roadmap = client.generate_initial_roadmap(idea_description)
        
        # Don't send standard reflection messages via status_callback
        # The animation will handle these messages
        
        # Call reflect_on_roadmap_with_answers with empty answers dict
        final_roadmap = client.reflect_on_roadmap_with_answers(initial_roadmap, idea_description, {})
        
        if status_callback:
            status_callback("✅ Roadmap generation complete!")
        
        return final_roadmap
    except ServiceOverloadedError as e:
        logger.error(f"Service overloaded even after retries: {str(e)}")
        if status_callback:
            status_callback("❌ Error: Service is currently overloaded. The application has attempted to retry but was unsuccessful.")
        raise Exception("Service is currently overloaded. Please try again later.")
    except Exception as e:
        logger.error(f"Error generating roadmap: {str(e)}")
        if status_callback:
            status_callback(f"❌ Error: {str(e)}")
        raise

def format_roadmap(roadmap_text):
    """
    Format the roadmap text if needed.
    This function could be expanded to add additional formatting or structure.
    """
    return roadmap_text

async def generate_roadmap_with_questions(idea_description, animation_type=AnimationType.SPINNER, status_callback=None):
    """
    Generate a roadmap with user customization questions.
    
    Args:
        idea_description: Description of the app idea
        animation_type: Type of animation to display
        status_callback: Optional callback function to update UI about current progress
    """
    client = ClaudeClient()
    
    try:
        # Step 1: Generate initial roadmap with animation
        roadmap_animation = LoadingAnimation("Generating roadmap based on your idea", animation_type)
        roadmap_animation.start()
        
        try:
            initial_roadmap = client.generate_initial_roadmap(idea_description)
            roadmap_animation.stop()
            
            if status_callback:
                status_callback("✅ Initial roadmap generation complete!")
        except Exception as e:
            roadmap_animation.stop()
            logger.error(f"Error generating initial roadmap: {str(e)}")
            if status_callback:
                status_callback(f"❌ Error: {str(e)}")
            raise
        
        # Generate questions animation
        questions_animation = LoadingAnimation("Analyzing roadmap and generating customized questions", animation_type)
        questions_animation.start()
        
        try:
            # Generate questions based on the roadmap content
            questions = generate_questions_from_roadmap(initial_roadmap, idea_description)
            
            questions_animation.stop()
            
            if status_callback:
                status_callback("✅ Customized questions generated!")
        except Exception as e:
            questions_animation.stop()
            logger.error(f"Error generating questions: {str(e)}")
            if status_callback:
                status_callback(f"❌ Error: {str(e)}")
            raise
        
        print("\nBased on the roadmap analysis, please answer these questions to help customize it further:")
        print("(Press Enter to skip any question you don't know or don't care about)\n")
        
        # Ask questions and collect answers
        answers = {}
        for i, (question_key, question_text) in enumerate(questions.items(), 1):
            user_answer = input(f"{i}. {question_text}\n   > ")
            if user_answer.strip():
                answers[question_key] = user_answer
        
        # Step 2: Reflection process with animation - use the same style as initial generation
        reflection_animation = LoadingAnimation("Starting reflection process with your input", animation_type)
        reflection_animation.start()
        
        try:
            # Package the answers with the roadmap for reflection
            final_roadmap = client.reflect_on_roadmap_with_answers(initial_roadmap, idea_description, answers)
            reflection_animation.stop()
            
            if status_callback:
                status_callback("✅ Roadmap customization complete!")
        except Exception as e:
            reflection_animation.stop()
            logger.error(f"Error during reflection process: {str(e)}")
            if status_callback:
                status_callback(f"❌ Error: {str(e)}")
            raise
        
        return final_roadmap
    except ServiceOverloadedError as e:
        logger.error(f"Service overloaded even after retries: {str(e)}")
        if status_callback:
            status_callback("❌ Error: Service is currently overloaded. The application has attempted to retry but was unsuccessful.")
        raise Exception("Service is currently overloaded. Please try again later with exponential backoff.")
    except Exception as e:
        logger.error(f"Error generating roadmap with questions: {str(e)}")
        if status_callback:
            status_callback(f"❌ Error: {str(e)}")
        raise

def generate_questions_from_roadmap(roadmap, idea_description):
    """
    Generate relevant questions based on the roadmap content.
    Uses Claude to generate specific questions based on the roadmap content.
    
    Returns a dictionary of question_key: question_text pairs
    """
    # Create a new instance of ClaudeClient
    client = ClaudeClient()
    
    try:
        # Use Claude to generate questions specific to this roadmap
        questions = client.generate_questions_for_roadmap(roadmap, idea_description)
        
        return questions
    except ServiceOverloadedError as e:
        logger.error(f"Service overloaded even after retries when generating questions: {str(e)}")
        raise Exception("Service is currently overloaded while generating questions. Please try again later.")
    except Exception as e:
        logger.error(f"Error generating questions from roadmap: {str(e)}")
        raise

def main():
    parser = argparse.ArgumentParser(description='Generate a project roadmap with dynamic loading indicators')
    parser.add_argument('--animation', choices=['spinner', 'dots', 'bar', 'typing'], default='spinner',
                      help='Type of animation to display during processing')
    parser.add_argument('--idea', type=str, required=True, help='Your project idea description')
    parser.add_argument('--with-questions', action='store_true', help='Enable customization questions')
    parser.add_argument('--output', type=str, help='Output file to save the roadmap')
    args = parser.parse_args()
    
    # Map string argument to enum
    animation_map = {
        'spinner': AnimationType.SPINNER,
        'dots': AnimationType.DOTS,
        'bar': AnimationType.BAR,
        'typing': AnimationType.TYPING
    }
    animation_type = animation_map.get(args.animation, AnimationType.SPINNER)
    
    try:
        if args.with_questions:
            # Generate roadmap with user customization questions
            roadmap = asyncio.run(generate_roadmap_with_questions(args.idea, animation_type))
        else:
            # Generate roadmap without questions
            roadmap = asyncio.run(generate_roadmap(args.idea))
        
        print("\nRoadmap generation complete!")
        
        if args.output:
            import os
            # Ensure roadmaps directory exists
            os.makedirs('roadmaps', exist_ok=True)
            # Save to roadmaps directory
            file_path = os.path.join('roadmaps', args.output)
            with open(file_path, 'w') as f:
                f.write(roadmap)
            print(f"Roadmap saved to {file_path}")
        else:
            print("\n" + roadmap)
    except Exception as e:
        print(f"\nError: {str(e)}")
        logger.error(f"Main process error: {str(e)}")
        import sys
        sys.exit(1)

if __name__ == "__main__":
    import asyncio
    main()