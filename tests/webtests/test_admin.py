
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

    def test_add_remove_subgroup(self):

        self.get('/admin')

        # group 5 = content managers
        self.get('/admin/groups')
        self.assertContains('link-to-guests')

        self.get('/admin/groups/5')
        self.assertDoesNotContain('link-to-guests')

        self.get('/admin/groups/5/edit')
        self.assertDoesNotContain('link-to-guests')

        try:
            self.get('/admin/groups/5/edit')
            self.chosen('subgroups', ['guests'])
            self.click('id=save_button')
            self.assertContains('link-to-guests')

        finally:
            # remove the subgroup we just added
            self.get('/admin/groups/5/edit')
            element = self.find('//*[@id="subgroups_chosen"]/ul/li[2]/a')
            element.click()
            self.click('id=save_button')

        self.get('/admin/groups/5')
        self.assertDoesNotContain('link-to-guests')

    def test_add_remove_role(self):

        self.get('/admin')

        # group 5 = content managers
        self.get('/admin/groups')
        self.assertContains('link-to-guests')

        self.get('/admin/groups/5')
        self.assertDoesNotContain('link-to-guests')

        self.get('/admin/groups/5/edit')
        self.assertDoesNotContain('link-to-guests')

        try:
            self.get('/admin/groups/5/edit')
            self.chosen('subgroups', ['guests'])
            self.click('id=save_button')
            self.assertContains('link-to-guests')

        finally:
            # remove the role we just added
            self.get('/admin/groups/5/edit')
            element = self.find('//*[@id="subgroups_chosen"]/ul/li[2]/a')
            element.click()
            self.click('id=save_button')

        self.get('/admin/groups/5')
        self.assertDoesNotContain('link-to-guests')

    def test_add_remove_app(self):

        # group 5 = content managers
        self.get('/admin/groups/5')
        self.assertDoesNotContain('Register')

        try:
            self.get('/admin/groups/5/edit')
            self.chosen('apps', ['Register'])
            self.click('id=save_button')
            self.assertContains('Register')

        finally:
            # remove the app we just added
            self.get('/admin/groups/5/edit')
            element = self.find('//*[@id="apps_chosen"]/ul/li[1]/a')
            element.click()
            self.click('id=save_button')

        self.get('/admin/groups/5')
        self.assertDoesNotContain('Register')

    def test_add_remove_several_apps(self):

        # group 5 = content managers
        self.get('/admin/groups/5')
        self.assertDoesNotContain('Register')

        # add an app
        self.get('/admin/groups/5/edit')
        self.chosen('apps', ['Register'])
        self.click('id=save_button')
        self.assertContains('Register')

        # add anpther app
        self.get('/admin/groups/5/edit')
        self.chosen('apps', ['Forgot'])
        self.click('id=save_button')
        self.assertContains('Register')
        self.assertContains('Forgot')

        # add one more app
        self.get('/admin/groups/5/edit')
        self.chosen('apps', ['Sample'])
        self.click('id=save_button')
        self.assertContains('Register')
        self.assertContains('Forgot')
        self.assertContains('Sample')

        # remove one of the apps we just added
        self.get('/admin/groups/5/edit')
        element = self.find('//*[@id="apps_chosen"]/ul/li[2]/a')
        element.click()
        self.click('id=save_button')
        self.assertContains('Forgot')
        self.assertDoesNotContain('Register')
        self.assertContains('Sample')

        # remove another one of the apps we just added
        self.get('/admin/groups/5/edit')
        element = self.find('//*[@id="apps_chosen"]/ul/li[2]/a')
        element.click()
        self.click('id=save_button')
        self.assertContains('Forgot')
        self.assertDoesNotContain('Register')
        self.assertDoesNotContain('Sample')

        # remove final app added
        self.get('/admin/groups/5/edit')
        element = self.find('//*[@id="apps_chosen"]/ul/li[1]/a')
        element.click()
        self.click('id=save_button')
        self.assertDoesNotContain('Forgot')
        self.assertDoesNotContain('Register')
        self.assertDoesNotContain('Sample')

    def test_add_remove_user(self):

        # group 5 = content managers
        self.get('/admin/groups/5')
        self.assertDoesNotContain('link-to-guest')

        try:
            self.get('/admin/groups/5/edit')
            self.chosen('users', ['guest'])
            self.click('id=save_button')
            self.assertContains('link-to-guest')

        finally:
            # remove the user we just added
            self.get('/admin/groups/5/edit')
            element = self.find('//*[@id="users_chosen"]/ul/li[1]/a')
            element.click()
            self.click('id=save_button')

        self.get('/admin/groups/5')
        self.assertDoesNotContain('link-to-guests')

    def test_impersonate_user(self):
        self.get('/admin')

        self.add_user('Sally', 'Jones', 'sally@testco.com', 'sally')

        self.get('/admin/users/sally')
        self.click('impersonate-action')

        self.assertContains('Impersonating sally')

        self.click('name=link-to-stop-impersonating')

        self.assertNotContains('Impersonating sally')

        self.delete_user('sally')

