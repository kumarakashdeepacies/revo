from django.db import models
from django.db.models import CharField, TextField


class HierarchyField(models.CharField):
    def __init__(self, hierarchy_group=None, field_type=None, *args, **kwargs):
        self.hierarchy_group = hierarchy_group
        self.field_type = "Hierarchy"
        # f"SELECT Hierarchy_name FROM users_hierarchy_table where hierarchy_group = '{hierarchy_group}';", con=engine)
        super().__init__(*args, **kwargs)


class ConcatenationField(models.CharField):
    def __init__(self, divider="-", columns=[], field_type=None, *args, **kwargs):
        self.field_type = "ConcatField"
        self.divider = divider
        self.columns = columns
        super(CharField, self).__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        kwargs["divider"] = self.divider
        kwargs["columns"] = self.columns
        return name, path, args, kwargs


class UniqueIDField(models.CharField):
    def __init__(self, uuid_config=None, field_type=None, *args, **kwargs):
        self.field_type = "UUID"
        super(CharField, self).__init__(*args, **kwargs)

        def deconstruct(self):
            name, path, args, kwargs = super().deconstruct()
            kwargs["uuid_config"] = self.uuid_config
            return name, path, args, kwargs


class URLField(models.TextField):
    def __init__(self, divider="-", columns=[], field_type=None, *args, **kwargs):
        self.field_type = "URL"
        super(TextField, self).__init__(*args, **kwargs)


class FileField(models.CharField):
    def __init__(self, file_extension=None, *args, **kwargs):
        self.field_type = "File"
        self.file_extension = file_extension
        super(CharField, self).__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        kwargs["file_extension"] = self.file_extension
        return name, path, args, kwargs


class VideoField(models.CharField):
    def __init__(self, video_type=None, *args, **kwargs):
        self.video_type = video_type
        super(CharField, self).__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        kwargs["video_type"] = self.video_type
        return name, path, args, kwargs


class DateRangeField(models.CharField):
    def __init__(self, field_type=None, *args, **kwargs):
        self.field_type = field_type
        super(CharField, self).__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        kwargs["daterange_type"] = self.field_type
        return name, path, args, kwargs


class DateTimeRangeField(models.CharField):
    def __init__(self, field_type=None, *args, **kwargs):
        self.field_type = field_type
        super(CharField, self).__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        kwargs["datetimerange_type"] = self.field_type
        return name, path, args, kwargs


class TimeRangeField(models.CharField):
    def __init__(self, field_type=None, *args, **kwargs):
        self.field_type = field_type
        super(CharField, self).__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        kwargs["timerange_type"] = self.field_type
        return name, path, args, kwargs


class CardField(models.CharField):
    def __init__(self, card_config=None, field_type=None, *args, **kwargs):
        self.field_type = "Card"
        super(CharField, self).__init__(*args, **kwargs)

        def deconstruct(self):
            name, path, args, kwargs = super().deconstruct()
            kwargs["card_config"] = self.card_config
            return name, path, args, kwargs


class CardCvvField(models.CharField):
    def __init__(self, field_type=None, *args, **kwargs):
        self.field_type = "CardCvv"
        super(CharField, self).__init__(*args, **kwargs)

        def deconstruct(self):
            name, path, args, kwargs = super().deconstruct()
            return name, path, args, kwargs


class CardExpiryField(models.CharField):
    def __init__(self, field_type=None, *args, **kwargs):
        self.field_type = "CardExpiry"
        super(CharField, self).__init__(*args, **kwargs)

        def deconstruct(self):
            name, path, args, kwargs = super().deconstruct()
            return name, path, args, kwargs


class CardTypeField(models.CharField):
    def __init__(self, field_type=None, *args, **kwargs):
        self.field_type = "CardType"
        super(CharField, self).__init__(*args, **kwargs)

        def deconstruct(self):
            name, path, args, kwargs = super().deconstruct()
            return name, path, args, kwargs


class EmailTypeField(models.CharField):
    def __init__(self, field_type=None, *args, **kwargs):
        self.field_type = field_type
        super(CharField, self).__init__(*args, **kwargs)

        def deconstruct(self):
            name, path, args, kwargs = super().deconstruct()
            return name, path, args, kwargs


class UserField(models.CharField):
    def __init__(self, field_type=None, *args, **kwargs):
        self.field_type = field_type
        super(CharField, self).__init__(*args, **kwargs)

        def deconstruct(self):
            name, path, args, kwargs = super().deconstruct()
            return name, path, args, kwargs


class MultiselectField(models.CharField):
    def __init__(self, card_config=None, field_type=None, *args, **kwargs):
        self.field_type = field_type
        super(CharField, self).__init__(*args, **kwargs)

        def deconstruct(self):
            name, path, args, kwargs = super().deconstruct()
            kwargs["mulsel_config"] = self.card_config
            return name, path, args, kwargs


class TableField(models.CharField):
    def __init__(self, table_config=None, field_type=None, *args, **kwargs):
        self.field_type = "TableField"
        super(CharField, self).__init__(*args, **kwargs)

        def deconstruct(self):
            name, path, args, kwargs = super().deconstruct()
            kwargs["table_config"] = self.table_config
            return name, path, args, kwargs


class RTFField(models.CharField):
    def __init__(self, field_type=None, *args, **kwargs):
        self.field_type = field_type
        super(CharField, self).__init__(*args, **kwargs)

        def deconstruct(self):
            name, path, args, kwargs = super().deconstruct()
            return name, path, args, kwargs


class PrivacyField(models.CharField):
    def __init__(self, privacy_config=None, field_type=None, *args, **kwargs):
        self.field_type = "PrivacyField"
        super(CharField, self).__init__(*args, **kwargs)

        def deconstruct(self):
            name, path, args, kwargs = super().deconstruct()
            kwargs["privacy_config"] = self.privacy_config
            return name, path, args, kwargs
