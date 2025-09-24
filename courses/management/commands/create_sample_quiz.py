from django.core.management.base import BaseCommand
from django.utils import timezone
from courses.models import Assignment, QuizQuestion, ModuleTopic, Module, Lesson
from programs.models import ProgramModule, ProgramLevel
from datetime import timedelta

class Command(BaseCommand):
    help = 'Creates a sample quiz with questions'

    def handle(self, *args, **kwargs):
        try:
            # First, get or create a module
            module = Module.objects.filter(module_type='young_theologians').first()
            if not module:
                module = Module.objects.create(
                    name='Module 1: Young Theologians and Gospel Advancing',
                    module_type='young_theologians',
                    description='Module for theological studies',
                    learning_objectives='Understand theological concepts'
                )
                self.stdout.write(self.style.SUCCESS(f'Created new module: {module.name}'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Found existing module: {module.name}'))

            # Get or create program level
            level = ProgramLevel.objects.filter(level_type='certificate').first()
            if not level:
                level = ProgramLevel.objects.create(
                    level_type='certificate',
                    name='Certificate Level',
                    description='Certificate program level'
                )
                self.stdout.write(self.style.SUCCESS(f'Created new program level: {level.name}'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Found existing program level: {level.name}'))

            # Get or create program module
            program_module = ProgramModule.objects.filter(module=module, program_level=level).first()
            if not program_module:
                program_module = ProgramModule.objects.create(
                    module=module,
                    program_level=level,
                    credits=3,
                    duration_weeks=12
                )
                self.stdout.write(self.style.SUCCESS(f'Created new program module'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Found existing program module'))

            # Get or create module topic
            topic = ModuleTopic.objects.filter(program_module=program_module, topic_number=1).first()
            if not topic:
                topic = ModuleTopic.objects.create(
                    program_module=program_module,
                    topic_number=1,
                    title='Introduction to Python',
                    description='Introduction to Python programming',
                    learning_objectives='Learn Python basics',
                    total_credits=1,
                    total_hours=10,
                    theory_hours=5,
                    practical_hours=5,
                    theory_content='Python basics theory',
                    practical_activities='Python coding exercises',
                    practical_deliverables='Working Python programs',
                    assessment_criteria='Code quality and functionality'
                )
                self.stdout.write(self.style.SUCCESS(f'Created new topic: {topic.title}'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Found existing topic: {topic.title}'))

            # Get or create lesson
            lesson = Lesson.objects.filter(topic=topic, lesson_number=1).first()
            if not lesson:
                lesson = Lesson.objects.create(
                    topic=topic,
                    lesson_number=1,
                    title='Python Fundamentals',
                    description='Learn the fundamentals of Python programming',
                    learning_objectives='Understand basic Python concepts',
                    lesson_type='theory',
                    duration_minutes=90,
                    content='Python programming basics content',
                    sequence_order=1
                )
                self.stdout.write(self.style.SUCCESS(f'Created new lesson: {lesson.title}'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Found existing lesson: {lesson.title}'))

            # Create the quiz assignment
            quiz = Assignment.objects.create(
                lesson=lesson,  # Link to the lesson
                title="Python Programming Basics Quiz",
                description="Test your knowledge of Python programming fundamentals.",
                instructions="Select the best answer for each question. You need 70% to pass.",
                assignment_type='quiz',
                is_quiz=True,
                max_points=100,
                due_date=timezone.now() + timedelta(days=7),
                time_limit_minutes=30,
                passing_score=70,
                shuffle_questions=True,
                show_correct_answers=True
            )

            # Question 1: Multiple Choice
            q1 = QuizQuestion.objects.create(
                assignment=quiz,
                question_type='multiple_choice',
                text="What is the output of: print(type([1, 2, 3]))?",
                points=20,
                order=1
            )
            q1.add_choice("<class 'list'>", True, "Lists in Python are represented by the 'list' class.")
            q1.add_choice("<class 'array'>", False, "Python doesn't have a built-in array class.")
            q1.add_choice("<class 'tuple'>", False, "Tuples use parentheses () not square brackets [].")
            q1.add_choice("<class 'set'>", False, "Sets use curly braces {} not square brackets [].")

            # Question 2: True/False
            q2 = QuizQuestion.objects.create(
                assignment=quiz,
                question_type='true_false',
                text="In Python, a tuple is mutable.",
                points=20,
                order=2
            )
            q2.add_choice("True", False, "Tuples are immutable - they cannot be changed after creation.")
            q2.add_choice("False", True, "Correct! Tuples are immutable in Python.")

            # Question 3: Multiple Choice
            q3 = QuizQuestion.objects.create(
                assignment=quiz,
                question_type='multiple_choice',
                text="Which of the following is the correct way to create an empty dictionary?",
                points=20,
                order=3
            )
            q3.add_choice("dict()", True, "Using the dict() constructor creates an empty dictionary.")
            q3.add_choice("{}", True, "Using curly braces creates an empty dictionary.")
            q3.add_choice("[]", False, "Square brackets create an empty list, not a dictionary.")
            q3.add_choice("()", False, "Parentheses create an empty tuple, not a dictionary.")

            # Question 4: Multiple Choice
            q4 = QuizQuestion.objects.create(
                assignment=quiz,
                question_type='multiple_choice',
                text="What does the 'len()' function return for a string?",
                points=20,
                order=4
            )
            q4.add_choice("The number of characters in the string", True, "len() counts all characters in a string.")
            q4.add_choice("The number of words in the string", False, "To count words, you would need to split the string first.")
            q4.add_choice("The size of the string in bytes", False, "len() counts characters, not bytes.")
            q4.add_choice("The number of lines in the string", False, "To count lines, you would need to split by newline characters.")

            # Question 5: Short Answer
            q5 = QuizQuestion.objects.create(
                assignment=quiz,
                question_type='short_answer',
                text="What Python function would you use to get user input from the console?",
                points=20,
                order=5
            )
            q5.add_choice("input()", True, "The input() function reads a line from the console.")

            self.stdout.write(self.style.SUCCESS(f'Successfully created quiz "{quiz.title}" with 5 questions'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating quiz: {str(e)}'))
            raise
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating quiz: {str(e)}'))
            return
            # Get or create a module
            module, _ = Module.objects.get_or_create(
                module_type='young_theologians',
                defaults={
                    'name': 'Young Theologians and Gospel Advancing',
                    'description': 'Module for theological studies',
                    'learning_objectives': 'Understand theological concepts'
                }
            )

            # Get or create program level
            level, _ = ProgramLevel.objects.get_or_create(
                level_type='certificate',
                defaults={
                    'name': 'Certificate Level',
                    'description': 'Certificate program level',
                }
            )

            # Get or create program module
            program_module, _ = ProgramModule.objects.get_or_create(
                module=module,
                program_level=level,
                defaults={
                    'credits': 3,
                    'duration_weeks': 12,
                }
            )

            # Get or create module topic
            topic, _ = ModuleTopic.objects.get_or_create(
                program_module=program_module,
                topic_number=1,
                defaults={
                    'title': 'Introduction to Python',
                    'description': 'Introduction to Python programming',
                    'learning_objectives': 'Learn Python basics',
                    'total_credits': 1,
                    'total_hours': 10,
                    'theory_hours': 5,
                    'practical_hours': 5,
                    'theory_content': 'Python basics theory',
                    'practical_activities': 'Python coding exercises',
                    'practical_deliverables': 'Working Python programs',
                    'assessment_criteria': 'Code quality and functionality'
                }
            )

            # Get or create lesson
            lesson, _ = Lesson.objects.get_or_create(
                topic=topic,
                lesson_number=1,
                defaults={
                    'title': 'Python Fundamentals',
                    'description': 'Learn the fundamentals of Python programming',
                    'learning_objectives': 'Understand basic Python concepts',
                    'lesson_type': 'theory',
                    'duration_minutes': 90,
                    'content': 'Python programming basics content',
                    'sequence_order': 1
                }
            )

            # Create the quiz assignment
            quiz = Assignment.objects.create(
                lesson=lesson,  # Link to the lesson
                title="Python Programming Basics Quiz",
                description="Test your knowledge of Python programming fundamentals.",
                instructions="Select the best answer for each question. You need 70% to pass.",
                assignment_type='quiz',
                is_quiz=True,
                max_points=100,
                due_date=timezone.now() + timedelta(days=7),
                time_limit_minutes=30,
                passing_score=70,
                shuffle_questions=True,
                show_correct_answers=True
            )

            # Question 1: Multiple Choice
            q1 = QuizQuestion.objects.create(
                assignment=quiz,
                question_type='multiple_choice',
                text="What is the output of: print(type([1, 2, 3]))?",
                points=20,
                order=1
            )
            q1.add_choice("<class 'list'>", True, "Lists in Python are represented by the 'list' class.")
            q1.add_choice("<class 'array'>", False, "Python doesn't have a built-in array class.")
            q1.add_choice("<class 'tuple'>", False, "Tuples use parentheses () not square brackets [].")
            q1.add_choice("<class 'set'>", False, "Sets use curly braces {} not square brackets [].")

            # Question 2: True/False
            q2 = QuizQuestion.objects.create(
                assignment=quiz,
                question_type='true_false',
                text="In Python, a tuple is mutable.",
                points=20,
                order=2
            )
            q2.add_choice("True", False, "Tuples are immutable - they cannot be changed after creation.")
            q2.add_choice("False", True, "Correct! Tuples are immutable in Python.")

            # Question 3: Multiple Choice
            q3 = QuizQuestion.objects.create(
                assignment=quiz,
                question_type='multiple_choice',
                text="Which of the following is the correct way to create an empty dictionary?",
                points=20,
                order=3
            )
            q3.add_choice("dict()", True, "Using the dict() constructor creates an empty dictionary.")
            q3.add_choice("{}", True, "Using curly braces creates an empty dictionary.")
            q3.add_choice("[]", False, "Square brackets create an empty list, not a dictionary.")
            q3.add_choice("()", False, "Parentheses create an empty tuple, not a dictionary.")

            # Question 4: Multiple Choice
            q4 = QuizQuestion.objects.create(
                assignment=quiz,
                question_type='multiple_choice',
                text="What does the 'len()' function return for a string?",
                points=20,
                order=4
            )
            q4.add_choice("The number of characters in the string", True, "len() counts all characters in a string.")
            q4.add_choice("The number of words in the string", False, "To count words, you would need to split the string first.")
            q4.add_choice("The size of the string in bytes", False, "len() counts characters, not bytes.")
            q4.add_choice("The number of lines in the string", False, "To count lines, you would need to split by newline characters.")

            # Question 5: Short Answer
            q5 = QuizQuestion.objects.create(
                assignment=quiz,
                question_type='short_answer',
                text="What Python function would you use to get user input from the console?",
                points=20,
                order=5
            )
            q5.add_choice("input()", True, "The input() function reads a line from the console.")

            self.stdout.write(self.style.SUCCESS(f'Successfully created quiz "{quiz.title}" with 5 questions'))
