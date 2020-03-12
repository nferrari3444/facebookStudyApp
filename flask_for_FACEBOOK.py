from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask import session as user_session
#from sqlalchemy import create_engine
#from sqlalchemy.orm import sessionmaker
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user,\
current_user
from oauth import OAuthSignIn
import datetime

app = Flask(__name__)

app.config['SECRET_KEY'] = 'top secret!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['OAUTH_CREDENTIALS'] = {
    'facebook' :{
        'id': '621313705348474',
        'secret': '241f431dc5ff97cc9f243c2ccdf3ba4a'
    }
}

db = SQLAlchemy(app)
lm = LoginManager(app)
lm.login_view = 'index'

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key = True)
    social_id = db.Column(db.String(64), nullable=False,unique=True)
    nickname = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(64), nullable=True)

@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/authorize/<provider>')
def oauth_authorize(provider):
    '''
    The route ensures that the user is not logged in, and then obtains the
    OAuthSignIn subclass appropiate for the given provider, and invokes its
    authorize() method to initiate the process
    '''

    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()


@app.route('/callback/<provider>')
def oauth_callback(provider):
    '''
    Routhe that handles the callback between the authentication and authorization step and the redirect to the 
    application 
    '''

    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    
    oauth = OAuthSignIn.get_provider(provider)
    social_id , username, email = oauth.callback()
    if social_id is None:
        flash('Authentication failed.')
        return redirect(url_for('index'))
    user = User.query.filter_by(social_id = social_id).first()
    if not user:
        user = User(social_id = social_id, nickname=username,email=email)
        db.session.add(user)
        db.session.commit()
    
    login_user(user,True)
    
    return redirect(url_for('newStudy'))



@app.route('/', methods=['GET','POST'])
@app.route('/CreateStudy', methods=['GET','POST'])
def newStudy():
    '''
    Create a lift study with a POST request to the Facebook Marketing API
    Args:
        
    Returns:
        return new study if
    '''
         
    if request.method == 'POST':
        businessId = int(request.form['businessId']) 
        studyName = str(request.form['name']) 
        
        description = str(request.form['description'])
        
        startTime = str(request.form['startTime'])
        endTime = str(request.form['endTime'])
        observationEndTime = str(request.form['observationEndTime'])

        testGroupName = str(request.form['testGroupName'])
        testGroupDescription = str(request.form['testGroupDescription'])
        treatmentPCT = float(request.form['treatmentPercentage'])
        controlPCT = float(request.form['controlPercentage'])
        
        account = int(request.form['account'])
        objectiveName = str(request.form['objectiveDescription'])
        objectiveDescription = str(request.form['objectiveDescription'])

    else:
        return render_template('createLiftStudy.html')


if __name__ == '__main__':
    app.secret_key = 'supersecretkey'
    db.create_all()
    app.debug = True
    app.run(host='0.0.0.0', port=8000)

