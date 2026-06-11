# Generated manually for library loan data integrity.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loans', '0001_initial'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='loan',
            constraint=models.UniqueConstraint(
                fields=('book_instance',),
                condition=models.Q(('actual_return_date__isnull', True)),
                name='unique_active_loan_per_book_instance',
            ),
        ),
    ]
