# Generated by Django 4.2.4 on 2023-08-14 06:07

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0005_groupchatroom_chatroom_uuid_message_uuid_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="groupchatroom",
            name="admin_user",
            field=models.ManyToManyField(
                blank=True, related_name="admins", to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AddField(
            model_name="groupchatroom",
            name="created_by",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="creator",
                to=settings.AUTH_USER_MODEL,
            ),
            preserve_default=False,
        ),
    ]
