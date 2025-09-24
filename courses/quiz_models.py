"""
Quiz-related models for the courses app.
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User


class QuizQuestion(models.Model):
    """Questions for quiz-type assignments"""
    QUESTION_TYPES = [
        ('multiple_choice', 'Multiple Choice'),
        ('true_false', 'True/False'),
        ('short_answer', 'Short Answer'),
        ('essay', 'Essay'),
    ]
    
    assignment = models.ForeignKey('courses.Assignment', on_delete=models.CASCADE, related_name='questions')
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    text = models.TextField()
    points = models.IntegerField(default=1, validators=[MinValueValidator(0)])
    order = models.IntegerField(default=0)
    
    class Meta:
        app_label = 'courses'
        ordering = ['order']

    def __str__(self):
        return f"{self.assignment.title} - Question {self.order}"

    def add_choice(self, text, is_correct=False, explanation=''):
        """Helper method to add a choice to the question"""
        order = self.choices.count()
        return self.choices.create(
            text=text,
            is_correct=is_correct,
            explanation=explanation,
            order=order
        )


class QuizChoice(models.Model):
    """Answer choices for multiple choice and true/false questions"""
    question = models.ForeignKey(QuizQuestion, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)
    explanation = models.TextField(blank=True, help_text='Explanation for why this choice is correct/incorrect')
    order = models.IntegerField(default=0)
    
    class Meta:
        app_label = 'courses'
        ordering = ['order']
        indexes = [
            models.Index(fields=['question', 'order'], name='quiz_choice_question_order_idx')
        ]

    def __str__(self):
        return self.text
