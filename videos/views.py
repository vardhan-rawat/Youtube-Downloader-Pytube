from django.http import FileResponse
from django.shortcuts import render,redirect
from pytube import YouTube
from urllib.parse import urlencode
from django.urls import reverse

def searching(request):
    if (request.method=="POST"):
        url = request.POST['linkinp']
        query_params = urlencode({'url':url})
        target_url = reverse('download') + f'?{query_params}'

        return redirect(target_url)   
    return render(request, "index.html")



def download(request):
    try:
      obj = YouTube(request.GET.get('url'))
      title=obj.title
      thumbnail=obj.thumbnail_url
      data={
          "title":title,
          "thumbnail":thumbnail,
      }
      if '720p' in request.POST:
        video=obj.streams.filter(progressive=True, file_extension='mp4',res='720p')    
        return FileResponse(open(video.order_by('resolution').desc().first().download(skip_existing=True),'rb'), as_attachment=True)
      elif '360p' in request.POST:
        video=obj.streams.filter(progressive=True, file_extension='mp4',res='360p')
        return FileResponse(open(video.order_by('resolution').desc().first().download(skip_existing=True),'rb'), as_attachment=True)
      elif '720pns' in request.POST:
        video=obj.streams.filter(only_video=True, file_extension='mp4',res='720p')
        return FileResponse(open(video.order_by('resolution').desc().first().download(skip_existing=True),'rb'), as_attachment=True)
      elif '360pns' in request.POST:
        video=obj.streams.filter(only_video=True, file_extension='mp4',res='360p')
        return FileResponse(open(video.order_by('resolution').desc().first().download(skip_existing=True),'rb'), as_attachment=True)
    except:
       return render(request,"goback.html") 
    return render(request,"download.html",data)


