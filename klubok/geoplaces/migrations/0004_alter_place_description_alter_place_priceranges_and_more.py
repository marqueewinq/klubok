# Generated by Django 4.1.3 on 2022-11-03 13:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("geoplaces", "0003_placeratingsubmission")]

    operations = [
        migrations.AlterField(
            model_name="place",
            name="description",
            field=models.CharField(db_index=True, max_length=1024),
        ),
        migrations.AlterField(
            model_name="place",
            name="priceranges",
            field=models.ManyToManyField(
                blank=True, related_name="places", to="geoplaces.placepricerange"
            ),
        ),
        migrations.AlterField(
            model_name="place",
            name="tags",
            field=models.ManyToManyField(
                blank=True, related_name="places", to="geoplaces.placetag"
            ),
        ),
        migrations.AlterField(
            model_name="place",
            name="title",
            field=models.CharField(db_index=True, max_length=255),
        ),
        migrations.AlterField(
            model_name="place",
            name="types",
            field=models.ManyToManyField(
                blank=True, related_name="places", to="geoplaces.placetype"
            ),
        ),
        migrations.AddIndex(
            model_name="place",
            index=models.Index(
                fields=["title", "description"], name="geoplaces_p_title_f62fd9_idx"
            ),
        ),
    ]