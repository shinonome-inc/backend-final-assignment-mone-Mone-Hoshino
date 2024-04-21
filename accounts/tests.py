from django.conf import settings
from django.contrib.auth import SESSION_KEY, get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class TestSignupView(TestCase):
    def setUp(self):
        self.url = reverse("accounts:signup")

    def test_success_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/signup.html")

    def test_success_post(self):
        valid_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password1": "testpassword",
            "password2": "testpassword",
        }

        response = self.client.post(self.url, valid_data)
        login_redirect_url = settings.LOGIN_REDIRECT_URL
        self.assertRedirects(
            response,
            reverse(login_redirect_url),
            status_code=302,
            target_status_code=200,
        )
        self.assertTrue(
            User.objects.filter(
                username=valid_data["username"],
                email=valid_data["email"],
            ).exists()
        )
        self.assertIn(SESSION_KEY, self.client.session)

    def test_failure_post_with_empty_form(self):
        empty_data = {
            "username": "",
            "email": "",
            "password1": "",
            "password2": "",
        }

        response = self.client.post(self.url, data=empty_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.all().count(), 0)

        context = response.context
        form = context["form"]
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["username"][0], "このフィールドは必須です。")
        self.assertEqual(form.errors["email"][0], "このフィールドは必須です。")
        self.assertEqual(form.errors["password1"][0], "このフィールドは必須です。")
        self.assertEqual(form.errors["password2"][0], "このフィールドは必須です。")

    def test_failure_post_with_empty_username(self):
        username_empty_data = {
            "username": "",
            "email": "testmail@example.com",
            "password1": "testpassword",
            "password2": "testpassword",
        }

        response = self.client.post(self.url, data=username_empty_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.all().count(), 0)

        context = response.context
        form = context["form"]
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["username"][0], "このフィールドは必須です。")

    def test_failure_post_with_empty_email(self):
        email_empty_data = {
            "username": "testuser",
            "email": "",
            "password1": "testpassword",
            "password2": "testpassword",
        }

        response = self.client.post(self.url, data=email_empty_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.all().count(), 0)

        context = response.context
        form = context["form"]
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["email"][0], "このフィールドは必須です。")

    def test_failure_post_with_empty_password(self):
        password_empty_data = {
            "username": "testuser",
            "email": "testmail@example.com",
            "password1": "",
            "password2": "",
        }

        response = self.client.post(self.url, data=password_empty_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.all().count(), 0)

        context = response.context
        form = context["form"]
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["password1"][0], "このフィールドは必須です。")
        self.assertEqual(form.errors["password2"][0], "このフィールドは必須です。")

    def test_failure_post_with_duplicated_user(self):
        duplicated_data = {
            "username": "testuser",
            "email": "testmail@example.com",
            "password1": "testpassword",
            "password2": "testpassword",
        }

        User.objects.create_user(
            username="testuser",
            email="testemali@example.com",
            password="testpassword",
        )

        response = self.client.post(self.url, data=duplicated_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.all().count(), 1)

        context = response.context
        form = context["form"]
        self.assertFalse(form.is_valid())
        self.assertEquals(form.errors["username"][0], "同じユーザー名が既に登録済みです。")

    def test_failure_post_with_invalid_email(self):
        invalid_email_data = {
            "username": "testuser",
            "email": "test",
            "password1": "testpassword",
            "password2": "testpassowrd",
        }

        response = self.client.post(self.url, data=invalid_email_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.all().count(), 0)

        context = response.context
        form = context["form"]
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["email"][0], "有効なメールアドレスを入力してください。")

    def test_failure_post_with_too_short_password(self):
        short_password_data = {
            "username": "testuser",
            "email": "testmail@example.com",
            "password1": "short",
            "password2": "short",
        }

        response = self.client.post(self.url, data=short_password_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.all().count(), 0)

        context = response.context
        form = context["form"]
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["password2"][0], "このパスワードは短すぎます。最低 8 文字以上必要です。")

    def test_failure_post_with_password_similar_to_username(self):
        password_similar_to_username_data = {
            "username": "testuser",
            "email": "testmail@example.com",
            "password1": "testuserr",
            "password2": "testuserr",
        }

        response = self.client.post(self.url, data=password_similar_to_username_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.all().count(), 0)

        context = response.context
        form = context["form"]
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["password2"][0], "このパスワードは ユーザー名 と似すぎています。")

    def test_failure_post_with_only_numbers_password(self):
        only_numbers_password_data = {
            "username": "testuser",
            "email": "testmail@example.com",
            "password1": "84927274",
            "password2": "84927274",
        }

        response = self.client.post(self.url, data=only_numbers_password_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.all().count(), 0)

        context = response.context
        form = context["form"]
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["password2"][0], "このパスワードは数字しか使われていません。")

    def test_failure_post_with_mismatch_password(self):
        mismatch_password_data = {
            "username": "testuser",
            "email": "testmail@example.com",
            "password1": "firstpassword",
            "password2": "secondpassword",
        }

        response = self.client.post(self.url, data=mismatch_password_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.all().count(), 0)

        context = response.context
        form = context["form"]
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["password2"][0], "確認用パスワードが一致しません。")


class TestLoginView(TestCase):
    def setUp(self):
        self.url = reverse("accounts:login")
        User.objects.create_user(username="testuser", password="testpassword")

    def test_success_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/login.html")

    def test_success_post(self):
        valid_data = {
            "username": "testuser",
            "password": "testpassword",
        }
        response = self.client.post(self.url, valid_data)

        self.assertRedirects(
            response,
            reverse(settings.LOGIN_REDIRECT_URL),
            status_code=302,
            target_status_code=200,
        )
        self.assertIn(SESSION_KEY, self.client.session)

    def test_failure_post_with_not_exists_user(self):
        nouser_data = {
            "username": "testuser1",
            "password": "testpassword",
        }
        response = self.client.post(self.url, nouser_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertNotIn(SESSION_KEY, self.client.session)
        self.assertIn(
            "正しいユーザー名とパスワードを入力してください。どちらのフィールドも大文字と小文字は区別されます。",
            form.errors["__all__"],
        )

    def test_failure_post_with_empty_password(self):
        emptypass_data = {
            "username": "testuser",
            "password": "",
        }
        response = self.client.post(self.url, emptypass_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertNotIn(SESSION_KEY, self.client.session)
        self.assertIn("このフィールドは必須です。", form.errors["password"])


class TestLogoutView(TestCase):
    def setUp(self):
        self.url = reverse("accounts:logout")
        User.objects.create_user(username="testuser", password="testpassword")
        self.client.login(username="testuser", password="testpassword")

    def test_success_post(self):
        response = self.client.post(self.url)

        self.assertRedirects(response, reverse(settings.LOGOUT_REDIRECT_URL), status_code=302, target_status_code=200)
        self.assertNotIn(SESSION_KEY, self.client.session)


# class TestUserProfileView(TestCase):
#     def test_success_get(self):


# class TestUserProfileEditView(TestCase):
#     def test_success_get(self):

#     def test_success_post(self):

#     def test_failure_post_with_not_exists_user(self):

#     def test_failure_post_with_incorrect_user(self):


# class TestFollowView(TestCase):
#     def test_success_post(self):

#     def test_failure_post_with_not_exist_user(self):

#     def test_failure_post_with_self(self):


# class TestUnfollowView(TestCase):
#     def test_success_post(self):

#     def test_failure_post_with_not_exist_tweet(self):

#     def test_failure_post_with_incorrect_user(self):


# class TestFollowingListView(TestCase):
#     def test_success_get(self):


# class TestFollowerListView(TestCase):
#     def test_success_get(self):
