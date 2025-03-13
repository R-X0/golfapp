# Pars.Golf

Pars.Golf is a platform where golf enthusiasts can vote on the best clubs, players, and courses.

**Tagline**: Par-Fect Your Game

## Tech Stack

- **Backend**: Python/Flask
- **Database**: PostgreSQL
- **Server**: Nginx
- **Hosting**: Digital Ocean

## Features

- User authentication system with OAuth support
- Voting system for golf clubs, players, and courses
- User profiles (pars.golf/@username format)
- Content moderation tools
- Role-based access control (User, Player, Employee, Admin)
- CSV import functionality for bulk data
- Product links for purchasing golf clubs
- Profile management (password reset, profile pictures)

## Setup Instructions

### Prerequisites

- Python 3.11+
- PostgreSQL
- Docker and Docker Compose (optional)

### Environment Variables

Create a `.env` file in the root directory with the following variables:

```
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://postgres:password@localhost/parsgolf
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
TWITTER_CLIENT_ID=your-twitter-client-id
TWITTER_CLIENT_SECRET=your-twitter-client-secret
MAIL_SERVER=smtp.example.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@example.com
MAIL_PASSWORD=your-email-password
MAIL_DEFAULT_SENDER=your-email@example.com
```

### Local Development Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/pars.golf.git
   cd pars.golf
   ```

2. Create a virtual environment and install dependencies:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Set up the database:
   ```
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

4. Create initial roles and admin user:
   ```
   flask shell
   >>> from app.models.user import Role, User
   >>> from app import db
   >>> roles = ['User', 'Player', 'Employee', 'Admin']
   >>> for role in roles:
   ...     r = Role(name=role)
   ...     db.session.add(r)
   >>> db.session.commit()
   >>> admin_role = Role.query.filter_by(name='Admin').first()
   >>> admin = User(username='admin', email='admin@example.com', role=admin_role)
   >>> admin.password = 'secure-password'
   >>> db.session.add(admin)
   >>> db.session.commit()
   >>> exit()
   ```

5. Run the development server:
   ```
   flask run
   ```

### Docker Setup

1. Build and start the containers:
   ```
   docker-compose up -d
   ```

2. Run database migrations:
   ```
   docker-compose exec web flask db upgrade
   ```

3. Access the application at http://localhost

## Deployment to Digital Ocean

1. Create a Digital Ocean Droplet with Docker installed
2. Clone the repository on the Droplet
3. Create a `.env` file with production values
4. Run Docker Compose:
   ```
   docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
   ```

## Color Scheme

- Primary Charcoal: #3A4257
- Red: #A24936
- Yellow: #FFBC42
- Lavender: #E2B6CF
- Cadet Grey: #83A0A0

## License

This project is licensed under the MIT License - see the LICENSE file for details.