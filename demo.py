"""Demo module for Wishlistly containing sample wishlists and items."""
from datetime import datetime

class DemoWishlist(dict):
    """Demo wishlist class that ensures items is always a list."""
    def __getitem__(self, key):
        value = super().__getitem__(key)
        if key == 'items':
            return value if isinstance(value, list) else []
        return value

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
                    "priority": "HIGH",
                    "image_url": "https://picsum.photos/400/300",
                    "url": "https://example.com/unicorn-plush"
                },
                {
                    "id": "demo-item-2",
                    "name": "Magic Art Set",
                    "description": "Complete art set with colored pencils, markers, and special glitter pens",
                    "price": 34.99,
                    "priority": "HIGH",
                    "image_url": "https://picsum.photos/400/301",
                    "url": "https://example.com/art-set"
                },
                {
                    "id": "demo-item-3",
                    "name": "Science Experiment Kit",
                    "description": "Educational kit with 50+ fun experiments",
                    "price": 45.99,
                    "priority": "MEDIUM",
                    "image_url": "https://picsum.photos/400/302",
                    "url": "https://example.com/science-kit"
                }
            ]
        },
        "christmas": {
            "id": "demo-christmas",
            "title": "Family Christmas Wishlist 2024",
            "description": "Our cozy Christmas wishes! ",
            "occasion": "christmas",
            "theme": "christmas_winter_wonderland",
            "created_at": datetime.now(),
            "items": [
                {
                    "id": "demo-item-4",
                    "name": "Board Game Collection",
                    "description": "Set of 3 classic family board games",
                    "price": 59.99,
                    "priority": "HIGH",
                    "image_url": "https://picsum.photos/400/303",
                    "url": "https://example.com/board-games"
                },
                {
                    "id": "demo-item-5",
                    "name": "Hot Chocolate Maker",
                    "description": "Deluxe hot chocolate machine with frother",
                    "price": 79.99,
                    "priority": "MEDIUM",
                    "image_url": "https://picsum.photos/400/304",
                    "url": "https://example.com/hot-chocolate"
                }
            ]
        },
        "graduation": {
            "id": "demo-graduation",
            "title": "Alex's Graduation Wishlist",
            "description": "Celebrating my college graduation! ",
            "occasion": "graduation",
            "theme": "graduation_modern",
            "created_at": datetime.now(),
            "items": [
                {
                    "id": "demo-item-6",
                    "name": "Professional Laptop",
                    "description": "High-performance laptop for work and creativity",
                    "price": 999.99,
                    "priority": "HIGH",
                    "image_url": "https://picsum.photos/400/305",
                    "url": "https://example.com/laptop"
                },
                {
                    "id": "demo-item-7",
                    "name": "Camera Kit",
                    "description": "Digital camera with accessories for photography",
                    "price": 649.99,
                    "priority": "MEDIUM",
                    "image_url": "https://picsum.photos/400/306",
                    "url": "https://example.com/camera"
                }
            ]
        }
    }
    
    # Convert each wishlist to a DemoWishlist instance
    return {k: DemoWishlist(v) for k, v in data.items()}
