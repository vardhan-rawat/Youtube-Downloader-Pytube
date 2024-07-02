from django.http import HttpResponse
from django.shortcuts import render, redirect
from pytube import YouTube
from urllib.parse import urlencode
from django.urls import reverse
import io


def searching(request):
    if request.method == "POST":
        url = request.POST['linkinp']
        query_params = urlencode({'url': url})
        target_url = reverse('download') + f'?{query_params}'

        return redirect(target_url)
    return render(request, "index.html")

def download(request):
    try:
        obj = YouTube(request.GET.get('url'))
        title = obj.title
        thumbnail = obj.thumbnail_url
        data = {
            "title": title,
            "thumbnail": thumbnail,
        }

        video_stream = None
        if '720p' in request.POST:
            video_stream = obj.streams.filter(progressive=True, file_extension='mp4', res='720p').order_by('resolution').desc().first()
        elif '360p' in request.POST:
            video_stream = obj.streams.filter(progressive=True, file_extension='mp4', res='360p').order_by('resolution').desc().first()
        elif '720pns' in request.POST:
            video_stream = obj.streams.filter(only_video=True, file_extension='mp4', res='720p').order_by('resolution').desc().first()
        elif '360pns' in request.POST:
            video_stream = obj.streams.filter(only_video=True, file_extension='mp4', res='360p').order_by('resolution').desc().first()
        
        if video_stream:
            video_bytes = io.BytesIO()
            video_stream.stream_to_buffer(video_bytes)
            video_bytes.seek(0)
            response = HttpResponse(video_bytes, content_type='video/mp4')
            response['Content-Disposition'] = f'attachment; filename="{title}.mp4"'
            return response

    except Exception as e:
        print(f"Error: {e}")
        return render(request, "goback.html")

    return render(request, "download.html", data)
