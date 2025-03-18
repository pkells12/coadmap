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
        
        # Ask the user questions interactively to customize the roadmap
        if status_callback:
            status_callback("Please answer the following questions to customize your roadmap:")
        
        answers = {}
        for i, (question, options) in enumerate(questions.items(), 1):
            print(f"\n{i}. {question}")
            
            if isinstance(options, list):
                # Multiple choice question
                for j, option in enumerate(options, 1):
                    print(f"   {j}) {option}")
                
                # Validate input
                while True:
                    try:
                        choice = int(input("   Enter your choice (number): "))
                        if 1 <= choice <= len(options):
                            answers[question] = options[choice-1]
                            break
                        else:
                            print(f"   Please enter a number between 1 and {len(options)}")
                    except ValueError:
                        print("   Please enter a valid number")
            else:
                # Open-ended question
                answers[question] = input("   Your answer: ")
        
        # Generate final roadmap with answers
        reflection_animation = LoadingAnimation("Enhancing roadmap based on your answers", animation_type)
        reflection_animation.start()
        
        try:
            # Call the reflection API with the user's answers
            final_roadmap = client.reflect_on_roadmap_with_answers(initial_roadmap, idea_description, answers)
            
            reflection_animation.stop()
            
            if status_callback:
                status_callback("✅ Enhanced roadmap generated based on your input!")
            
            return final_roadmap
        except Exception as e:
            reflection_animation.stop()
            logger.error(f"Error reflecting on roadmap: {str(e)}")
            if status_callback:
                status_callback(f"❌ Error: {str(e)}")
            raise
    except Exception as e:
        logger.error(f"Error in roadmap generation with questions: {str(e)}")
        raise

def generate_questions_from_roadmap(roadmap, idea_description):
    """
    Generate customization questions based on the roadmap content.
    
    Returns a dictionary of questions with either list of options (for multiple choice)
    or None (for open-ended questions).
    """
    # These are generic questions that work well for most projects
    questions = {
        "What is your team size?": ["Solo developer", "Small team (2-5 people)", "Medium team (6-15 people)", "Large team (15+ people)"],
        "What is your experience level with the technologies mentioned in the roadmap?": ["Beginner", "Intermediate", "Advanced", "Mix of experience levels"],
        "What is your timeline for this project?": ["Quick prototype (days)", "Short-term project (weeks)", "Medium-term project (months)", "Long-term project (6+ months)"],
        "What are your top priority features for the MVP?": None,
        "Are there any specific technologies or frameworks you want to use?": None,
    }
    
    return questions

def main():
    """
    Main function to run the roadmap generator from the command line.
    """
    parser = argparse.ArgumentParser(description="Generate a coding roadmap for your app idea")
    parser.add_argument("idea", help="Your app idea description")
    parser.add_argument("--animation", choices=["spinner", "dots", "bar", "typing"], default="spinner", help="Animation type")
    parser.add_argument("--interactive", action="store_true", help="Use interactive mode with customization questions")
    
    args = parser.parse_args()
    
    # Map string to enum
    animation_map = {
        'spinner': AnimationType.SPINNER,
        'dots': AnimationType.DOTS,
        'bar': AnimationType.BAR,
        'typing': AnimationType.TYPING
    }
    animation_type = animation_map.get(args.animation, AnimationType.SPINNER)
    
    if args.interactive:
        # Interactive mode with questions
        roadmap = generate_roadmap_with_questions(args.idea, animation_type)
    else:
        # Simple mode without questions
        loading_animation = LoadingAnimation("Generating roadmap based on your idea", animation_type)
        loading_animation.start()
        
        try:
            roadmap = generate_roadmap(args.idea)
            loading_animation.stop()
        except Exception as e:
            loading_animation.stop()
            print(f"Error: {str(e)}")
            return
    
    print("\nRoadmap generated:")
    print(roadmap)

if __name__ == "__main__":
    main()