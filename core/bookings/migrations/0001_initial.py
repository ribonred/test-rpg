# Generated by Django 4.2.4 on 2023-08-11 06:56

from django.db import migrations, models
import django.db.models.deletion
import django_lifecycle.mixins


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("rooms", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="BookingEvent",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created", models.DateTimeField(editable=False)),
                ("updated", models.DateTimeField(editable=False)),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
                (
                    "rpg_status",
                    models.IntegerField(
                        choices=[(1, "Booking"), (2, "Cancellation")], default=1
                    ),
                ),
                ("night_of_stay", models.DateField()),
                (
                    "room",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="bookings",
                        to="rooms.room",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=(models.Model, django_lifecycle.mixins.LifecycleModelMixin),
        ),
    ]
