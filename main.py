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

#initializes the database
class Blog(db.Model):
    subject = db.StringProperty(required = True)
    blogpost = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class MainHandler(webapp2.RequestHandler):
    def get(self):
        #redirects to the /blog
        self.redirect("/blog")

class BlogPage(MainHandler):
    #query to get the last 5 created blogposts
    def get(self , subject="", blogpost="", created=""):
        all_posts = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC LIMIT 5")

        #renders the posts
        t = jinja_env.get_template("main-page.html")
        page = t.render(subject = subject, blogpost = blogpost, created = created, all_posts = all_posts)
        self.response.write(page)

class ViewPostHandler(MainHandler):
    # function to handle the output
    def post_form(self, id, subject = "", blogpost = "", created = ""):
        #retrieves the entry from the Blog entity
        selected_post = Blog.get_by_id(int(id))

        #renders the page
        t = jinja_env.get_template("selected_post.html")
        page = t.render(subject = subject, blogpost = blogpost, created = created, selected_post = selected_post)
        self.response.write(page)

    def get(self, id):
        #sends the id to the post form if the id exists in the datastore
        if id:
            self.post_form(id)
        else:
            # the form renders an error in the subject should the entry be invalid
            self.post_form(id, subject = "The entry does not exist")

class NewPost(MainHandler):
    def get(self):
        #renders the new post form
        t = jinja_env.get_template("newpost.html")
        page = t.render()
        self.response.write(page)

    def post(self):
        # retrieves the input fields
        subject_text = self.request.get("subject_text")
        blog_entry = self.request.get("blog_entry")

        # handles the escape for both entries
        escaped_subject = cgi.escape(subject_text, quote=True)
        escaped_blog = cgi.escape(blog_entry, quote=True)

        # sends a redirect to the ViewPostHandler with the post id
        if subject_text and blog_entry:
            blog_list = Blog(subject = escaped_subject, blogpost = escaped_blog)
            blog_list.put()
            self.redirect("/blog/" + str(blog_list.key().id()))
        else:
            # error message if both fields are not completed
            error = "Both fields must be filled out to submit the form"
            t = jinja_env.get_template("newpost.html")
            page = t.render(subject = escaped_subject, blogpost = escaped_blog, error = error)
            self.response.write(page)


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/blog', BlogPage),
    ('/newpost', NewPost),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
], debug=True)
