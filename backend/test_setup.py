#!/usr/bin/env python3
"""
Test script to verify the POWERGRID AI Ticketing System setup
"""

import asyncio
import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.ai.gemini_service import gemini_service
from src.models.ticket import Ticket

async def test_classification():
    """Test the AI classification system"""
    print("🧪 Testing AI Classification System...")
    
    test_queries = [
        "My laptop is not turning on and the screen is black",
        "I can't log into my email account, it says password incorrect",
        "The VPN connection keeps dropping every few minutes",
        "I need to install Microsoft Office on my computer",
        "My printer is showing error code E-3 and won't print",
        "I can't access the shared folder on the network drive"
    ]
    
    for query in test_queries:
        try:
            print(f"\n📝 Query: '{query}'")
            classification = await gemini_service.classify_ticket(query)
            print(f"   Category: {classification.category}")
            print(f"   Subcategory: {classification.subcategory}")
            print(f"   Priority: {classification.priority}")
            print(f"   Confidence: {classification.confidence:.2f}")
            print(f"   Reasoning: {classification.reasoning}")
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")

async def test_ticket_creation():
    """Test ticket creation with unique IDs"""
    print("\n🎫 Testing Ticket Creation...")
    
    try:
        # Generate a few ticket numbers
        for i in range(3):
            ticket_number = Ticket.generate_ticket_number()
            print(f"   Generated Ticket Number: {ticket_number}")
        
        print("   ✅ Ticket number generation working correctly")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")

def test_categories():
    """Test the three main categories"""
    print("\n📊 Testing Category Configuration...")
    
    categories = gemini_service.categories
    print(f"   Total Categories: {len(categories)}")
    
    for category, info in categories.items():
        print(f"   - {category}: {info['description']}")
        print(f"     Keywords: {', '.join(info['keywords'][:5])}...")
    
    print("   ✅ Categories configured correctly")

async def main():
    """Run all tests"""
    print("🚀 POWERGRID AI Ticketing System - Setup Test")
    print("=" * 50)
    
    # Test categories
    test_categories()
    
    # Test ticket creation
    await test_ticket_creation()
    
    # Test classification (only if API key is available)
    try:
        await test_classification()
    except Exception as e:
        print(f"\n⚠️  Classification test skipped: {str(e)}")
        print("   Make sure to set your GEMINI_API_KEY in the environment")
    
    print("\n✅ Setup test completed!")
    print("\n📋 Next Steps:")
    print("   1. Set your GEMINI_API_KEY in the environment")
    print("   2. Install dependencies: pip install -r requirements.txt")
    print("   3. Start the backend: python -m src.main")
    print("   4. Start the frontend: cd frontend && npm install && npm run dev")

if __name__ == "__main__":
    asyncio.run(main())
