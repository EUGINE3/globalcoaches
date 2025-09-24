from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from programs.models import ProgramModule
from courses.models import ModuleTopic, ModuleDiscussion, TopicDiscussion, DiscussionPost
from django.utils import timezone


class Command(BaseCommand):
    help = 'Create demo discussion data'

    def handle(self, *args, **options):
        self.stdout.write('Creating demo discussion data...')
        
        # Get or create a demo user
        demo_user, created = User.objects.get_or_create(
            username='demo_student',
            defaults={
                'first_name': 'Demo',
                'last_name': 'Student',
                'email': 'demo@example.com',
                'is_active': True
            }
        )
        if created:
            demo_user.set_password('demo123')
            demo_user.save()
            self.stdout.write(f'Created demo user: {demo_user.username}')
        
        # Get first program module
        program_module = ProgramModule.objects.filter(is_active=True).first()
        if not program_module:
            self.stdout.write(self.style.ERROR('No active program modules found'))
            return
        
        # Create module discussion
        module_discussion, created = ModuleDiscussion.objects.get_or_create(
            program_module=program_module,
            defaults={
                'title': f"{program_module.module.name} Discussion",
                'description': f"General discussion forum for {program_module.module.name}"
            }
        )
        if created:
            self.stdout.write(f'Created module discussion: {module_discussion.title}')
        
        # Create some demo posts for module discussion
        module_posts = [
            {
                'title': 'Welcome to the Module!',
                'content': 'Hi everyone! Welcome to this module. I\'m excited to learn alongside all of you. Feel free to share your thoughts and ask questions here.'
            },
            {
                'title': 'Study Group Formation',
                'content': 'Would anyone be interested in forming a study group? We could meet virtually once a week to discuss the topics and help each other with assignments.'
            },
            {
                'title': 'Resource Recommendations',
                'content': 'I found some great additional resources that complement this module. Has anyone else found helpful materials they\'d like to share?'
            }
        ]
        
        for post_data in module_posts:
            post, created = DiscussionPost.objects.get_or_create(
                module_discussion=module_discussion,
                author=demo_user,
                title=post_data['title'],
                defaults={'content': post_data['content']}
            )
            if created:
                self.stdout.write(f'Created module post: {post.title}')
        
        # Get first topic
        topic = ModuleTopic.objects.filter(program_module=program_module, is_active=True).first()
        if topic:
            # Create topic discussion
            topic_discussion, created = TopicDiscussion.objects.get_or_create(
                topic=topic,
                defaults={
                    'title': f"{topic.title} Discussion",
                    'description': f"Discussion forum for {topic.title}"
                }
            )
            if created:
                self.stdout.write(f'Created topic discussion: {topic_discussion.title}')
            
            # Create some demo posts for topic discussion
            topic_posts = [
                {
                    'title': 'Understanding the Key Concepts',
                    'content': f'I\'m working through the key concepts in {topic.title}. The learning objectives are really comprehensive. What aspects are you finding most challenging?'
                },
                {
                    'title': 'Practical Application Question',
                    'content': 'How do you think we can apply what we\'re learning in this topic to real-world scenarios? I\'d love to hear your perspectives.'
                },
                {
                    'title': 'Assignment Discussion',
                    'content': 'Has anyone started working on the assignments for this topic? I\'d be happy to discuss approaches (without sharing answers, of course!).'
                }
            ]
            
            for post_data in topic_posts:
                post, created = DiscussionPost.objects.get_or_create(
                    topic_discussion=topic_discussion,
                    author=demo_user,
                    title=post_data['title'],
                    defaults={'content': post_data['content']}
                )
                if created:
                    self.stdout.write(f'Created topic post: {post.title}')
        
        # Create some replies
        first_module_post = DiscussionPost.objects.filter(module_discussion=module_discussion).first()
        if first_module_post:
            reply, created = DiscussionPost.objects.get_or_create(
                module_discussion=module_discussion,
                author=demo_user,
                parent_post=first_module_post,
                title='Re: Welcome to the Module!',
                defaults={
                    'content': 'Thank you for the warm welcome! I\'m looking forward to collaborating with everyone and learning from your experiences.'
                }
            )
            if created:
                self.stdout.write(f'Created reply: {reply.title}')
        
        self.stdout.write(
            self.style.SUCCESS('Successfully created demo discussion data!')
        )
        self.stdout.write(
            f'Module Discussion: {module_discussion.total_posts} posts'
        )
        if topic:
            self.stdout.write(
                f'Topic Discussion: {topic_discussion.total_posts} posts'
            )
