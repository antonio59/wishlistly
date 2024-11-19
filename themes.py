"""
Theme definitions for wishlists.
Each theme includes a name, description, and associated CSS classes/styles.
"""

OCCASIONS = [
    {
        'id': 'birthday',
        'name': 'Birthday',
        'icon': 'fa-birthday-cake'
    },
    {
        'id': 'christmas',
        'name': 'Christmas',
        'icon': 'fa-tree'
    },
    {
        'id': 'graduation',
        'name': 'Graduation',
        'icon': 'fa-graduation-cap'
    },
    {
        'id': 'general',
        'name': 'General',
        'icon': 'fa-gift'
    }
]

WISHLIST_THEMES = {
    "birthday-classic": {
        "name": "birthday-classic",
        "title": "Classic Birthday",
        "description": "Traditional birthday theme with balloons and confetti",
        "icon": "fa-birthday-cake",
        "background": "#ff69b4",
        "accent_color": "#ff1493",
        "text_color": "#ffffff",
        "card_style": "classic",
        "animations": True,
        "decorations": ["balloons", "confetti", "stars"],
        'occasions': ['birthday']
    },
    "birthday-rainbow": {
        "name": "birthday-rainbow",
        "title": "Rainbow Birthday",
        "description": "Colorful rainbow birthday celebration theme",
        "icon": "fa-rainbow",
        "background": "#ff69b4",
        "accent_color": "#ff1493",
        "text_color": "#ffffff",
        "card_style": "rainbow",
        "animations": True,
        "decorations": ["rainbow", "balloons", "stars"],
        'occasions': ['birthday']
    },
    "birthday-sparkle": {
        "name": "birthday-sparkle",
        "title": "Sparkly Birthday",
        "description": "Glittery and sparkly birthday theme",
        "icon": "fa-star",
        "background": "#ff69b4",
        "accent_color": "#ff1493",
        "text_color": "#ffffff",
        "card_style": "sparkly",
        "animations": True,
        "decorations": ["sparkles", "balloons", "stars"],
        'occasions': ['birthday']
    },
    "birthday-unicorn": {
        "name": "birthday-unicorn",
        "title": "Magical Unicorn",
        "description": "Magical unicorn theme with rainbows and sparkles",
        "icon": "fa-horse",
        "background": "#ff69b4",
        "accent_color": "#ff1493",
        "text_color": "#ffffff",
        "card_style": "unicorn",
        "animations": True,
        "decorations": ["unicorn", "rainbow", "stars"],
        'occasions': ['birthday']
    },
    "birthday-galaxy": {
        "name": "birthday-galaxy",
        "title": "Space Galaxy",
        "description": "Out of this world galaxy theme with stars",
        "icon": "fa-star",
        "background": "#ff69b4",
        "accent_color": "#ff1493",
        "text_color": "#ffffff",
        "card_style": "galaxy",
        "animations": True,
        "decorations": ["galaxy", "stars", "planets"],
        'occasions': ['birthday']
    },
    "birthday-princess": {
        "name": "birthday-princess",
        "title": "Princess Party",
        "description": "Royal princess theme with crowns and glitter",
        "icon": "fa-crown",
        "background": "#ff69b4",
        "accent_color": "#ff1493",
        "text_color": "#ffffff",
        "card_style": "princess",
        "animations": True,
        "decorations": ["crown", "glitter", "stars"],
        'occasions': ['birthday']
    },
    "birthday-superhero": {
        "name": "birthday-superhero",
        "title": "Superhero Adventure",
        "description": "Action-packed superhero celebration theme",
        "icon": "fa-bolt",
        "background": "#ff69b4",
        "accent_color": "#ff1493",
        "text_color": "#ffffff",
        "card_style": "superhero",
        "animations": True,
        "decorations": ["superhero", "city", "stars"],
        'occasions': ['birthday']
    },
    "birthday-dinosaur": {
        "name": "birthday-dinosaur",
        "title": "Dinosaur Party",
        "description": "Prehistoric fun with dinosaurs",
        "icon": "fa-dragon",
        "background": "#ff69b4",
        "accent_color": "#ff1493",
        "text_color": "#ffffff",
        "card_style": "dinosaur",
        "animations": True,
        "decorations": ["dinosaur", "leaves", "stars"],
        'occasions': ['birthday']
    },
    "christmas-traditional": {
        "name": "christmas-traditional",
        "title": "Traditional Christmas",
        "description": "Classic Christmas theme with red and green",
        "icon": "fa-tree",
        "background": "#1a4c6e",
        "accent_color": "#2e7cb8",
        "text_color": "#ffffff",
        "card_style": "traditional",
        "animations": True,
        "decorations": ["tree", "presents", "stars"],
        'occasions': ['christmas']
    },
    "christmas-snow": {
        "name": "christmas-snow",
        "title": "Winter Wonderland",
        "description": "Snowy Christmas theme with snowflakes",
        "icon": "fa-snowflake",
        "background": "#1a4c6e",
        "accent_color": "#2e7cb8",
        "text_color": "#ffffff",
        "card_style": "snowy",
        "animations": True,
        "decorations": ["snowflakes", "trees", "stars"],
        'occasions': ['christmas']
    },
    "christmas-cozy": {
        "name": "christmas-cozy",
        "title": "Cozy Christmas",
        "description": "Warm and cozy Christmas theme",
        "icon": "fa-mug-hot",
        "background": "#1a4c6e",
        "accent_color": "#2e7cb8",
        "text_color": "#ffffff",
        "card_style": "cozy",
        "animations": True,
        "decorations": ["mug", "cookies", "stars"],
        'occasions': ['christmas']
    },
    "graduation-classic": {
        "name": "graduation-classic",
        "title": "Classic Graduation",
        "description": "Traditional graduation theme with academic elements",
        "icon": "fa-graduation-cap",
        "background": "#2c3e50",
        "accent_color": "#3498db",
        "text_color": "#ffffff",
        "card_style": "classic",
        "animations": True,
        "decorations": ["cap", "scroll", "stars"],
        'occasions': ['graduation']
    },
    "graduation-modern": {
        "name": "graduation-modern",
        "title": "Modern Graduation",
        "description": "Contemporary graduation theme with clean lines",
        "icon": "fa-user-graduate",
        "background": "#2c3e50",
        "accent_color": "#3498db",
        "text_color": "#ffffff",
        "card_style": "modern",
        "animations": True,
        "decorations": ["graduate", "city", "stars"],
        'occasions': ['graduation']
    },
    "graduation-celebration": {
        "name": "graduation-celebration",
        "title": "Graduation Celebration",
        "description": "Festive graduation theme with celebratory elements",
        "icon": "fa-hat-wizard",
        "background": "#2c3e50",
        "accent_color": "#3498db",
        "text_color": "#ffffff",
        "card_style": "celebration",
        "animations": True,
        "decorations": ["hat", "confetti", "stars"],
        'occasions': ['graduation']
    },
    "elegant": {
        "name": "elegant",
        "title": "Elegant",
        "description": "Sophisticated theme with clean lines and subtle patterns",
        "icon": "fa-gem",
        "background": "#2c3e50",
        "accent_color": "#3498db",
        "text_color": "#ffffff",
        "card_style": "elegant",
        "animations": True,
        "decorations": ["gem", "flowers", "stars"],
        'occasions': ['general', 'graduation', 'birthday', 'christmas']
    },
    "minimalist": {
        "name": "minimalist",
        "title": "Minimalist",
        "description": "Clean and simple theme with focus on content",
        "icon": "fa-minus",
        "background": "#2c3e50",
        "accent_color": "#3498db",
        "text_color": "#ffffff",
        "card_style": "minimalist",
        "animations": True,
        "decorations": ["minus", "dots", "stars"],
        'occasions': ['general', 'graduation', 'birthday', 'christmas']
    },
    "nature": {
        "name": "nature",
        "title": "Nature",
        "description": "Organic theme with natural elements and colors",
        "icon": "fa-leaf",
        "background": "#2c3e50",
        "accent_color": "#3498db",
        "text_color": "#ffffff",
        "card_style": "nature",
        "animations": True,
        "decorations": ["leaf", "flowers", "stars"],
        'occasions': ['general', 'graduation', 'birthday']
    },
    "ocean": {
        "name": "ocean",
        "title": "Ocean",
        "description": "Calming theme inspired by the sea",
        "icon": "fa-water",
        "background": "#2c3e50",
        "accent_color": "#3498db",
        "text_color": "#ffffff",
        "card_style": "ocean",
        "animations": True,
        "decorations": ["water", "fish", "stars"],
        'occasions': ['general', 'birthday']
    },
    "modern": {
        "name": "modern",
        "title": "Modern",
        "description": "Contemporary theme with bold geometric elements",
        "icon": "fa-vector-square",
        "background": "#2c3e50",
        "accent_color": "#3498db",
        "text_color": "#ffffff",
        "card_style": "modern",
        "animations": True,
        "decorations": ["square", "circles", "stars"],
        'occasions': ['general', 'graduation', 'birthday']
    },
    "rustic": {
        "name": "rustic",
        "title": "Rustic",
        "description": "Warm and cozy theme with natural textures",
        "icon": "fa-tree",
        "background": "#2c3e50",
        "accent_color": "#3498db",
        "text_color": "#ffffff",
        "card_style": "rustic",
        "animations": True,
        "decorations": ["tree", "wood", "stars"],
        'occasions': ['general', 'christmas']
    }
}

def get_theme_by_id(theme_id):
    """Get a theme by its ID."""
    return WISHLIST_THEMES.get(theme_id, WISHLIST_THEMES["birthday-classic"])

def get_all_themes():
    """Get all available themes."""
    return WISHLIST_THEMES

def get_themes_by_occasion(occasion_id):
    """Get themes filtered by occasion."""
    return [theme for theme in WISHLIST_THEMES.values() if occasion_id in theme['occasions']]

def get_all_occasions():
    """Get all available occasions."""
    return OCCASIONS

def get_occasion_by_id(occasion_id):
    """Get an occasion by its ID."""
    return next((occasion for occasion in OCCASIONS if occasion['id'] == occasion_id), None)
