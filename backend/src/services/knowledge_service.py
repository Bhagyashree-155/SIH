import logging
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
import re
from collections import Counter

from src.models.knowledge_base import (
    KnowledgeArticle, TicketResolution, CommonIssuePattern, 
    Solution, SolutionType, AutomatedAction, ArticleStatus
)
from src.ai.gemini_service import ClassificationResult, SolutionRecommendation, gemini_service
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class KnowledgeSearchResult(BaseModel):
    """Result from knowledge base search"""
    article_id: str
    title: str
    content: str
    relevance_score: float
    matched_keywords: List[str]
    solution_type: str
    estimated_time: int


class KnowledgeFragment(BaseModel):
    """A fragment of knowledge extracted from text"""
    content: str
    keywords: List[str]
    confidence: float
    source: str


class KnowledgeBaseService:
    """
    Intelligent Knowledge Base service that provides AI-powered solution matching,
    learning from resolutions, and continuous improvement.
    """
    
    async def find_solutions(self, 
                            classification: ClassificationResult, 
                            user_query: str,
                            user_context: Optional[Dict] = None) -> List[SolutionRecommendation]:
        """
        Find the best solutions for a classified ticket using multiple approaches:
        1. Direct knowledge base match
        2. AI-generated solutions
        3. Historical resolution patterns
        4. Collaborative filtering based on similar tickets
        5. Contextual relevance based on user's role and department
        """
        try:
            # Step 1: Find relevant knowledge base articles
            kb_articles = await self._find_relevant_articles(classification, user_query)
            
            # Step 2: Get AI-generated solutions with KB context
            ai_solutions = await gemini_service.generate_solution(
                classification, user_query, kb_articles
            )
            
            # Step 3: Enhance with historical data
            enhanced_solutions = await self._enhance_with_history(ai_solutions, classification)
            
            # Step 4: Apply collaborative filtering
            if classification.similar_tickets:
                enhanced_solutions = await self._apply_collaborative_filtering(enhanced_solutions, classification.similar_tickets)
            
            # Step 5: Adjust based on user context
            if user_context:
                enhanced_solutions = self._adjust_for_user_context(enhanced_solutions, user_context)
            
            # Step 6: Rank and return best solutions
            return self._rank_solutions(enhanced_solutions, classification)
            
        except Exception as e:
            logger.error(f"Error finding solutions: {str(e)}")
            return []
    
    async def create_knowledge_article(self, 
                                     title: str,
                                     description: str, 
                                     content: str,
                                     category: str,
                                     solutions: List[Solution],
                                     author_id: str,
                                     author_name: str) -> KnowledgeArticle:
        """Create a new knowledge base article"""
        article = KnowledgeArticle(
            title=title,
            description=description,
            content=content,
            category=category,
            author_id=author_id,
            author_name=author_name,
            solutions=solutions,
            primary_solution=solutions[0] if solutions else None,
            status=ArticleStatus.DRAFT
        )
        
        # Enhance with AI
        enhanced_article = await gemini_service.enhance_knowledge_article(article)
        
        # Save to database
        await enhanced_article.insert()
        
        return enhanced_article
    
    async def record_resolution(self, 
                              ticket_id: str,
                              original_query: str,
                              classification: ClassificationResult,
                              resolution_method: str,
                              resolved_successfully: bool,
                              resolution_time_minutes: int,
                              knowledge_article_id: Optional[str] = None,
                              solution_used: Optional[Solution] = None,
                              user_feedback: Optional[str] = None,
                              user_satisfaction: Optional[int] = None,
                              resolver_id: Optional[str] = None,
                              resolver_name: Optional[str] = None,
                              actual_solution: Optional[str] = None) -> TicketResolution:
        """
        Record how a ticket was resolved to improve future recommendations
        """
        resolution = TicketResolution(
            ticket_id=ticket_id,
            original_query=original_query,
            classified_category=classification.category,
            classified_subcategory=classification.subcategory,
            resolution_method=resolution_method,
            knowledge_article_id=knowledge_article_id,
            solution_used=solution_used,
            resolved_successfully=resolved_successfully,
            resolution_time_minutes=resolution_time_minutes,
            user_satisfaction=user_satisfaction,
            user_feedback=user_feedback,
            resolver_id=resolver_id,
            resolver_name=resolver_name,
            actual_solution=actual_solution
        )
        
        await resolution.insert()
        
        # Update knowledge base statistics
        if knowledge_article_id and resolved_successfully:
            await self._update_article_stats(knowledge_article_id, True, resolution_time_minutes)
        
        # Learn new patterns
        await self._learn_from_resolution(resolution)
        
        return resolution
    
    async def search_articles(self, 
                            query: str, 
                            category: Optional[str] = None,
                            limit: int = 10) -> List[KnowledgeArticle]:
        """Search knowledge base articles using text search and filters"""
        
        # Build search filter
        search_filter = {"status": ArticleStatus.PUBLISHED}
        if category:
            search_filter["category"] = category
        
        # Use MongoDB text search
        articles = await KnowledgeArticle.find(
            {
                "$text": {"$search": query},
                **search_filter
            }
        ).limit(limit).to_list()
        
        # If no results, try keyword matching
        if not articles:
            articles = await self._keyword_search(query, category, limit)
        
        return articles
    
    async def get_trending_issues(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get trending issues based on recent ticket patterns"""
        
        # Aggregate recent resolutions by category
        recent_resolutions = await TicketResolution.find(
            {"created_at": {"$gte": datetime.utcnow().replace(day=datetime.utcnow().day - days)}}
        ).to_list()
        
        # Count by category
        category_counts = Counter(r.classified_category for r in recent_resolutions)
        
        # Calculate success rates
        trending = []
        for category, count in category_counts.most_common(10):
            successful = len([r for r in recent_resolutions 
                            if r.classified_category == category and r.resolved_successfully])
            success_rate = successful / count if count > 0 else 0
            
            trending.append({
                "category": category,
                "ticket_count": count,
                "success_rate": success_rate,
                "avg_resolution_time": self._calculate_avg_time(
                    [r for r in recent_resolutions if r.classified_category == category]
                )
            })
        
        return trending
    
    async def update_solution_feedback(self, 
                                     solution_id: str, 
                                     helpful: bool,
                                     user_feedback: Optional[str] = None):
        """Update solution based on user feedback"""
        
        # Find the knowledge article containing this solution
        article = await KnowledgeArticle.find_one({"solutions.id": solution_id})
        
        if article:
            # Update vote counts
            if helpful:
                article.helpful_votes += 1
            else:
                article.unhelpful_votes += 1
            
            # Record feedback
            if user_feedback:
                # Could implement feedback tracking here
                logger.info(f"User feedback for article {article.id}: {user_feedback}")
            
            await article.save()
    
    async def _find_relevant_articles(self, 
                                    classification: ClassificationResult, 
                                    user_query: str) -> List[KnowledgeArticle]:
        """Find relevant knowledge base articles for a classified query"""
        
        # First, try category-based search
        articles = await KnowledgeArticle.find({
            "category": classification.category,
            "status": ArticleStatus.PUBLISHED
        }).limit(5).to_list()
        
        # If not enough articles, search by keywords
        if len(articles) < 3:
            keyword_search = await self.search_articles(user_query, classification.category, 5)
            articles.extend(keyword_search)
        
        # Remove duplicates and limit
        seen_ids = set()
        unique_articles = []
        for article in articles:
            if str(article.id) not in seen_ids:
                unique_articles.append(article)
                seen_ids.add(str(article.id))
                if len(unique_articles) >= 5:
                    break
        
        return unique_articles
    
    async def _enhance_with_history(self, 
                                   solutions: List[SolutionRecommendation],
                                   classification: ClassificationResult) -> List[SolutionRecommendation]:
        """Enhance AI solutions with historical success data"""
        
        # Get historical resolution data for this category
        historical_resolutions = await TicketResolution.find({
            "classified_category": classification.category,
            "resolved_successfully": True
        }).limit(100).to_list()
        
        # Analyze successful resolution patterns
        successful_methods = Counter(r.resolution_method for r in historical_resolutions)
        avg_times = {}
        
        for method in successful_methods:
            method_resolutions = [r for r in historical_resolutions if r.resolution_method == method]
            avg_times[method] = sum(r.resolution_time_minutes for r in method_resolutions) / len(method_resolutions)
        
        # Adjust solution confidence based on historical data
        for solution in solutions:
            method_key = solution.solution_type.value
            if method_key in successful_methods:
                # Boost confidence if this method has been successful before
                historical_success_rate = successful_methods[method_key] / len(historical_resolutions)
                solution.confidence = min(0.95, solution.confidence * (1 + historical_success_rate))
                
                # Update estimated time based on historical data
                if method_key in avg_times:
                    solution.estimated_time = int((solution.estimated_time + avg_times[method_key]) / 2)
        
        return solutions
    
    async def _apply_collaborative_filtering(self, solutions: List[SolutionRecommendation], similar_tickets: List[str]) -> List[SolutionRecommendation]:
        """Apply collaborative filtering based on similar tickets"""
        try:
            # Find resolutions for similar tickets
            similar_resolutions = []
            for ticket_id in similar_tickets:
                resolution = await TicketResolution.find_one({"ticket_id": ticket_id})
                if resolution and resolution.resolved_successfully:
                    similar_resolutions.append(resolution)
            
            if not similar_resolutions:
                return solutions
            
            # Boost confidence for solutions that worked for similar tickets
            for solution in solutions:
                for resolution in similar_resolutions:
                    if resolution.solution_used and solution.title.lower() in resolution.solution_used.title.lower():
                        solution.confidence = min(1.0, solution.confidence + 0.15)
            
            return solutions
        except Exception as e:
            logger.error(f"Error applying collaborative filtering: {str(e)}")
            return solutions
            
    def _adjust_for_user_context(self, solutions: List[SolutionRecommendation], user_context: Dict) -> List[SolutionRecommendation]:
        """Adjust solutions based on user context (role, department, etc.)"""
        try:
            user_role = user_context.get("role", "").lower()
            user_department = user_context.get("department", "").lower()
            user_location = user_context.get("location", "").lower()
            
            # Define role-specific adjustments
            technical_roles = ["it", "developer", "engineer", "technical", "admin"]
            non_technical_roles = ["manager", "executive", "hr", "finance", "sales"]
            
            for solution in solutions:
                # Adjust for technical vs non-technical users
                if any(role in user_role for role in technical_roles):
                    # Technical users might prefer more detailed solutions
                    if "technical" in solution.title.lower() or "advanced" in solution.title.lower():
                        solution.confidence = min(1.0, solution.confidence + 0.1)
                elif any(role in user_role for role in non_technical_roles):
                    # Non-technical users might prefer simpler solutions
                    if "simple" in solution.title.lower() or "basic" in solution.title.lower():
                        solution.confidence = min(1.0, solution.confidence + 0.1)
                
                # Adjust for department-specific solutions
                if user_department in solution.title.lower() or user_department in solution.description.lower():
                    solution.confidence = min(1.0, solution.confidence + 0.1)
                    
                # Adjust for location-specific solutions
                if user_location in solution.title.lower() or user_location in solution.description.lower():
                    solution.confidence = min(1.0, solution.confidence + 0.1)
            
            return solutions
        except Exception as e:
            logger.error(f"Error adjusting for user context: {str(e)}")
            return solutions
    
    def _rank_solutions(self, 
                       solutions: List[SolutionRecommendation],
                       classification: ClassificationResult) -> List[SolutionRecommendation]:
        """Rank solutions by relevance and success probability"""
        
        def solution_score(solution: SolutionRecommendation) -> float:
            score = solution.confidence
            
            # Boost self-service solutions
            if solution.solution_type == SolutionType.SELF_SERVICE_LINK:
                score += 0.1
            
            # Boost automated solutions
            elif solution.solution_type == SolutionType.AUTOMATED_SCRIPT:
                score += 0.05
            
            # Penalize escalation unless high priority
            elif solution.solution_type == SolutionType.ESCALATION_REQUIRED:
                if classification.priority not in ["High", "Urgent", "Critical"]:
                    score -= 0.2
            
            # Factor in estimated time (prefer quicker solutions)
            time_factor = max(0, 1 - (solution.estimated_time / 120))  # 2 hours max
            score += time_factor * 0.1
            
            return score
        
        # Sort by score (highest first)
        return sorted(solutions, key=solution_score, reverse=True)
    
    async def _update_article_stats(self, 
                                   article_id: str, 
                                   successful: bool, 
                                   resolution_time: int):
        """Update knowledge article success statistics"""
        
        article = await KnowledgeArticle.get(article_id)
        if article:
            article.total_attempts += 1
            if successful:
                article.success_resolutions += 1
            
            # Update primary solution stats if it exists
            if article.primary_solution:
                article.primary_solution.success_rate = (
                    article.success_resolutions / article.total_attempts
                )
            
            await article.save()
    
    async def _learn_from_resolution(self, resolution: TicketResolution):
        """Learn from successful ticket resolutions to improve knowledge base"""
        try:
            if not resolution.resolved_successfully or not resolution.actual_solution:
                return
                
            # Check if we already have a knowledge article for this category/subcategory
            existing_article = await KnowledgeArticle.find_one({
                "category": resolution.classified_category,
                "subcategory": resolution.classified_subcategory
            })
            
            if existing_article:
                # Update existing article with new solution if it's significantly different
                if not self._solution_exists(existing_article, resolution.actual_solution):
                    new_solution = Solution(
                        title=f"Solution from ticket {resolution.ticket_id}",
                        description=resolution.actual_solution,
                        steps=[resolution.actual_solution],  # Simple conversion for now
                        solution_type=SolutionType.MANUAL,
                        estimated_time=resolution.resolution_time_minutes
                    )
                    
                    existing_article.solutions.append(new_solution)
                    await existing_article.save()
                    
                    logger.info(f"Added new solution to existing article {existing_article.id}")
            else:
                # Create new knowledge article from this resolution
                await self._create_article_from_resolution(resolution)
                
            # Check if we can identify a common issue pattern
            await self._identify_common_patterns(resolution)
                
        except Exception as e:
            logger.error(f"Error learning from resolution: {str(e)}")
            
    async def _create_article_from_resolution(self, resolution: TicketResolution):
        """Create a new knowledge article from a successful resolution"""
        try:
            # Create a solution from the resolution
            solution = Solution(
                title=f"Solution for {resolution.classified_category} issue",
                description=resolution.actual_solution,
                steps=[resolution.actual_solution],  # Simple conversion for now
                solution_type=SolutionType.MANUAL,
                estimated_time=resolution.resolution_time_minutes
            )
            
            # Create the article
            article = KnowledgeArticle(
                title=f"How to resolve {resolution.classified_category} issues",
                description=resolution.original_query,
                content=resolution.actual_solution,
                category=resolution.classified_category,
                subcategory=resolution.classified_subcategory,
                author_id=resolution.resolver_id or "system",
                author_name=resolution.resolver_name or "System",
                solutions=[solution],
                primary_solution=solution,
                status=ArticleStatus.DRAFT,  # Set as draft for review
                source_ticket_id=resolution.ticket_id
            )
            
            # Save the article
            await article.insert()
            
            logger.info(f"Created new knowledge article from resolution: {article.id}")
            
            return article
            
        except Exception as e:
            logger.error(f"Error creating article from resolution: {str(e)}")
            
    async def _identify_common_patterns(self, resolution: TicketResolution):
        """Identify common issue patterns from resolutions"""
        try:
            # Find similar resolutions
            similar_resolutions = await TicketResolution.find({
                "classified_category": resolution.classified_category,
                "resolved_successfully": True
            }).limit(20).to_list()
            
            if len(similar_resolutions) < 5:  # Need at least 5 samples to identify a pattern
                return
                
            # Extract common keywords from original queries
            all_words = []
            for res in similar_resolutions:
                if res.original_query:
                    words = re.findall(r'\w+', res.original_query.lower())
                    all_words.extend(words)
                    
            # Count word frequencies
            word_counts = Counter(all_words)
            common_words = [word for word, count in word_counts.most_common(10) if count >= 3]
            
            if not common_words:
                return
                
            # Check if we already have this pattern
            pattern_text = " ".join(common_words)
            existing_pattern = await CommonIssuePattern.find_one({"pattern": {"$regex": pattern_text, "$options": "i"}})
            
            if not existing_pattern:
                # Create new pattern
                pattern = CommonIssuePattern(
                    category=resolution.classified_category,
                    subcategory=resolution.classified_subcategory,
                    pattern=pattern_text,
                    frequency=len(similar_resolutions),
                    avg_resolution_time=self._calculate_avg_time(similar_resolutions),
                    common_solutions=[res.actual_solution for res in similar_resolutions if res.actual_solution][:3]
                )
                
                await pattern.insert()
                logger.info(f"Identified new common issue pattern: {pattern_text}")
                
        except Exception as e:
            logger.error(f"Error identifying common patterns: {str(e)}")
            
    def _solution_exists(self, article: KnowledgeArticle, solution_text: str) -> bool:
        """Check if a similar solution already exists in the article"""
        for existing_solution in article.solutions:
            # Simple text similarity check
            if existing_solution.description and solution_text:
                similarity = self._calculate_text_similarity(existing_solution.description, solution_text)
                if similarity > 0.7:  # 70% similarity threshold
                    return True
        return False
        
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate simple text similarity between two strings"""
        # Convert to sets of words for simple Jaccard similarity
        words1 = set(re.findall(r'\w+', text1.lower()))
        words2 = set(re.findall(r'\w+', text2.lower()))
        
        if not words1 or not words2:
            return 0.0
            
        # Jaccard similarity: intersection / union
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
        
    def _calculate_avg_time(self, resolutions: List[TicketResolution]) -> int:
        """Calculate average resolution time from a list of resolutions"""
        times = [res.resolution_time_minutes for res in resolutions if res.resolution_time_minutes]
        if not times:
            return 30  # Default to 30 minutes if no data
        return int(sum(times) / len(times))
    
    async def _keyword_search(self, 
                            query: str, 
                            category: Optional[str] = None,
                            limit: int = 10) -> List[KnowledgeArticle]:
        """Fallback keyword-based search"""
        
        # Extract keywords from query
        keywords = re.findall(r'\b\w+\b', query.lower())
        
        # Build search filter
        search_filter = {"status": ArticleStatus.PUBLISHED}
        if category:
            search_filter["category"] = category
        
        # Search in keywords and tags
        search_filter["$or"] = [
            {"keywords": {"$in": keywords}},
            {"tags": {"$in": keywords}},
            {"problem_patterns": {"$regex": "|".join(keywords), "$options": "i"}}
        ]
        
        return await KnowledgeArticle.find(search_filter).limit(limit).to_list()
    
    async def search_knowledge_base(self, query: str, limit: int = 5) -> List[KnowledgeSearchResult]:
        """Search knowledge base for relevant information using semantic search
        
        This method performs a semantic search on the knowledge base using vector embeddings
        to find the most relevant knowledge fragments for the given query.
        
        Args:
            query: The search query
            limit: Maximum number of results to return
            
        Returns:
            List of KnowledgeSearchResult objects sorted by relevance
        """
        try:
            results = []
            
            # Generate embedding for the query
            query_embedding = await self._get_query_embedding(query)
            if not query_embedding:
                # Fall back to keyword search if embedding fails
                logger.warning("Falling back to keyword search for knowledge base query")
                return await self._keyword_search_knowledge(query, limit)
                
            # Find all knowledge fragments
            all_fragments = await KnowledgeFragment.find().to_list()
            
            # Calculate similarity scores
            scored_fragments = []
            for fragment in all_fragments:
                if fragment.embedding:
                    similarity = self._calculate_vector_similarity(query_embedding, fragment.embedding)
                    scored_fragments.append((fragment, similarity))
            
            # Sort by similarity score (descending)
            scored_fragments.sort(key=lambda x: x[1], reverse=True)
            
            # Take top results
            for fragment, score in scored_fragments[:limit]:
                # Find the source article
                source_article = await KnowledgeArticle.find_one({"fragments.id": fragment.id})
                
                result = KnowledgeSearchResult(
                    fragment=fragment,
                    score=score,
                    article_id=source_article.id if source_article else None,
                    article_title=source_article.title if source_article else None
                )
                results.append(result)
                
            return results
            
        except Exception as e:
            logger.error(f"Error searching knowledge base: {str(e)}")
            return []
            
    async def _get_query_embedding(self, query: str) -> List[float]:
        """Generate embedding vector for a search query"""
        try:
            # Call embedding API with single query
            embeddings = await self._call_embedding_api([query])
            if embeddings and len(embeddings) > 0:
                return embeddings[0]
            return None
        except Exception as e:
            logger.error(f"Error generating query embedding: {str(e)}")
            return None
            
    def _calculate_vector_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        try:
            if len(vec1) != len(vec2):
                return 0.0
                
            # Compute dot product
            dot_product = sum(a * b for a, b in zip(vec1, vec2))
            
            # Compute magnitudes
            mag1 = math.sqrt(sum(a * a for a in vec1))
            mag2 = math.sqrt(sum(b * b for b in vec2))
            
            # Compute cosine similarity
            if mag1 > 0 and mag2 > 0:
                return dot_product / (mag1 * mag2)
            return 0.0
            
        except Exception as e:
            logger.error(f"Error calculating vector similarity: {str(e)}")
            return 0.0
            
    async def _keyword_search_knowledge(self, query: str, limit: int = 5) -> List[KnowledgeSearchResult]:
        """Fallback keyword-based search for knowledge base"""
        try:
            results = []
            
            # Extract keywords from query
            keywords = re.findall(r'\b\w+\b', query.lower())
            if not keywords:
                return []
                
            # Find fragments containing keywords
            search_filter = {
                "$text": {"$search": " ".join(keywords)}
            }
            
            fragments = await KnowledgeFragment.find(search_filter).limit(limit*2).to_list()
            
            # Score fragments by keyword matches
            scored_fragments = []
            for fragment in fragments:
                # Count keyword occurrences
                text_lower = fragment.text.lower()
                matches = sum(1 for keyword in keywords if keyword in text_lower)
                score = matches / len(keywords) if keywords else 0
                
                scored_fragments.append((fragment, score))
                
            # Sort by score
            scored_fragments.sort(key=lambda x: x[1], reverse=True)
            
            # Take top results
            for fragment, score in scored_fragments[:limit]:
                # Find the source article
                source_article = await KnowledgeArticle.find_one({"fragments.id": fragment.id})
                
                result = KnowledgeSearchResult(
                    fragment=fragment,
                    score=score,
                    article_id=source_article.id if source_article else None,
                    article_title=source_article.title if source_article else None
                )
                results.append(result)
                
            return results
            
        except Exception as e:
            logger.error(f"Error performing keyword search: {str(e)}")
            return []
            
    async def extract_knowledge(self, text: str) -> List[KnowledgeFragment]:
        """Extract knowledge fragments from text
        
        This method analyzes text to identify key knowledge fragments that can be
        added to the knowledge base. It uses NLP techniques to extract:
        1. Key concepts and definitions
        2. Procedural steps
        3. Troubleshooting information
        4. Technical specifications
        
        Args:
            text: The text to extract knowledge from
            
        Returns:
            List of KnowledgeFragment objects
        """
        try:
            fragments = []
            
            # Split text into sentences
            sentences = re.split(r'(?<=[.!?])\s+', text)
            
            # Process each sentence to identify knowledge fragments
            current_fragment = None
            for sentence in sentences:
                # Skip very short sentences
                if len(sentence.strip()) < 10:
                    continue
                    
                # Check if this is a definition (contains "is", "means", "refers to")
                if re.search(r'\b(is|are|means|refers to|defined as)\b', sentence, re.IGNORECASE):
                    fragments.append(KnowledgeFragment(
                        text=sentence,
                        fragment_type=FragmentType.DEFINITION,
                        confidence=0.8
                    ))
                
                # Check if this is a procedural step (starts with action verb or contains step indicator)
                elif re.search(r'^(\d+\.\s*|first|second|third|next|then|finally)\s*\w+', sentence, re.IGNORECASE) or \
                     re.search(r'\b(click|select|choose|enter|type|go to|navigate|open|close|run|execute)\b', 
                              sentence, re.IGNORECASE):
                    if current_fragment and current_fragment.fragment_type == FragmentType.PROCEDURE:
                        # Continue the current procedure
                        current_fragment.text += " " + sentence
                    else:
                        # Start a new procedure
                        current_fragment = KnowledgeFragment(
                            text=sentence,
                            fragment_type=FragmentType.PROCEDURE,
                            confidence=0.7
                        )
                        fragments.append(current_fragment)
                
                # Check if this is troubleshooting info (contains problem indicators)
                elif re.search(r'\b(error|issue|problem|fail|bug|exception|warning|troubleshoot)\b', 
                              sentence, re.IGNORECASE):
                    fragments.append(KnowledgeFragment(
                        text=sentence,
                        fragment_type=FragmentType.TROUBLESHOOTING,
                        confidence=0.75
                    ))
                    
                # Check if this contains technical specifications
                elif re.search(r'\b(specification|config|parameter|setting|version|requirement)\b', 
                              sentence, re.IGNORECASE):
                    fragments.append(KnowledgeFragment(
                        text=sentence,
                        fragment_type=FragmentType.TECHNICAL_SPEC,
                        confidence=0.6
                    ))
                else:
                    # General knowledge
                    fragments.append(KnowledgeFragment(
                        text=sentence,
                        fragment_type=FragmentType.GENERAL,
                        confidence=0.5
                    ))
            
            # Generate embeddings for the fragments
            await self._generate_embeddings(fragments)
            
            return fragments
            
        except Exception as e:
            logger.error(f"Error extracting knowledge: {str(e)}")
            return []
            
    async def _generate_embeddings(self, fragments: List[KnowledgeFragment]):
        """Generate embeddings for knowledge fragments
        
        This method creates vector embeddings for knowledge fragments to enable
        semantic search and similarity matching.
        
        Args:
            fragments: List of KnowledgeFragment objects to generate embeddings for
        """
        try:
            if not fragments:
                return
                
            # Process fragments in batches to avoid overloading the embedding API
            batch_size = 10
            for i in range(0, len(fragments), batch_size):
                batch = fragments[i:i+batch_size]
                texts = [fragment.text for fragment in batch]
                
                # Call embedding API
                embeddings = await self._call_embedding_api(texts)
                
                # Assign embeddings to fragments
                if embeddings and len(embeddings) == len(batch):
                    for j, embedding in enumerate(embeddings):
                        batch[j].embedding = embedding
                        
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            
    async def _call_embedding_api(self, texts: List[str]) -> List[List[float]]:
        """Call the embedding API to generate vector embeddings
        
        Args:
            texts: List of text strings to generate embeddings for
            
        Returns:
            List of embedding vectors (or None if API call fails)
        """
        try:
            # Use the AI service to generate embeddings
            # This is a placeholder - in a real implementation, you would call an
            # embedding API like OpenAI's text-embedding-ada-002 or a local model
            
            # For now, we'll generate random embeddings for demonstration
            # In production, replace this with actual API calls
            import random
            import math
            
            embeddings = []
            for _ in texts:
                # Generate a 384-dimensional embedding vector (typical size)
                random_embedding = [random.uniform(-1, 1) for _ in range(384)]
                # Normalize the vector
                magnitude = math.sqrt(sum(x*x for x in random_embedding))
                normalized = [x/magnitude for x in random_embedding]
                embeddings.append(normalized)
                
            return embeddings
            
        except Exception as e:
            logger.error(f"Error calling embedding API: {str(e)}")
            return None


# Global instance
knowledge_service = KnowledgeBaseService()
