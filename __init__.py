import os

from flask import Flask, render_template
# from flask.ext.markdown import Markdown
#

def create_app(test_config=None):
    # create and configure the app

    # instance_path = os.path.join(os.getcwd(), 'instance')
    
    app = Flask(__name__, 
                
                # instance_path=instance_path,
                instance_relative_config=True
                )

    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'emc_subset.sqlite')
    )

    print(app.config)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import db
    db.init_app(app)

    # Markdown(app)

    # Index page stuff
    from . import index
    app.register_blueprint(index.bp)

    # Needed for login
    from . import auth
    app.register_blueprint(auth.bp)

    # Everything to do with meets + reports
    from . import meets
    app.register_blueprint(meets.bp)
    # app.add_url_rule('/meets.html', 'meetsindex')

    # anything to do with the members list, including committee members
    from . import members
    app.register_blueprint(members.bp)

    ##
    # Static pages which don't need a blueprint
    ##

    @app.route('/history.html')
    def history():
        return render_template('history.html')
    
    @app.route('/climbing.html')
    def climbing():
        return render_template('climbing.html')

    @app.route('/links.html')
    def links():
        return render_template('links.html')

    @app.route('/mailinglists.html')
    def mailinglists():
        return render_template('email.html')
    
    @app.route('/cookies.html')
    def cookies():
        return render_template('cookies.md')

    @app.route('/dataprivacy.html')
    def dataprivacy():
        return render_template('dataprivacy.html')
    

    return app

# if __name__ == "__main__":
#     app = create_app()
#     app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))