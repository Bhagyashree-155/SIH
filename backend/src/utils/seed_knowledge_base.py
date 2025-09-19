"""
Script to seed the knowledge base with sample articles for POWERGRID
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from datetime import datetime

from src.core.config import settings
from src.models.knowledge_base import KnowledgeArticle, Solution, SolutionType, AutomatedAction, ArticleStatus
from src.models.user import User
from src.models.knowledge_base import TicketResolution, CommonIssuePattern
from src.models import Team, Notification, AuditLog
from src.models.ticket import Ticket


async def seed_knowledge_base():
    """Seed the knowledge base with sample articles"""
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    
    # Initialize Beanie
    await init_beanie(
        database=client[settings.MONGODB_DB_NAME],
        document_models=[
            User, Ticket, KnowledgeArticle, TicketResolution, CommonIssuePattern, Team, Notification, AuditLog
        ]
    )
    
    print("🌱 Seeding Knowledge Base with sample articles...")
    
    # Sample articles
    articles = [
        {
            "title": "Password Reset - Self Service Portal",
            "description": "How to reset your POWERGRID password using the self-service portal",
            "content": """
            ## Password Reset Guide

            If you've forgotten your POWERGRID password, you can reset it yourself using our self-service portal.

            ### Steps:
            1. Go to https://selfservice.powergrid.in
            2. Click on "Forgot Password"
            3. Enter your employee ID or email address
            4. Answer your security questions
            5. Check your email for the temporary password
            6. Login with the temporary password and set a new permanent password

            ### Requirements:
            - Valid employee ID
            - Access to registered email
            - Security questions must be configured

            ### Troubleshooting:
            - If you don't receive the email, check spam folder
            - If security questions are not set up, contact IT support
            - Password must meet complexity requirements: 8+ characters, uppercase, lowercase, number, special character
            """,
            "category": "Password",
            "subcategory": "Reset",
            "tags": ["password", "reset", "self-service", "portal"],
            "keywords": ["password", "reset", "forgot", "login", "access"],
            "problem_patterns": [
                "I forgot my password",
                "Can't login to my account", 
                "Password expired",
                "Need to reset password",
                "Login not working"
            ],
            "symptoms": ["Unable to login", "Password rejected", "Account locked"],
            "error_codes": ["AUTH_FAILED", "PASSWORD_EXPIRED"],
            "solutions": [
                Solution(
                    solution_type=SolutionType.SELF_SERVICE_LINK,
                    title="Self-Service Password Reset",
                    description="Use the POWERGRID self-service portal to reset your password",
                    steps=[
                        "Visit https://selfservice.powergrid.in",
                        "Click 'Forgot Password'",
                        "Enter your employee ID",
                        "Follow email instructions"
                    ],
                    estimated_resolution_time=5,
                    success_rate=0.95,
                    portal_link="https://selfservice.powergrid.in",
                    automated_action=AutomatedAction(
                        action_type="password_reset",
                        api_endpoint="/api/actions/password-reset",
                        parameters={"method": "email"},
                        success_message="Password reset email sent successfully",
                        failure_message="Failed to send password reset email"
                    )
                )
            ],
            "affected_systems": ["Active Directory", "Email", "VPN"],
            "business_impact": "Medium",
            "author_id": "system",
            "author_name": "System Administrator"
        },
        {
            "title": "VPN Connection Issues - Troubleshooting Guide",
            "description": "Common VPN connectivity problems and their solutions for POWERGRID employees",
            "content": """
            ## VPN Connection Troubleshooting

            This guide helps resolve common VPN connectivity issues for remote access to POWERGRID systems.

            ### Common Issues:

            #### 1. Cannot Connect to VPN
            - Check internet connectivity
            - Verify VPN client is latest version
            - Ensure firewall allows VPN traffic
            - Try different VPN servers

            #### 2. VPN Connects but No Internet
            - Check DNS settings
            - Disable IPv6 if problematic
            - Restart network adapters

            #### 3. Slow VPN Performance
            - Try different server locations
            - Switch VPN protocols
            - Check for bandwidth limitations

            ### Server Locations:
            - Primary: Mumbai (vpn-mum.powergrid.in)
            - Secondary: Delhi (vpn-del.powergrid.in)
            - Backup: Bangalore (vpn-blr.powergrid.in)
            """,
            "category": "VPN",
            "subcategory": "Connection",
            "tags": ["vpn", "connection", "remote", "access"],
            "keywords": ["vpn", "connection", "remote", "access", "internet"],
            "problem_patterns": [
                "VPN not connecting",
                "Can't connect to VPN",
                "VPN connection failed",
                "VPN is slow",
                "No internet through VPN"
            ],
            "symptoms": ["Connection timeout", "Slow browsing", "Cannot access internal systems"],
            "error_codes": ["VPN_CONNECTION_FAILED", "TUNNEL_ERROR"],
            "solutions": [
                Solution(
                    solution_type=SolutionType.MANUAL_STEPS,
                    title="VPN Troubleshooting Steps",
                    description="Step-by-step troubleshooting for VPN issues",
                    steps=[
                        "Check internet connection",
                        "Restart VPN client",
                        "Try different server",
                        "Clear DNS cache",
                        "Restart network adapter"
                    ],
                    estimated_resolution_time=15,
                    success_rate=0.85,
                    automated_action=AutomatedAction(
                        action_type="vpn_reconnect",
                        parameters={"server": "auto"},
                        success_message="VPN configuration refreshed",
                        failure_message="Could not refresh VPN configuration"
                    )
                )
            ],
            "affected_systems": ["VPN", "Network", "Firewall"],
            "business_impact": "High",
            "author_id": "system",
            "author_name": "Network Administrator"
        },
        {
            "title": "Email Quota Exceeded - Cleanup Guide", 
            "description": "How to manage and clean up your POWERGRID email when quota is exceeded",
            "content": """
            ## Email Quota Management

            When your email quota is exceeded, you cannot send or receive new emails. Follow this guide to free up space.

            ### Immediate Actions:
            1. Delete large attachments from Sent Items
            2. Empty Deleted Items folder
            3. Remove old calendar appointments
            4. Archive old emails to PST files

            ### Preventive Measures:
            - Enable auto-archive for emails older than 6 months
            - Use shared mailboxes for team communications
            - Store large files on shared drives instead of email
            - Regularly clean up Sent Items

            ### Quota Limits:
            - Standard Users: 10 GB
            - Managers: 15 GB
            - Executives: 20 GB

            ### Auto-Archive Setup:
            1. File → Options → Advanced
            2. AutoArchive Settings
            3. Enable "Run AutoArchive every X days"
            4. Set archive location
            """,
            "category": "Email",
            "subcategory": "Quota",
            "tags": ["email", "quota", "storage", "cleanup"],
            "keywords": ["email", "quota", "full", "storage", "space", "cleanup"],
            "problem_patterns": [
                "Email quota exceeded",
                "Cannot send emails",
                "Mailbox full",
                "Email storage full",
                "Need more email space"
            ],
            "symptoms": ["Cannot send emails", "Bounce back messages", "Quota warning"],
            "error_codes": ["QUOTA_EXCEEDED", "MAILBOX_FULL"],
            "solutions": [
                Solution(
                    solution_type=SolutionType.AUTOMATED_SCRIPT,
                    title="Email Cleanup Assistant",
                    description="Automated cleanup of old emails and large attachments",
                    steps=[
                        "Scan for large attachments",
                        "Archive emails older than 6 months", 
                        "Empty deleted items",
                        "Generate cleanup report"
                    ],
                    estimated_resolution_time=30,
                    success_rate=0.90,
                    automated_action=AutomatedAction(
                        action_type="email_quota_check",
                        parameters={"cleanup": True, "archive": True},
                        success_message="Email cleanup completed successfully",
                        failure_message="Could not complete email cleanup"
                    )
                )
            ],
            "affected_systems": ["Exchange Server", "Email"],
            "business_impact": "Medium",
            "author_id": "system", 
            "author_name": "Email Administrator"
        },
        {
            "title": "GLPI Asset Registration and Updates",
            "description": "How to register new assets and update existing ones in GLPI system",
            "content": """
            ## GLPI Asset Management

            GLPI is POWERGRID's IT asset management system. Use this guide for asset registration and updates.

            ### New Asset Registration:
            1. Login to GLPI portal: https://glpi.powergrid.in
            2. Navigate to Assets → Computers/Devices
            3. Click "Add New Asset"
            4. Fill mandatory fields:
               - Asset Tag
               - Serial Number
               - Location
               - User Assignment
               - Purchase Date
            5. Submit for approval

            ### Updating Existing Assets:
            1. Search for asset by tag or serial number
            2. Click "Edit" 
            3. Update required fields
            4. Add comments explaining changes
            5. Submit changes

            ### Asset Categories:
            - Computers (Desktop, Laptop)
            - Mobile Devices (Phone, Tablet)
            - Network Equipment (Router, Switch)
            - Printers and Scanners
            - Software Licenses
            """,
            "category": "GLPI",
            "subcategory": "Asset Management",
            "tags": ["glpi", "asset", "registration", "inventory"],
            "keywords": ["glpi", "asset", "inventory", "register", "update"],
            "problem_patterns": [
                "Need to register new asset in GLPI",
                "Update asset information",
                "GLPI asset not found",
                "Asset registration failed"
            ],
            "symptoms": ["Asset not in GLPI", "Outdated asset info", "Cannot find asset"],
            "solutions": [
                Solution(
                    solution_type=SolutionType.MANUAL_STEPS,
                    title="Asset Registration Process",
                    description="Complete process for registering assets in GLPI",
                    steps=[
                        "Gather asset information",
                        "Login to GLPI portal",
                        "Create new asset entry",
                        "Fill all required fields",
                        "Submit for approval"
                    ],
                    estimated_resolution_time=20,
                    success_rate=0.95,
                    portal_link="https://glpi.powergrid.in"
                )
            ],
            "affected_systems": ["GLPI", "Asset Management"],
            "business_impact": "Low",
            "author_id": "system",
            "author_name": "Asset Administrator"
        }
    ]
    
    # Insert articles
    created_count = 0
    for article_data in articles:
        try:
            # Check if article already exists
            existing = await KnowledgeArticle.find_one({"title": article_data["title"]})
            if existing:
                print(f"⏭️  Article '{article_data['title']}' already exists, skipping...")
                continue
            
            # Create the article
            article = KnowledgeArticle(
                title=article_data["title"],
                description=article_data["description"],
                content=article_data["content"],
                category=article_data["category"],
                subcategory=article_data.get("subcategory"),
                tags=article_data["tags"],
                keywords=article_data["keywords"],
                problem_patterns=article_data["problem_patterns"],
                symptoms=article_data["symptoms"],
                error_codes=article_data.get("error_codes", []),
                solutions=article_data["solutions"],
                primary_solution=article_data["solutions"][0] if article_data["solutions"] else None,
                status=ArticleStatus.PUBLISHED,
                author_id=article_data["author_id"],
                author_name=article_data["author_name"],
                affected_systems=article_data["affected_systems"],
                business_impact=article_data["business_impact"],
                ai_generated=False,
                confidence_score=0.95
            )
            
            await article.insert()
            created_count += 1
            print(f"✅ Created article: {article.title}")
            
        except Exception as e:
            print(f"❌ Error creating article '{article_data['title']}': {str(e)}")
    
    print(f"\n🎉 Knowledge base seeding complete! Created {created_count} new articles.")
    
    # Close connection
    client.close()


if __name__ == "__main__":
    asyncio.run(seed_knowledge_base())
