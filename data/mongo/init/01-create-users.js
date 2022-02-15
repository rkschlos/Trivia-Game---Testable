conn = Mongo();
db = conn.getDB('trivia-game');
db.createUser(
  {
    user: 'trivia-game-user',
    pwd: 'secret',
    roles: [
      {role: 'readWrite', db: 'trivia-game',}
    ]
  }
)
