# Kid's Wishlist Creator 🎁

A child-friendly web application that lets kids create and personalize their wishlists for special occasions like birthdays, Christmas, and other events!

## Features

- 🎨 Customizable themes and colorful interface
- 📝 Easy wishlist creation and management
- 👨‍👩‍👧‍👦 Parent-friendly controls
- 🔗 Secure wishlist sharing
- 🎯 Smart purchase tracking
- 🌈 Multiple occasion support

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file with:
```
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key
```

4. Initialize the database:
```bash
flask db upgrade
```

5. Run the application:
```bash
flask run
```

Visit `http://localhost:5000` in your web browser to start using the application!

## Security Note

This application is designed with children's safety in mind. Parents can monitor and manage their children's wishlists, and sharing is controlled through secure links.
