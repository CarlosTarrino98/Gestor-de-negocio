from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('base', '0014_alter_factura_direccion_emisor'),
    ]

    operations = [
        migrations.CreateModel(
            name='FacturasIVA',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('proveedor', models.CharField(max_length=100)),
                ('numero_factura', models.CharField(max_length=50)),
                ('fecha', models.DateField()),
                ('total', models.DecimalField(decimal_places=2, max_digits=10)),
                ('pagada', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ['-fecha'],
            },
        ),
        migrations.CreateModel(
            name='FacturaTienda',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('proveedor', models.CharField(max_length=100)),
                ('fecha', models.DateField()),
                ('total', models.DecimalField(decimal_places=2, max_digits=10)),
            ],
            options={
                'ordering': ['-fecha'],
            },
        ),
    ]
