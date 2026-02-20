"""Level 1: junction table name generation, FK/M2M reference properties."""

import pytest

from matrx_orm.core.fields import UUIDField, ForeignKey as FieldFK
from matrx_orm.core.relations import (
    ForeignKeyReference,
    InverseForeignKeyReference,
    ManyToManyField,
    ManyToManyReference,
)


class TestManyToManyFieldJunctionName:
    def test_auto_generated_sorted(self):
        field = ManyToManyField(to_model="Tag")
        name = field.get_junction_table_name("Post")
        assert name == "post_tag"

    def test_auto_generated_reverse_order(self):
        field = ManyToManyField(to_model="Alpha")
        name = field.get_junction_table_name("Zebra")
        assert name == "alpha_zebra"

    def test_custom_db_table(self):
        field = ManyToManyField(to_model="Tag", db_table="custom_junction")
        name = field.get_junction_table_name("Post")
        assert name == "custom_junction"

    def test_same_model_name(self):
        field = ManyToManyField(to_model="User")
        name = field.get_junction_table_name("User")
        assert name == "user_user"


class TestForeignKeyReference:
    def test_attributes(self):
        ref = ForeignKeyReference(
            column_name="author_id",
            to_model="User",
            to_column="id",
            related_name="posts",
            on_delete="CASCADE",
            on_update="CASCADE",
        )
        assert ref.column_name == "author_id"
        assert ref.to_model == "User"
        assert ref.to_column == "id"
        assert ref.related_name == "posts"
        assert ref.on_delete == "CASCADE"
        assert ref.on_update == "CASCADE"

    def test_defaults(self):
        ref = ForeignKeyReference(
            column_name="user_id",
            to_model="User",
            to_column="id",
        )
        assert ref.related_name is None
        assert ref.is_native is False
        assert ref.on_delete == "CASCADE"
        assert ref.on_update == "CASCADE"


class TestInverseForeignKeyReference:
    def test_attributes(self):
        ref = InverseForeignKeyReference(
            from_model="Post",
            from_field="author_id",
            referenced_field="id",
            related_name="authored_posts",
        )
        assert ref.from_model == "Post"
        assert ref.from_field == "author_id"
        assert ref.referenced_field == "id"
        assert ref.related_name == "authored_posts"

    def test_defaults(self):
        ref = InverseForeignKeyReference(
            from_model="Post",
            from_field="author_id",
            referenced_field="id",
        )
        assert ref.related_name is None
        assert ref.is_native is False


class TestManyToManyReference:
    def test_attributes(self):
        ref = ManyToManyReference(
            junction_table="post_tag",
            source_column="post_id",
            target_column="tag_id",
            target_model="Tag",
            related_name="tags",
        )
        assert ref.junction_table == "post_tag"
        assert ref.source_column == "post_id"
        assert ref.target_column == "tag_id"
        assert ref.target_model == "Tag"
        assert ref.related_name == "tags"

    def test_junction_schema_default(self):
        ref = ManyToManyReference(
            junction_table="j",
            source_column="s",
            target_column="t",
            target_model="M",
            related_name="r",
        )
        assert ref.junction_schema is None

    def test_junction_schema_set(self):
        ref = ManyToManyReference(
            junction_table="j",
            source_column="s",
            target_column="t",
            target_model="M",
            related_name="r",
            junction_schema="custom",
        )
        assert ref.junction_schema == "custom"


class TestManyToManyFieldIsNative:
    def test_not_native(self):
        field = ManyToManyField(to_model="Tag")
        assert field.is_native is False
