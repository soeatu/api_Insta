from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.conf import settings

#プロフィール画像受け取り関数
def upload_avatar_path(instance, filename):
    ext = filename.split('.')[-1]
    return '/'.join(['avatars', str(instance.userProfile.id)+str(instance.nickName)+str(".")+str(ext)])

#投稿時の画像受け取り
def upload_post_path(instance, filename):
    ext = filename.split('.')[-1]
    return '/'.join(['posts', str(instance.userPost.id)+str(instance.title)+str(".")+str(ext)])

#user作成
class UserManager(BaseUserManager):
    def create_user(self, email, password=None):
        #emailをマストにする
        if not email:
            raise ValueError('email is must')
        #emailハッシュ化
        user = self.model(email=self.normalize_email(email))
        #パスワード暗号化
        user.set_password(password)
        #dbに保存
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        user = self.create_user(email, password)
        #Dashboardにログイン権限
        user.is_staff = True
        #全ての権限
        user.is_superuser = True
        user.save(using= self._db)

        return user
#ユーザーモデル
class User(AbstractBaseUser, PermissionsMixin):
    #重複emailを不可
    email = models.EmailField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    #UserManagerを継承
    objects = UserManager()

    USERNAME_FIELD = 'email'
    #文字列を返す特殊関数
    def __str__(self):
        return self.email

#プロフィールモデル
class Profile(models.Model):
    #ユーザー名
    nickName = models.CharField(max_length=20)
    #プロフィール　ユーザー削除時にプロフィールも消す
    userProfile = models.OneToOneField(
        settings.AUTH_USER_MODEL, related_name='userProfile',
        on_delete=models.CASCADE
    )
    created_on = models.DateTimeField(auto_now_add=True)
    img = models.ImageField(blank=True, null=True, upload_to=upload_avatar_path)

    def __str__(self):
        return self.nickName

#postモデル
class Post(models.Model):
    #内容
    title = models.CharField(max_length=100)
    #どのユーザーが投稿したか　
    userPost = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='userPost',
        on_delete=models.CASCADE
    )
    created_on = models.DateTimeField(auto_now_add=True)
    img = models.ImageField(blank=True, null=True, upload_to=upload_post_path)
    liked = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked',blank=True)

    def __str__(self):
        return self.title

#コメントモデル
class Comment(models.Model):
    #内容
    text = models.CharField(max_length=100)
    #誰がコメントしたか
    userComment = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='userComment',
        on_delete=models.CASCADE
    )
    #どの投稿に対してか
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    def __str__(self):
        return self.text