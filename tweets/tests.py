from django.test import TestCase
from django.urls import reverse

from accounts.forms import User

from .models import Tweet


class TestHomeView(TestCase):
    def setUp(self):
        self.url = reverse("tweets:home")
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.client.login(username="testuser", password="testpassword")
        self.tweet = Tweet.objects.create(user=self.user, content="Test tweet")

    def test_success_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        context_tweets = response.context["tweets"]
        db_tweets = Tweet.objects.all()
        self.assertQuerysetEqual(context_tweets, db_tweets, ordered=False)


class TestTweetCreateView(TestCase):
    def setUp(self):
        self.url = reverse("tweets:create")
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.client.login(username="testuser", password="testpassword")

    def test_success_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_success_post(self):
        valid_data = {"content": "test tweet"}
        response = self.client.post(self.url, valid_data)
        self.assertRedirects(response, "/tweets/home/", status_code=302)
        self.assertTrue(Tweet.objects.filter(content=valid_data["content"]).exists())

    def test_failure_post_with_empty_content(self):
        invalid_data = {"content": ""}
        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]
        self.assertEqual(response.status_code, 200)
        self.assertIn("このフィールドは必須です。", form.errors["content"])
        self.assertFalse(Tweet.objects.filter(content=invalid_data["content"]).exists())

    def test_failure_post_with_too_long_content(self):
        invalid_data = {
            "content": "testtesttesttesttesttesttesttesttesttesttesttesttesttest"
            "testtesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttest"
            "testtesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttest"
        }
        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            f"この値は 140 文字以下でなければなりません( {len(invalid_data['content'])} 文字になっています)。",
            form.errors["content"],
        )
        self.assertFalse(Tweet.objects.filter(content=invalid_data["content"]).exists())


class TestTweetDetailView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.client.login(username="testuser", password="testpassword")
        self.tweet = Tweet.objects.create(user=self.user, content="Test tweet")
        self.url = reverse("tweets:detail", kwargs={"pk": self.tweet.pk})

    def test_success_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Tweet.objects.filter(content=self.tweet.content))


class TestTweetDeleteView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.client.login(username="testuser", password="testpassword")
        self.tweet = Tweet.objects.create(user=self.user, content="Test tweet")
        self.url = reverse("tweets:delete", kwargs={"pk": self.tweet.pk})

    def test_success_post(self):
        response = self.client.post(self.url)
        self.assertRedirects(response, "/tweets/home/", status_code=302)
        self.assertFalse(Tweet.objects.filter(pk=self.tweet.pk).exists())

    def test_failure_post_with_not_exist_tweet(self):
        queryset_before_deletion = Tweet.objects.all()
        not_exist_tweet_pk = 999
        response = self.client.post(reverse("tweets:delete", kwargs={"pk": not_exist_tweet_pk}))
        self.assertEqual(response.status_code, 404)
        self.assertQuerysetEqual(Tweet.objects.all(), queryset_before_deletion)

    def test_failure_post_with_incorrect_user(self):
        queryset_before_deletion = Tweet.objects.all()
        self.user = User.objects.create_user(username="testuser2", password="testpassword2")
        self.client.login(username="testuser2", password="testpassword2")
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 403)
        self.assertQuerysetEqual(Tweet.objects.all(), queryset_before_deletion)


# class TestLikeView(TestCase):
#     def test_success_post(self):

#     def test_failure_post_with_not_exist_tweet(self):

#     def test_failure_post_with_liked_tweet(self):


# class TestUnLikeView(TestCase):

#     def test_success_post(self):

#     def test_failure_post_with_not_exist_tweet(self):

#     def test_failure_post_with_unliked_tweet(self):
