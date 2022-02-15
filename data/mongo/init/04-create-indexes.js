conn = Mongo();
db = conn.getDB('trivia-game');

db.clues.createIndex(
  { category_id: 1 }
);

db.categories.createIndex(
  { title: 1 }, { unique: true }
);
