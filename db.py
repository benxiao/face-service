import pymysql
import json
import numpy as np
import os


class FaceDB:
    def __init__(self, config="db.json"):
        if not os.path.isfile(config):
            raise ValueError(f"{config} not found")

        with open(config) as fp:
            json_obj = json.load(fp)
        self._conn = pymysql.connect(user=json_obj['user'],
                                     password=json_obj['password'],
                                     database=json_obj['database'],
                                     port=json_obj['port'],
                                     host=json_obj['host'])

    def clear(self):
        with self._conn.cursor() as cursor:
            cursor.execute("""
                drop table if exists person
            """)
            cursor.execute("""
                create table person (
                    id serial primary key,
                    name VARCHAR(100) unique not null,
                    encoding json not null
                )
            """)

    def __len__(self):
        with self._conn.cursor() as cursor:
            cursor.execute("select count(*) from person")
            return cursor.fetchone()[0]

    def load_encodings(self):
        with self._conn.cursor() as cursor:
            cursor.execute("select * from person")
            ret = {}
            for _, name, encoding in cursor.fetchall():
                ret[name] = np.array(json.loads(encoding))
        return ret

    def populate_with_sample_data(self):
        self.remember("ben", [1, 2, 3, 4])
        self.remember("alex", [3, 1, 2, 4])
        self.remember("kian", [4, 1, 2, 3])

    def remember(self, name, encoding):
        with self._conn.cursor() as cursor:
            json_str = json.dumps(list(encoding))
            cursor.execute(
                """
                    insert into person (name, encoding) values (%s, %s)
                """, (name, json_str)
            )
        self._conn.commit()

    def forget(self, name):
        with self._conn.cursor() as cursor:
            cursor.execute(
                """
                    delete from person where name = %s
                """, (name,)
            )
        self._conn.commit()

    def __del__(self):
        self._conn.close()


if __name__ == '__main__':
    face_db = FaceDB()
    face_db.clear()
    face_db.populate_with_sample_data()
    print(face_db.load_encodings())
