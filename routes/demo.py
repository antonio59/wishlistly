from flask import Blueprint, render_template, abort
from demo import get_demo_wishlists, DemoWishlist

demo = Blueprint('demo', __name__)

@demo.route('/demo')
def demo_page():
    """Demo page showcasing different wishlist themes and features."""
    demo_wishlists = get_demo_wishlists()
    return render_template('demo.html', demo_wishlists=demo_wishlists)

@demo.route('/demo/wishlist/<wishlist_id>')
def view_demo_wishlist(wishlist_id):
    """View a demo wishlist."""
    demo_wishlists = get_demo_wishlists()
    if wishlist_id not in demo_wishlists:
        abort(404)
    wishlist = demo_wishlists[wishlist_id]
    return render_template('view_demo_wishlist.html', wishlist=wishlist)
