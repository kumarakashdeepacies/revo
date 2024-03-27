class FieldInfo:
    def __init__(
        self,
        name,
        verbose_name,
        primary_key,
        internal_type,
        is_nullable,
        is_unique,
        max_length=None,
        choices=None,
        default=None,
        auto_now=None,
        use_seconds=None,
        editable=None,
        columns=None,
        secure_with=None,
        datakey=None,
        divider=None,
        parent_model=None,
        db_column=None,
        validators={},
        hierarchy_group=None,
        hierarchy_level=None,
        blank=True,
        upload_to=None,
        computed_field=0,
        uuid_config=None,
        file_extension=None,
        video_type=None,
        timerange_type=None,
        datetimerange_type=None,
        daterange_type=None,
        card_config=None,
        table_config=None,
        blacklist_chars=None,
        mulsel_config=None,
        privacy_config=None,
        computed_input=None,
    ):
        self.name = name
        self.verbose_name = verbose_name
        self.primary_key = primary_key
        self.internal_type = internal_type
        self.null = is_nullable
        self.unique = is_unique
        self.editable = False
        self.default = default
        self.editable = editable
        self.parent = parent_model
        self.db_column = db_column
        self.validators = validators
        self.choices = choices
        self.blank = blank
        self.computed_field = computed_field
        self.blacklist_chars = blacklist_chars
        self.computed_input = computed_input
        if self.internal_type in ["CharField", "TextField", "FileField", "URLField", "EmailTypeField"]:
            self.max_length = max_length
            if self.internal_type in ["CharField"]:
                self.secure_with = secure_with
                self.datakey = datakey
        if self.internal_type in ["DateField", "DateTimeField", "TimeField"]:
            self.auto_now = auto_now
            if self.internal_type != "DateField":
                self.use_seconds = use_seconds
        if self.internal_type == "ConcatenationField":
            self.divider = divider
            self.columns = columns
            self.max_length = max_length
        if self.internal_type == "HierarchyField":
            self.hierarchy_group = hierarchy_group
            self.hierarchy_level = hierarchy_level
        if self.internal_type == "FileField":
            self.upload_to = upload_to
        if self.internal_type == "UniqueIDField":
            self.max_length = max_length
            self.uuid_config = uuid_config
        if self.internal_type == "FileField":
            self.file_extension = file_extension
        if self.internal_type == "VideoField":
            self.video_type = video_type
            self.upload_to = upload_to
            self.max_length = max_length
        if self.internal_type == "TimeRangeField":
            self.timerange_type = timerange_type
        if self.internal_type == "DateTimeRangeField":
            self.datetimerange_type = datetimerange_type
        if self.internal_type == "DateRangeField":
            self.daterange_type = daterange_type
        if self.internal_type == "CardField":
            self.max_length = max_length
            self.card_config = card_config
            self.secure_with = secure_with
            self.datakey = datakey
        if self.internal_type == "CardCvvField":
            self.max_length = max_length
            self.secure_with = secure_with
            self.datakey = datakey
        if self.internal_type in ["CardExpiryField", "CardTypeField"]:
            self.secure_with = secure_with
            self.datakey = datakey
        if self.internal_type == "TableField":
            self.max_length = max_length
            self.table_config = table_config
        if self.internal_type == "MultiselectField":
            self.mulsel_config = mulsel_config
        if self.internal_type == "PrivacyField":
            self.privacy_config = privacy_config

    def get_internal_type(self):
        return self.internal_type

    def get_default(self):
        return self.default


class ModelInfo:
    def __init__(self, model_name, json_data, other_config={}):
        self.name = model_name
        self.other_config = other_config
        self.db_table = "users_" + model_name.lower()
        self.concrete_fields = []
        self.field_dict = {}
        self.many_to_many = []
        self.pk = None
        for field, fp in json_data.items():
            verbose_name = fp["verbose_name"]
            internal_type = fp["internal_type"]
            is_nullable = fp["null"]
            is_unique = 0
            is_blank = True
            if fp.get("blank"):
                is_blank = fp["blank"]
            if fp.get("unique"):
                is_unique = fp["unique"]
            editable = True
            if fp.get("editable") not in [None]:
                editable = fp["editable"]
            max_length = 500
            if fp.get("max_length"):
                max_length = fp["max_length"]
            choices = None
            if fp.get("choices"):
                choices = fp["choices"]
            default = None
            if fp.get("default"):
                default = fp["default"]
            auto_now = None
            if fp.get("auto_now"):
                auto_now = fp["auto_now"]
            use_seconds = None
            if fp.get("use_seconds"):
                use_seconds = fp["use_seconds"]
            secure_with = None
            if fp.get("secure_with"):
                secure_with = fp["secure_with"]
            datakey = None
            if fp.get("datakey"):
                datakey = fp["datakey"]
            columns = None
            if fp.get("columns"):
                columns = fp["columns"]
            divider = None
            if fp.get("divider"):
                divider = fp["divider"]
            uuid_config = None
            if fp.get("uuid_config"):
                uuid_config = fp["uuid_config"]
            file_extension = None
            if fp.get("file_extension"):
                file_extension = fp["file_extension"]
            video_type = None
            if fp.get("video_type"):
                video_type = fp["video_type"]
            daterange_type = None
            if fp.get("daterange_type"):
                daterange_type = fp["daterange_type"]
            parent = None
            if fp.get("parent"):
                parent = fp["parent"]
            db_column = None
            if fp.get("db_column"):
                db_column = fp["db_column"]
            primary_key = False
            if fp.get("primary_key"):
                primary_key = fp["primary_key"]
            hierarchy_group = None
            if fp.get("hierarchy_group"):
                hierarchy_group = fp["hierarchy_group"]
            hierarchy_level = None
            if fp.get("hierarchy_level_name"):
                hierarchy_level = fp["hierarchy_level_name"]
            validators = {}
            if fp.get("validators"):
                validators = fp["validators"]
            upload_to = "kore_investment/uploaded_files"
            if fp.get("upload_to"):
                upload_to = fp["upload_to"]
            computed_field = 0
            if fp.get("computed value"):
                computed_field = fp["computed value"]
            timerange_type = None
            if fp.get("timerange_type"):
                timerange_type = fp["timerange_type"]
            datetimerange_type = None
            if fp.get("datetimerange_type"):
                datetimerange_type = fp["datetimerange_type"]
            card_config = None
            if fp.get("card_config"):
                card_config = fp["card_config"]
            table_config = None
            if fp.get("table_config"):
                table_config = fp["table_config"]
            blacklist_chars = None
            if fp.get("blacklist characters"):
                blacklist_chars = fp["blacklist characters"]
            mulsel_config = None
            if fp.get("mulsel_config"):
                mulsel_config = fp["mulsel_config"]
            privacy_config = None
            if fp.get("privacy_config"):
                privacy_config = fp["privacy_config"]
            computed_input = None
            if fp.get("computed input"):
                computed_input = fp["computed input"]
            field_class = FieldInfo(
                name=field,
                verbose_name=verbose_name,
                primary_key=primary_key,
                internal_type=internal_type,
                is_nullable=is_nullable,
                is_unique=is_unique,
                max_length=max_length,
                choices=choices,
                default=default,
                auto_now=auto_now,
                use_seconds=use_seconds,
                editable=editable,
                columns=columns,
                secure_with=secure_with,
                datakey=datakey,
                divider=divider,
                uuid_config=uuid_config,
                parent_model=parent,
                db_column=db_column,
                hierarchy_group=hierarchy_group,
                hierarchy_level=hierarchy_level,
                validators=validators,
                blank=is_blank,
                upload_to=upload_to,
                computed_field=computed_field,
                file_extension=file_extension,
                video_type=video_type,
                timerange_type=timerange_type,
                datetimerange_type=datetimerange_type,
                daterange_type=daterange_type,
                card_config=card_config,
                table_config=table_config,
                blacklist_chars=blacklist_chars,
                mulsel_config=mulsel_config,
                privacy_config=privacy_config,
                computed_input=computed_input,
            )
            self.concrete_fields.append(field_class)
            if primary_key:
                self.pk = field_class
            self.field_dict[field] = field_class
        self._meta = self

    def get_field(self, field_name):
        return self.field_dict[field_name]

    def get_access_controls(self):
        if self.other_config.get("access_controls"):
            return self.other_config.get("access_controls")
        else:
            return None

    def __str__(self):
        return self.name

    def __name__(self):
        return self.name
