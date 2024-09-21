# Generated by Django 3.0.14 on 2021-11-28 14:03

import django.db.models.deletion
import filer.fields.image
from django.conf import settings
from django.db import migrations, models

import djangocms_blog.models


class Migration(migrations.Migration):
    dependencies = [
        ("djangocms_blog", "0040_post_include_in_rss"),
    ]

    operations = [
        migrations.AddField(
            model_name="blogcategory",
            name="main_image",
            field=filer.fields.image.FilerImageField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="djangocms_category_image",
                to=settings.FILER_IMAGE_MODEL,
                verbose_name="main image",
            ),
        ),
        migrations.AddField(
            model_name="blogcategory",
            name="main_image_full",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="djangocms_category_full",
                to="filer.ThumbnailOption",
                verbose_name="main image full",
            ),
        ),
        migrations.AddField(
            model_name="blogcategory",
            name="main_image_thumbnail",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="djangocms_category_thumbnail",
                to="filer.ThumbnailOption",
                verbose_name="main image thumbnail",
            ),
        ),
        migrations.AddField(
            model_name="blogcategory",
            name="priority",
            field=models.IntegerField(blank=True, null=True, verbose_name="priority"),
        ),
        migrations.AddField(
            model_name="blogcategorytranslation",
            name="abstract",
            field=djangocms_blog.models.HTMLField(blank=True, default="", verbose_name="abstract"),
        ),
        migrations.AddField(
            model_name="post",
            name="pinned",
            field=models.IntegerField(blank=True, null=True, verbose_name="priority"),
        ),
    ]
