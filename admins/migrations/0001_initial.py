# Generated by Django 3.2.2 on 2021-06-27 09:56

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AdminAdditional',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hospital_name', models.CharField(max_length=100)),
                ('hospital_address', models.CharField(max_length=100)),
                ('is_recruiting', models.BooleanField(blank=True, default=False)),
            ],
        ),
        migrations.CreateModel(
            name='HospitalDoctors',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('applied', 'Applied'), ('rejected', 'Rejected'), ('approved', 'Approved')], max_length=10)),
            ],
        ),
    ]