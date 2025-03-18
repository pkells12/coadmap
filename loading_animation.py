import sys
import time
import threading
import itertools
from enum import Enum

class AnimationType(Enum):
    SPINNER = 1
    DOTS = 2
    BAR = 3
    TYPING = 4

class LoadingAnimation:
    def __init__(self, message="Processing", animation_type=AnimationType.SPINNER, max_time=None):
        self.message = message
        self.animation_type = animation_type
        self.max_time = max_time
        self.is_running = False
        self.thread = None
    
    def _spinner_animation(self):
        spinner = itertools.cycle(['-', '/', '|', '\\'])
        while self.is_running:
            if self.message:
                sys.stdout.write(f"\r{self.message} {next(spinner)} ")
            else:
                sys.stdout.write(f"\r{next(spinner)} ")
            sys.stdout.flush()
            time.sleep(0.1)
    
    def _dots_animation(self):
        dots = 0
        max_dots = 3
        while self.is_running:
            dots = (dots + 1) % (max_dots + 1)
            if self.message:
                sys.stdout.write(f"\r{self.message}" + "." * dots + " " * (max_dots - dots))
            else:
                sys.stdout.write("\r" + "." * dots + " " * (max_dots - dots))
            sys.stdout.flush()
            time.sleep(0.5)
    
    def _bar_animation(self):
        bar_width = 20
        position = 0
        direction = 1  # 1 for right, -1 for left
        
        while self.is_running:
            # Update position
            position += direction
            if position >= bar_width - 1:
                direction = -1
            elif position <= 0:
                direction = 1
                
            # Draw bar
            bar = "[" + " " * position + "=" + " " * (bar_width - position - 1) + "]"
            if self.message:
                sys.stdout.write(f"\r{self.message} {bar}")
            else:
                sys.stdout.write(f"\r{bar}")
            sys.stdout.flush()
            time.sleep(0.1)
    
    def _typing_animation(self):
        original_message = self.message
        if not original_message:
            # If no message, use a simple dot animation instead
            return self._dots_animation()
            
        while self.is_running:
            for i in range(len(original_message) + 1):
                if not self.is_running:
                    break
                sys.stdout.write(f"\r{original_message[:i]}")
                sys.stdout.flush()
                time.sleep(0.1)
            time.sleep(0.7)  # Pause at the end
            if self.is_running:
                sys.stdout.write("\r" + " " * len(original_message))
                sys.stdout.flush()
                time.sleep(0.3)
    
    def start(self):
        self.is_running = True
        
        if self.animation_type == AnimationType.SPINNER:
            self.thread = threading.Thread(target=self._spinner_animation)
        elif self.animation_type == AnimationType.DOTS:
            self.thread = threading.Thread(target=self._dots_animation)
        elif self.animation_type == AnimationType.BAR:
            self.thread = threading.Thread(target=self._bar_animation)
        elif self.animation_type == AnimationType.TYPING:
            self.thread = threading.Thread(target=self._typing_animation)
        
        self.thread.daemon = True
        self.thread.start()
        
        if self.max_time:
            time.sleep(self.max_time)
            self.stop()
    
    def stop(self):
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=1)
        # Clear the line
        sys.stdout.write("\r" + " " * (len(self.message) + 10))
        sys.stdout.write("\r")
        sys.stdout.flush()

# Example usage
if __name__ == "__main__":
    print("Starting demo of loading animations...")
    
    # Spinner demo
    print("\nSpinner animation:")
    spinner = LoadingAnimation("Generating roadmap based on your idea", AnimationType.SPINNER, 3)
    spinner.start()
    
    # Dots demo
    print("\nDots animation:")
    dots = LoadingAnimation("Starting reflection process to improve the roadmap", AnimationType.DOTS, 3)
    dots.start()
    
    # Bar demo
    print("\nBar animation:")
    bar = LoadingAnimation("Processing your request", AnimationType.BAR, 3)
    bar.start()
    
    # Typing demo
    print("\nTyping animation:")
    typing = LoadingAnimation("Generating roadmap based on your idea", AnimationType.TYPING, 5)
    typing.start()
    
    print("\nAnimation demos complete!") 