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
            'https://www.youtube.com/watch?',
            'https://www.youtube.com/watch?abc=123',
            'https://www.youtube.com/watch?v=',
            'https://github.com',
            '12345678',
            'hhhhhhhhttps://www.youtube.com/watch',
            'https://minneapolis.edu'
            'https://minneapolis.edu?v=123456'
            '',
            '    sdfsdf sdfsdf   sfsdfsdf',
            '    https://minneapolis.edu?v=123456     ',
            '[',
            '??????????????',
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


class TestVideoList(TestCase):

    # All videos shown on list page, sorted by name, case insensitive

    def test_all_videos_displayed_in_correct_order(self):

        v1 = Video.objects.create(name='XYZ', notes='example', url='https://www.youtube.com/watch?v=123')
        v2 = Video.objects.create(name='ABC', notes='example', url='https://www.youtube.com/watch?v=456')
        v3 = Video.objects.create(name='lmn', notes='example', url='https://www.youtube.com/watch?v=789')
        v4 = Video.objects.create(name='def', notes='example', url='https://www.youtube.com/watch?v=101')

        expected_video_order = [v2, v4, v3, v1]
        response = self.client.get(reverse('video_list'))
        videos_in_template = list(response.context['videos'])
        self.assertEqual(expected_video_order, videos_in_template)


    # No video message 

    def test_no_video_message(self):
        response = self.client.get(reverse('video_list'))
        videos_in_template = response.context['videos']
        self.assertContains(response, 'No videos')
        self.assertEquals(0, len(videos_in_template))


    # 1 video vs 4 videos message

    def test_video_number_message_single_video(self):
        v1 = Video.objects.create(name='XYZ', notes='example', url='https://www.youtube.com/watch?v=123')
        response = self.client.get(reverse('video_list'))
        self.assertContains(response, '1 video')
        self.assertNotContains(response, '1 videos')   # check this, because '1 videos' contains '1 video'


    def test_video_number_message_multiple_videos(self):
        v1 = Video.objects.create(name='XYZ', notes='example', url='https://www.youtube.com/watch?v=123')
        v2 = Video.objects.create(name='ABC', notes='example', url='https://www.youtube.com/watch?v=456')
        v3 = Video.objects.create(name='uvw', notes='example', url='https://www.youtube.com/watch?v=789')
        v4 = Video.objects.create(name='def', notes='example', url='https://www.youtube.com/watch?v=101')

        response = self.client.get(reverse('video_list'))
        self.assertContains(response, '4 videos')


    # search only shows matching videos, partial case-insensitive matches

    def test_video_search_matches(self):
        v1 = Video.objects.create(name='ABC', notes='example', url='https://www.youtube.com/watch?v=456')
        v2 = Video.objects.create(name='nope', notes='example', url='https://www.youtube.com/watch?v=789')
        v3 = Video.objects.create(name='abc', notes='example', url='https://www.youtube.com/watch?v=123')
        v4 = Video.objects.create(name='hello aBc!!!', notes='example', url='https://www.youtube.com/watch?v=101')
        
        expected_video_order = [v1, v3, v4]
        response = self.client.get(reverse('video_list') + '?search_term=abc')
        videos_in_template = list(response.context['videos'])
        self.assertEqual(expected_video_order, videos_in_template)


    def test_video_search_no_matches(self):
        v1 = Video.objects.create(name='ABC', notes='example', url='https://www.youtube.com/watch?v=456')
        v2 = Video.objects.create(name='nope', notes='example', url='https://www.youtube.com/watch?v=789')
        v3 = Video.objects.create(name='abc', notes='example', url='https://www.youtube.com/watch?v=123')
        v4 = Video.objects.create(name='hello aBc!!!', notes='example', url='https://www.youtube.com/watch?v=101')
        
        expected_video_order = []  # empty list 
        response = self.client.get(reverse('video_list') + '?search_term=kittens')
        videos_in_template = list(response.context['videos'])
        self.assertEqual(expected_video_order, videos_in_template)
        self.assertContains(response, 'No videos')


class TestVideoModel(TestCase):

    def test_create_id(self):
        video = Video.objects.create(name='example', url='https://www.youtube.com/watch?v=IODxDxX7oi4')
        self.assertEqual('IODxDxX7oi4', video.video_id)


    def test_create_id_valid_url_with_time_parameter(self):
        # a video that is playing and paused may have a timestamp in the query
        video = Video.objects.create(name='example', url='https://www.youtube.com/watch?v=IODxDxX7oi4&ts=14')
        self.assertEqual('IODxDxX7oi4', video.video_id)


    def test_create_video_notes_optional(self):
        v1 = Video.objects.create(name='example', url='https://www.youtube.com/watch?v=67890')
        v2 = Video.objects.create(name='different example', notes='example', url='https://www.youtube.com/watch?v=12345')
        expected_videos = [v1, v2]
        database_videos = Video.objects.all()
        self.assertCountEqual(expected_videos, database_videos)  # check contents of two lists/iterables but order doesn't matter.