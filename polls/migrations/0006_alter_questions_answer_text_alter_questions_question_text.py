from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0005_note_set_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='questions',
            name='answer_text',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='questions',
            name='question_text',
            field=models.TextField(),
        ),
    ]
