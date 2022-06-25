# Generated by Django 3.2.3 on 2021-06-29 19:39

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='faculty',
            fields=[
                ('name', models.CharField(max_length=50)),
                ('email', models.EmailField(max_length=254, primary_key=True, serialize=False)),
                ('dob', models.DateField()),
                ('address', models.CharField(max_length=300)),
                ('password', models.CharField(default='None', max_length=1000)),
                ('profilePic', models.ImageField(null=True, upload_to='')),
                ('isActive', models.BooleanField(null=True)),
            ],
        ),
    ]
