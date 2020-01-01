from django.core.management.base import BaseCommand
import json
from django.contrib.gis.geos import fromstr
from pathlib import Path
from core.models import Shop, Author, Post, Tag
from django.db import connection


def load_posts():
    nancy = Author.objects.create(name="Nancy Blogaday")
    jim = Author.objects.create(name="Jim Blogwriter")

    databases = Tag.objects.create(name="Databases")
    programming = Tag.objects.create(name="Programming")
    python = Tag.objects.create(name="Python")
    postgres = Tag.objects.create(name="Postgres")
    django = Tag.objects.create(name="Django")

    django_post = Post.objects.create(
        title="Django, the western character",
        content="Django is a character who appears in a number of spaghetti "
        "western films.",
        author=jim,
    )
    django_post.tags.add(django)

    python_post = Post.objects.create(
        title="Python is a programming language",
        content="Python is a programming language created by Guido van Rossum "
        "and first released in 1991. Django is written in Python. Python "
        "can connect to databases.",
        author=nancy,
    )
    python_post.tags.add(django, programming, python)

    postgres_post = Post.objects.create(
        title="What is Postgres",
        content="PostgreSQL, commonly Postgres, is an open-source, "
        "object-relational database (ORDBMS).",
        author=nancy,
    )
    postgres_post.tags.add(databases, postgres)


def load_data():
    jsonfile = "data.json"

    with open(str(jsonfile)) as datafile:
        objects = json.load(datafile)
        for obj in objects["elements"]:
            try:
                objType = obj["type"]
                if objType == "node":
                    tags = obj["tags"]
                    name = tags.get("name", "no-name")
                    longitude = obj.get("lon", 0)
                    latitude = obj.get("lat", 0)
                    location = fromstr(f"POINT({longitude} {latitude})", srid=4326)
                    Shop(name=name, location=location).save()
            except KeyError:
                pass


def install_trigger():
    sql = """
                        -- Trigger on insert or update of core.Post
            CREATE OR REPLACE FUNCTION post_search_vector_trigger() RETURNS trigger AS $$
            BEGIN
            SELECT setweight(to_tsvector(NEW.title), 'A') ||
                    setweight(to_tsvector(NEW.content), 'C') ||
                    setweight(to_tsvector(author.name), 'B') ||
                    setweight(to_tsvector(COALESCE(string_agg(tag.name, ', '), '')), 'B')
            INTO NEW.search_vector
            FROM core_post AS post
            JOIN core_author AS author ON author.id = post.author_id
                LEFT JOIN core_post_tags AS post_tags ON post_tags.post_id = post.id
                LEFT JOIN core_tag AS tag ON tag.id = post_tags.tag_id
            WHERE post.id = NEW.id
            GROUP BY post.id, author.id;
            RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
            CREATE TRIGGER search_vector_update BEFORE INSERT OR UPDATE ON core_post
            FOR EACH ROW EXECUTE PROCEDURE post_search_vector_trigger();

            -- Trigger after core.Author is updated
            CREATE OR REPLACE FUNCTION author_search_vector_trigger() RETURNS trigger AS $$
            BEGIN
            UPDATE core_post SET id = id WHERE author_id = NEW.id;
            RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
            CREATE TRIGGER search_vector_update AFTER INSERT OR UPDATE ON core_author
            FOR EACH ROW EXECUTE PROCEDURE author_search_vector_trigger();

            -- Trigger after core.Post.tags are added, deleted from a post
            CREATE OR REPLACE FUNCTION tags_search_vector_trigger() RETURNS trigger AS $$
            BEGIN
            IF (TG_OP = 'DELETE') THEN
                UPDATE core_post SET id = id WHERE id = OLD.post_id;
                RETURN OLD;
            ELSE
                UPDATE core_post SET id = id WHERE id = NEW.post_id;
                RETURN NEW;
            END IF;
            END;
            $$ LANGUAGE plpgsql;
            CREATE TRIGGER search_vector_update AFTER INSERT OR UPDATE OR DELETE ON core_post_tags
            FOR EACH ROW EXECUTE PROCEDURE tags_search_vector_trigger();

            -- Trigger after core.Tag is updated
            CREATE OR REPLACE FUNCTION tag_search_vector_trigger() RETURNS trigger AS $$
            BEGIN
            UPDATE core_post SET id = id WHERE id IN (
                SELECT post_id FROM core_post_tags WHERE tag_id = NEW.id
            );
            RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
            CREATE TRIGGER search_vector_update AFTER UPDATE ON core_tag
            FOR EACH ROW EXECUTE PROCEDURE tag_search_vector_trigger();

    """
    with connection.cursor() as cursor:
        cursor.execute(sql)


class Command(BaseCommand):
    help = "fake data generator"

    def handle(self, *args, **options):

        install_trigger()
        load_data()
        load_posts()

        self.stdout.write(self.style.SUCCESS("done!"))

