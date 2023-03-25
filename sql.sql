SELECT * FROM messages;

UPDATE messages SET content = "Hey how are you?"  WHERE content = "Hi Pedders how's it going?";

UPDATE messages SET content = "Hi everyone" WHERE content = "I'm not sure if I can make it guys I might be ovulating";

UPDATE games SET creator = "Jon"  WHERE creator = "Jake"

SELECT playing_in.player_id, games.location, games.datetime, games.length_in_mins, games.creator FROM playing_in JOIN users ON users.id = playing_in.player_id JOIN games ON games.id = playing_in.game_id WHERE playing_in.player_id = 9;

SELECT playing_in.player_id, games.location, games.datetime, games.length_in_mins, games.creator FROM playing_in JOIN users ON users.id = playing_in.player_id JOIN games ON games.id = playing_in.game_id;





