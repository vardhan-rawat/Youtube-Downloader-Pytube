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

from django.http import JsonResponse

def download(request):
    if request.method == "GET":
        try:
            obj = YouTube(request.GET.get('url'))
            title = obj.title
            thumbnail = obj.thumbnail_url
            data = {
                "title": title,
                "thumbnail": thumbnail,
            }
            return render(request, "download.html", data)
        except Exception:
            return redirect('goback_with_error')

    elif request.method == "POST":
        try:
            obj = YouTube(request.GET.get('url'))
            title = obj.title

            video_stream = None
            if '720p' in request.POST:
                video_stream = obj.streams.filter(progressive=True, file_extension='mp4', res='720p').order_by('resolution').desc().first()
            elif '360p' in request.POST:
                video_stream = obj.streams.filter(progressive=True, file_extension='mp4', res='360p').order_by('resolution').desc().first()
            elif '1080pns' in request.POST:
                video_stream = obj.streams.filter(only_video=True, file_extension='mp4', res='1080p').order_by('resolution').desc().first()    
            elif '720pns' in request.POST:
                video_stream = obj.streams.filter(only_video=True, file_extension='mp4', res='720p').order_by('resolution').desc().first()
            elif '360pns' in request.POST:
                video_stream = obj.streams.filter(only_video=True, file_extension='mp4', res='360p').order_by('resolution').desc().first()
            elif 'audio' in request.POST:
                video_stream = obj.streams.filter(only_audio=True, file_extension='mp4', abr='128kbps').first()
            
            if video_stream:
                video_bytes = io.BytesIO()
                video_stream.stream_to_buffer(video_bytes)
                video_bytes.seek(0)
                response = HttpResponse(video_bytes, content_type='video/mp4')
                response['Content-Disposition'] = f'attachment; filename="{title}.mp4"'
                response['X-Download-Success'] = 'true'
                return response
            else:
                raise Exception("No suitable stream found")

        except Exception:
            return JsonResponse({'error': 'Error downloading video'}, status=500)

    return redirect('searching')

def goback_with_error(request):
    return render(request, "goback.html", {"error_message": "An error occurred. Please try again."})