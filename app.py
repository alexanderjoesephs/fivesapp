from flask import Flask, render_template, flash, request, session, redirect
import sqlite3
from flask_session.__init__ import Session
from tempfile import mkdtemp
from datetime import datetime

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
def home():
    return render_template("index.html")
        


@app.route("/games", methods=["GET", "POST"])
def games():
    conn = sqlite3.connect('players.db')
    cursor = conn.cursor()
    list_of_games_past=[]
    list_of_games_future=[]
    list_of_all_games = []
    games = cursor.execute("SELECT playing_in.player_id, games.location, games.datetime, games.length_in_mins, games.creator, games.id FROM playing_in JOIN users ON users.id = playing_in.player_id JOIN games ON games.id = playing_in.game_id WHERE playing_in.player_id = ? ORDER BY games.datetime", (session["user_id"], ))
    
    for g in games: 
        list_of_all_games.append(g)
        datetimestring = g[2]
        dtgame = datetime.strptime(datetimestring, '%Y-%m-%d %H:%M:%S') 
        now = datetime.now()
        if dtgame < now:
            list_of_games_past.append(g[5])
        else:
            list_of_games_future.append(g[5])
    
    return render_template("games.html", games=games, list_of_all_games=list_of_all_games, list_of_games_past=list_of_games_past, list_of_games_future=list_of_games_future)



@app.route("/register", methods=["GET", "POST"])
def register():

    session.clear()
    
    if request.method == "GET":
        return render_template("register.html")

    if request.method == "POST":
        if(request.form.get("password") != request.form.get("confirmation")):
            return apology("passwords don't match")
        conn = sqlite3.connect('players.db')
        cursor = conn.cursor()
        data = cursor.execute("SELECT * FROM users")
        for row in data:
            if row[1] == request.form.get("username"):
                conn.close()
                return apology("username taken")
    cursor.execute("INSERT INTO users (username, firstname, surname, password) VALUES (?, ?, ?, ?)", (request.form.get("username"), request.form.get("firstname"), request.form.get("surname"), request.form.get("password")))
    conn.commit()
    cursor.execute("SELECT id, username FROM users ORDER BY id DESC LIMIT 1")
    user_id = cursor.fetchone()
    session["user_id"] = user_id[0]
    session["username"] = user_id[1]
    conn.commit()
    conn.close()
    return redirect("/")

        
@app.route("/login", methods=["GET", "POST"])
def login():
    
    session.clear()

    if request.method=="GET":
        return render_template("login.html")
    else:
        conn = sqlite3.connect('players.db')
        cursor = conn.cursor()
        data = cursor.execute("SELECT id, username, password FROM users")
        
        for row in data:
            if request.form.get("username")==row[1] and request.form.get("password")==row[2]:
                session["user_id"] = row[0]
                session["username"] = row[1]
                session['logged_in'] = True
                return redirect("/")

                    
        return apology("invalid username or password")

@app.route("/logout")
def logout():
    session.clear()
    session['logged_in'] = False
    return redirect("/login")



@app.route("/create", methods=["GET", "POST"])
def create():

    if request.method=="GET":
        return render_template("create.html")
    else:
        datetimestring = request.form.get("date_and_time")
        dtobject = datetime.strptime(datetimestring, '%Y-%m-%dT%H:%M')
        length = int(request.form.get("length"))
        number_players=int(request.form.get("number_players"))
        conn = sqlite3.connect('players.db', detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO games (location, datetime, length_in_mins, number_of_players, creator, open_spots) VALUES (?, ?, ?, ?, ?, ?)", (request.form.get("location"), dtobject, length, number_players,session["username"], number_players ) )
        conn.commit()
        conn.close()
        return redirect("/")


@app.route("/play", methods=["GET", "POST"])
def play():
    if request.method=="GET":
        
        #open cursor
        conn = sqlite3.connect('players.db')
        cursor = conn.cursor()
        #find all the games a user is playing in 
        games_user_playing_in = []
        data = cursor.execute("SELECT game_id FROM playing_in WHERE player_id = ?", (session["user_id"] ,))
        for d in data:
            games_user_playing_in.append(d[0])
        

        #append all games to a list of tuples
        games = []
        data2 = cursor.execute("SELECT location, datetime, length_in_mins, number_of_players, creator, open_spots, id FROM games ORDER BY datetime")
        for d in data2:
            games.append(d)

        #iterate through list finding all games future
        list_of_games_future = []
        for g in games:
            datetimegame = datetime.strptime(g[1], '%Y-%m-%d %H:%M:%S')
            now = datetime.now()
            if datetimegame > now:
                list_of_games_future.append(g[6])
        
        
        return render_template("play.html", games=games, list_of_games_future=list_of_games_future,games_user_playing_in=games_user_playing_in)
    
    if request.method=="POST":
        player_id = session["user_id"]
        game_id = request.form.get("game_id")
        conn = sqlite3.connect('players.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO playing_in(player_id, game_id) VALUES (?, ?)", (player_id, game_id))
        cursor.execute("UPDATE games SET open_spots=open_spots-1 WHERE id = ?", (game_id, ) )
        conn.commit()
        conn.close()
        return redirect("/")



@app.route("/view_game/<int:game_id>", methods=["GET", "POST"])
def view_game(game_id:int):
    if request.method=="GET":
        conn = sqlite3.connect('players.db')
        cursor = conn.cursor()
        game = cursor.execute("SELECT location, datetime, length_in_mins, number_of_players, creator, open_spots, id FROM games WHERE id = ? ORDER BY games.datetime", (game_id, ))
        game_info = []
        for g in game:
            for x in g:
                game_info.append(x)

        line_up_list = []
        line_up_iterator = cursor.execute("SELECT playing_in.*, users.username FROM playing_in JOIN users ON users.id=playing_in.player_id WHERE game_id = ?", (game_id, ));
        for l in line_up_iterator:
            line_up_list.append(l[2])

        message_iterator = cursor.execute("SELECT date, author, content FROM messages WHERE game_id = ? ORDER BY date", (game_id, ))
        message_list = []

        for m in message_iterator:
            message_list.append(m)

        

        conn.close()
        return render_template("/view_game.html", game_info=game_info,line_up_list=line_up_list, message_list=message_list)
    
    else:
        text_message = request.form.get("message")
        conn = sqlite3.connect('players.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO messages (content, author, player_id, game_id) VALUEs (?, ?, ?, ?)", (text_message, session["username"], session["user_id"], game_id) )


        game = cursor.execute("SELECT location, datetime, length_in_mins, number_of_players, creator, open_spots, id FROM games WHERE id = ? ORDER BY games.datetime", (game_id, ))
        game_info = []
        for g in game:
            for x in g:
                game_info.append(x)

        line_up_list = []
        line_up_iterator = cursor.execute("SELECT playing_in.*, users.username FROM playing_in JOIN users ON users.id=playing_in.player_id WHERE game_id = ?", (game_id, ));
        for l in line_up_iterator:
            line_up_list.append(l[2])

        message_iterator = cursor.execute("SELECT date, author, content FROM messages WHERE game_id = ? ORDER BY date", (game_id, ))
        message_list = []

        for m in message_iterator:
            message_list.append(m)
        conn.commit()
        conn.close()
        return render_template("/view_game.html", game_info=game_info,line_up_list=line_up_list, message_list=message_list)

        



@app.route("/deregister", methods=["GET", "POST"])
def deregister():
    game_to_dereg = int(request.form.get("game_id_dereg"))
    print(game_to_dereg)
    print(session["user_id"])
    conn = sqlite3.connect('players.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM playing_in WHERE game_id = ? AND player_id = ?", (game_to_dereg, session["user_id"]))
    cursor.execute("UPDATE games SET open_spots = open_spots + 1 WHERE id = ?", (game_to_dereg, ))
    conn.commit()
    conn.close()
    return redirect ("/games")



if __name__ == "__main__":
    app.run()



    


"""
Register users - done
Login a user - done
Create a game using a from which links to games table - done
Ensure your tables and code are working with date and time in the best way - done

Register for a game using playing in table - done

Use playing in table to get the play route to return the amount of open spots for each row in the list - done

Stop a user registering for the same game twice - done
    -Use playing_in to create a list of games the player is in
    -When iterating through rows if the id is in that list don't show it

Stop a user registering for a full game - done
    - only use a register button when the open_spots is above 0


Main functionality - 
    Only show games if date is later than current date in play and games - done
    Adjust the play route to only show future games, then show a "you're in" if user already in, "full" if game is full and a button if spots are open - done
    Click on a game to show the list of players registered and any comments - done
    Create a function where the author of a game can edit the game
    Allow a user to deregister for the game
    Create a played in route showing past games

Sort teams functionality
    Score top three players after a game
    Write function to organise teams
"""