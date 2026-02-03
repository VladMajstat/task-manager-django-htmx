from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    class Meta:
        db_table = "user"
        verbose_name = "РљРѕСЂРёСЃС‚СѓРІР°С‡Р°"
        verbose_name_plural = "РљРѕСЂРёСЃС‚СѓРІР°С‡С–"

    def __str__(self):
        return self.username
