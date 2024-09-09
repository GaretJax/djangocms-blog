from django.conf import settings
from django.db import migrations, models


class BareVersion:
    """Patches the save method of a model to standard model save."""
    def __init__(self, model):
        self.model = model

    def __enter__(self):
        self.original_save_method = self.model.save
        self.model.save = models.Model.save
        return self.model

    def __exit__(self, exc_type, exc_value, traceback):
        self.model.save = self.original_save_method


def move_plugins(source, content, content_type):
    if source:
        new_placeholder = source.__class__.objects.create(
            slot=source.slot,
            default_width=source.default_width,
            content_type=content_type,
            object_id=content.pk,
        )
        source.cmsplugin_set.filter(language=content.language).update(placeholder=new_placeholder)


def move_plugins_to_blog_content(apps, schema_editor):
    """Adds instances for the new model.
    ATTENTION: All fields of the model must have a valid default value!"""

    User = apps.get_model(*settings.AUTH_USER_MODEL.split("."))
    Post = apps.get_model("djangocms_blog", "Post")
    PostContent = apps.get_model("djangocms_blog", "PostContent")
    ContentType = apps.get_model("contenttypes", "ContentType")
    content_type, _ = ContentType.objects.get_or_create(app_label="djangocms_blog", model="postcontent")

    versioning_installed = apps.is_installed("djangocms_versioning")
    if versioning_installed:
        if getattr(settings, "CMS_MIGRATION_USER_ID", None):
            migration_user = User.objects.get(pk=settings.CMS_MIGRATION_USER_ID)
        else:
            migration_user = User.objects.filter(is_superuser=True, is_acitve=True).first()
    else:
        migration_user = None

    for post in Post.objects.all():
        if not post.postcontent_set.exists():
            # Not yet migrated
            for translation in post.translations.all():
                print(f"Copying {translation.language_code} to post content...")
                content, created = PostContent.objects.get_or_create(
                    language=translation.language_code,
                    post=post,
                    defaults={
                        "title": translation.title,
                        "slug": translation.slug,
                        "subtitle": translation.subtitle,
                        "abstract": translation.abstract,
                        "meta_description": translation.meta_description,
                        "meta_keywords": translation.meta_keywords,
                        "meta_title": translation.meta_title,
                        "post_text": translation.post_text,
                    }
                )
                if created:
                    if versioning_installed:
                        from djangocms_versioning.constants import DRAFT, PUBLISHED

                        Version = apps.get_model("djangocms_versioning", "Version")
                        with BareVersion(Version) as Version:
                            Version.objects.create(
                                number="1",
                                content_type=content_type,  # content generic relation is not avialable in migrations
                                object_id=content.pk,
                                created_by=migration_user,
                                state=PUBLISHED if post.publish else DRAFT,
                            )
                    translation.delete()

                    move_plugins(post.media, content, content_type)
                    move_plugins(post.content, content, content_type)
                    move_plugins(post.liveblog, content, content_type)
                else:
                    print(f"Post content {translation.title} ({translation.language}) already exists, skipping...")

        if post.media:
            post.media.delete()
        if post.content:
            post.content.delete()
        if post.liveblog:
            post.liveblog.delete()


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
