import json
import logging
import asyncio
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from dataclasses import dataclass

import aiohttp
from src.core.config import settings
from src.models.knowledge_base import KnowledgeArticle, Solution, SolutionType, AutomatedAction

logger = logging.getLogger(__name__)


@dataclass
class ClassificationResult:
    category: str
    subcategory: Optional[str]
    priority: str
    confidence: float
    reasoning: str
    suggested_keywords: List[str]
    urgency_level: str
    sentiment_score: float = 0.0
    similar_tickets: List[str] = None
    auto_resolution_possible: bool = False
    suggested_assignee: Optional[str] = None
    estimated_resolution_time: Optional[int] = None


@dataclass
class SolutionRecommendation:
    solution_id: Optional[str]
    title: str
    description: str
    steps: List[str]
    solution_type: SolutionType
    confidence: float
    estimated_time: int
    automated_action: Optional[Dict[str, Any]] = None


class GeminiAIService:
    """
    Service for integrating with Google Gemini AI for ticket classification,
    solution generation, and intelligent automation.
    """
    
    async def _enhance_with_sentiment_analysis(self, classification: ClassificationResult, user_query: str) -> ClassificationResult:
        """Enhance classification with sentiment analysis"""
        try:
            # Simple sentiment analysis based on keywords
            negative_words = ["angry", "frustrated", "terrible", "awful", "horrible", "upset"]
            positive_words = ["happy", "pleased", "grateful", "satisfied", "excellent"]
            
            sentiment_score = 0.0
            for word in negative_words:
                if word in user_query.lower():
                    sentiment_score -= 0.2
            
            for word in positive_words:
                if word in user_query.lower():
                    sentiment_score += 0.2
            
            # Clamp between -1.0 and 1.0
            sentiment_score = max(-1.0, min(1.0, sentiment_score))
            classification.sentiment_score = sentiment_score
            
            return classification
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {str(e)}")
            return classification
    
    async def _find_similar_tickets(self, classification: ClassificationResult, user_query: str) -> ClassificationResult:
        """Find similar tickets based on classification and query"""
        try:
            # This would typically involve a vector search in a real implementation
            # For now, we'll just set a placeholder
            classification.similar_tickets = ["TICKET-1234", "TICKET-5678"]
            return classification
        except Exception as e:
            logger.error(f"Error finding similar tickets: {str(e)}")
            return classification
    
    async def _suggest_assignee(self, classification: ClassificationResult) -> ClassificationResult:
        """Suggest an assignee based on ticket category and subcategory"""
        try:
            # Simple mapping of categories to teams/individuals
            assignee_map = {
                "VPN": "network_team",
                "Password": "access_management_team",
                "Email": "messaging_team",
                "Hardware": "desktop_support",
                "Software": "application_support",
                "Network": "network_team",
                "Access Control": "security_team",
                "Printer": "desktop_support",
                "GLPI": "asset_management_team",
                "SAP": "erp_support_team"
            }
            
            classification.suggested_assignee = assignee_map.get(classification.category, "helpdesk_team")
            return classification
        except Exception as e:
            logger.error(f"Error suggesting assignee: {str(e)}")
            return classification
    
    async def _check_auto_resolution_possibility(self, classification: ClassificationResult, user_query: str) -> ClassificationResult:
        """Check if the ticket can be automatically resolved"""
        try:
            # Simple rules for auto-resolution
            auto_resolvable_categories = ["Password", "Email"]
            auto_resolvable_subcategories = ["reset", "unlock", "quota"]
            
            if classification.category in auto_resolvable_categories:
                if classification.subcategory and classification.subcategory.lower() in auto_resolvable_subcategories:
                    classification.auto_resolution_possible = True
            
            return classification
        except Exception as e:
            logger.error(f"Error checking auto-resolution: {str(e)}")
            return classification
    
    async def _estimate_resolution_time(self, classification: ClassificationResult) -> ClassificationResult:
        """Estimate resolution time based on category and priority"""
        try:
            # Base times in minutes for different categories
            base_times = {
                "VPN": 30,
                "Password": 15,
                "Email": 45,
                "Hardware": 120,
                "Software": 90,
                "Network": 60,
                "Access Control": 45,
                "Printer": 30,
                "GLPI": 60,
                "SAP": 120
            }
            
            # Priority multipliers
            priority_multipliers = {
                "Low": 1.5,
                "Medium": 1.0,
                "High": 0.8,
                "Urgent": 0.6,
                "Critical": 0.5
            }
            
            base_time = base_times.get(classification.category, 60)
            multiplier = priority_multipliers.get(classification.priority, 1.0)
            
            classification.estimated_resolution_time = int(base_time * multiplier)
            return classification
        except Exception as e:
            logger.error(f"Error estimating resolution time: {str(e)}")
            classification.estimated_resolution_time = 60  # Default 1 hour
            return classification
    
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.base_url = settings.GEMINI_API_URL
        self.model_name = "gemini-1.5-flash"  # Using the latest efficient model
        
        # Predefined categories for POWERGRID
        self.categories = {
            "VPN": ["connection", "access", "authentication", "slow", "disconnect"],
            "Password": ["reset", "forgot", "expired", "change", "unlock"],
            "Email": ["quota", "sync", "access", "attachment", "delivery"],
            "Hardware": ["laptop", "desktop", "monitor", "keyboard", "mouse", "printer"],
            "Software": ["installation", "update", "license", "crash", "error"],
            "Network": ["internet", "wifi", "connectivity", "slow", "timeout"],
            "Access Control": ["permissions", "folder", "drive", "application", "system"],
            "Printer": ["print", "scan", "jam", "quality", "driver"],
            "GLPI": ["asset", "inventory", "tracking", "update", "sync"],
            "SAP": ["solman", "transaction", "login", "performance", "error"]
        }
        
    async def classify_ticket(self, user_query: str, user_context: Optional[Dict] = None) -> ClassificationResult:
        """
        Classify a user query into appropriate category, priority, and extract key information.
        Also performs sentiment analysis, finds similar tickets, and suggests assignees.
        """
        try:
            # Prepare the classification prompt
            classification_prompt = self._build_classification_prompt(user_query, user_context)
            
            # Call Gemini API
            response = await self._call_gemini_api(classification_prompt)
            
            # Parse classification result
            classification = self._parse_classification_response(response, user_query)
            
            # Enhance with sentiment analysis
            classification = await self._enhance_with_sentiment_analysis(classification, user_query)
            
            # Find similar tickets
            classification = await self._find_similar_tickets(classification, user_query)
            
            # Suggest assignee based on category and subcategory
            classification = await self._suggest_assignee(classification)
            
            # Determine if auto-resolution is possible
            classification = await self._check_auto_resolution_possibility(classification, user_query)
            
            # Estimate resolution time
            classification = await self._estimate_resolution_time(classification)
            
            return classification
            
        except Exception as e:
            logger.error(f"Error in ticket classification: {str(e)}")
            # Fallback to basic keyword matching
            return self._fallback_classification(user_query)
    
    async def generate_solution(self, 
                              classification: ClassificationResult, 
                              user_query: str,
                              knowledge_articles: List[KnowledgeArticle] = None) -> List[SolutionRecommendation]:
        """
        Generate solution recommendations based on classification and available knowledge.
        """
        try:
            # Build solution generation prompt
            solution_prompt = self._build_solution_prompt(
                classification, user_query, knowledge_articles
            )
            
            # Call Gemini API
            response = await self._call_gemini_api(solution_prompt)
            
            # Parse and return solutions
            return self._parse_solution_response(response, classification)
            
        except Exception as e:
            logger.error(f"Error in solution generation: {str(e)}")
            # Return fallback solutions
            return self._get_fallback_solutions(classification)
    
    async def enhance_knowledge_article(self, article: KnowledgeArticle) -> KnowledgeArticle:
        """
        Use AI to enhance existing knowledge articles with better keywords, 
        problem patterns, and solution improvements.
        """
        try:
            enhancement_prompt = self._build_enhancement_prompt(article)
            response = await self._call_gemini_api(enhancement_prompt)
            
            return self._apply_enhancements(article, response)
            
        except Exception as e:
            logger.error(f"Error enhancing knowledge article: {str(e)}")
            return article
    
    async def _call_gemini_api(self, prompt: str) -> Dict[str, Any]:
        """Make an API call to Google Gemini"""
        try:
            url = f"{self.base_url}{self.model_name}:generateContent?key={self.api_key}"
            
            payload = {
                "contents": [{
                    "parts": [{
                        "text": prompt
                    }]
                }],
                "generationConfig": {
                    "temperature": 0.3,  # Lower temperature for more consistent results
                    "topP": 0.8,
                    "topK": 40,
                    "maxOutputTokens": 2048,
                    "candidateCount": 1
                },
                "safetySettings": [
                    {
                        "category": "HARM_CATEGORY_HARASSMENT",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    },
                    {
                        "category": "HARM_CATEGORY_HATE_SPEECH",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    }
                ]
            }
            
            headers = {
                "Content-Type": "application/json"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result
                    else:
                        error_text = await response.text()
                        logger.error(f"Gemini API error: {response.status} - {error_text}")
                        raise Exception(f"Gemini API error: {response.status} - {error_text}")
        except Exception as e:
            logger.error(f"Error calling Gemini API: {str(e)}")
            raise
    
    def _build_classification_prompt(self, user_query: str, user_context: Optional[Dict] = None) -> str:
        """Build a detailed prompt for ticket classification"""
        context_info = ""
        if user_context:
            context_info = f"""
            User Context:
            - Role: {user_context.get('role', 'Unknown')}
            - Department: {user_context.get('department', 'Unknown')}
            - Location: {user_context.get('location', 'Unknown')}
            """
        
        categories_str = ", ".join(self.categories.keys())
        
        prompt = f"""
        You are an AI assistant for POWERGRID's IT helpdesk. Analyze the following user query and provide a structured classification.
        
        User Query: "{user_query}"
        {context_info}
        
        Available Categories: {categories_str}
        
        Please analyze and respond with a JSON object containing:
        {{
            "category": "most appropriate category from the list",
            "subcategory": "more specific subcategory if applicable",
            "priority": "Low/Medium/High/Urgent/Critical based on business impact",
            "confidence": "confidence score between 0.0 and 1.0",
            "reasoning": "brief explanation of your classification decision",
            "suggested_keywords": ["list", "of", "relevant", "keywords", "for", "search"],
            "urgency_level": "immediate/same_day/next_day/scheduled based on user impact",
            "business_impact": "description of how this affects POWERGRID operations",
            "possible_root_causes": ["list", "of", "potential", "causes"]
        }}
        
        Consider these factors:
        1. POWERGRID operates critical power infrastructure
        2. VPN and access issues affect remote work capability
        3. Email issues impact communication
        4. Hardware failures can halt productivity
        5. GLPI and SAP systems are business-critical
        
        Respond only with valid JSON, no additional text.
        """
        
        return prompt.strip()
    
    def _build_solution_prompt(self, 
                             classification: ClassificationResult, 
                             user_query: str,
                             knowledge_articles: List[KnowledgeArticle] = None) -> str:
        """Build prompt for solution generation"""
        
        kb_context = ""
        if knowledge_articles:
            kb_context = "Existing Knowledge Base Articles:\n"
            for article in knowledge_articles[:3]:  # Limit to top 3 relevant articles
                kb_context += f"- {article.title}: {article.description}\n"
                if article.primary_solution:
                    kb_context += f"  Solution: {article.primary_solution.description}\n"
        
        prompt = f"""
        You are a POWERGRID IT support specialist. Generate comprehensive solution recommendations for this classified issue.
        
        User Query: "{user_query}"
        Classification:
        - Category: {classification.category}
        - Subcategory: {classification.subcategory}
        - Priority: {classification.priority}
        - Urgency: {classification.urgency_level}
        
        {kb_context}
        
        Generate 2-3 solution recommendations as a JSON array. Each solution should include:
        {{
            "solutions": [
                {{
                    "title": "clear solution title",
                    "description": "detailed solution description",
                    "steps": ["step 1", "step 2", "step 3"],
                    "solution_type": "manual_steps|automated_script|self_service_link|escalation_required",
                    "confidence": 0.95,
                    "estimated_time": 15,
                    "success_rate": 0.85,
                    "prerequisites": ["any requirements"],
                    "troubleshooting_tips": ["additional tips"],
                    "automated_action": {{
                        "action_type": "if applicable (e.g., password_reset, vpn_reconnect)",
                        "api_endpoint": "/api/actions/password-reset",
                        "parameters": {{"user_id": "placeholder"}},
                        "success_message": "Password reset successfully",
                        "failure_message": "Failed to reset password"
                    }},
                    "escalation_info": {{
                        "escalate_to": "team name if manual intervention needed",
                        "escalation_criteria": "when to escalate"
                    }},
                    "self_service_options": {{
                        "portal_link": "https://selfservice.powergrid.in/...",
                        "video_tutorial": "link to tutorial if available",
                        "documentation": "relevant documentation link"
                    }}
                }}
            ]
        }}
        
        Prioritize solutions in this order:
        1. Self-service options (if user can resolve independently)
        2. Automated actions (if system can resolve automatically)
        3. Manual steps (guided troubleshooting)
        4. Escalation (if expert intervention needed)
        
        Focus on POWERGRID-specific systems and processes. Respond only with valid JSON.
        """
        
        return prompt.strip()
    
    def _build_enhancement_prompt(self, article: KnowledgeArticle) -> str:
        """Build prompt for enhancing knowledge articles"""
        prompt = f"""
        Enhance this POWERGRID knowledge base article with better structure and AI-powered improvements.
        
        Current Article:
        Title: {article.title}
        Category: {article.category}
        Content: {article.content}
        Current Keywords: {article.keywords}
        
        Provide enhancements as JSON:
        {{
            "improved_keywords": ["enhanced", "keyword", "list", "for", "better", "search"],
            "problem_patterns": ["common ways users describe this issue"],
            "symptoms": ["observable symptoms of this problem"],
            "error_codes": ["relevant error codes if applicable"],
            "related_categories": ["other categories this might relate to"],
            "difficulty_level": "Beginner/Intermediate/Advanced",
            "estimated_resolution_time": 30,
            "success_indicators": ["how to know the solution worked"],
            "prevention_tips": ["how to avoid this issue in future"]
        }}
        
        Focus on making the article more discoverable and useful for POWERGRID users.
        Respond only with valid JSON.
        """
        
        return prompt.strip()
    
    def _parse_classification_response(self, response: Dict, original_query: str) -> ClassificationResult:
        """Parse Gemini's classification response"""
        try:
            # Extract the text content from Gemini's response
            content = response['candidates'][0]['content']['parts'][0]['text']
            
            # Parse JSON from the response
            classification_data = json.loads(content)
            
            return ClassificationResult(
                category=classification_data.get('category', 'General'),
                subcategory=classification_data.get('subcategory'),
                priority=classification_data.get('priority', 'Medium'),
                confidence=float(classification_data.get('confidence', 0.5)),
                reasoning=classification_data.get('reasoning', ''),
                suggested_keywords=classification_data.get('suggested_keywords', []),
                urgency_level=classification_data.get('urgency_level', 'next_day'),
                sentiment_score=0.0,  # Will be filled by sentiment analysis
                similar_tickets=[],    # Will be filled by similar ticket finder
                auto_resolution_possible=False,  # Will be determined later
                suggested_assignee=None,  # Will be determined later
                estimated_resolution_time=None  # Will be estimated later
            )
            
        except (KeyError, json.JSONDecodeError, ValueError) as e:
            logger.error(f"Error parsing classification response: {e}")
            return self._fallback_classification(original_query)
    
    def _parse_solution_response(self, response: Dict, classification: ClassificationResult) -> List[SolutionRecommendation]:
        """Parse Gemini's solution response"""
        try:
            content = response['candidates'][0]['content']['parts'][0]['text']
            solution_data = json.loads(content)
            
            recommendations = []
            for solution in solution_data.get('solutions', []):
                # Parse automated action if present
                automated_action = None
                if 'automated_action' in solution and solution['automated_action']:
                    automated_action = solution['automated_action']
                
                recommendation = SolutionRecommendation(
                    solution_id=None,  # Will be assigned if matching KB article found
                    title=solution.get('title', 'Solution'),
                    description=solution.get('description', ''),
                    steps=solution.get('steps', []),
                    solution_type=SolutionType(solution.get('solution_type', 'manual_steps')),
                    confidence=float(solution.get('confidence', 0.5)),
                    estimated_time=int(solution.get('estimated_time', 30)),
                    automated_action=automated_action
                )
                recommendations.append(recommendation)
            
            return recommendations
            
        except (KeyError, json.JSONDecodeError, ValueError) as e:
            logger.error(f"Error parsing solution response: {e}")
            return self._get_fallback_solutions(classification)
    
    def _apply_enhancements(self, article: KnowledgeArticle, response: Dict) -> KnowledgeArticle:
        """Apply AI enhancements to knowledge article"""
        try:
            content = response['candidates'][0]['content']['parts'][0]['text']
            enhancements = json.loads(content)
            
            # Apply enhancements
            article.keywords = enhancements.get('improved_keywords', article.keywords)
            article.problem_patterns = enhancements.get('problem_patterns', [])
            article.symptoms = enhancements.get('symptoms', [])
            article.error_codes = enhancements.get('error_codes', [])
            
            # Update metadata
            article.updated_at = datetime.utcnow()
            article.ai_generated = True
            article.confidence_score = 0.8  # AI enhanced content
            
        except (KeyError, json.JSONDecodeError) as e:
            logger.error(f"Error applying enhancements: {e}")
        
        return article
    
    def _fallback_classification(self, user_query: str) -> ClassificationResult:
        """Fallback classification using keyword matching"""
        # Simple keyword-based classification
        category = "Other"
        subcategory = None
        priority = "Medium"
        confidence = 0.5
        keywords = []
        
        # Check for category matches
        for cat, keywords_list in self.categories.items():
            for keyword in keywords_list:
                if keyword.lower() in user_query.lower():
                    category = cat
                    keywords.append(keyword)
                    
        # Check for priority indicators
        urgent_words = ["urgent", "critical", "emergency", "immediately", "asap"]
        for word in urgent_words:
            if word in user_query.lower():
                priority = "High"
                break
                
        return ClassificationResult(
            category=category,
            subcategory=subcategory,
            priority=priority,
            confidence=confidence,
            reasoning="Fallback classification based on keyword matching",
            suggested_keywords=keywords,
            urgency_level="Medium",
            sentiment_score=0.0,
            similar_tickets=[],
            auto_resolution_possible=False,
            suggested_assignee=None,
            estimated_resolution_time=60  # Default 1 hour
        )
        
        for category, keywords in self.categories.items():
            matches = sum(1 for keyword in keywords if keyword.lower() in query_lower)
            if matches > 0:
                best_category = category
                confidence = min(0.7, 0.3 + (matches * 0.1))
                break
        
        return ClassificationResult(
            category=best_category,
            subcategory=None,
            priority="Medium",
            confidence=confidence,
            reasoning="Fallback classification using keyword matching",
            suggested_keywords=[],
            urgency_level="next_day"
        )
    
    def _get_fallback_solutions(self, classification: ClassificationResult) -> List[SolutionRecommendation]:
        """Provide fallback solutions based on category"""
        fallback_solutions = {
            "Password": [
                SolutionRecommendation(
                    solution_id=None,
                    title="Self-Service Password Reset",
                    description="Use POWERGRID's self-service portal to reset your password",
                    steps=[
                        "Go to https://selfservice.powergrid.in",
                        "Click on 'Forgot Password'",
                        "Enter your employee ID",
                        "Follow the instructions sent to your registered email"
                    ],
                    solution_type=SolutionType.SELF_SERVICE_LINK,
                    confidence=0.8,
                    estimated_time=5
                )
            ],
            "VPN": [
                SolutionRecommendation(
                    solution_id=None,
                    title="VPN Connection Troubleshooting",
                    description="Basic steps to resolve VPN connectivity issues",
                    steps=[
                        "Check your internet connection",
                        "Restart the VPN client",
                        "Try different VPN servers",
                        "Contact IT if issue persists"
                    ],
                    solution_type=SolutionType.MANUAL_STEPS,
                    confidence=0.7,
                    estimated_time=15
                )
            ]
        }
        
        return fallback_solutions.get(classification.category, [
            SolutionRecommendation(
                solution_id=None,
                title="Contact IT Support",
                description="This issue requires manual assistance from IT support team",
                steps=["Contact IT helpdesk at it-support@powergrid.in"],
                solution_type=SolutionType.ESCALATION_REQUIRED,
                confidence=0.5,
                estimated_time=60
            )
        ])


# Global instance
gemini_service = GeminiAIService()
