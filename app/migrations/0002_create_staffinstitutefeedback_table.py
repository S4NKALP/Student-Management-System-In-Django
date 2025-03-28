from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            """
            CREATE TABLE IF NOT EXISTS "app_staffinstitutefeedback" (
                "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                "feedback_type" integer NOT NULL,
                "feedback_text" text NOT NULL,
                "rating" integer NOT NULL,
                "is_anonymous" bool NOT NULL,
                "created_at" datetime NOT NULL,
                "staff_id" integer NOT NULL REFERENCES "app_staff" ("id") DEFERRABLE INITIALLY DEFERRED
            );
            """,
            "DROP TABLE IF EXISTS app_staffinstitutefeedback;"
        ),
    ] 