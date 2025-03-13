from app import create_app, db
from app.models.user import User, Role
from app.models.content import Club, Player, Course, Vote

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db, 
        'User': User, 
        'Role': Role, 
        'Club': Club, 
        'Player': Player, 
        'Course': Course,
        'Vote': Vote
    }

if __name__ == '__main__':
    app.run(debug=True)