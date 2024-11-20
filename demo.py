"""Demo module for Wishlistly containing sample wishlists and items."""
from datetime import datetime

class DemoWishlist(dict):
    """Demo wishlist class that ensures items is always a list."""
    def __init__(self, data):
        super().__init__(data)
        self.id = data.get('id')
        self.title = data.get('title')
        self.description = data.get('description')
        self.occasion = data.get('occasion')
        self.theme = data.get('theme')
        self.created_at = data.get('created_at')
        self.items = data.get('items', [])

    def __getitem__(self, key):
        value = super().__getitem__(key)
        if key == 'items':
            return value if isinstance(value, list) else []
        return value

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

def get_demo_wishlists():
    """Return the demo wishlists data."""
    data = {
        "birthday": {
            "id": "demo-birthday",
            "title": "Sarah's 7th Birthday Wishlist",
            "description": "My dream birthday wishlist! ",
            "occasion": "birthday",
            "theme": "birthday_sparkly",
            "created_at": datetime.now(),
            "items": [
                {
                    "id": "demo-item-1",
                    "name": "Unicorn Dream Plushie",
                    "description": "Super soft and sparkly unicorn plush toy with rainbow mane",
                    "price": 24.99,
                    "priority": "Must Have",
                    "image_url": "https://picsum.photos/400/300",
                    "url": "https://example.com/unicorn-plush",
                    "purchased": False,
                    "purchased_by": None
                },
                {
                    "id": "demo-item-2",
                    "name": "Magic Art Set",
                    "description": "Complete art set with colored pencils, markers, and special glitter pens",
                    "price": 34.99,
                    "priority": "Would Love",
                    "image_url": "https://picsum.photos/400/301",
                    "url": "https://example.com/art-set",
                    "purchased": True,
                    "purchased_by": "Grandma"
                },
                {
                    "id": "demo-item-3",
                    "name": "Science Experiment Kit",
                    "description": "Educational kit with 50+ fun experiments",
                    "price": 45.99,
                    "priority": "Nice to Have",
                    "image_url": "https://picsum.photos/400/302",
                    "url": "https://example.com/science-kit",
                    "purchased": False,
                    "purchased_by": None
                }
            ]
        },
        "christmas": {
            "id": "demo-christmas",
            "title": "Holiday Wishlist 2024",
            "description": "My Christmas wishes for this year!",
            "occasion": "christmas",
            "theme": "winter_wonderland",
            "created_at": datetime.now(),
            "items": [
                {
                    "id": "demo-item-4",
                    "name": "Robot Building Kit",
                    "description": "Build and program your own robot!",
                    "price": 79.99,
                    "priority": "Must Have",
                    "image_url": "https://picsum.photos/400/303",
                    "url": "https://example.com/robot-kit",
                    "purchased": False,
                    "purchased_by": None
                },
                {
                    "id": "demo-item-5",
                    "name": "Cozy Reading Nook Tent",
                    "description": "Perfect for reading adventures",
                    "price": 49.99,
                    "priority": "Would Love",
                    "image_url": "https://picsum.photos/400/304",
                    "url": "https://example.com/reading-tent",
                    "purchased": True,
                    "purchased_by": "Uncle Bob"
                }
            ]
        }
    }
    
    # Convert each wishlist to a DemoWishlist object
    return {k: DemoWishlist(v) for k, v in data.items()}
