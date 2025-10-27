from django.db import migrations

def seed_plans(apps, schema_editor):
    Plan = apps.get_model('planes', 'Plan')
    defaults = [
        # Primaria
        dict(nombre='Primaria - Matemática', nivel='primaria', area='matematica'),
        dict(nombre='Primaria - Matemática + Comunicación', nivel='primaria', area='ambos'),

        # Secundaria
        dict(nombre='Secundaria - Matemática', nivel='secundaria', area='matematica'),
        dict(nombre='Secundaria - Comunicación', nivel='secundaria', area='comunicacion'),
    ]
    for d in defaults:
        Plan.objects.update_or_create(
            nivel=d['nivel'], area=d['area'],
            defaults={**d, 'activo': True}
        )

def unseed_plans(apps, schema_editor):
    Plan = apps.get_model('planes', 'Plan')
    Plan.objects.filter(
        nombre__in=[
            'Primaria - Matemática',
            'Primaria - Matemática + Comunicación',
            'Secundaria - Matemática',
            'Secundaria - Comunicación',
            'Secundaria - Matemática + Comunicación',
        ]
    ).delete()

class Migration(migrations.Migration):
    dependencies = [
        ('planes', '0001_initial'),
    ]
    operations = [
        migrations.RunPython(seed_plans, unseed_plans),
    ]
