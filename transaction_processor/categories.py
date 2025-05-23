"""
Category patterns for transaction categorization.
"""

CATEGORY_PATTERNS = {
    "Groceries": [
        "grocery", "wholefds", "whole foods", "trader joe", "safeway", "kroger", 
        "albertsons", "food", "market", "smith's", "smiths food", "target", "walmart",
        "costco", "sam's club", "aldi", "publix", "food lion", "meijer", "wegmans",
        "sprouts", "fresh market", "natural grocers", "winco", "harmons", "good earth",
        "ocean mart", "market basket", "shop n save", "heb", "food4less", "giant", "jewel"
    ],
    "Dining": [
        "restaurant", "cafe", "coffee", "starbucks", "mcdonald", "burger king", "wendys",
        "doordash", "grubhub", "uber eat", "pizza", "taco", "burger", "chipotle",
        "panera", "subway", "dunkin", "ihop", "applebee", "chili", "olive garden",
        "outback", "denny", "cheesecake", "betos", "mexican", "thai", "sushi", "ramen",
        "curry", "bbq", "grill", "steakhouse", "seafood", "bakery", "bagel", "sandwich",
        "tst*", "cafe rio", "kfc", "popeyes", "panda express", "tandoor", "taco bell",
        "five guys", "in-n-out", "whataburger", "wing", "buffalo wild", "domino", "papa john",
        "little caesars", "jimmy john", "tortas", "juice", "smoothie", "dessert", "ice cream"
    ],
    "Transportation": [
        "gas", "fuel", "shell", "chevron", "exxon", "mobil", "bp", "7-eleven", "marathon",
        "uber", "lyft", "taxi", "cab", "parking", "transit", "train", "bus", "metro", "subway",
        "airline", "air", "flight", "amtrak", "rental car", "zipcar", "tolls", "toll road",
        "caltrain", "bart", "light rail", "commuter", "airport", "delta", "united", "southwest",
        "american airlines", "frontier", "spirit airlines", "jetblue", "oil change", "tire",
        "auto parts", "mechanic", "oreilly", "autozone", "auto zone", "pepboys", "goodyear",
        "firestone", "midas", "jiffy lube", "valvoline", "car wash", "auto service", "smog check"
    ],
    "Utilities": [
        "utility", "electric", "water", "gas bill", "internet", "phone", "mobile", "cellphone", 
        "cell phone", "cable", "satellite", "dish", "directv", "sewer", "garbage", "trash", 
        "waste", "energy", "power", "solar", "utility bill", "water works", "water bill",
        "con edison", "pge", "duke energy", "xcel", "comcast", "spectrum", "verizon", "at&t",
        "t-mobile", "sprint", "centurylink", "cox", "optimum", "earthlink"
    ],
    "Entertainment": [
        "spotify", "netflix", "hulu", "disney+", "amazon prime", "hbo", "showtime", "movie", 
        "theater", "cinema", "concert", "ticket", "live", "show", "venue", "theme park", 
        "disney", "universal", "seaworld", "six flags", "zoo", "museum", "event", "garden",
        "apple tv", "pandora", "youtube premium", "youtube music", "xbox", "playstation",
        "nintendo", "activision", "ea", "steam", "epic games", "humble bundle", "twitch",
        "starz", "peacock", "paramount+", "espn+", "dazn", "tidal", "audible", "sirius",
        "amc", "regal", "cinemark", "movie theater", "megaplex", "imax"
    ],
    "Shopping": [
        "amazon", "ebay", "walmart", "target", "costco", "best buy", "macy", "nordstrom", 
        "tjmaxx", "marshalls", "ross", "kohls", "old navy", "gap", "nike", "adidas", 
        "clothing", "apparel", "shop", "store", "retail", "outlet", "mall", "boutique",
        "footwear", "shoe", "home goods", "homegoods", "bed bath", "ikea", "furniture", 
        "electronics", "appliance", "jewelry", "accessory", "lowe's", "lowes", "home depot",
        "wayfair", "etsy", "hobby lobby", "michaels", "joann", "crafts", "sporting goods",
        "dick's", "ulta", "sephora", "bath & body", "staples", "office depot", "bookstore",
        "petco", "petsmart", "gamestop", "apple store", "microsoft", "toy", "kohl's",
        "jcpenney", "sears", "bloomingdale", "neiman marcus", "forever 21", "h&m", "zara",
        "victoria's secret", "gucci", "louis vuitton", "ralph lauren", "calvin klein",
        "online purchase", "nuuly", "dr. squatch", "ups store"
    ],
    "Healthcare": [
        "doctor", "physician", "hospital", "clinic", "medical", "dental", "dentist", "orthodontist",
        "eye", "optometrist", "opthamologist", "pharmacy", "prescription", "cvs", "walgreen", 
        "rite aid", "healthcare", "copay", "deductible", "therapy", "counseling", "urgent care", 
        "emergency", "ambulance", "specialist", "vision", "glasses", "contact lens", "walgreens",
        "medicare", "medicaid", "laboratory", "lab test", "x-ray", "mri", "ct scan", "diagnostic",
        "vaccine", "immunization", "physical therapy", "occupational therapy", "chiropractor",
        "psychologist", "psychiatrist", "mental health", "dermatologist", "gynecologist", "obgyn",
        "cardiologist", "pediatrician", "white pine dental"
    ],
    "Housing": [
        "mortgage", "rent", "hoa", "homeowners association", "home", "apartment", "lease", 
        "property", "housing", "condo", "townhouse", "real estate", "realty", "roof", "plumbing",
        "electrician", "hvac", "air conditioning", "heating", "landscaping", "lawn", "garden", 
        "pool", "maintenance", "repair", "remodel", "renovation", "hardware", "carpet", "flooring",
        "paint", "home security", "protection", "alarm", "pest control", "termite", "exterminator",
        "cleaning service", "maid", "janitor", "window", "door", "fence", "deck", "patio",
        "home warranty", "hybrid pest", "home improvement", "locksmith", "contractor"
    ],
    "Insurance": [
        "geico", "state farm", "allstate", "nationwide", "liberty mutual", 
        "progressive", "farmers", "travelers", "safeco", "aaa", "usaa", "american family",
        "metlife", "mutual", "premium", "policy", "coverage", "auto insurance", "car insurance",
        "vehicle insurance", "home insurance", "renters insurance", "life insurance", "health insurance",
        "dental insurance", "vision insurance", "flood insurance", "earthquake insurance",
        "liability", "umbrella policy", "insurance agent", "broker", "underwriter", "deductible",
        "claim", "farm bureau", "insurance company", "insurance provider"
    ],
    "Debt": [
        "loan", "loan payment", "credit card payment", "student loan", "car payment", "auto loan",
        "personal loan", "financing", "credit", "interest", "principal", "debt", "collections",
        "payoff", "refinance", "consolidation", "heloc", "home equity", "line of credit",
        "installment", "payday loan", "cash advance", "sallie mae", "navient", "fedloan", "nelnet",
        "great lakes", "sofi", "lending club", "prosper", "earnest", "affirm", "klarna", "afterpay",
        "chase card", "amex", "discover card", "capital one", "citi", "wells fargo", "bank of america",
        "barclays", "synchrony", "credit union"
    ],
    "Savings": [
        "transfer to savings", "deposit", "savings account", "emergency fund", "rainy day fund",
        "money market", "certificate of deposit", "cd", "bank transfer", "atm deposit", "direct deposit",
        "mobile deposit", "check deposit", "savings goal", "reserve", "set aside", "put away"
    ],
    "Investment": [
        "investment", "401k", "ira", "roth", "stock", "bond", "etf", "mutual fund", "index fund",
        "dividend", "capital gain", "fidelity", "vanguard", "schwab", "e*trade", "td ameritrade", 
        "robinhood", "coinbase", "crypto", "bitcoin", "ethereum", "brokerage", "portfolio",
        "securities", "wealth management", "financial advisor", "asset management", "retirement",
        "trading", "shares", "options", "futures", "forex", "margin", "hedge", "liquidity",
        "annuity", "reit", "real estate investment", "p2p lending", "peer to peer"
    ],
    "Subscriptions": [
        "subscription", "membership", "monthly", "annual", "recurring", "renewal", "access", "premium",
        "prime", "plus", "pro", "member", "club", "adobe", "microsoft", "office365", "icloud",
        "google one", "dropbox", "lastpass", "vpn", "norton", "mcafee", "antivirus", "security",
        "audible", "kindle unlimited", "apple music", "tidal", "deezer", "sirius", "pandora",
        "fitness", "gym", "workout", "peloton", "classpass", "beachbody", "meal kit", "hellofresh",
        "blue apron", "home chef", "freshly", "magazine", "newspaper", "journal", "times", "post",
        "news", "box", "crate", "club", "monthly box", "getsequence"
    ],
    "Income": [
        "salary", "payroll", "paycheck", "direct deposit", "deposit", "wage", "compensation",
        "bonus", "commission", "payment received", "client payment", "customer payment", "fee",
        "invoice payment", "contractor payment", "freelance", "side gig", "refund", "tax refund",
        "reimbursement", "cash back", "reward", "credit", "dividend", "interest", "royalty",
        "alimony", "child support", "benefit", "pension", "annuity", "social security", "disability",
        "unemployment", "welfare", "stipend", "grant", "scholarship", "financial aid", "gift",
        "inheritance", "sale", "proceeds", "liquidation", "withdrawal", "distribution", "rental income"
    ],
    "Education": [
        "tuition", "school", "university", "college", "education", "academic", "class", "course",
        "degree", "diploma", "certificate", "training", "workshop", "seminar", "lecture", "lesson",
        "textbook", "book", "supplies", "student", "professor", "teacher", "instructor", "mentor",
        "tutor", "scholarship", "grant", "financial aid", "student loan", "study abroad", "campus",
        "library", "research", "lab", "science", "art", "music", "sports", "activity", "club",
        "organization", "fraternity", "sorority", "dormitory", "housing", "meal plan", "cafeteria"
    ],
    "Donations": [
        "donation", "charity", "nonprofit", "non-profit", "foundation", "fund", "relief", "support",
        "contribute", "gift", "giving", "fundraising", "campaign", "cause", "community", "volunteer",
        "service", "humanitarian", "welfare", "aid", "assistance", "help", "care", "outreach",
        "mission", "ministry", "church", "temple", "mosque", "synagogue", "religious", "spiritual",
        "faith", "belief", "worship", "congregation", "gathering", "meeting", "service", "tithe",
        "offering", "pledge", "commitment", "benevolence", "generosity", "philanthropy"
    ],
    "Personal Care": [
        "salon", "barber", "hair", "cut", "style", "color", "nail", "manicure", "pedicure", "spa",
        "massage", "facial", "skin care", "beauty", "cosmetic", "makeup", "fragrance", "perfume",
        "cologne", "deodorant", "soap", "shampoo", "conditioner", "lotion", "cream", "oil", "razor",
        "shave", "wax", "threading", "tattoo", "piercing", "jewelry", "accessory", "wellness",
        "health", "fitness", "gym", "workout", "exercise", "yoga", "pilates", "crossfit", "training",
        "personal trainer", "coach", "diet", "nutrition", "vitamin", "supplement", "protein",
        "weight loss", "weight management", "therapy", "counseling", "self-care", "relaxation"
    ]
}

# Define which categories are essential vs lifestyle
ESSENTIAL_CATEGORIES = [
    "Groceries", "Utilities", "Housing", "Healthcare", 
    "Transportation", "Insurance", "Education", "Debt"
]

# Define which categories typically have fixed expenses
FIXED_CATEGORIES = [
    "Housing", "Insurance", "Utilities", "Subscriptions", "Debt"
]