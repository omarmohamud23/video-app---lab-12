from django.test import TestCase
from django.urls import reverse



from .models import Video

class TestHomePageMessage(TestCase):

    def test_app_title_message_shown_on_home_page(self):
        url = reverse('home')
        response = self.client.get(url)
        self.assertContains(response, 'Exercise Videos')



class TestAddVideos(TestCase):


    def test_add_video(self):

        valid_video = {
            'name': 'yoga',
            'url': 'https://www.youtube.com/watch?v=4vTJHUDB5ak',
            'notes': 'yoga for neck and shoulders'
        }
        
        url = reverse('add_video')
        response = self.client.post(url, data=valid_video, follow=True)

        # redirect to video list 
        self.assertTemplateUsed('video_collection/video_list.html')

        # does video list show new video? 
        self.assertContains(response, 'yoga')
        self.assertContains(response, 'https://www.youtube.com/watch?v=4vTJHUDB5ak')
        self.assertContains(response, 'yoga for neck and shoulders')
        
        video_count = Video.objects.count()
        self.assertEqual(1, video_count)

        video = Video.objects.first() 

        self.assertEqual('yoga', video.name)
        self.assertEqual('https://www.youtube.com/watch?v=4vTJHUDB5ak', video.url)
        self.assertEqual('yoga for neck and shoulders', video.notes)
        self.assertEqual('4vTJHUDB5ak', video.video_id)


    def test_add_video_invalid_url_not_added(self):

        

        invalid_video_urls = [
            'https://www.youtube.com/watch',
            'https://www.youtube.com/watch/somethingelse',
            'https://www.youtube.com/watch/somethingelse?v=1234567',
            'https://www.youtube.com/watch?',
            'https://www.youtube.com/watch?abc=123',
            'https://www.youtube.com/watch?v=',
            'https://github.com',
            '12345678',
            'hhhhhhhhttps://www.youtube.com/watch',
            'http://www.youtube.com/watch/somethingelse?v=1234567',
            'https://minneapolis.edu'
            'https://minneapolis.edu?v=123456'
            '',
            '    sdfsdf sdfsdf   sfsdfsdf',
            '    https://minneapolis.edu?v=123456     ',
            '[',
            '☂️🌟🌷',
            '!@#$%^&*(',
            '//',
            'file://sdfsdf',
        ]


        for invalid_url in invalid_video_urls:

            new_video = {
                'name': 'yoga',
                'url': invalid_url,
                'notes': 'yoga for neck and shoulders'
            }
            
            url = reverse('add_video')
            response = self.client.post(url, new_video, follow=True)

             
            self.assertTemplateUsed('video_collection/add.html')

            
            messages = response.context['messages']
            message_texts = [ message.message for message in messages ]
            
            self.assertIn('Invalid YouTube URL', message_texts)
            self.assertIn('Please check the data entered.', message_texts)
            

            video_count = Video.objects.count()
            self.assertEqual(0, video_count)