import requests
import json
import time
import os
import sys

# Backend configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
USERNAME = os.getenv("DEMO_USERNAME")
PASSWORD = os.getenv("DEMO_PASSWORD")

if not USERNAME or not PASSWORD:
    print("❌ Error: DEMO_USERNAME and DEMO_PASSWORD environment variables must be set")
    print("Usage: DEMO_USERNAME=myuser DEMO_PASSWORD=mypass python create_demo_notes.py")
    sys.exit(1)

# Login and get token
def get_auth_token():
    login_data = {
        "username": USERNAME,
        "password": PASSWORD
    }
    response = requests.post(
        f"{BACKEND_URL}/auth/token",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        raise Exception(f"Login failed: {response.text}")

# Create a note
def create_note(token, title, content, note_type="note"):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    note_data = {
        "title": title,
        "content": content,
        "type": note_type
    }
    response = requests.post(
        f"{BACKEND_URL}/notes/",
        json=note_data,
        headers=headers
    )
    if response.status_code == 200:
        print(f"✅ Created note: {title}")
        return response.json()
    else:
        print(f"❌ Failed to create note {title}: {response.text}")
        return None

# Demo business notes
business_notes = [
    {
        "title": "Strategic Business Planning 2025",
        "content": """# Strategic Business Planning for 2025

## Key Objectives
- Expand market share by 25%
- Launch 3 new product lines
- Improve customer satisfaction to 95%
- Achieve $10M annual revenue

## Market Analysis
Our target market shows strong growth potential in the technology sector. Key competitors include TechCorp, Innovation Inc, and StartupXYZ. We need to focus on our unique value proposition: AI-powered solutions with exceptional customer service.

## Strategic Initiatives
1. **Digital Transformation**: Implement cloud-based infrastructure
2. **Product Innovation**: Develop AI-enhanced features
3. **Market Expansion**: Enter European and Asian markets
4. **Team Growth**: Hire 50 new employees across engineering and sales

## Success Metrics
- Revenue growth: 40% YoY
- Customer acquisition cost: <$500
- Customer lifetime value: >$5000
- Employee satisfaction: >85%""",
        "type": "important"
    },
    {
        "title": "AI Product Development Roadmap",
        "content": """# AI Product Development Roadmap

## Phase 1: Foundation (Q1 2025)
- Machine learning infrastructure setup
- Data pipeline architecture
- Core AI model development
- Initial prototype testing

## Phase 2: Enhancement (Q2 2025)
- Natural language processing integration
- Computer vision capabilities
- Real-time analytics dashboard
- Beta testing with key customers

## Phase 3: Scale (Q3-Q4 2025)
- Multi-language support
- Advanced predictive analytics
- Enterprise-grade security
- Full market launch

## Technical Requirements
- Python, TensorFlow, PyTorch
- Cloud computing (AWS/Azure)
- Microservices architecture
- API-first design

## Budget Allocation
- R&D: $2M
- Infrastructure: $800K
- Testing & QA: $500K
- Marketing: $1.2M""",
        "type": "concept"
    },
    {
        "title": "Customer Success Strategy",
        "content": """# Customer Success Strategy

## Customer Journey Mapping
Understanding our customers' needs at every touchpoint is crucial for success. We've identified 5 key stages:

1. **Awareness**: How customers discover our products
2. **Evaluation**: Decision-making process and criteria
3. **Onboarding**: First 90 days experience
4. **Growth**: Expansion and upselling opportunities
5. **Advocacy**: Turning customers into promoters

## Key Performance Indicators
- Net Promoter Score (NPS): Target >50
- Customer Retention Rate: >95%
- Time to Value: <30 days
- Support Response Time: <2 hours

## Customer Segmentation
- **Enterprise**: Large corporations with 1000+ employees
- **Mid-Market**: Companies with 100-1000 employees  
- **SMB**: Small businesses with 10-100 employees
- **Startups**: Early-stage companies seeking growth

## Success Programs
- Dedicated Customer Success Managers
- Quarterly Business Reviews
- Training and certification programs
- Community forums and knowledge base""",
        "type": "concept"
    },
    {
        "title": "Marketing Campaign Q1 2025",
        "content": """# Marketing Campaign - Q1 2025

## Campaign Theme: "Innovate. Automate. Accelerate."

## Target Audience
- Tech executives (CTO, VP Engineering)
- Product managers
- Business analysts
- Innovation leaders

## Channel Strategy
1. **Digital Marketing**
   - LinkedIn targeted ads
   - Google Ads for AI-related keywords
   - Content marketing via blog
   - Webinar series

2. **Event Marketing**
   - Tech conferences (CES, SXSW)
   - Industry trade shows
   - Hosted networking events
   - Speaking engagements

3. **Content Marketing**
   - Weekly blog posts
   - Monthly whitepapers
   - Quarterly case studies
   - Video testimonials

## Budget: $500K
- Digital ads: 40%
- Events: 30%
- Content creation: 20%
- Tools and platforms: 10%

## Success Metrics
- 10,000 new leads
- 500 demo requests
- 50 new enterprise customers
- 25% brand awareness increase""",
        "type": "topic"
    },
    {
        "title": "Financial Projections 2025",
        "content": """# Financial Projections 2025

## Revenue Forecast
**Total Projected Revenue: $10.5M**

### By Quarter:
- Q1: $2.0M (Existing customer base + new sales)
- Q2: $2.5M (Product launch impact)
- Q3: $3.0M (Market expansion)
- Q4: $3.0M (Holiday season boost)

### By Product Line:
- Core AI Platform: $6.5M (62%)
- Professional Services: $2.5M (24%)
- Training & Certification: $1.0M (9%)
- Hardware Solutions: $0.5M (5%)

## Expense Budget
**Total Operating Expenses: $7.8M**

- **Personnel**: $4.5M (58%)
  - Engineering: $2.5M
  - Sales & Marketing: $1.2M
  - Operations: $0.8M

- **Technology**: $1.8M (23%)
  - Cloud infrastructure: $1.2M
  - Software licenses: $0.4M
  - Hardware: $0.2M

- **Marketing**: $1.0M (13%)
- **Facilities**: $0.3M (4%)
- **Other**: $0.2M (2%)

## Profitability Analysis
- Gross Margin: 75%
- Operating Margin: 26%
- Net Profit: $2.7M""",
        "type": "important"
    },
    {
        "title": "Competitive Analysis Report",
        "content": """# Competitive Analysis Report

## Direct Competitors

### TechCorp Solutions
**Strengths:**
- Market leader with 35% market share
- Strong enterprise relationships
- Robust product portfolio
- Excellent brand recognition

**Weaknesses:**
- Legacy technology stack
- Slow innovation cycle
- Higher pricing
- Poor customer service ratings

**Market Position:** Premium leader
**Revenue:** ~$50M annually

### Innovation Inc
**Strengths:**
- Cutting-edge AI technology
- Strong R&D team
- Venture capital backing
- Agile development

**Weaknesses:**
- Limited market presence
- Unproven at scale
- High customer churn
- Pricing volatility

**Market Position:** Disruptive innovator
**Revenue:** ~$8M annually

### StartupXYZ
**Strengths:**
- Low-cost solution
- Simple user interface
- Fast implementation
- Good for SMBs

**Weaknesses:**
- Limited features
- Scalability issues
- Basic security
- No enterprise support

**Market Position:** Budget alternative
**Revenue:** ~$3M annually

## Our Competitive Advantage
1. **AI-First Architecture**: Built for modern requirements
2. **Customer Success Focus**: Dedicated support team
3. **Flexible Pricing**: Multiple tiers for all business sizes
4. **Rapid Innovation**: Monthly feature releases
5. **Security & Compliance**: Enterprise-grade protection""",
        "type": "concept"
    },
    {
        "title": "Team Structure & Hiring Plan",
        "content": """# Team Structure & Hiring Plan 2025

## Current Team: 25 employees

### Engineering Team (12)
- **VP Engineering**: Sarah Chen
- **Senior Engineers**: 4 developers
- **Frontend Developers**: 3 specialists
- **Backend Developers**: 2 specialists
- **DevOps Engineer**: 1 infrastructure expert
- **QA Engineers**: 2 testing specialists

### Sales & Marketing (8)
- **VP Sales**: Mike Rodriguez
- **Sales Reps**: 4 account executives
- **Marketing Manager**: Lisa Wang
- **Content Creator**: 1 specialist
- **Customer Success**: 2 managers

### Operations (5)
- **CEO**: Alex Thompson
- **CFO**: Jennifer Park
- **HR Manager**: David Kim
- **Office Manager**: 1 coordinator
- **Legal Counsel**: External consultant

## 2025 Hiring Plan: 50 new hires

### Q1 Priorities (15 hires)
- Senior AI Engineers (3)
- Sales Development Reps (4)
- Customer Success Managers (3)
- Product Managers (2)
- Marketing Specialists (3)

### Q2 Priorities (15 hires)
- Full-stack Developers (5)
- Technical Writers (2)
- Sales Engineers (3)
- Data Scientists (3)
- Security Engineers (2)

### Q3-Q4 Priorities (20 hires)
- International sales team (8)
- Engineering managers (3)
- Support specialists (4)
- Business analysts (3)
- Administrative staff (2)

## Budget: $3.2M for new hires
## Target: Build world-class team for rapid scaling""",
        "type": "topic"
    },
    {
        "title": "Technology Infrastructure Plan",
        "content": """# Technology Infrastructure Plan

## Current Architecture
- **Frontend**: React.js with TypeScript
- **Backend**: Python FastAPI microservices
- **Database**: PostgreSQL with Redis caching
- **AI/ML**: TensorFlow, PyTorch, Hugging Face
- **Cloud**: AWS with multi-region deployment
- **Monitoring**: DataDog, Sentry, CloudWatch

## 2025 Infrastructure Goals

### Scalability Improvements
- **Auto-scaling**: Handle 10x traffic spikes
- **Load Balancing**: Multi-region deployment
- **Database Optimization**: Read replicas and sharding
- **CDN**: Global content delivery network

### Security Enhancements
- **Zero Trust Architecture**: Identity-based security
- **Encryption**: End-to-end data protection
- **Compliance**: SOC 2, GDPR, HIPAA ready
- **Threat Detection**: AI-powered security monitoring

### Performance Targets
- **API Response Time**: <100ms average
- **Uptime**: 99.99% availability
- **Page Load Speed**: <2 seconds
- **Mobile Performance**: Lighthouse score >90

## Technology Investments
- **Kubernetes**: Container orchestration
- **Serverless**: Lambda functions for scaling
- **Machine Learning**: MLOps pipeline
- **Analytics**: Real-time data processing

## Budget: $1.8M
- Infrastructure: $1.2M
- Security tools: $300K
- Monitoring & analytics: $200K
- Development tools: $100K""",
        "type": "concept"
    },
    {
        "title": "Partnership Strategy",
        "content": """# Partnership Strategy 2025

## Strategic Partnership Categories

### Technology Partners
**Integration Partners:**
- Salesforce (CRM integration)
- Microsoft (Office 365 connectivity)
- Slack (Communication platform)
- Zapier (Automation workflows)

**Cloud Partners:**
- AWS (Primary cloud provider)
- Google Cloud (AI/ML services)
- Microsoft Azure (Enterprise customers)

### Channel Partners
**Reseller Network:**
- Regional system integrators
- Consulting firms
- Technology distributors
- Industry specialists

**Solution Partners:**
- Implementation consultants
- Training providers
- Custom development agencies
- Support specialists

### Strategic Alliances
**Industry Leaders:**
- Joint go-to-market initiatives
- Co-marketing opportunities
- Shared technology development
- Customer referral programs

## Partnership Goals
- **Revenue Target**: $2M through partners (20% of total)
- **Partner Count**: 25 active partners
- **Certified Partners**: 15 technical certifications
- **Joint Customers**: 100 shared accounts

## Partner Program Benefits
- **Training & Certification**: Free technical training
- **Marketing Support**: Co-branded materials
- **Sales Support**: Joint sales calls
- **Technical Support**: Dedicated partner portal

## Success Metrics
- Partner-driven leads: 500/month
- Partner revenue: $2M annually
- Partner satisfaction: >90%
- Time to first deal: <60 days""",
        "type": "topic"
    },
    {
        "title": "Product Innovation Labs",
        "content": """# Product Innovation Labs Initiative

## Mission Statement
Establish dedicated innovation labs to explore cutting-edge technologies and develop next-generation products that will position us as industry leaders.

## Lab Focus Areas

### AI Research Lab
**Objectives:**
- Advanced machine learning algorithms
- Natural language understanding
- Computer vision applications
- Predictive analytics models

**Team:** 8 researchers and engineers
**Budget:** $800K annually

### User Experience Lab
**Objectives:**
- Human-computer interaction research
- Accessibility improvements
- Voice and gesture interfaces
- Augmented reality experiences

**Team:** 6 designers and developers  
**Budget:** $400K annually

### Future Technology Lab
**Objectives:**
- Quantum computing applications
- Blockchain integration
- IoT connectivity
- Edge computing solutions

**Team:** 5 specialists
**Budget:** $600K annually

## Innovation Process
1. **Ideation**: Quarterly brainstorming sessions
2. **Prototyping**: 30-day proof of concepts
3. **Validation**: Customer feedback and testing
4. **Development**: 6-month MVP creation
5. **Launch**: Market introduction and scaling

## Expected Outcomes
- 12 new patents filed
- 5 breakthrough innovations
- 3 new product lines
- Industry recognition and awards

## Key Projects 2025
- **AI-Powered Personal Assistant**
- **Predictive Business Analytics**
- **Automated Code Generation**
- **Real-time Collaboration Platform**

Total Innovation Investment: $1.8M""",
        "type": "important"
    }
]

def main():
    print("🧠 Creating SecondBrain Demo Notes")
    print("=" * 60)
    
    # Get authentication token
    try:
        token = get_auth_token()
        print(f"✅ Successfully authenticated as {USERNAME}")
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        return
    
    # Create all demo notes
    created_notes = []
    for note in business_notes:
        result = create_note(token, note["title"], note["content"], note["type"])
        if result:
            created_notes.append(result)
        time.sleep(0.5)  # Small delay to avoid rate limiting
    
    print(f"\n🎉 Successfully created {len(created_notes)} demo notes!")
    print("\nDemo notes include:")
    for note in business_notes:
        print(f"  📝 {note['title']} ({note['type']})")
    
    print(f"\n🔍 These notes demonstrate:")
    print("  • Semantic search capabilities")
    print("  • Note type categorization (note, concept, topic, important)")
    print("  • Business relationship mapping")
    print("  • 3D visualization with different node types")
    print("  • Vector similarity connections")
    
    print(f"\n🌐 Access your SecondBrain at: http://localhost:3000")
    print(f"🔑 Login with your credentials: {USERNAME}")

if __name__ == "__main__":
    main()