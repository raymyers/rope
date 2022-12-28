import pytest

from rope.contrib.autoimport import models


class TestQuery:
    def test_select_non_existent_column(self):
        expected_msg = """Unknown column names passed: {['"]doesnotexist['"]}"""
        with pytest.raises(ValueError, match=expected_msg):
            models.Name.objects.select("doesnotexist")._query


class TestNameModel:
    def test_name_objects(self):
        assert models.Name.objects.select_star()._query == "SELECT * FROM names"

    def test_search_submodule_like(self):
        assert (
            models.Name.search_submodule_like.select_star()._query
            == 'SELECT * FROM names WHERE module LIKE ("%." || ?)'
        )

    def test_search_module_like(self):
        assert (
            models.Name.search_module_like.select_star()._query
            == "SELECT * FROM names WHERE module LIKE (?)"
        )

    def test_import_assist(self):
        assert (
            models.Name.import_assist.select_star()._query
            == "SELECT * FROM names WHERE name LIKE (? || '%')"
        )

    def test_search_by_name_like(self):
        assert (
            models.Name.search_by_name_like.select_star()._query
            == "SELECT * FROM names WHERE name LIKE (?)"
        )

    def test_delete_by_module_name(self):
        assert (
            models.Name.delete_by_module_name._query
            == "DELETE FROM names WHERE module = ?"
        )


class TestPackageModel:
    def test_objects(self):
        assert (
            models.Package.objects.select_star()._query == "SELECT * FROM packages"
        )

    def test_delete_by_package_name(self):
        assert (
            models.Package.delete_by_package_name._query
            == "DELETE FROM packages WHERE package = ?"
        )
