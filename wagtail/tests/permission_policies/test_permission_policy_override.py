from django.test import TestCase, override_settings

from wagtail.models.pages import Locale
from wagtail.models.sites import Site
from wagtail.permission_policies.base import BasePermissionPolicy, ModelPermissionPolicy
from wagtail.permissions import get_permission_policy


class TestPermissionPolicy(BasePermissionPolicy):
    pass


class TestModelPermissionPolicy(BasePermissionPolicy):
    pass


class TestOverridePermissionPolicy(TestCase):
    # Test that the default permission policy is returned when no override is set
    def test_get_permission_policy_without_override(self):
        policy = get_permission_policy("test", ModelPermissionPolicy)(Site)

        self.assertIsInstance(policy, ModelPermissionPolicy)
        self.assertNotIsInstance(policy, TestPermissionPolicy)

    # Test overriding the permission policy using the WAGTAIL_PERMISSION_POLICY_OVERRIDES setting
    @override_settings(
        WAGTAIL_PERMISSION_POLICY_OVERRIDES={
            "test": "wagtail.tests.permission_policies.test_permission_policy_override.TestPermissionPolicy"
        }
    )
    def test_get_permission_policy_with_override(self):
        policy = get_permission_policy("test", ModelPermissionPolicy)(Site)

        self.assertNotIsInstance(policy, ModelPermissionPolicy)
        self.assertIsInstance(policy, TestPermissionPolicy)
        self.assertIsInstance(policy, BasePermissionPolicy)

    # Test if setting the `model` permission policy trickles to other policies that default to the model permission policy.
    @override_settings(
        WAGTAIL_PERMISSION_POLICY_OVERRIDES={
            "model": "wagtail.tests.permission_policies.test_permission_policy_override.TestPermissionPolicy"
        }
    )
    def test_get_permission_policy_with_model_override_trickles_down(self):
        model_permission_policy_class = get_permission_policy(
            "model", default=ModelPermissionPolicy
        )

        locale_permission_policy = get_permission_policy(
            "locale", default=model_permission_policy_class
        )(Locale)

        self.assertNotIsInstance(locale_permission_policy, ModelPermissionPolicy)
        self.assertIsInstance(locale_permission_policy, TestPermissionPolicy)
        self.assertIsInstance(locale_permission_policy, BasePermissionPolicy)

    # Test if setting both model and site policies overrides the default policy for site and locale permission policies.
    @override_settings(
        WAGTAIL_PERMISSION_POLICY_OVERRIDES={
            "model": "wagtail.tests.permission_policies.test_permission_policy_override.TestModelPermissionPolicy",
            "site": "wagtail.tests.permission_policies.test_permission_policy_override.TestPermissionPolicy",
        }
    )
    def test_get_permission_policy_with_model_override_and_site_override(self):
        model_permission_policy_class = get_permission_policy(
            "model", default=ModelPermissionPolicy
        )

        site_permission_policy = get_permission_policy(
            "site", default=model_permission_policy_class
        )(Site)

        locale_permission_policy = get_permission_policy(
            "locale", default=model_permission_policy_class
        )(Locale)

        # The site permission policy should be an instance of TestPermissionPolicy.
        self.assertIsInstance(site_permission_policy, TestPermissionPolicy)
        self.assertIsInstance(site_permission_policy, BasePermissionPolicy)
        self.assertNotIsInstance(site_permission_policy, TestModelPermissionPolicy)

        # The locale permission policy should be an instance of TestModelPermissionPolicy.
        self.assertIsInstance(locale_permission_policy, TestModelPermissionPolicy)
        self.assertIsInstance(locale_permission_policy, BasePermissionPolicy)
        self.assertNotIsInstance(locale_permission_policy, TestPermissionPolicy)
