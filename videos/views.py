from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from pytube import YouTube
# from pytubefix import YouTube
from urllib.parse import urlencode
from django.urls import reverse
import io

from pytube.innertube import _default_clients
from pytube import cipher
import re

_default_clients["ANDROID"]["context"]["client"]["clientVersion"] = "19.08.35"
_default_clients["IOS"]["context"]["client"]["clientVersion"] = "19.08.35"
_default_clients["ANDROID_EMBED"]["context"]["client"]["clientVersion"] = "19.08.35"
_default_clients["IOS_EMBED"]["context"]["client"]["clientVersion"] = "19.08.35"
_default_clients["IOS_MUSIC"]["context"]["client"]["clientVersion"] = "6.41"
_default_clients["ANDROID_MUSIC"] = _default_clients["ANDROID_CREATOR"]



def get_throttling_function_name(js: str) -> str:
    """Extract the name of the function that computes the throttling parameter.

    :param str js:
        The contents of the base.js asset file.
    :rtype: str
    :returns:
        The name of the function used to compute the throttling parameter.
    """
    function_patterns = [
        r'a\.[a-zA-Z]\s*&&\s*\([a-z]\s*=\s*a\.get\("n"\)\)\s*&&\s*'
        r'\([a-z]\s*=\s*([a-zA-Z0-9$]+)(\[\d+\])?\([a-z]\)',
        r'\([a-z]\s*=\s*([a-zA-Z0-9$]+)(\[\d+\])\([a-z]\)',
    ]
    #logger.debug('Finding throttling function name')
    for pattern in function_patterns:
        regex = re.compile(pattern)
        function_match = regex.search(js)
        if function_match:
            #logger.debug("finished regex search, matched: %s", pattern)
            if len(function_match.groups()) == 1:
                return function_match.group(1)
            idx = function_match.group(2)
            if idx:
                idx = idx.strip("[]")
                array = re.search(
                    r'var {nfunc}\s*=\s*(\[.+?\]);'.format(
                        nfunc=re.escape(function_match.group(1))),
                    js
                )
                if array:
                    array = array.group(1).strip("[]").split(",")
                    array = [x.strip() for x in array]
                    return array[int(idx)]

    raise YouTube.RegexMatchError(
        caller="get_throttling_function_name", pattern="multiple"
    )

cipher.get_throttling_function_name = get_throttling_function_name


def searching(request):
    if request.method == "POST":
        url = request.POST.get('linkinp')
        if url:
            query_params = urlencode({'url': url})
            target_url = reverse('download') + f'?{query_params}'
            return redirect(target_url)
        else:
            return redirect('goback_with_error')
    return render(request, "index.html")


def download(request):
    if request.method == "GET":
        url = request.GET.get('url')
        if url:
            try:
                obj = YouTube(url)
                title = obj.title
                thumbnail = obj.thumbnail_url
                data = {
                    "title": title,
                    "thumbnail": thumbnail,
                }
                return render(request, "download.html", data)
            except Exception as e:
                return redirect('goback_with_error')
        else:
            return redirect('goback_with_error')

    elif request.method == "POST":
        url = request.GET.get('url')
        if url:
            try:
                obj = YouTube(url)
                title = obj.title

                # Determine the requested stream
                video_stream = None
                if '720p' in request.POST:
                    video_stream = obj.streams.filter(progressive=True, file_extension='mp4', res='720p').first()
                elif '360p' in request.POST:
                    video_stream = obj.streams.filter(progressive=True, file_extension='mp4', res='360p').first()
                elif '1080pns' in request.POST:
                    video_stream = obj.streams.filter(only_video=True, file_extension='mp4', res='1080p').first()
                elif '720pns' in request.POST:
                    video_stream = obj.streams.filter(only_video=True, file_extension='mp4', res='720p').first()
                elif '360pns' in request.POST:
                    video_stream = obj.streams.filter(only_video=True, file_extension='mp4', res='360p').first()
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
                    return JsonResponse({'error': 'No suitable stream found'}, status=500)

            except Exception as e:
                return JsonResponse({'error': 'Error downloading video'}, status=500)
        else:
            return redirect('goback_with_error')

    return redirect('searching')

def goback_with_error(request):
    return render(request, "goback.html")
