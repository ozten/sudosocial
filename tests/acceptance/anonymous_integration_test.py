#!/usr/bin/env python
import unittest

import selenium

tagline = 'sudoSocial - sudo make me social'
env = 'http://patchouli.ubuntu:8000'

class AnonymousIntegrationTestCase(unittest.TestCase):
    def setUp(self):
        self.selenium = selenium.selenium("localhost", 4444, "*firefox", env)
        self.selenium.start()
        
    def tearDown(self):
        self.selenium.stop()
        pass
        
    def testAnonymousVisitor(self):
        sel = self.selenium
        sel.open('/')
        self.assertEquals(tagline, sel.get_title(), "Homepage rendered")
        self.assertTrue(sel.is_element_present('css=#auth a'))
        actual = sel.get_eval("""
            window.document.getElementById('auth').children[0].getAttribute('href');
                                           """)
        self.assertEquals(actual, "https://sudosocial.me/auth")
        
        sel.click('css=#basic-demo')
        sel.wait_for_page_to_load(3000)
        self.assertTrue(sel.get_eval("window.$('.feed-entry').length;") > 10, "We should have atleast 10 items")
        sel.go_back()
        sel.wait_for_page_to_load(3000)
        
        sel.click('css=#auth a')
        sel.wait_for_page_to_load(6000)
        
        actual = sel.get_body_text().find('OpenID')        
        self.assertTrue(actual > 0, "There is some OpenId copy %d" % actual)
        self.assertTrue(sel.is_element_present('id_openid_identifier'))
        
        sel.open("%s/auth" % env)
        sel.wait_for_page_to_load(3000)
        
        sel.type('id_openid_identifier', 'ozten_test.myopenid.com')
        sel.submit('fopenid')
        #sel.wait_for_page_to_load(5000)
        wait_for_text(sel, 'connect')
        
        sel.type('password', 'password')
        sel.submit('password-signin-form')
        sel.wait_for_page_to_load(5000)
        
        sel.click('continue-button')
        sel.wait_for_page_to_load(5000)
        
        actual = sel.get_body_text().find('profile info')
        self.assertTrue(actual > 0, "We are on the confirm profile page ___%s___" % sel.get_body_text())

def wait_for_it(f):
    print "building a waited func"
    
    def helper(*args):
        print "calling a waited func"
        if f(*args):
            print "method was good"
            return True
        else:
            print "method was bad"
            call_count += 1
            if call_count < 10:
                print "will retry"
                sleep(1)
                helper(*args)
            return False
    return helper

@wait_for_it
def wait_for_text(selenium, text):
    print "in wait for text"
    return text in selenium.get_body_text()


if __name__ == '__main__':
    unittest.main()