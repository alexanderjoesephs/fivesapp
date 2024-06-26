# Fives
#### Video Demo:  <URL https://youtu.be/ieNW6zg1IcA>
#### Description:
This is an app that allows users to register for small sided football games. Users can use the create option to create a game. The play option will then return a list of games that other players have created and they can register for. If they click on the game it takes them to a link where they can see the other players playing and post on a message board. Finally, if they go to games they can see a list of games they're playing in and a list of past games they've yet to play in.

I used flask and python to run the app, similar to finance in pset9. However, I used it on my PC rather than the codespace so I had to download python, flask and flask session. I also used the python sql module rather than the CS50 one which returns SELECT statements as iterators rather than lists of dictionaries. Finding out what these iterators were and how to use them was quite a big challenge.

I decided I wanted an app where users could message each other so used a sql table to implement a message wall on the route that returns information for a game. One challenge was to use CSS to style this message wall differently to the other tables so it was clear it was a distinct feature.

I was pleased with the look of the project and the fact that using sql statements allowed me to figure out how many open spots are in the game and return a list of the players playing. This functionality would make the app really useful for people trying to make sure they have enough players. I think to improve it further the option to vote for a player of the match would be good and to keep this infomration would be a feature users might want.

I enjoyed learning more about sql, expecially seeing how these databases could be used to implement things like message walls where you can send a message and a few columns like date and author can help show that message in the right place in the website.

The app has two options when you first visit the site, register and login. Register uses an html form to take a username, first and last name and a password. The python code will check the username against the database to see if it's unique and will check the password matches the confirmation. The log in feature logs a user in using the session part of flask.

The play option allows a user to register for a number of games. These games are stored in a database and have different IDs. They also have different numbers of players and open spots. If there are spots open and a user isn;t already registered for a game the html will render a button to allow the users to register. Once the user registers they are added to a playing in table with the game so the app can track who is playing in which game. The amount of open spots for the game is also incremented down by one. This is important as when it reaches 0 the html will not register a play button but will instead simply say 'full game'.

The games option shows all the games a user is registered for ordered by time. They can also click on the game to return a list of the players playing, information about how many spots remain open and a message board. They can post a message to the board using a form at the bottom of the page. This is all handled by a sql database which tracks the content, the game the message is relevant to and the timestamp used to order messages so they can be rendered in order of the time they sent. This is sytled differently to the other tables so it's clear it is a different feature of the app.

Fianlly there is a create option which allows the user to create a game. They can enter a date, location, time and choose from a few options for the length of the game. This game will then be inserted into the games database so users can register for it from the play section or post messages to discuss the games location, teams or any other important inofrmation.
