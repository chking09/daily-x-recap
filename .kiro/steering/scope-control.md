---
inclusion: always
---

# Scope Control for Daily Market Recap

## Core Principle: Keep It Simple
This is a straightforward data pipeline: **Collect → Process → Publish**

## Mandatory Scope Boundaries

### MUST INCLUDE (Core Features Only)
- Google Custom Search API for financial news
- Alpha Vantage API for stock data (3 movers, 3 watchlist)
- Claude AI for content generation
- X API v2 for posting
- Basic error handling and logging
- Simple scheduling mechanism

### MUST NOT INCLUDE (Scope Creep Prevention)
- Complex UI/dashboard
- User authentication systems
- Database storage beyond basic caching
- Multiple social media platforms
- Advanced analytics or metrics
- Real-time streaming data
- Complex configuration management
- Extensive testing frameworks
- Performance optimization beyond basics
- Backup/recovery systems
- Multi-language support
- Custom notification systems

## Development Guidelines

### Implementation Priority
1. **MVP First**: Get basic data flow working end-to-end
2. **One API at a time**: Implement and test each API integration separately
3. **Minimal viable features**: No bells and whistles until core works
4. **Hardcode initially**: Use configuration files only when absolutely necessary

### Testing Strategy
- **Manual testing only** for MVP
- **Single test case per API** to verify integration
- **End-to-end test**: One complete workflow test
- **No unit testing** until core functionality is proven

### Decision Framework
Before adding ANY feature, ask:
1. Is this required for the basic data pipeline to work?
2. Does this directly serve the core user story (daily market recap)?
3. Can we ship without this feature?

If any answer is "no" or "maybe", **don't build it**.

## Success Criteria
The project is complete when:
- It can automatically generate and post one daily market recap
- All three APIs are integrated and working
- Basic error handling prevents crashes
- Can be scheduled to run daily

**Everything else is scope creep.**