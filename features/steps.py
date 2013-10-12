# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from lettuce import step, world


Given = When = Then = And = step


@When(u'an anonymous user goes to "([^"]*)"')
def an_anonymous_user_goes_to_group1(step, url_path):
    world.browser.visit("http://localhost:5000")
    world.dom = world.get_dom(response.data)


@When(u'I fill up the "([^"]*)" with "([^"]*)"')
def when_i_fill_up_the_group1_with_group2(step, input_name, value):
    pass

@And(u'submit the form')
def and_submit_the_form(step):
    pass


@Then(u'the email "([^"]*)" is recorded as subscriber')
def then_the_email_group1_is_recorded_as_subscriber(step, group1):
    assert False, 'This step must be implemented'

@And(u'check the option "([^"]*)"')
def and_check_the_option_group1(step, expected_label_content):
    pass

@Then(u'the email "([^"]*)" is recorded as (.*)')
def then_the_email_group1_is_recorded_as_KIND(step, email, kind):
    pass
