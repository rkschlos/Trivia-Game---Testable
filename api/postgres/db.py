from math import ceil
from psycopg_pool import ConnectionPool
from psycopg.errors import UniqueViolation

pool = ConnectionPool()


class DuplicateTitle(RuntimeError):
    pass


class CategoryQueries:
    def get_all_categories(self, page: int):
        with pool.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT COUNT(*) FROM categories;
                """
                )
                page_count = ceil(cursor.fetchone()[0] / 10)
                cursor.execute(
                    """
                    SELECT a.id, a.title, a.canon, COUNT(*) AS num_clues
                    FROM categories a
                    LEFT JOIN clues l ON (l.category_id = a.id)
                    GROUP BY a.id, a.title, a.canon
                    ORDER BY title
                    LIMIT 10 OFFSET %s
                """,
                    [page * 10],
                )
                rows = cursor.fetchall()
                return page_count, list(rows)

    def get_category(self, id: int):
        with pool.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id, title, canon
                    FROM categories
                    WHERE id = %s
                """,
                    [id],
                )
                return cursor.fetchone()

    def insert_category(self, title):
        with pool.connection() as connection:
            with connection.cursor() as cursor:
                try:
                    cursor.execute(
                        """
                        INSERT INTO categories(title, canon)
                        VALUES (%s, false)
                        RETURNING id, title, canon
                    """,
                        [title],
                    )
                    return cursor.fetchone()
                except UniqueViolation:
                    raise DuplicateTitle()

    def update_category(self, id, title):
        with pool.connection() as connection:
            with connection.cursor() as cursor:
                try:
                    cursor.execute(
                        """
                        UPDATE categories
                        SET title = %s
                        WHERE id = %s
                        AND canon = false
                        RETURNING id, title, canon
                    """,
                        [title, id],
                    )
                    return cursor.fetchone()
                except UniqueViolation:
                    raise DuplicateTitle()

    def delete_category(self, id):
        with pool.connection() as connection:
            with connection.cursor() as cursor:
                try:
                    cursor.execute(
                        """
                        DELETE FROM categories
                        WHERE id = %s
                        AND canon = false
                    """,
                        [id],
                    )
                except UniqueViolation:
                    raise DuplicateTitle()


class ClueQueries:
    def get_all_clues(self, page, value):
        query = """
            SELECT l.id
                    , l.answer
                    , l.question
                    , l.value
                    , l.invalid_count
                    , l.canon
                    , a.id
                    , a.title
                    , a.canon
            FROM clues AS l
            INNER JOIN categories AS a ON (l.category_id = a.id)
        """
        parameters = []
        if value > 0:
            query += """
                WHERE l.value = %s
            """
            parameters.append(value)
        query += """
            LIMIT 100 OFFSET %s
        """
        parameters.append(page * 100)
        print(query, parameters)
        with pool.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT COUNT(*) FROM clues
                """
                )
                page_count = ceil(cursor.fetchone()[0] / 100)
                cursor.execute(query, parameters)
                return page_count, list(cursor.fetchall())

    def get_clue(self, id):
        with pool.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT l.id
                         , l.answer
                         , l.question
                         , l.value
                         , l.invalid_count
                         , l.canon
                         , a.id
                         , a.title
                         , a.canon
                    FROM clues AS l
                    INNER JOIN categories AS a ON (l.category_id = a.id)
                    WHERE l.id = %s
                """,
                    [id],
                )
                return cursor.fetchone()

    def get_random_clue(self, count=1):
        with pool.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT l.id
                         , l.answer
                         , l.question
                         , l.value
                         , l.invalid_count
                         , l.canon
                         , a.id
                         , a.title
                         , a.canon
                    FROM clues AS l
                    INNER JOIN categories AS a ON (l.category_id = a.id)
                    ORDER BY RANDOM()
                    LIMIT %s
                """,
                    [count],
                )
                if count == 1:
                    return cursor.fetchone()
                return list(cursor.fetchall())

    def increment_invalid_count(self, id):
        with pool.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE clues
                    SET invalid_count = COALESCE(invalid_count, 0) + 1
                    WHERE id = %s
                """,
                    [id],
                )
        return self.get_clue(id)


class GameQueries:
    def get_game(self, id):
        with pool.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT g.id, g.episode_id, g.aired, g.canon, SUM(COALESCE(c.value, 0))
                    FROM games g
                    LEFT JOIN clues c ON (g.id = c.game_id)
                    WHERE g.id = %s
                    GROUP BY g.id, g.episode_id, g.aired, g.canon
                """,
                    [id],
                )
                return cursor.fetchone()


class CustomGameQueries:
    def create(self):
        clue_queries = ClueQueries()
        clues = clue_queries.get_random_clue(30)
        with pool.connection() as connection:
            with connection.cursor() as cursor:
                with connection.transaction():
                    cursor.execute(
                        """
                        INSERT INTO game_definitions(created_on)
                        VALUES (CURRENT_TIMESTAMP)
                        RETURNING id;
                    """
                    )
                    new_game_id = cursor.fetchone()[0]
                    for clue_row in clues:
                        cursor.execute(
                            """
                            INSERT INTO game_definition_clues (game_definition_id, clue_id)
                            VALUES (%s, %s);
                        """,
                            [new_game_id, clue_row[0]],
                        )
                cursor.execute(
                    """
                    SELECT l.id
                         , l.answer
                         , l.question
                         , l.value
                         , l.invalid_count
                         , l.canon
                         , a.id
                         , a.title
                         , a.canon
                         , g.id
                         , g.created_on
                    FROM game_definitions AS g
                    INNER JOIN game_definition_clues AS gdc ON (g.id = gdc.game_definition_id)
                    INNER JOIN clues AS l ON (gdc.clue_id = l.id)
                    INNER JOIN categories AS a ON (l.category_id = a.id)
                    WHERE g.id = %s
                """,
                    [new_game_id],
                )
                return list(cursor.fetchall())

    def get_custom_game(self, id):
        with pool.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT l.id
                         , l.answer
                         , l.question
                         , l.value
                         , l.invalid_count
                         , l.canon
                         , a.id
                         , a.title
                         , a.canon
                         , g.id
                         , g.created_on
                    FROM game_definitions AS g
                    INNER JOIN game_definition_clues AS gdc ON (g.id = gdc.game_definition_id)
                    INNER JOIN clues AS l ON (gdc.clue_id = l.id)
                    INNER JOIN categories AS a ON (l.category_id = a.id)
                    WHERE g.id = %s
                """,
                    [id],
                )
                return list(cursor.fetchall())
