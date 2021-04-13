from urllib import parse
from django.db import models
from django.core.exceptions import ValidationError

# Create your models here.

class Video(models.Model):
    name = models.CharField(max_length=200)
    url = models.CharField(max_length=400)
    notes = models.TextField(blank=True, null=True)
    video_id = models.CharField(max_length=40, unique=True)


    def save(self, *args, **kwargs):
        #extract the video id from a youtube url
        if not self.url.startswith('https://www.youtube.com/watch'):
            raise ValidationError(f'Not a Youtube URL {self.url}')
            
        url_components = parse.urlparse(self.url)
        query_string = url_components.query
        if not query_string:
            raise ValidationError(f'Invalid Youtube URL {self.url}')
        parameters = parse.parse_qs(query_string, strict_parsing=True) #dictionary
        v_parameters_list = parameters.get('v') #return None if no key found
        if not v_parameters_list:   # empty string, empty list... 
            raise ValidationError(f'Invalid YouTube URL parameters {self.url}')
        self.video_id = v_parameters_list[0] #string

        super().save(*args, **kwargs) 




    def __str__(self):
        return f'ID: {self.pk}, Name: {self.name}, URL: {self.url}, Video ID: {self.video_id}, Notes: {self.notes[:200]}'
    
