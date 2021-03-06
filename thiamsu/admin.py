import os
from collections import OrderedDict

from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import AdminTextInputWidget
from django.utils.translation import ugettext_lazy as _
from embed_video.admin import AdminVideoMixin, AdminVideoWidget
from embed_video.fields import EmbedVideoField
from social_django.models import Association, Nonce, UserSocialAuth
from solo.admin import SingletonModelAdmin

from thiamsu.forms import SongAdminForm
from thiamsu.models.hanzi_hanlo_mapping import HanziHanloMapping
from thiamsu.models.headline import Headline
from thiamsu.models.new_word import NewWord
from thiamsu.models.privacy_policy import PrivacyPolicy
from thiamsu.models.song import Song
from thiamsu.models.translation import Translation


class HanziHanloMappingAdmin(admin.ModelAdmin):
    list_display = ("hanzi", "hanlo")
    search_fields = ("hanzi",)


class HeadlineAdmin(admin.ModelAdmin):
    list_display = ("song", "start_time", "end_time")

    raw_id_fields = ("song",)
    autocomplete_lookup_fields = {"fk": ["song"]}


class NewWordInline(admin.StackedInline):
    model = NewWord

    extra = 0
    classes = ("grp-collapse grp-open",)
    inline_classes = ("grp-collapse grp-open",)


class AdminVideoTextInputWidget(AdminTextInputWidget, AdminVideoWidget):
    pass


class AdminVideoTextInputMixin(AdminVideoMixin):
    def formfield_for_dbfield(self, db_field, **kwargs):
        if isinstance(db_field, EmbedVideoField):
            return db_field.formfield(widget=AdminVideoTextInputWidget)

        return super(AdminVideoMixin, self).formfield_for_dbfield(db_field, **kwargs)


class PrivacyPolicyAdmin(SingletonModelAdmin):
    class Media:
        js = ["thiamsu/js/tinymce/tinymce.min.js", "thiamsu/js/tinymce_settings.js"]


class SongAdmin(AdminVideoTextInputMixin, admin.ModelAdmin):
    LYRIC_FIELD_LABEL_PREFIX = _("song_original_lyrics")
    LYRIC_FIELD_LABEL_LINE_NO_TMPL = _("line no %d")
    LYRIC_FIELD_NAME_PREFIX = "original_lyrics_line_"
    LYRIC_FIELD_NAME_LINE_NO_TMPL = "%04d"
    LYRIC_MAX_LENGTH = 100

    list_display = ("original_title", "performer", "progress", "created_at")
    search_fields = ("original_title", "performer")
    form = SongAdminForm
    inlines = [NewWordInline]

    def get_form(self, request, obj=None, **kwargs):
        if obj is None:
            self.exclude = ("progress", "title_alias", "performer_alias")
        else:
            self.exclude = (
                "progress",
                "title_alias",
                "performer_alias",
                "original_lyrics",
            )

        # reset declared_fields
        self.form.declared_fields = OrderedDict()
        return super().get_form(request, obj, **kwargs)

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        if obj is None:  # add song
            return fields

        # change song
        for i, lyric in enumerate(obj.original_lyrics.split(os.linesep), start=1):
            label = self.LYRIC_FIELD_LABEL_PREFIX + (
                self.LYRIC_FIELD_LABEL_LINE_NO_TMPL % i
            )
            name = self.LYRIC_FIELD_NAME_PREFIX + (
                self.LYRIC_FIELD_NAME_LINE_NO_TMPL % i
            )
            lyric = lyric.strip()

            # append to fields if not added
            if name not in fields:
                fields.append(name)

            # add to form declared fields if not added
            if name not in self.form.declared_fields:
                self.form.declared_fields[name] = forms.CharField(
                    label=label,
                    max_length=self.LYRIC_MAX_LENGTH,
                    initial=lyric,
                    required=bool(lyric),
                    widget=AdminVideoTextInputWidget,
                )

            # update field value if added
            else:
                self.form.declared_fields[name].initial = lyric

            # disable blank line
            if not self.form.declared_fields[name].initial:
                self.form.declared_fields[name].initial = ""
                self.form.declared_fields[name].disabled = True

        return fields

    def save_changed_original_lyrics(self, request, obj, form, change):
        def lyrics_changed(form):
            for c in form.changed_data:
                if c.startswith(self.LYRIC_FIELD_NAME_PREFIX):
                    return True
            return False

        if lyrics_changed(form):
            lyric_fields = [
                f
                for f in form.cleaned_data
                if f.startswith(self.LYRIC_FIELD_NAME_PREFIX)
            ]
            lyrics = os.linesep.join(
                [form.cleaned_data[f] for f in sorted(lyric_fields)]
            )
            obj.original_lyrics = lyrics
        obj.save()

    def save_model(self, request, obj, form, change):
        self.save_changed_original_lyrics(request, obj, form, change)
        return super().save_model(request, obj, form, change)


class TranslationAdmin(admin.ModelAdmin):
    list_display = (
        "song",
        "line_no",
        "content",
        "original_lyric",
        "lang",
        "created_at",
    )

    search_fields = ("song__original_title",)

    change_list_template = "admin/change_list_filter_sidebar.html"
    change_list_filter_template = "admin/filter_listing.html"
    list_filter = ("lang",)


admin.site.unregister(Association)
admin.site.unregister(Nonce)
admin.site.unregister(UserSocialAuth)
admin.site.register(HanziHanloMapping, HanziHanloMappingAdmin)
admin.site.register(Headline, HeadlineAdmin)
admin.site.register(PrivacyPolicy, PrivacyPolicyAdmin)
admin.site.register(Song, SongAdmin)
admin.site.register(Translation, TranslationAdmin)
