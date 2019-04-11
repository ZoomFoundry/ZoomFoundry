
# -*- coding: utf-8 -*-

"""
    zoom.tests.webdriver_tests.test_admin

    test admin app functions
"""

from zoom.testing.webtest import AdminTestCase


class SystemTests(AdminTestCase):
    """MyApp system tests"""

    def add_user(self, first_name, last_name, email, username):
        self.get('/admin')
        self.get('/admin/users')
        self.get('/admin/users/new')
        self.fill(
            dict(
                first_name=first_name,
                last_name=last_name,
                email=email,
                username=username,
            )
        )
        self.chosen('memberships', ['managers'])
        self.click('create_button')

    def delete_user(self, username):
        self.get('/admin')
        self.get('/admin/users')
        self.click_link(username)
        self.click('id=delete-action')
        self.click('name=delete_button')

    def add_group(self, name, description):
        self.get('/admin/groups/new')
        self.fill(
            dict(
                name=name,
            )
        )
        element = self.find('//*[@id="description"]')
        element.send_keys(description)
        self.click('create_button')

    def delete_group(self, name):
        self.get('/admin/groups')
        self.click_link(name)
        self.click('id=delete-action')
        self.click('name=delete_button')

    def test_admin_add_remove_user(self):
        self.get('/admin/users')
        self.assertDoesNotContain('sally')

        self.add_user('Sally', 'Jones', 'sally@testco.com', 'sally')

        self.get('/admin/users')
        self.assertContains('sally')

        self.delete_user('sally')
        self.get('/admin/users')
        self.assertDoesNotContain('sally')

    def test_deactivate_activate_user(self):
        self.get('/admin/users')
        self.assertDoesNotContain('sally')

        try:
            self.add_user('Sally', 'Jones', 'sally@testco.com', 'sally')
            self.assertContains('sally')
            self.get('/admin/users/sally')
            self.assertContains('sally@testco.com')
            self.assertContains('Deactivate')

            self.click('Deactivate')
            self.assertNotContains('Deactivate')

            self.assertContains('sally@testco.com')
            self.assertContains('Activate')
            self.click('Activate')
            self.assertNotContains('Activate')
            self.assertContains('Deactivate')

        finally:
            self.delete_user('sally')
            self.get('/admin/users')
            self.assertDoesNotContain('sally')

    def test_index_search(self):
        self.get('/admin')
        self.fill(dict(q='sally'))
        self.click('search-button')
        self.assertContains('no records found')

        self.add_user('Sally', 'Jones', 'sally@testco.com', 'sally')

        self.get('/admin')
        self.fill(dict(q='sally'))
        self.click('search-button')
        self.assertNotContains('no records found')
        self.assertContains('sally@testco.com')

        self.delete_user('sally')

        self.get('/admin')
        self.fill(dict(q='sally'))
        self.click('search-button')
        self.assertContains('no records found')

    def test_change_group_admin(self):
        self.get('/admin/groups')
        self.assertDoesNotContain('special_group')

        self.add_group('special_group', 'special test group')
        try:

            self.get('/admin/groups')
            self.assertContains('special_group')

            self.get('/admin/groups')
            self.find('//*[@name="link-to-special_group"]').click()
            self.find('//*[@name="link-to-administrators"]')

            self.find('//*[@id="edit-action"]').click()
            self.click("//select[@id='admin_group_id']/option[text()='users']")
            self.click('save_button')
            self.find('//*[@name="link-to-users"]')

            self.find('//*[@id="edit-action"]').click()
            self.click("//select[@id='admin_group_id']/option[text()='administrators']")
            self.click('save_button')
            self.find('//*[@name="link-to-administrators"]')

        finally:
            self.delete_group('special_group')
            self.get('/admin/groups')
            self.assertDoesNotContain('special_group')

