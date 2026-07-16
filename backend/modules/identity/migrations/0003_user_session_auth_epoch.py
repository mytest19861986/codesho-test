from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("identity", "0002_passcodecredential")]

    operations = [
        migrations.AddField(
            model_name="user",
            name="session_auth_epoch",
            field=models.PositiveBigIntegerField(default=1),
        )
    ]
