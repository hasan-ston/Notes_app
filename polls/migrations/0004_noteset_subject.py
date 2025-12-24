from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0003_note_set_questions_delete_task'),
    ]

    operations = [
        migrations.AddField(
            model_name='note_set',
            name='subject',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
