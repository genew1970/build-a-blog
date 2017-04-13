#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import cgi
import jinja2
import os
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir))

class Blog(db.Model):
    subject = db.StringProperty(required = True)
    blogpost = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class MainHandler(webapp2.RequestHandler):
    def get(self):
        all_posts = db.GqlQuery("SELECT * FROM Blog")
        t = jinja_env.get_template("main-page.html")
        page = t.render(blogpots = all_posts)
        self.response.write(page)

class NewPost(MainHandler):
    def get(self):
        t = jinja_env.get_template("newpost.html")
        page = t.render()
        self.response.write(page)

    def post(self):
        subject_text = self.request.get("subject_text")
        blog_entry = self.request.get("blog_entry")


        escaped_subject = cgi.escape(subject_text, quote=True)
        escaped_blog = cgi.escape(blog_entry, quote=True)

        blog_list = Blog(subject = escaped_subject, blogpost = escaped_blog)
        blog_list.put()

        t = jinja_env.get_template("main-page.html")
        content = t.render(subject_text = subject_text, blog_entry = blog_entry)
        self.response.write(content)

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/newpost', NewPost)
], debug=True)
