"""
Test script to verify the model_cls refactoring works correctly.

This test creates a simple model with a field named 'model' to ensure
there are no conflicts with the internal model_cls parameter.
"""

from matrx_orm import Model, Field


class TestModel(Model):
    """Test model with a field named 'model' to verify no conflicts."""
    
    _table_name = "test_models"
    _database = "test"
    
    id = Field(primary_key=True)
    name = Field()
    model = Field()  # This should now work without conflicts!
    description = Field()


def test_model_definition():
    """Test that the model can be defined with a 'model' field."""
    print("✓ Model definition successful")
    print(f"  Table name: {TestModel._table_name}")
    print(f"  Fields: {list(TestModel._fields.keys())}")
    assert 'model' in TestModel._fields, "Field 'model' should be in _fields"
    print("✓ Field 'model' is properly defined")


def test_model_instantiation():
    """Test that we can create instances with the 'model' field."""
    instance = TestModel(
        id=1,
        name="Test Item",
        model="GPT-4",  # Using 'model' as a field
        description="Test description"
    )
    print("✓ Model instantiation successful")
    print(f"  Instance.model: {instance.model}")
    assert instance.model == "GPT-4", "Field 'model' should store the value"
    print("✓ Field 'model' stores and retrieves values correctly")


def test_reserved_names_doc():
    """Verify the RESERVED_NAMES.md file exists."""
    import os
    doc_path = "/home/arman/projects/matrx-orm/RESERVED_NAMES.md"
    assert os.path.exists(doc_path), "RESERVED_NAMES.md should exist"
    print("✓ RESERVED_NAMES.md documentation exists")


if __name__ == "__main__":
    print("=" * 60)
    print("Testing model_cls Refactoring")
    print("=" * 60)
    print()
    
    try:
        test_model_definition()
        print()
        test_model_instantiation()
        print()
        test_reserved_names_doc()
        print()
        print("=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print()
        print("Summary:")
        print("- Models can now have fields named 'model' without conflicts")
        print("- Internal operations use 'model_cls' parameter")
        print("- RESERVED_NAMES.md documents all reserved names")
        print()
    except AssertionError as e:
        print()
        print("=" * 60)
        print("❌ TEST FAILED!")
        print("=" * 60)
        print(f"Error: {e}")
        exit(1)
    except Exception as e:
        print()
        print("=" * 60)
        print("❌ UNEXPECTED ERROR!")
        print("=" * 60)
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
