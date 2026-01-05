from datetime import time, timedelta
from django.utils import timezone
from django.utils.text import slugify
from tenant.models import Department, Ticket, TicketCategories, Task
from tenant.models.SettingModel import EmailTemplateCategory, EmailTemplate, EmailConfig
from tenant.models.SlaXModel import SLA, Holidays, SLATarget, BusinessHoursx
from tenant.models.KnowledgeBase import KBCategory
from users.models import Users
from util.email.templates import EMAIL_TEMPLATES
from util.Holidays import HOLIDAYS
from util.Helper import Helper


class BusinessSetup:
    def __init__(self, business, user):
        self.business = business
        # Try to use system user, fall back to business owner
        self.user = Users.objects.filter(email="system@safaridesk.io").first()
        if not self.user:
            self.user = user  # Use the business owner if system user doesn't exist

    def run_setup(self):
        if not self.user:
            return  # Do not run setup if there is no owner
        
        self.seed_default_sla()
        self.seed_default_email_templates()
        self.seed_default_email_config()
        self.seed_default_holidays()
        self.seed_default_departments_and_categories()
        # self.create_welcome_ticket()


    def seed_default_sla(self):
        # Create Default SLA
        sla_data = {
            "name": "Default SLA",
            "description": "Default SLA for all tickets",
            "operational_hours": "business",
            "evaluation_method": "ticket_creation",
            "is_active": True,
            "created_by": self.user,
        }
        if self.business:
            sla_data['business'] = self.business
        default_sla = SLA.objects.create(**sla_data)

        # Create SLA Targets
        priorities = ["urgent", "high", "medium", "low"]
        target_times = {
            "urgent": {"first_response": 1, "first_unit": "hours", "resolution": 4, "resolution_unit": "hours"},
            "high": {"first_response": 2, "first_unit": "hours", "resolution": 8, "resolution_unit": "hours"},
            "medium": {"first_response": 4, "first_unit": "hours", "resolution": 24, "resolution_unit": "hours"},
            "low": {"first_response": 8, "first_unit": "hours", "resolution": 48, "resolution_unit": "hours"},
        }

        for priority in priorities:
            target_data = target_times[priority]
            SLATarget.objects.create(
                sla=default_sla,
                priority=priority,
                first_response_time=target_data["first_response"],
                first_response_unit=target_data["first_unit"],
                next_response_time=None,  # No next response time for default
                next_response_unit="hours",
                resolution_time=target_data["resolution"],
                resolution_unit=target_data["resolution_unit"],
                operational_hours="business",
                reminder_enabled=False,
                escalation_enabled=False
            )

        # Create Business Hours (Monday to Friday, 8 AM - 5 PM)
        for day_of_week in range(5):
            hours_data = {
                "name": f"{BusinessHoursx.DAYS_OF_WEEK[day_of_week][1]}",
                "day_of_week": day_of_week,
                "start_time": time(8, 0),
                "end_time": time(17, 0),
                "is_working_day": True,
            }
            if self.business:
                hours_data['business'] = self.business
            BusinessHoursx.objects.create(**hours_data)

    def seed_default_email_templates(self):
        category_kwargs = {'name': "Default Email Templates"}
        if self.business:
            category_kwargs['business'] = self.business
        category, created = EmailTemplateCategory.objects.get_or_create(**category_kwargs)

        for template_name, template_data in EMAIL_TEMPLATES.items():
            template_kwargs = {'name': template_name}
            if self.business:
                template_kwargs['business'] = self.business
            EmailTemplate.objects.update_or_create(
                **template_kwargs,
                defaults={
                    "description": template_data["description"],
                    "subject": template_data["subject"],
                    "body": template_data["body"],
                    "type": template_data["type"],
                    "category": category,
                }
            )

    def seed_default_email_config(self):
        category_kwargs = {'name': "Default Email Templates"}
        if self.business:
            category_kwargs['business'] = self.business
        category = EmailTemplateCategory.objects.get(**category_kwargs)
        config_data = {
            'default_template': category,
            'email_fetching': True,
        }
        if self.business:
            config_data['business'] = self.business
        EmailConfig.objects.create(**config_data)

    def seed_default_holidays(self):
        for holiday in HOLIDAYS:
            holiday_kwargs = {
                'name': holiday["name"],
                'date': holiday["date"],
            }
            if self.business:
                holiday_kwargs['business'] = self.business
            Holidays.objects.get_or_create(
                **holiday_kwargs,
                defaults={'is_recurring': True}
            )

    def seed_default_departments_and_categories(self):
        """
        Add default departments, ticket categories, and KB categories for the business
        """
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            # Default departments
            departments_data = [
                {'name': 'Human Resources (HR)', 'support_email': 'hr@example.com'},
                {'name': 'Finance/Accounting', 'support_email': 'finance@example.com'},
                {'name': 'IT/Technology', 'support_email': 'it@example.com'},
                {'name': 'Marketing/Sales', 'support_email': 'marketing@example.com'},
            ]

            # Add departments
            for dept_data in departments_data:
                dept_kwargs = {'name': dept_data['name']}
                if self.business:
                    dept_kwargs['business'] = self.business
                dept, created = Department.objects.get_or_create(
                    **dept_kwargs,
                    defaults={'support_email': dept_data['support_email']}
                )
                if created:
                    business_name = self.business.name if self.business else 'single tenant'
                    logger.info(f"Created department: {dept.name} for business: {business_name}")

            # Default ticket categories
            ticket_categories_data = [
                {
                    'name': 'Administrations',
                    'description': 'Includes HR, finance, compliance, and internal management tasks.',
                },
                {
                    'name': 'Marketing & Sales',
                    'description': 'Covers promotion, branding, outreach, and customer engagement.',
                },
                {
                    'name': 'Operations',
                    'description': 'Covers day-to-day business processes and workflows.',
                },
                {
                    'name': 'Other / Miscellaneous',
                    'description': 'For anything that doesn\'t fit neatly into the above categories.',
                },
                {
                    'name': 'Technology',
                    'description': 'Encompasses IT support, software, networks, and cybersecurity.',
                },
            ]

            # Add ticket categories
            for cat_data in ticket_categories_data:
                cat_kwargs = {'name': cat_data['name']}
                if self.business:
                    cat_kwargs['business'] = self.business
                cat, created = TicketCategories.objects.get_or_create(
                    **cat_kwargs,
                    defaults={
                        'description': cat_data['description'],
                        'is_active': True,
                    }
                )
                if created:
                    business_name = self.business.name if self.business else 'single tenant'
                    logger.info(f"Created ticket category: {cat.name} for business: {business_name}")

            # Default KB categories
            kb_categories_data = [
                {
                    'name': 'Account & Access',
                    'description': 'Covers login issues, password resets, permissions, and user account management.',
                },
                {
                    'name': 'Billing & Payments',
                    'description': 'Information about invoices, subscriptions, pricing, and refund policies.',
                },
                {
                    'name': 'Technical Support',
                    'description': 'Articles addressing common technical problems, troubleshooting steps, and maintenance tips.',
                },
                {
                    'name': 'Product Guides',
                    'description': 'Step-by-step instructions, manuals, and feature explanations for your products or services.',
                },
                {
                    'name': 'Policies & Compliance',
                    'description': 'Details company policies, compliance standards, data protection, and legal guidelines.',
                },
                {
                    'name': 'Updates & Announcements',
                    'description': 'News, version releases, and updates related to the system or organization.',
                },
                {
                    'name': 'FAQs',
                    'description': 'Frequently asked questions with short, helpful answers covering general user concerns.',
                },
                {
                    'name': 'Community & Feedback',
                    'description': 'Information about user forums, feedback submission, and community engagement.',
                },
                {
                    'name': 'Other / Miscellaneous',
                    'description': 'For any general or uncategorized articles not covered by the other sections.',
                },
            ]

            # Add KB categories
            for i, cat_data in enumerate(kb_categories_data):
                slug = slugify(cat_data['name'])
                kb_cat_kwargs = {'name': cat_data['name']}
                if self.business:
                    kb_cat_kwargs['business'] = self.business
                kb_cat, created = KBCategory.objects.get_or_create(
                    **kb_cat_kwargs,
                    defaults={
                        'slug': slug,
                        'description': cat_data['description'],
                        'is_public': True,
                        'sort_order': i,
                    }
                )
                if created:
                    business_name = self.business.name if self.business else 'single tenant'
                    logger.info(f"Created KB category: {kb_cat.name} for business: {business_name}")

        except Exception as e:
            business_name = self.business.name if self.business else 'single tenant'
            logger.error(f"Error seeding default departments and categories for business {business_name}: {str(e)}", exc_info=True)

    def create_welcome_ticket(self):
        # Create default department if it doesn't exist
        department, _ = Department.objects.get_or_create(
            name="Support",
            business=self.business
        )

        # Create default category if it doesn't exist
        category, _ = TicketCategories.objects.get_or_create(
            name="Getting Started",
            business=self.business,
            defaults={'description': 'Initial setup and guidance'}
        )

        html_content = """
<h1>Welcome to SafariDesk!</h1>
<p>Here's a quick guide to get you started:</p>
<ul>
    <li><strong>Set up your departments:</strong> Go to Settings > Departments to organize your support teams.</li>
    <li><strong>Invite your team:</strong> Go to Settings > Agents to add your support staff.</li>
    <li><strong>Configure SLAs:</strong> Define your service level agreements in Settings > SLAs to set response and resolution time targets.</li>
    <li><strong>Customize your support portal:</strong> Go to Settings > Support Portal to customize the look and feel of your customer-facing portal.</li>
</ul>
<p>If you have any questions, feel free to reach out to our support team.</p>
<p>Happy ticketing!</p>
"""
        ticket_id = Helper().generate_incident_code()
        default_sla = SLA.objects.filter(business=self.business, name="Default SLA").first()
        ticket = Ticket.objects.create(
            ticket_id=ticket_id,
            title="Get started",
            description=html_content,
            category=category,
            department=department,
            creator_name=self.user.full_name(),
            creator_email=self.user.email,
            created_by=self.user,
            business=self.business,
            priority="low",
            status="open",
            source='internal',
            sla=default_sla
        )

        # Create individual tasks for the welcome ticket
        tasks_to_create = [
            {
                "title": "Set up your departments",
                "description": "Go to Settings > Departments to organize your support teams."
            },
            {
                "title": "Invite your team",
                "description": "Go to Settings > Agents to add your support staff."
            },
            {
                "title": "Configure SLAs",
                "description": "Define your service level agreements in Settings > SLAs to set response and resolution time targets."
            },
            {
                "title": "Customize your support portal",
                "description": "Go to Settings > Support Portal to customize the look and feel of your customer-facing portal."
            }
        ]

        due_date = timezone.now() + timedelta(days=7)

        for task_data in tasks_to_create:
            Task.objects.create(
                title=task_data["title"],
                description=task_data["description"],
                due_date=due_date,
                assigned_to=self.user,
                task_trackid=Helper().generate_task_code(),
                department=department,
                linked_ticket=ticket,
                business=self.business,
                created_by=self.user
            )
