from django.shortcuts import render

def support_center(request):
    """Support center main page"""
    return render(request, 'support/support_center.html')

def faq(request):
    """FAQ page"""
    return render(request, 'support/faq.html')

def contact(request):
    """Contact us page"""
    return render(request, 'support/contact.html')

def feedback(request):
    """Feedback form page"""
    return render(request, 'support/feedback.html')

