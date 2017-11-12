from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect

from thiamsu.forms import TranslationFormSet
from thiamsu.models.song import Song
from thiamsu.models.translation import Translation


def home(request):
    songs = Song.objects.order_by('original_title')
    paginator = Paginator(songs, settings.PAGINATION_MAX_ITMES_PER_PAGE)
    return render(request, 'thiamsu/song_list.html', {
        'songs': paginator.page(1),
    })


def search(request):
    query = request.GET.get('q', '')
    if query == '':
        return redirect('/')

    query_type = request.GET.get('type', '')
    if query_type not in ['song-title', 'performer']:
        return redirect('/')

    if query_type == 'song-title':
        filtered_songs = Song.objects.filter(
            Q(original_title__contains=query) |
            Q(hanzi_title__contains=query) |
            Q(tailo_title__contains=query))
    else:  # performer
        filtered_songs = Song.objects.filter(
            Q(performer__contains=query))

    paginator = Paginator(
        filtered_songs, settings.PAGINATION_MAX_ITMES_PER_PAGE)
    return render(request, 'thiamsu/song_list.html', {
        'query': query,
        'songs': paginator.page(1),
    })


def song_detail(request, id):
    try:
        song = Song.objects.get(id=id)
    except ObjectDoesNotExist:
        return redirect('/')

    return render(request, 'thiamsu/song_detail.html', {
        'song': song,
        'lyrics': [{
            'original': lyric,
            'translation': 'siâ-khì，si-tshàu，môo-sîn-á'
        } for lyric in song.original_lyrics.split('\n')],
    })


def song_edit(request, id):
    try:
        song = Song.objects.get(id=id)
    except ObjectDoesNotExist:
        return redirect('/')

    lyrics = song.get_lyrics_with_translations()

    forms = {}
    for lang in ['tailo', 'hanzi']:
        forms[lang] = TranslationFormSet(
            original_lyrics=[lyric['original'] for lyric in lyrics if lyric['original']],
            initial=[{
                'line_no': line_no,
                'lang': lang,
                'content': lyric[lang]
            } for line_no, lyric in enumerate(lyrics) if lyric['original']])

    return render(request, 'thiamsu/song_edit.html', {
        'song': song,
        'forms': forms
    })


def song_translation_post(request, id):
    if request.method != 'POST':
        return redirect('/')
    try:
        song = Song.objects.get(id=id)
    except ObjectDoesNotExist:
        return redirect('/')

    formset = TranslationFormSet(data=request.POST)
    for form in formset:
        # validate data
        if not form.is_valid():
            continue
        if not form.cleaned_data['content']:
            continue

        # compare with current
        update_translation = False
        try:
            current_translation = (
                Translation.objects
                .filter(song=song)
                .filter(line_no=form.cleaned_data['line_no'])
                .filter(lang=form.cleaned_data['lang'])
                .latest('created_at')
            )
        except ObjectDoesNotExist:
            update_translation = True
        else:
            if form.cleaned_data['content'] != current_translation.content:
                update_translation = True

        # update
        if update_translation is True:
            new_translation = Translation(
                song=song,
                line_no=form.cleaned_data['line_no'],
                lang=form.cleaned_data['lang'],
                content=form.cleaned_data['content'],
                contributor=request.user if request.user.is_authenticated() else None
            )
            new_translation.save()

    return HttpResponseRedirect(reverse('song_edit', kwargs={'id': id}))
