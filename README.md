# Global Coaches Academy - Django Web Application

A comprehensive learning management system for Global Coaches Academy, empowering leaders through transformational education and mentorship for global impact.

## 🌟 Live Application

**Public URL:** https://8000-ii4pr6u5z03c8qggur3dd-b10c5215.manusvm.computer

## 📋 Features Overview

### 🏠 Landing Page
- **Hero Section:** Welcome message and mission statement
- **Call to Action:** "Join a Track" | "Explore Faculties" | "Login"
- **Partners Bar:** Logos for ICY Africa, Africa for SDGs, LADA, UN SDGs
- **Testimonials:** From graduates, mentors, and founders
- **Statistics:** 7 Core Faculties, 1000+ Students, 50+ Mentors, 95% Completion Rate

### 🎓 Faculties Overview
- **7 Core Faculties:**
  1. Church & Theological Education and Transformation
  2. Missional Leadership
  3. SDGs & Community Transformation
  4. Education for Sustainable Development & Global Citizenship
  5. Global Leadership & Diplomacy
  6. Entrepreneurship & Political Economics
  7. Climate Warriors (Environmental Leadership & Action)

- **3 Academic Levels:**
  - 🔹 Masterclass (6 months)
  - 🔹 Diploma (12 months)
  - 🔹 Higher Diploma (12 months)

### 📚 Course Module System
- **Monthly Modules** with course codes (e.g., GCCT-M101)
- **Credits System** (2–3 per month)
- **Weekly Breakdown** (4 weeks per module):
  - Theme and Value focus
  - Scripture/Thought Quote (for faith-based faculties)
  - Weekly Practical Assignments
- **Assignment Submission** with file upload and text editor
- **Progress Tracking** with completion indicators

### 👤 Student Dashboard
- **Enrollment Tracking** for faculty and level
- **Module Progress** with completion status
- **Assignment Upload** zone with drag-and-drop functionality
- **Certificate Management** and downloads
- **User Profile** management with personal information

### 🤝 Mentorship & Peer Learning Portal
- **Mentor Pairing** (automated based on availability)
- **Weekly Check-ins** with mood ratings and progress reports
- **Peer Review System** for assignment feedback
- **Messaging Framework** for mentor-student communication
- **Progress Monitoring** and support tracking

### 🎯 Graduation & Certification
- **Credit Calculation** system for graduation requirements
- **Certificate Generation** upon completion
- **Final Project** submission and evaluation
- **Graduation Status** tracking and notifications

### 🛠️ Admin Panel
- **Comprehensive Django Admin** interface
- **Content Management** for all modules and courses
- **User Management** (students, mentors, admin team)
- **Assignment Review** and approval system
- **Analytics Dashboard** with completion rates and user activity
- **Email/Notification** management system

### 🆘 Support & Help System
- **FAQ Section** with accordion-style interface
- **Feedback Forms** with categorized feedback types
- **Contact Forms** with full support team integration
- **Support Tickets** management system

## 🏗️ Technical Architecture

### Backend Framework
- **Django 5.2.4** with Python 3.11
- **SQLite Database** for development
- **Django REST Framework** for API endpoints
- **Django CORS Headers** for cross-origin requests

### Frontend Technologies
- **HTML5/CSS3** with responsive design
- **Bootstrap 5** for UI components
- **JavaScript** for interactive elements
- **Custom CSS** for branding and animations

### Database Models
- **User Management:** Extended user profiles, roles, permissions
- **Academic Structure:** Faculties, programs, modules, weeks
- **Learning Management:** Assignments, submissions, progress tracking
- **Mentorship System:** Mentor profiles, pairings, check-ins, reviews
- **Support System:** FAQs, feedback, contact information, tickets

### Security Features
- **User Authentication** with Django's built-in system
- **Session Management** with secure cookies
- **CSRF Protection** on all forms
- **Permission-based Access** control
- **Admin Interface** with superuser privileges

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Django 5.2.4
- SQLite (included with Python)

### Installation
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run migrations: `python manage.py migrate`
4. Create superuser: `python manage.py createsuperuser`
5. Start server: `python manage.py runserver`

### Admin Access
- **URL:** `/admin/`
- **Test Superuser:** testuser / testpass123

### Default Test Account
- **Username:** testuser
- **Password:** testpass123

## 📱 Application Structure

```
global_coaches_academy/
├── core/                 # Main app with landing page and auth
├── faculties/           # Faculty management and overview
├── courses/             # Course modules and assignments
├── students/            # Student dashboard and profiles
├── mentorship/          # Mentorship and peer learning
├── support/             # Help system and feedback
├── templates/           # HTML templates
├── static/              # CSS, JS, images
├── media/               # User uploads
└── manage.py           # Django management script
```

## 🎨 Design Features

### Visual Design
- **Professional Color Scheme** with blue primary and warm accents
- **Responsive Layout** for desktop and mobile devices
- **Modern Typography** with clear hierarchy
- **Interactive Elements** with hover effects and animations
- **Consistent Branding** throughout all pages

### User Experience
- **Intuitive Navigation** with clear menu structure
- **Progress Indicators** for learning journey
- **Interactive Forms** with validation and feedback
- **Accessibility Features** with proper ARIA labels
- **Mobile-First Design** for all screen sizes

## 📊 Key Metrics & Analytics

### Student Engagement
- **Enrollment Tracking** across all faculties
- **Completion Rates** by program and level
- **Assignment Submission** statistics
- **Mentorship Participation** metrics

### Content Management
- **Module Creation** and editing capabilities
- **Assignment Management** with review workflows
- **Progress Monitoring** for individual students
- **Certificate Generation** automation

## 🔧 Admin Capabilities

### Content Management
- **Add/Edit Faculties** with descriptions and images
- **Create Course Modules** with weekly breakdowns
- **Manage Assignments** and submission requirements
- **Upload Resources** and learning materials

### User Management
- **Student Registration** approval and management
- **Mentor Assignment** and profile management
- **Role-based Permissions** for different user types
- **Communication Tools** for announcements

### Analytics & Reporting
- **Student Progress** tracking and reporting
- **Completion Statistics** by faculty and program
- **Mentor Performance** metrics and feedback
- **System Usage** analytics and insights

## 🌍 Global Impact Focus

### SDG Alignment
- **Sustainable Development Goals** integration
- **Community Transformation** emphasis
- **Environmental Leadership** programs
- **Global Citizenship** education

### Leadership Development
- **Transformational Education** approach
- **Practical Application** focus
- **Mentorship Support** system
- **Real-world Impact** measurement

## 📞 Support & Contact

### Technical Support
- **Email:** info@globalcoachesacademy.org
- **Phone:** +1 (555) 123-4567
- **Support Portal:** Available within the application

### Educational Support
- **Mentor Network:** 50+ expert mentors
- **Peer Learning:** Community-driven support
- **Resource Library:** Comprehensive learning materials
- **Regular Check-ins:** Weekly progress monitoring

---

**© 2024 Global Coaches Academy. All rights reserved.**

*Empowering leaders through transformational education and mentorship for global impact.*

# global
