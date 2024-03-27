from threading import Thread

from rest_framework import serializers

from .computations import dynamic_model_create
from .computations.db_centralised_function import extract_foreign_keys
from .models import Hierarchy_table


class ThreadWithReturnValue(Thread):
    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None, *, daemon=None):
        Thread.__init__(self, group, target, name, args, kwargs, daemon=daemon)

        self._return = None

    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args, **self._kwargs)

    def join(self):
        Thread.join(self)
        return self._return


def relationship(model_name, column_list, model, request, model_dict, table_fk_data):

    # Fetching column wise parent and child relationships
    rel_list = [
        dynamic_model_create.relationships(
            model_name, col, request, model, model_dict=model_dict, table_fk_data=table_fk_data
        )
        for col in column_list
    ]
    return rel_list


class TablesSerializer(serializers.Serializer):
    def to_representation(self, instance):
        model_name = instance["tablename"]
        request = self.context["request"]
        # Fetching list of columns for table
        model = dynamic_model_create.get_model_class(model_name, self.context["request"])
        column_list = [field.name for field in model.concrete_fields]
        model_dict = self.context["model_mapping_dict"]
        user_db_engine, db_type, schema = dynamic_model_create.app_engine_generator(request)
        table_fk_data = extract_foreign_keys(f"users_{model_name.lower()}", user_db_engine, db_type)
        twrv = ThreadWithReturnValue(
            target=relationship,
            args=(model_name, column_list, model, request, model_dict, table_fk_data),
        )
        twrv.start()

        rel_list = twrv.join()

        representation = {
            "id": instance["id"],
            "tablename": instance["tablename"],
            "fields": column_list,
            "model_type": instance["model_type"],
            "relationships": rel_list,
        }
        return representation


class RelationshipSerializer(serializers.Serializer):
    """Your data serializer, define your fields here."""

    parent_table = serializers.CharField()
    child_table = serializers.CharField()
    child_element = serializers.CharField()


class HierarchySerializer(serializers.ModelSerializer):
    class Meta:
        model = Hierarchy_table
        fields = (
            "hierarchy_type",
            "hierarchy_group",
            "hierarchy_name",
            "hierarchy_parent_name",
            "hierarchy_level",
            "hierarchy_level_name",
            "hierarchy_description",
            "configuration_date",
        )


class HierarchyGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hierarchy_table
        fields = ("id", "hierarchy_group")


class AddHierarchySerializer(serializers.Serializer):
    """Your data serializer, define your fields here."""

    group_name = serializers.CharField()
    level_name = serializers.CharField()
    field_name = serializers.CharField()
    table_name = serializers.CharField()
