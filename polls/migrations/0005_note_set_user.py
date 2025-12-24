from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('polls', '0004_noteset_subject'),
    ]

    operations = [
        migrations.AddField(
            model_name='note_set',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='note_sets', to=settings.AUTH_USER_MODEL),
        ),
    ]
