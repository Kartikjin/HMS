# Generated by Django 3.2.2 on 2021-06-27 14:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admins', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hospitaldoctors',
            name='status',
            field=models.CharField(choices=[('applied', 'Applied'), ('rejected', 'Rejected'), ('approved', 'Approved'), ('laidoff', 'Laid-off')], max_length=10),
        ),
    ]
