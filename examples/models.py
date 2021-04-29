import datetime

from fastapi_admin.providers.login import AbstractUser
from tortoise import Model, fields

from examples.enums import Action, ProductType, Status


class User(AbstractUser):
    last_login = fields.DatetimeField(
        description="Last Login", default=datetime.datetime.now
    )
    avatar = fields.CharField(max_length=200, default="")
    intro = fields.TextField(default="")
    created_at = fields.DatetimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.pk}#{self.username}"


class Category(Model):
    slug = fields.CharField(max_length=200)
    name = fields.CharField(max_length=200)
    created_at = fields.DatetimeField(auto_now_add=True)


class Product(Model):
    categories = fields.ManyToManyField("models.Category")
    name = fields.CharField(max_length=50)
    view_num = fields.IntField(description="View Num")
    sort = fields.IntField()
    is_reviewed = fields.BooleanField(description="Is Reviewed")
    type = fields.IntEnumField(ProductType, description="Product Type")
    image = fields.CharField(max_length=200)
    body = fields.TextField()
    created_at = fields.DatetimeField(auto_now_add=True)


class Config(Model):
    label = fields.CharField(max_length=200)
    key = fields.CharField(
        max_length=20, unique=True, description="Unique key for config"
    )
    value = fields.JSONField()
    status: Status = fields.IntEnumField(Status, default=Status.on)


class Log(Model):
    user = fields.ForeignKeyField("models.User")
    content = fields.TextField()
    resource = fields.CharField(max_length=50)
    action = fields.CharEnumField(Action, default=Action.create)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        ordering = ["-id"]
