from app import create_app, db
from app.models.user import User, Role
from app.models.content import Club, Player, Course, Vote
import os
from datetime import datetime

app = create_app()

def init_db():
    with app.app_context():
        # Create tables
        db.create_all()
        
        # Check if roles already exist
        if Role.query.count() == 0:
            print("Creating roles...")
            roles = ['User', 'Player', 'Employee', 'Admin']
            for role_name in roles:
                role = Role(name=role_name)
                db.session.add(role)
            db.session.commit()
        
        # Create admin user if not exists
        admin_role = Role.query.filter_by(name='Admin').first()
        if User.query.filter_by(username='admin').first() is None:
            print("Creating admin user...")
            admin = User(
                username='admin',
                email='admin@pars.golf',
                role=admin_role
            )
            admin.password = 'AdminPassword123!'
            db.session.add(admin)
            db.session.commit()
        
        # Create employee user if not exists
        employee_role = Role.query.filter_by(name='Employee').first()
        if User.query.filter_by(username='moderator').first() is None:
            print("Creating moderator user...")
            employee = User(
                username='moderator',
                email='moderator@pars.golf',
                role=employee_role
            )
            employee.password = 'ModeratorPassword123!'
            db.session.add(employee)
            db.session.commit()
        
        # Create regular user if not exists
        user_role = Role.query.filter_by(name='User').first()
        if User.query.filter_by(username='golfuser').first() is None:
            print("Creating regular user...")
            user = User(
                username='golfuser',
                email='user@pars.golf',
                role=user_role
            )
            user.password = 'UserPassword123!'
            db.session.add(user)
            db.session.commit()
        
        # Check if sample clubs already exist
        if Club.query.count() == 0:
            print("Adding sample golf clubs...")
            admin_user = User.query.filter_by(username='admin').first()
            
            clubs = [
                {
                    'name': 'Stealth 2 Driver',
                    'brand': 'TaylorMade',
                    'club_type': 'driver',
                    'description': 'The TaylorMade Stealth 2 Driver features a 60X Carbon Twist Face designed to enhance energy transfer for more distance off the tee.',
                    'image_url': '/static/img/clubs/taylormade_stealth2.jpg',
                    'purchase_link': 'https://www.taylormadegolf.com/Stealth-2-Driver/DW-TA192.html',
                    'price': 599.99,
                    'release_year': 2023,
                    'approved': True
                },
                {
                    'name': 'Apex Pro 24 Irons',
                    'brand': 'Callaway',
                    'club_type': 'iron',
                    'description': 'The Callaway Apex Pro 24 Irons deliver exceptional feel and precision for the skilled player seeking workability and control.',
                    'image_url': '/static/img/clubs/callaway_apex_pro.jpg',
                    'purchase_link': 'https://www.callawaygolf.com/golf-clubs/iron-sets/irons-2023-apex-pro.html',
                    'price': 1299.99,
                    'release_year': 2023,
                    'approved': True
                },
                {
                    'name': 'Scotty Cameron Select Newport 2',
                    'brand': 'Titleist',
                    'club_type': 'putter',
                    'description': 'The iconic Scotty Cameron Select Newport 2 putter features precision milled 303 stainless steel and multi-material technology for exceptional feel and performance.',
                    'image_url': '/static/img/clubs/scotty_cameron_newport.jpg',
                    'purchase_link': 'https://www.titleist.com/golf-clubs/putters/special-select-newport-2',
                    'price': 399.99,
                    'release_year': 2022,
                    'approved': True
                }
            ]
            
            for club_data in clubs:
                club = Club(
                    name=club_data['name'],
                    brand=club_data['brand'],
                    club_type=club_data['club_type'],
                    description=club_data['description'],
                    image_url=club_data['image_url'],
                    purchase_link=club_data['purchase_link'],
                    price=club_data['price'],
                    release_year=club_data['release_year'],
                    submitter=admin_user,
                    approved=club_data['approved']
                )
                db.session.add(club)
            
            db.session.commit()
        
        # Check if sample players already exist
        if Player.query.count() == 0:
            print("Adding sample golf players...")
            admin_user = User.query.filter_by(username='admin').first()
            
            players = [
                {
                    'name': 'Tiger Woods',
                    'profile_image': '/static/img/players/tiger_woods.jpg',
                    'bio': 'One of the greatest golfers of all time, Tiger Woods has won 15 major championships and 82 PGA Tour events.',
                    'country': 'United States',
                    'world_ranking': 1206,
                    'pro_since': 1996,
                    'major_wins': 15,
                    'tour_wins': 82,
                    'verified': True,
                    'approved': True
                },
                {
                    'name': 'Rory McIlroy',
                    'profile_image': '/static/img/players/rory_mcilroy.jpg',
                    'bio': 'Rory McIlroy is a professional golfer from Northern Ireland who has won four major championships and is a former world number one.',
                    'country': 'Northern Ireland',
                    'world_ranking': 2,
                    'pro_since': 2007,
                    'major_wins': 4,
                    'tour_wins': 24,
                    'verified': True,
                    'approved': True
                },
                {
                    'name': 'Scottie Scheffler',
                    'profile_image': '/static/img/players/scottie_scheffler.jpg',
                    'bio': 'Scottie Scheffler is an American professional golfer who plays on the PGA Tour. He won the Masters Tournament in 2022.',
                    'country': 'United States',
                    'world_ranking': 1,
                    'pro_since': 2018,
                    'major_wins': 1,
                    'tour_wins': 6,
                    'verified': True,
                    'approved': True
                }
            ]
            
            for player_data in players:
                player = Player(
                    name=player_data['name'],
                    profile_image=player_data['profile_image'],
                    bio=player_data['bio'],
                    country=player_data['country'],
                    world_ranking=player_data['world_ranking'],
                    pro_since=player_data['pro_since'],
                    major_wins=player_data['major_wins'],
                    tour_wins=player_data['tour_wins'],
                    verified=player_data['verified'],
                    submitter=admin_user,
                    approved=player_data['approved']
                )
                db.session.add(player)
            
            db.session.commit()
        
        # Check if sample courses already exist
        if Course.query.count() == 0:
            print("Adding sample golf courses...")
            admin_user = User.query.filter_by(username='admin').first()
            
            courses = [
                {
                    'name': 'Augusta National Golf Club',
                    'location': 'Augusta, Georgia, USA',
                    'description': 'Home of the Masters Tournament, Augusta National is one of the most famous golf courses in the world.',
                    'image_url': '/static/img/courses/augusta_national.jpg',
                    'website': 'https://www.masters.com',
                    'par': 72,
                    'length_yards': 7475,
                    'difficulty_rating': 9.8,
                    'year_built': 1933,
                    'designer': 'Alister MacKenzie, Bobby Jones',
                    'is_public': False,
                    'has_hosted_major': True,
                    'approved': True
                },
                {
                    'name': 'St Andrews Links (Old Course)',
                    'location': 'St Andrews, Scotland, UK',
                    'description': 'Known as the "Home of Golf", the Old Course at St Andrews is one of the oldest golf courses in the world.',
                    'image_url': '/static/img/courses/st_andrews.jpg',
                    'website': 'https://www.standrews.com',
                    'par': 72,
                    'length_yards': 6721,
                    'difficulty_rating': 9.2,
                    'year_built': 1552,
                    'designer': 'Mother Nature',
                    'is_public': True,
                    'has_hosted_major': True,
                    'approved': True
                },
                {
                    'name': 'Pebble Beach Golf Links',
                    'location': 'Pebble Beach, California, USA',
                    'description': 'This iconic public golf course on California\'s Monterey Peninsula has hosted multiple U.S. Open Championships.',
                    'image_url': '/static/img/courses/pebble_beach.jpg',
                    'website': 'https://www.pebblebeach.com',
                    'par': 72,
                    'length_yards': 7075,
                    'difficulty_rating': 9.5,
                    'year_built': 1919,
                    'designer': 'Jack Neville, Douglas Grant',
                    'is_public': True,
                    'has_hosted_major': True,
                    'approved': True
                }
            ]
            
            for course_data in courses:
                course = Course(
                    name=course_data['name'],
                    location=course_data['location'],
                    description=course_data['description'],
                    image_url=course_data['image_url'],
                    website=course_data['website'],
                    par=course_data['par'],
                    length_yards=course_data['length_yards'],
                    difficulty_rating=course_data['difficulty_rating'],
                    year_built=course_data['year_built'],
                    designer=course_data['designer'],
                    is_public=course_data['is_public'],
                    has_hosted_major=course_data['has_hosted_major'],
                    submitter=admin_user,
                    approved=course_data['approved']
                )
                db.session.add(course)
            
            db.session.commit()
        
        print("Database initialization complete!")

if __name__ == '__main__':
    init_db()