from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import migrations, models

User = get_user_model()


class BareVersion:
    """Patches the save method of a model to standard model save."""
    def __init__(self, model):
        self.model = model

    def __enter__(self):
        self.save_method = self.model.save
        self.model.save = lambda self, *args, **kwargs: super(models.Model, self).save(*args, **kwargs)
        return self.model

    def __exit(self, exc_type, exc_value, traceback):
        self.model.save = self.save_method


def move_plugins_to_blog_content(apps, schema_editor):
    """Adds instances for the new model.
    ATTENTION: All fields of the model must have a valid default value!"""

    versioning_installed = apps.is_installed("djangocms_versioning")
    if versioning_installed:
        if getattr(settings, "CMS_MIGRATION_USER_ID", None):
            migration_user = User.objects.get(pk=settings.CMS_MIGRATION_USER_ID)
        else:
            migration_user = User.objects.filter(is_superuser=True, is_acitve=True).first()
    else:
        migration_user = None

    Post = apps.get_model("djangocms_blog", "Post")
    PostContent = apps.get_model("djangocms_blog", "PostContent")
    ContentType = apps.get_model("contenttypes", "ContentType")
    content_type, _ = ContentType.objects.get_or_create(app_label="djangocms_blog", model="postcontent")

    for post in Post.objects.all():
        if not post.postcontent_set.exists():
            # Not yet migrated
            for translation in post.translations.all():
                print(f"Copying {translation.language_code} to post content...")
                content = PostContent(
                    language=translation.language_code,
                    title=translation.title,
                    slug=translation.slug,
                    subtitle=translation.subtitle,
                    abstract=translation.abstract,
                    meta_description=translation.meta_description,
                    meta_keywords=translation.meta_keywords,
                    meta_title=translation.meta_title,
                    post_text=translation.post_text,
                    post=post,
                )
                content.save()  # This does not create a Version object even if versioning is installed
                if versioning_installed:
                    from djangocms_versioning.constants import DRAFT, PUBLISHED

                    Version = apps.get_model("djangocms_versioning", "Version")
                    with BareVersion(Version) as Version:
                        Version.objects.create(
                            number="1",
                            content=content,
                            created_by=migration_user,
                            state=PUBLISHED if post.publish else DRAFT,
                        )
                translation.delete()

                if post.media:
                    post.media.content_type = content_type
                    post.media.object_id = content.pk
                    post.media.save()
                if post.content:
                    post.content.content_type = content_type
                    post.content.object_id = content.pk
                    post.content.save()
                if post.liveblog:
                    post.liveblog.content_type = content_type
                    post.liveblog.object_id = content.pk
                    post.liveblog.save()


def move_plugins_back_to_blog(apps, schema_editor):
    """Adds instances for the new model.ATTENTION: All fields of the model must have a valid default value!"""
    raise NotImplementedError()


class Migration(migrations.Migration):
    dependencies = [
        ("djangocms_blog", "0043_postcontent"),
    ]

    operations = [
        migrations.RunPython(move_plugins_to_blog_content, move_plugins_back_to_blog, elidable=True),
    ]
