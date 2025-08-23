#!/usr/bin/env python3
"""
Script to generate expanded training dataset with 500+ documents
"""
import csv
import random

# Enhanced politics documents
politics_templates = [
    "The government announced {policy} to address {issue} and improve {area}.",
    "Parliament voted on {legislation} that will {action} for {beneficiary}.",
    "The president signed {document} focusing on {topic} and {goal}.",
    "Congressional leaders debated {bill} to strengthen {sector} and promote {value}.",
    "The senate committee investigated {concern} affecting {group} across the nation.",
    "Local officials implemented {program} to enhance {service} and reduce {problem}.",
    "International diplomats negotiated {agreement} to improve {relationship} between nations.",
    "The supreme court ruled on {case} with implications for {rights} and {justice}.",
    "Election officials announced {changes} to ensure {integrity} in the democratic process.",
    "Policy makers proposed {reform} to modernize {system} and increase {efficiency}.",
    "The governor declared {initiative} to combat {crisis} and support {community}.",
    "Legislative committees approved {funding} for {infrastructure} and {development}.",
    "Political analysts predicted {outcome} based on {polling} and {trends}.",
    "Government agencies launched {campaign} to promote {awareness} about {issue}.",
    "Diplomatic missions worked to resolve {conflict} and maintain {peace} in the region.",
]

politics_vars = {
    "policy": [
        "new economic policies",
        "environmental regulations",
        "healthcare reforms",
        "education initiatives",
        "tax reforms",
        "immigration policies",
        "defense strategies",
        "social programs",
    ],
    "issue": [
        "climate change",
        "unemployment",
        "public safety",
        "housing shortage",
        "healthcare access",
        "education quality",
        "economic inequality",
        "infrastructure decay",
    ],
    "area": [
        "public transportation",
        "renewable energy",
        "job creation",
        "social welfare",
        "national security",
        "environmental protection",
        "economic growth",
        "public health",
    ],
    "legislation": [
        "the infrastructure bill",
        "healthcare reform",
        "education funding bill",
        "climate action legislation",
        "voting rights act",
        "immigration reform",
        "tax reform bill",
    ],
    "action": [
        "provide funding",
        "establish protections",
        "create opportunities",
        "improve access",
        "strengthen regulations",
        "expand coverage",
        "increase support",
    ],
    "beneficiary": [
        "working families",
        "small businesses",
        "students",
        "seniors",
        "veterans",
        "rural communities",
        "urban areas",
        "disadvantaged groups",
    ],
    "document": [
        "executive orders",
        "federal legislation",
        "trade agreements",
        "defense authorization",
        "budget proposals",
        "international treaties",
    ],
    "topic": [
        "economic recovery",
        "national security",
        "environmental protection",
        "healthcare access",
        "education reform",
        "infrastructure investment",
    ],
    "goal": [
        "job creation",
        "deficit reduction",
        "innovation promotion",
        "public safety",
        "sustainable development",
        "social equity",
    ],
    "bill": [
        "defense spending bills",
        "environmental legislation",
        "healthcare proposals",
        "education reforms",
        "tax policies",
        "immigration measures",
    ],
    "sector": [
        "public education",
        "healthcare system",
        "national defense",
        "transportation networks",
        "energy infrastructure",
        "social services",
    ],
    "value": [
        "transparency",
        "accountability",
        "equality",
        "sustainability",
        "innovation",
        "security",
        "prosperity",
    ],
    "concern": [
        "election security",
        "government corruption",
        "foreign interference",
        "civil rights violations",
        "economic inequality",
        "environmental damage",
    ],
    "group": [
        "voters",
        "taxpayers",
        "workers",
        "students",
        "families",
        "businesses",
        "communities",
        "minorities",
    ],
    "program": [
        "voter education programs",
        "community development initiatives",
        "public safety measures",
        "economic assistance programs",
    ],
    "service": [
        "public transportation",
        "emergency services",
        "social services",
        "municipal services",
        "public utilities",
    ],
    "problem": [
        "bureaucratic inefficiency",
        "service delays",
        "budget deficits",
        "infrastructure problems",
        "administrative costs",
    ],
    "agreement": [
        "trade agreements",
        "peace treaties",
        "climate accords",
        "defense pacts",
        "economic partnerships",
    ],
    "relationship": [
        "diplomatic relations",
        "trade partnerships",
        "security cooperation",
        "cultural exchanges",
        "economic ties",
    ],
    "case": [
        "constitutional cases",
        "civil rights disputes",
        "federal jurisdiction matters",
        "regulatory challenges",
    ],
    "rights": [
        "voting rights",
        "civil liberties",
        "constitutional protections",
        "human rights",
        "individual freedoms",
    ],
    "justice": [
        "equal protection",
        "due process",
        "fair representation",
        "legal equality",
        "constitutional principles",
    ],
    "changes": [
        "security enhancements",
        "procedural improvements",
        "technology upgrades",
        "accessibility measures",
    ],
    "integrity": [
        "electoral integrity",
        "transparency",
        "fairness",
        "accountability",
        "public trust",
    ],
    "reform": [
        "democratic reforms",
        "institutional changes",
        "structural improvements",
        "procedural updates",
    ],
    "system": [
        "electoral systems",
        "government processes",
        "administrative procedures",
        "public institutions",
    ],
    "efficiency": [
        "operational efficiency",
        "cost effectiveness",
        "service quality",
        "public accountability",
    ],
    "initiative": [
        "emergency measures",
        "recovery programs",
        "development plans",
        "assistance programs",
    ],
    "crisis": [
        "natural disasters",
        "economic downturns",
        "public health emergencies",
        "social unrest",
    ],
    "community": [
        "affected communities",
        "local residents",
        "vulnerable populations",
        "business owners",
    ],
    "funding": [
        "federal funding",
        "state appropriations",
        "emergency funds",
        "development grants",
    ],
    "infrastructure": [
        "road infrastructure",
        "public facilities",
        "communication networks",
        "transportation systems",
    ],
    "development": [
        "economic development",
        "community development",
        "infrastructure development",
        "social development",
    ],
    "outcome": [
        "election results",
        "policy changes",
        "legislative outcomes",
        "political shifts",
    ],
    "polling": [
        "voter surveys",
        "opinion polls",
        "demographic studies",
        "trend analysis",
    ],
    "trends": [
        "political trends",
        "voting patterns",
        "demographic changes",
        "public opinion",
    ],
    "campaign": [
        "awareness campaigns",
        "public information drives",
        "educational initiatives",
        "outreach programs",
    ],
    "awareness": [
        "public awareness",
        "citizen education",
        "community understanding",
        "stakeholder engagement",
    ],
    "conflict": [
        "international disputes",
        "territorial conflicts",
        "trade disagreements",
        "diplomatic tensions",
    ],
    "peace": [
        "regional stability",
        "international peace",
        "diplomatic harmony",
        "peaceful coexistence",
    ],
}

# Enhanced business documents
business_templates = [
    "The company reported {performance} with {metric} increasing by {percentage} due to {factor}.",
    "{company_type} announced {action} to {goal} and expand {area}.",
    "Investors showed {sentiment} as {indicator} reached {level} in the {period}.",
    "The board approved {decision} focusing on {strategy} and {objective}.",
    "Market analysts predicted {forecast} based on {data} and {trends}.",
    "The startup secured {funding} from {source} to develop {product}.",
    "Corporate executives launched {initiative} to improve {aspect} and reduce {cost}.",
    "Financial reports showed {result} with {revenue} exceeding {expectations}.",
    "The merger between {entity1} and {entity2} created {outcome} in the {sector}.",
    "Technology companies invested in {technology} to enhance {capability} and {competitiveness}.",
    "Retail sales demonstrated {growth} as consumers increased {spending} on {category}.",
    "The acquisition of {target} will strengthen {position} and provide {advantage}.",
    "Supply chain improvements resulted in {benefit} and {efficiency} across {operations}.",
    "Digital transformation initiatives helped {company} adapt to {change} and {demand}.",
    "International expansion plans include {market} to capture {opportunity} and {growth}.",
]

business_vars = {
    "performance": [
        "strong quarterly results",
        "record annual earnings",
        "exceptional growth",
        "solid financial performance",
        "improved profitability",
    ],
    "metric": [
        "revenue",
        "profit margins",
        "market share",
        "customer satisfaction",
        "operational efficiency",
        "stock price",
    ],
    "percentage": ["15%", "20%", "25%", "30%", "12%", "18%", "22%", "28%"],
    "factor": [
        "successful product launches",
        "market expansion",
        "cost optimization",
        "strategic partnerships",
        "innovation initiatives",
    ],
    "company_type": [
        "Technology giants",
        "Manufacturing companies",
        "Financial institutions",
        "Retail chains",
        "Healthcare providers",
    ],
    "action": [
        "strategic partnerships",
        "acquisition deals",
        "expansion plans",
        "product launches",
        "investment initiatives",
    ],
    "goal": [
        "increase market share",
        "improve efficiency",
        "enhance customer experience",
        "drive innovation",
        "reduce costs",
    ],
    "area": [
        "international markets",
        "digital services",
        "product lines",
        "customer base",
        "operational capacity",
    ],
    "sentiment": [
        "strong confidence",
        "cautious optimism",
        "growing interest",
        "positive outlook",
        "increased enthusiasm",
    ],
    "indicator": [
        "market indices",
        "economic indicators",
        "performance metrics",
        "growth rates",
        "profit margins",
    ],
    "level": [
        "record highs",
        "significant levels",
        "unprecedented heights",
        "new benchmarks",
        "historic peaks",
    ],
    "period": [
        "fiscal quarter",
        "financial year",
        "reporting period",
        "business cycle",
        "market session",
    ],
    "decision": [
        "strategic investments",
        "expansion initiatives",
        "restructuring plans",
        "acquisition proposals",
        "innovation projects",
    ],
    "strategy": [
        "growth strategies",
        "market penetration",
        "cost reduction",
        "digital transformation",
        "customer engagement",
    ],
    "objective": [
        "operational excellence",
        "market leadership",
        "customer satisfaction",
        "financial growth",
        "competitive advantage",
    ],
    "forecast": [
        "continued growth",
        "market recovery",
        "increased demand",
        "positive trends",
        "strong performance",
    ],
    "data": [
        "market research",
        "consumer surveys",
        "economic indicators",
        "industry reports",
        "financial analysis",
    ],
    "trends": [
        "market trends",
        "consumer behavior",
        "industry patterns",
        "economic cycles",
        "technological advances",
    ],
    "funding": [
        "venture capital",
        "series funding",
        "private investment",
        "bank loans",
        "government grants",
    ],
    "source": [
        "venture capitalists",
        "private investors",
        "institutional funds",
        "strategic partners",
        "crowdfunding",
    ],
    "product": [
        "innovative solutions",
        "digital platforms",
        "mobile applications",
        "AI technologies",
        "cloud services",
    ],
    "initiative": [
        "sustainability programs",
        "efficiency projects",
        "quality improvements",
        "innovation labs",
        "training programs",
    ],
    "aspect": [
        "customer service",
        "operational efficiency",
        "product quality",
        "employee satisfaction",
        "environmental impact",
    ],
    "cost": [
        "operational costs",
        "production expenses",
        "administrative overhead",
        "supply chain costs",
        "marketing expenses",
    ],
    "result": [
        "positive outcomes",
        "strong performance",
        "improved results",
        "exceptional growth",
        "record achievements",
    ],
    "revenue": [
        "total revenue",
        "gross income",
        "net earnings",
        "operating income",
        "sales figures",
    ],
    "expectations": [
        "analyst projections",
        "market forecasts",
        "investor expectations",
        "industry benchmarks",
        "target goals",
    ],
    "entity1": [
        "global corporations",
        "industry leaders",
        "market players",
        "technology companies",
        "financial institutions",
    ],
    "entity2": [
        "strategic partners",
        "complementary businesses",
        "innovative startups",
        "regional leaders",
        "specialized firms",
    ],
    "outcome": [
        "market leadership",
        "competitive advantages",
        "operational synergies",
        "enhanced capabilities",
        "increased value",
    ],
    "sector": [
        "technology sector",
        "financial industry",
        "healthcare market",
        "retail segment",
        "manufacturing industry",
    ],
    "technology": [
        "artificial intelligence",
        "machine learning",
        "blockchain technology",
        "cloud computing",
        "automation systems",
    ],
    "capability": [
        "operational capabilities",
        "technical expertise",
        "market reach",
        "service delivery",
        "innovation capacity",
    ],
    "competitiveness": [
        "market competitiveness",
        "pricing advantages",
        "service quality",
        "operational efficiency",
        "customer value",
    ],
    "growth": [
        "steady growth",
        "robust expansion",
        "significant increases",
        "strong momentum",
        "positive development",
    ],
    "spending": [
        "consumer spending",
        "purchasing behavior",
        "investment activity",
        "expenditure patterns",
        "buying decisions",
    ],
    "category": [
        "technology products",
        "consumer goods",
        "services",
        "luxury items",
        "essential products",
    ],
    "target": [
        "strategic targets",
        "key companies",
        "valuable assets",
        "market leaders",
        "innovative firms",
    ],
    "position": [
        "market position",
        "competitive standing",
        "industry leadership",
        "strategic advantage",
        "business portfolio",
    ],
    "advantage": [
        "competitive advantages",
        "operational benefits",
        "market opportunities",
        "strategic value",
        "growth potential",
    ],
    "benefit": [
        "cost savings",
        "efficiency gains",
        "quality improvements",
        "time reductions",
        "performance enhancements",
    ],
    "efficiency": [
        "operational efficiency",
        "process optimization",
        "resource utilization",
        "workflow improvements",
        "productivity gains",
    ],
    "operations": [
        "business operations",
        "manufacturing processes",
        "service delivery",
        "supply chains",
        "organizational functions",
    ],
    "company": [
        "forward-thinking companies",
        "industry innovators",
        "market leaders",
        "growing businesses",
        "established firms",
    ],
    "change": [
        "market changes",
        "technological shifts",
        "consumer preferences",
        "industry evolution",
        "competitive dynamics",
    ],
    "demand": [
        "customer demand",
        "market requirements",
        "consumer needs",
        "business expectations",
        "service requests",
    ],
    "market": [
        "emerging markets",
        "international territories",
        "new regions",
        "growth markets",
        "strategic locations",
    ],
    "opportunity": [
        "market opportunities",
        "growth potential",
        "business prospects",
        "investment possibilities",
        "development chances",
    ],
}

# Enhanced health documents
health_templates = [
    "Medical researchers discovered {breakthrough} that could {impact} for patients with {condition}.",
    "Healthcare providers implemented {intervention} to improve {outcome} and reduce {problem}.",
    "Clinical trials showed {result} for {treatment} in treating {disease}.",
    "Public health officials announced {program} to address {issue} and promote {wellness}.",
    "The study revealed {finding} about {factor} and its effect on {health_aspect}.",
    "Hospital systems adopted {technology} to enhance {care} and streamline {process}.",
    "Pharmaceutical companies developed {drug} targeting {mechanism} for {therapeutic_area}.",
    "Health experts recommended {guidelines} to prevent {risk} and maintain {health_goal}.",
    "The research team published {study} demonstrating {effectiveness} of {approach}.",
    "Healthcare workers received {training} on {protocol} to improve {safety}.",
    "Mental health services expanded {access} to provide {support} for {population}.",
    "Diagnostic tools improved {detection} of {pathology} enabling {intervention}.",
    "Preventive medicine initiatives focused on {prevention} to reduce {disease_burden}.",
    "Surgical techniques advanced with {innovation} improving {procedure} outcomes.",
    "Healthcare policy changes aimed to {reform} and increase {accessibility} for {patients}.",
]

health_vars = {
    "breakthrough": [
        "breakthrough treatments",
        "innovative therapies",
        "novel approaches",
        "cutting-edge research",
        "revolutionary findings",
    ],
    "impact": [
        "transform treatment options",
        "improve patient outcomes",
        "save lives",
        "reduce suffering",
        "enhance quality of life",
    ],
    "condition": [
        "cancer",
        "diabetes",
        "heart disease",
        "neurological disorders",
        "autoimmune diseases",
        "mental health conditions",
    ],
    "intervention": [
        "new protocols",
        "evidence-based practices",
        "quality improvement measures",
        "safety initiatives",
        "care coordination",
    ],
    "outcome": [
        "patient outcomes",
        "treatment effectiveness",
        "care quality",
        "safety measures",
        "health indicators",
    ],
    "problem": [
        "medical errors",
        "infection rates",
        "readmissions",
        "wait times",
        "costs",
        "complications",
    ],
    "result": [
        "promising results",
        "positive outcomes",
        "significant improvements",
        "encouraging findings",
        "notable benefits",
    ],
    "treatment": [
        "new medications",
        "therapeutic approaches",
        "surgical procedures",
        "rehabilitation methods",
        "intervention strategies",
    ],
    "disease": [
        "chronic diseases",
        "rare disorders",
        "infectious diseases",
        "genetic conditions",
        "metabolic disorders",
    ],
    "program": [
        "vaccination programs",
        "screening initiatives",
        "wellness campaigns",
        "education programs",
        "prevention strategies",
    ],
    "issue": [
        "public health crises",
        "disease outbreaks",
        "health disparities",
        "access barriers",
        "environmental health",
    ],
    "wellness": [
        "community wellness",
        "preventive care",
        "healthy behaviors",
        "population health",
        "wellness education",
    ],
    "finding": [
        "significant findings",
        "important discoveries",
        "clinical evidence",
        "research insights",
        "scientific observations",
    ],
    "factor": [
        "genetic factors",
        "environmental influences",
        "lifestyle choices",
        "risk factors",
        "protective factors",
    ],
    "health_aspect": [
        "cardiovascular health",
        "mental wellbeing",
        "immune function",
        "cognitive performance",
        "physical fitness",
    ],
    "technology": [
        "artificial intelligence",
        "telemedicine platforms",
        "electronic health records",
        "medical devices",
        "diagnostic tools",
    ],
    "care": [
        "patient care",
        "clinical services",
        "treatment delivery",
        "healthcare coordination",
        "medical management",
    ],
    "process": [
        "clinical processes",
        "administrative workflows",
        "care delivery",
        "treatment protocols",
        "patient management",
    ],
    "drug": [
        "new medications",
        "therapeutic compounds",
        "innovative drugs",
        "treatment options",
        "pharmaceutical solutions",
    ],
    "mechanism": [
        "biological pathways",
        "cellular processes",
        "molecular targets",
        "disease mechanisms",
        "therapeutic targets",
    ],
    "therapeutic_area": [
        "oncology",
        "cardiology",
        "neurology",
        "psychiatry",
        "endocrinology",
        "immunology",
    ],
    "guidelines": [
        "clinical guidelines",
        "best practices",
        "evidence-based recommendations",
        "treatment protocols",
        "care standards",
    ],
    "risk": [
        "disease risk",
        "health complications",
        "adverse outcomes",
        "medical risks",
        "safety concerns",
    ],
    "health_goal": [
        "optimal health",
        "wellbeing",
        "disease prevention",
        "health maintenance",
        "quality of life",
    ],
    "study": [
        "clinical studies",
        "research findings",
        "scientific reports",
        "medical research",
        "evidence reviews",
    ],
    "effectiveness": [
        "clinical effectiveness",
        "therapeutic benefits",
        "treatment success",
        "positive outcomes",
        "measurable improvements",
    ],
    "approach": [
        "treatment approaches",
        "therapeutic methods",
        "intervention strategies",
        "care models",
        "clinical practices",
    ],
    "training": [
        "specialized training",
        "continuing education",
        "skill development",
        "competency training",
        "professional development",
    ],
    "protocol": [
        "safety protocols",
        "clinical procedures",
        "treatment guidelines",
        "care standards",
        "best practices",
    ],
    "safety": [
        "patient safety",
        "care quality",
        "treatment safety",
        "clinical safety",
        "healthcare standards",
    ],
    "access": [
        "healthcare access",
        "service availability",
        "treatment access",
        "care delivery",
        "medical services",
    ],
    "support": [
        "psychological support",
        "therapeutic assistance",
        "care services",
        "treatment support",
        "patient advocacy",
    ],
    "population": [
        "vulnerable populations",
        "patient groups",
        "communities",
        "specific demographics",
        "at-risk individuals",
    ],
    "detection": [
        "early detection",
        "accurate diagnosis",
        "disease identification",
        "screening effectiveness",
        "diagnostic accuracy",
    ],
    "pathology": [
        "disease conditions",
        "medical disorders",
        "health problems",
        "clinical conditions",
        "pathological states",
    ],
    "intervention": [
        "early intervention",
        "timely treatment",
        "therapeutic intervention",
        "medical care",
        "clinical response",
    ],
    "prevention": [
        "disease prevention",
        "health promotion",
        "risk reduction",
        "preventive care",
        "wellness strategies",
    ],
    "disease_burden": [
        "disease burden",
        "health impacts",
        "medical costs",
        "healthcare utilization",
        "population health",
    ],
    "innovation": [
        "technological innovations",
        "surgical advances",
        "medical breakthroughs",
        "treatment innovations",
        "clinical improvements",
    ],
    "procedure": [
        "surgical procedures",
        "medical interventions",
        "treatment methods",
        "clinical procedures",
        "therapeutic techniques",
    ],
    "reform": [
        "improve healthcare delivery",
        "enhance access",
        "reduce costs",
        "improve quality",
        "strengthen systems",
    ],
    "accessibility": [
        "healthcare accessibility",
        "service availability",
        "care access",
        "treatment options",
        "medical services",
    ],
    "patients": [
        "all patients",
        "underserved populations",
        "vulnerable groups",
        "diverse communities",
        "patient populations",
    ],
}


def generate_text(templates, variables):
    """Generate text from templates and variables"""
    texts = []
    for template in templates:
        for _ in range(10):  # Generate 10 variations per template
            text = template
            # Replace placeholders with random choices
            import re

            placeholders = re.findall(r"\{(\w+)\}", template)
            for placeholder in placeholders:
                if placeholder in variables:
                    replacement = random.choice(variables[placeholder])
                    text = text.replace(f"{{{placeholder}}}", replacement)
            texts.append(text)
    return texts


def create_expanded_dataset():
    """Create expanded training dataset with 500+ documents"""

    # Generate texts for each category
    politics_texts = generate_text(politics_templates, politics_vars)
    business_texts = generate_text(business_templates, business_vars)
    health_texts = generate_text(health_templates, health_vars)

    # Balance the dataset
    target_per_category = 170  # Approximately 500 total documents

    politics_texts = politics_texts[:target_per_category]
    business_texts = business_texts[:target_per_category]
    health_texts = health_texts[:target_per_category]

    # Create combined dataset
    all_documents = []

    for text in politics_texts:
        all_documents.append({"category": "politics", "text": text})

    for text in business_texts:
        all_documents.append({"category": "business", "text": text})

    for text in health_texts:
        all_documents.append({"category": "health", "text": text})

    # Shuffle the dataset
    random.shuffle(all_documents)

    return all_documents


def save_to_csv(documents, filename):
    """Save documents to CSV file"""
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["category", "text"])
        writer.writeheader()
        for doc in documents:
            writer.writerow(doc)


if __name__ == "__main__":
    print("Generating expanded training dataset...")
    documents = create_expanded_dataset()

    print(f"Generated {len(documents)} documents")
    print(f"Categories distribution:")
    for category in ["politics", "business", "health"]:
        count = sum(1 for doc in documents if doc["category"] == category)
        print(f"  {category}: {count}")

    # Save to file
    save_to_csv(documents, "training_documents_expanded.csv")
    print("Saved to training_documents_expanded.csv")
